import random

import numpy
import pandas
import pandas.api.types as ptypes
import pytest
from pydantic import ValidationError

from tktl.core.serializers.base import CustomDeserializingModelT
from tktl.core.serializers.rest.typed import replace_nans_and_infs, to_pydantic
from tktl.core.t import RestSchemaTypes


def random_string():
    return "".join([random.choice("abcde") for _ in range(10)])


def test_from_single_value():
    id_ = random_string()
    schema = to_pydantic(342314, unique_id=id_)
    assert schema.__name__ == f"SingleValue__{id_}"
    assert schema.validate({"value": 1})
    deser = schema(**{"value": 1}).deserialize()
    assert deser == 1


def test_from_series(serializer_df_inputs: pandas.DataFrame):
    series = serializer_df_inputs.A
    id_ = random_string()
    schema = to_pydantic(series, unique_id=id_)
    assert schema.__name__ == f"Series__{id_}"
    rand_values = {"A": [1, 1, 12, 1, 1, 321, None]}
    assert schema.validate(rand_values)
    deser = schema(**rand_values).deserialize()
    assert isinstance(deser, pandas.Series)
    assert ptypes.is_float_dtype(deser.dtype)


def test_from_frame(serializer_df_inputs: pandas.DataFrame):
    id_ = random_string()
    schema = to_pydantic(serializer_df_inputs, unique_id=id_)
    assert schema.__name__ == f"DataFrame__{id_}"
    rand_values = [
        {k: numpy.random.randn(1)[0] for k in serializer_df_inputs.columns}
    ] * 10
    assert schema.validate(rand_values)
    deser = schema.parse_obj(rand_values).deserialize()
    assert isinstance(deser, pandas.DataFrame)
    for col in deser.columns:
        assert ptypes.is_float_dtype(deser[col].dtype)


def test_from_array_1d():
    arr = numpy.random.randn(100)
    id_ = random_string()
    schema = to_pydantic(arr, unique_id=id_)
    assert schema.__name__ == f"{RestSchemaTypes.FLAT_ARRAY.value}__{id_}"
    assert isinstance(schema(value=[1]).__root__, list)
    assert isinstance(schema(value=[1, 10000.0]).__root__, list)


def test_from_multi_dim_array():
    arr = numpy.random.randint(0, 100, size=(10, 5, 2, 2))
    schema = to_pydantic(arr)
    assert schema.__name__ == RestSchemaTypes.ARRAY.value
    sample = numpy.random.randint(0, 100, size=(5, 2, 2)).tolist()
    assert schema.validate([sample])
    with pytest.raises(ValidationError):
        assert schema.validate([[[312, 432], [312, 432]]])

    deser = schema.parse_obj([sample]).deserialize()
    assert isinstance(deser, numpy.ndarray)


def test_nan_handling():
    arr = numpy.random.randn(100)
    arr[0:5] = numpy.nan
    arr[5:10] = numpy.NaN
    schema = to_pydantic(arr)
    assert schema.__name__ == RestSchemaTypes.FLAT_ARRAY.value
    assert isinstance(schema(value=[1]).__root__, list)
    assert schema.schema()["properties"]["value"]["items"]["type"] == "number"
    assert schema.schema()["properties"]["value"]["items"]["type"] == "number"


def test_replace():
    arr = numpy.array([[numpy.nan, 1.1, 1.1], [numpy.inf, 1.1, 3.1]])
    assert replace_nans_and_infs(arr).tolist() == [[None, 1.1, 1.1], [0.0, 1.1, 3.1]]


def test_nan_handling_multi_dim():
    arr = numpy.array(
        [[[numpy.nan, 1.1, numpy.inf], [12.1, 1, 3]], [[1, numpy.nan, 1], [None, 1, 3]]]
    )
    schema = to_pydantic(arr)
    assert schema.__name__ == RestSchemaTypes.ARRAY.value
    sample = numpy.random.randn(2, 3).tolist()
    assert schema.validate([sample])
    assert schema.schema()["items"]["items"]["items"]["type"] == "number"
    assert schema.schema()["example"] == [[[None, 1.1, 0.0], [12.1, 1, 3]]]
    with pytest.raises(ValidationError):
        assert schema.validate([[[312, 432], [312, 432]]])

    deser = schema.parse_obj([sample]).deserialize()
    assert isinstance(deser, numpy.ndarray)


def test_from_sequence():
    sequence = numpy.random.randint(0, 5, size=(10, 2, 2)).tolist()
    schema = to_pydantic(sequence)
    with pytest.raises(ValidationError):
        schema.parse_obj([[1, 2], [3]])
    with pytest.raises(ValidationError):
        schema.parse_obj([[3, 1, 3]])

    parsed = schema.parse_obj([[1, 2], [3, 4]])
    assert isinstance(parsed, CustomDeserializingModelT)
    assert parsed.deserialize() == [[1, 2], [3, 4]]

    deeply_nested_sequence = numpy.random.randint(0, 5, size=(10, 2, 2, 2, 2)).tolist()
    schema = to_pydantic(deeply_nested_sequence)
    parsed = schema.parse_obj(
        [[[[1, 2], [3, 4]], [[1, 2], [3, 4]]], [[[1, 2], [3, 4]], [[1, 2], [3, 4]]]]
    )
    assert parsed.deserialize() == [
        [[[1, 2], [3, 4]], [[1, 2], [3, 4]]],
        [[[1, 2], [3, 4]], [[1, 2], [3, 4]]],
    ]


def test_from_dict_or_list_of_dicts():
    sequence = [{"a": 1, "b": 2}, {"a": 1, "b": 100}]
    mapping_model = to_pydantic(sequence)
    valid = mapping_model(**{"a": 10, "b": 20})
    assert valid.deserialize() == {"a": 10, "b": 20}

    with pytest.raises(ValidationError):
        mapping_model(**{"c": 20, "b": "sdfgasdfg"})
