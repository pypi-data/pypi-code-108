from enum import Enum
from typing import List

import pandas
from numpy.testing import assert_array_equal
from pydantic import BaseModel

from tktl.core.serializers import to_pydantic
from tktl.core.serializers.rest import (
    DataFrameSerializer,
    PassThroughSerializer,
    SeriesSerializer,
)


def test_frame_serializer(serializer_df_inputs: pandas.DataFrame):
    model = to_pydantic(serializer_df_inputs)
    as_pydantic_model = DataFrameSerializer.serialize(
        serializer_df_inputs, output_model=model
    )
    assert isinstance(as_pydantic_model, list)
    assert as_pydantic_model[0].index == serializer_df_inputs.index.values[0]
    serialized = model.parse_obj(serializer_df_inputs.to_dict(orient="records"))
    deser = serialized.deserialize()
    assert isinstance(deser, pandas.DataFrame)
    assert list(deser.columns) == list(serializer_df_inputs.columns)
    assert_array_equal(deser["A"].values, serializer_df_inputs["A"].values)
    assert set(serializer_df_inputs.columns.tolist()).issubset(
        set(serialized.dict()["__root__"][0].keys())
    )


def test_series_serializer(serializer_series_inputs: pandas.Series):
    model = to_pydantic(serializer_series_inputs)
    as_pydantic_model = SeriesSerializer.serialize(
        serializer_series_inputs, output_model=model
    )
    assert isinstance(as_pydantic_model, BaseModel)
    assert isinstance(as_pydantic_model.dict()["B"], list)


def test_custom_serializer():
    class Transformation(str, Enum):
        upper = "upper"
        lower = "lower"

    class Payload(BaseModel):
        data: List[str]
        transformation: Transformation

    class Response(BaseModel):
        prediction: List[str]
        transformation: str

    model = to_pydantic(Payload)
    as_pydantic_model = PassThroughSerializer.serialize(
        value=model, output_model=Response
    )
    assert as_pydantic_model == model
