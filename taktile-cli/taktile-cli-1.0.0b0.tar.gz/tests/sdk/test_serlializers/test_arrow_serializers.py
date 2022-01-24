import json
from typing import Dict, List, Tuple

import numpy
import pandas
import pyarrow
import pytest
from numpy.testing import assert_array_equal
from pandas.testing import assert_frame_equal, assert_series_equal

from tktl.core.exceptions import UnsupportedInputTypeException
from tktl.core.serializers.arrow import (
    ArraySerializer,
    BinarySerializer,
    DataFrameSerializer,
    SequenceSerializer,
    SeriesSerializer,
)


def assert_custom_metadata(table, cls_name, deserialize_steps=None):
    assert table.schema.metadata[b"CLS"] == cls_name.encode()
    if deserialize_steps:
        assert (
            json.loads(table.schema.metadata[b"DESERIALIZERS"].decode("utf-8"))
            == deserialize_steps
        )
    if not deserialize_steps and b"DESERIALIZERS" in table.schema.metadata.keys():
        raise ValueError("Should've passed deserialize_steps")


def test_frame_serializer(serializer_df_inputs: pandas.DataFrame):
    as_arrow = DataFrameSerializer.serialize(serializer_df_inputs)
    assert as_arrow.num_rows == len(serializer_df_inputs)
    assert all([a in as_arrow.column_names for a in list(serializer_df_inputs.columns)])
    deserialized = DataFrameSerializer.deserialize(as_arrow)
    assert_frame_equal(serializer_df_inputs, deserialized)
    assert_custom_metadata(table=as_arrow, cls_name=DataFrameSerializer.__name__)


def test_series_serializer(serializer_series_inputs: pandas.Series):
    as_arrow = SeriesSerializer.serialize(serializer_series_inputs)
    assert as_arrow.column(0).null_count == serializer_series_inputs.isna().sum()
    assert len(as_arrow) == len(serializer_series_inputs)
    deserialized = SeriesSerializer.deserialize(as_arrow)
    assert_series_equal(serializer_series_inputs, deserialized)
    assert_custom_metadata(table=as_arrow, cls_name=SeriesSerializer.__name__)


def test_series_serializer_multi_index(serializer_series_inputs: pandas.Series):
    serializer_series_inputs.index = pandas.MultiIndex.from_arrays(
        [
            serializer_series_inputs.index.tolist(),
            numpy.random.randn(len(serializer_series_inputs)).tolist(),
        ]
    )
    as_arrow = SeriesSerializer.serialize(serializer_series_inputs)
    deserialized = SeriesSerializer.deserialize(as_arrow)
    assert_series_equal(serializer_series_inputs, deserialized)


def test_frame_serializer_with_custom_metadata(serializer_df_inputs: pandas.DataFrame):
    # https://arrow.apache.org/docs/python/data.html#custom-schema-and-field-metadata
    # Undocumented as of 28/9/2020
    as_arrow = DataFrameSerializer.serialize(serializer_df_inputs)
    assert as_arrow.num_rows == len(serializer_df_inputs)
    assert all([a in as_arrow.column_names for a in list(serializer_df_inputs.columns)])
    deserialized = DataFrameSerializer.deserialize(as_arrow)
    assert_frame_equal(serializer_df_inputs, deserialized)


def test_sequence_serializer(
    serializer_dict_inputs: Dict,
    serializer_l_of_d_sequence_inputs: List[Dict],
    serializer_list_and_tuple_inputs: Tuple[List, List, Tuple],
):
    ser = SequenceSerializer.serialize(serializer_dict_inputs)
    assert isinstance(ser, pyarrow.Table)
    deser = SequenceSerializer.deserialize(ser)
    assert isinstance(deser, dict)
    assert deser.keys() == serializer_dict_inputs.keys()
    assert deser["a"] == serializer_dict_inputs["a"]
    assert deser["b"] == serializer_dict_inputs["b"]
    assert_custom_metadata(
        table=ser,
        cls_name=SequenceSerializer.__name__,
        deserialize_steps=["NATIVE_dict", "FINAL_first"],
    )

    ser = SequenceSerializer.serialize(serializer_l_of_d_sequence_inputs)
    assert isinstance(ser, pyarrow.Table)
    deser = SequenceSerializer.deserialize(ser)
    assert isinstance(deser, list)
    assert len(deser) == len(serializer_l_of_d_sequence_inputs)
    assert all(
        [deser[i] == serializer_l_of_d_sequence_inputs[i] for i in range(len(deser))]
    )

    expected_pipeline_steps = (
        ["SELECT_column", "NATIVE_list"],
        ["SELECT_column", "NATIVE_list"],
        ["SELECT_column", "NATIVE_list"],
        ["SELECT_column", "NATIVE_list"],
        ["SELECT_column", "NATIVE_list", "FINAL_tuple"],
    )

    for inp, eps in zip(serializer_list_and_tuple_inputs, expected_pipeline_steps):
        ser = SequenceSerializer.serialize(inp)
        assert isinstance(ser, pyarrow.Table)
        deser = SequenceSerializer.deserialize(ser)
        assert deser == inp
        assert_custom_metadata(
            table=ser, cls_name=SequenceSerializer.__name__, deserialize_steps=eps
        )


def test_1d_and_2d_array_serializer():
    for shapes in [(100,), (50, 2), (25, 4), (10, 10)]:
        arr = numpy.random.randn(100).reshape(shapes)
        as_arrow = ArraySerializer.serialize(arr)
        assert isinstance(as_arrow, pyarrow.Table)
        deserialized = ArraySerializer.deserialize(as_arrow)
        assert isinstance(deserialized, numpy.ndarray)
        assert deserialized.shape == arr.shape
        assert_array_equal(deserialized, arr)
        assert_custom_metadata(table=as_arrow, cls_name=ArraySerializer.__name__)


def test_numpy_ndim_gt_2_arbitrary_serializer():
    arr = numpy.random.randn(100).reshape((10, 5, 2))
    with pytest.raises(UnsupportedInputTypeException):
        ArraySerializer.serialize(arr)

    as_arrow = BinarySerializer.serialize(arr)
    assert isinstance(as_arrow, pyarrow.Table)
    deserialized = BinarySerializer.deserialize(as_arrow)
    assert isinstance(deserialized, numpy.ndarray)
    assert deserialized.shape == arr.shape
    assert_array_equal(deserialized, arr)
