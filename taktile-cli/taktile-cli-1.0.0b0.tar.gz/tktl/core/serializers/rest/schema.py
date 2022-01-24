import json
from collections.abc import Sequence
from datetime import datetime
from typing import Any, Dict, List, Type, Union

import numpy  # type: ignore
import pandas  # type: ignore
from pydantic import BaseModel, Field, conlist, validator

from tktl.core.serializers.base import CustomDeserializingModelT
from tktl.core.serializers.utils import get_list_shape


def get_single_value_model(_value: Any) -> Type[CustomDeserializingModelT]:
    class SingleValueModel(CustomDeserializingModelT):
        value: type(_value)  # type: ignore

        def deserialize(self):
            return self.value

    return SingleValueModel


def get_dataframe_model(
    base_model: Type[BaseModel], example: List[Dict], unique_id: str = None
) -> Type[CustomDeserializingModelT]:
    validates_dt_model = _dt_validator_model(base_model, unique_id=unique_id)

    class DataFrame(CustomDeserializingModelT):
        __root__: List[validates_dt_model]  # type: ignore

        class Config:
            schema_extra = {"example": example}

        def __iter__(self):
            return iter(self.__root__)

        def deserialize(self):
            values = self.dict()["__root__"]
            index = [v.pop("index") for v in values]
            if not all(index):
                return pandas.DataFrame.from_records(values)
            else:
                return pandas.DataFrame.from_records(
                    values, index=pandas.Index(data=index)
                )

    return DataFrame


def get_series_model(
    series: pandas.Series, base_model: Type[BaseModel], example: Dict[str, List] = None
) -> Type[CustomDeserializingModelT]:
    class Series(base_model, CustomDeserializingModelT):  # type: ignore
        _name = series.name
        _dtype = series.dtype

        def deserialize(self):
            values = self.dict()[self._name]
            _series = pandas.Series(values)
            _series = _series.astype(self._dtype)  # column types
            return _series

        class Config:
            schema_extra = {"example": example}

    return Series


def get_jsonable_encoder_sequence_model(
    base_model: Type[BaseModel],
) -> Type[CustomDeserializingModelT]:
    class JsonableEncoderModel(base_model, CustomDeserializingModelT):  # type: ignore
        def deserialize(self):
            return json.loads(self.values)

    return JsonableEncoderModel


def get_nested_sequence_model(sequence: Sequence) -> Type[CustomDeserializingModelT]:
    shape, types = get_list_shape(sequence)
    shape = (None,) + shape[1:]
    inner_model = conlist(Union[types], max_items=shape[-1], min_items=shape[-1])  # type: ignore
    for s in reversed(shape[:-1]):
        inner_model = conlist(inner_model, max_items=s, min_items=s)
    return _nested_sequence_model(inner_models=inner_model)  # type: ignore


def get_array_model(base_model, example: List[Any]) -> Type[CustomDeserializingModelT]:
    class ArrayModel(base_model, CustomDeserializingModelT):  # type: ignore
        def deserialize(self):
            return numpy.array(self.dict()["__root__"])

        class Config:
            schema_extra = {"example": example}

    return ArrayModel


def get_flat_array_model(inner_type: type, example: List[Any]):
    class FlatArray(BaseModel):
        __root__: List[inner_type] = Field(..., alias="value")  # type: ignore

        def deserialize(self):
            return numpy.array(self.dict()["value"])

        class Config:
            schema_extra = {"example": example}

    return FlatArray


def get_mapping_model(base_model: Type[BaseModel]) -> Type[CustomDeserializingModelT]:
    class MappingModel(base_model, CustomDeserializingModelT):  # type: ignore
        def deserialize(self):
            return self.dict()

    return MappingModel


def _dt_validator_model(base_model, unique_id=None):
    class DtValidateModel(base_model):
        @validator("*", each_item=True, allow_reuse=True)
        def remove_tz(cls, v):  # type: ignore
            if isinstance(v, datetime):
                return v.replace(tzinfo=None)
            return v

    DtValidateModel.__name__ = unique_id
    return DtValidateModel


class SequenceEncoderModel(CustomDeserializingModelT):
    __root__: List

    def __iter__(self):
        return iter(self.__root__)

    def deserialize(self):
        return self.dict()["__root__"]


def _nested_sequence_model(inner_models: Type[BaseModel]):
    class NestedSequenceModel(SequenceEncoderModel):
        __root__: inner_models  # type: ignore

    return NestedSequenceModel


def get_custom_model(base_model) -> Type[CustomDeserializingModelT]:
    class CustomModel(base_model, CustomDeserializingModelT):  # type: ignore
        def deserialize(self):
            return self.dict()

    return CustomModel
