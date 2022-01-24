from collections.abc import Sequence
from functools import singledispatch
from typing import List, Type, Union, _GenericAlias  # type: ignore

import numpy  # type: ignore
import pandas  # type: ignore
from pydantic import BaseModel

from tktl.core.serializers import rest
from tktl.core.serializers.base import CustomDeserializingModelT


def deserialize_rest(
    model_input: Union[List[CustomDeserializingModelT], CustomDeserializingModelT]
):
    if isinstance(model_input, list):
        return [v.deserialize() for v in model_input]
    else:
        return model_input.deserialize()


@singledispatch
def serialize_rest(
    model_input, output_model: Union[Type[BaseModel], Type[CustomDeserializingModelT]]
):
    return output_model(**{"value": model_input})


@serialize_rest.register
def _pass_through(model_input: BaseModel, output_model: Type[BaseModel]):
    return rest.PassThroughSerializer.serialize(
        value=model_input, output_model=output_model
    )


@serialize_rest.register
def _sequence(model_input: Sequence, output_model: Type[BaseModel]):
    return rest.SequenceSerializer.serialize(
        value=model_input, output_model=output_model
    )


@serialize_rest.register(dict)
def _dict(model_input, output_model: Type[BaseModel]):
    return rest.SequenceSerializer.serialize(
        value=model_input, output_model=output_model
    )


@serialize_rest.register
def _ndarray(model_input: numpy.ndarray, output_model: Type[BaseModel]):
    return rest.ArraySerializer.serialize(value=model_input, output_model=output_model)


@serialize_rest.register
def _df(model_input: pandas.DataFrame, output_model: Type[BaseModel]):
    return rest.DataFrameSerializer.serialize(
        value=model_input, output_model=output_model
    )


@serialize_rest.register
def _series(model_input: pandas.Series, output_model: Type[BaseModel]):
    return rest.SeriesSerializer.serialize(value=model_input, output_model=output_model)


@serialize_rest.register
def _generic(model_input: _GenericAlias, output_model: Type[BaseModel]):
    return model_input
