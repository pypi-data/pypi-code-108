from typing import Any, Dict, List, Sequence, Tuple, Type, Union

import numpy  # type: ignore
import pandas  # type: ignore
from pydantic import BaseModel, parse_obj_as
from pydantic.main import ModelMetaclass

from tktl.core.serializers.base import CustomDeserializingModelT, ObjectSerializer
from tktl.core.t import RestSchemaTypes


class DataFrameSerializer(ObjectSerializer):
    @classmethod
    def deserialize(cls, value: CustomDeserializingModelT) -> pandas.DataFrame:
        return value.deserialize()

    @classmethod
    def serialize(
        cls, value: pandas.DataFrame, output_model: Type[BaseModel] = None
    ) -> List[Tuple[str, BaseModel]]:
        assert output_model
        with_index = [
            {**rec, **{"index": value.index[i]}}
            for i, rec in enumerate(value.to_dict(orient="records"))
        ]
        return [p for p in output_model.parse_obj(with_index)]


class SeriesSerializer(ObjectSerializer):
    @classmethod
    def deserialize(cls, value: CustomDeserializingModelT) -> pandas.DataFrame:
        return value.deserialize()

    @classmethod
    def serialize(
        cls, value: pandas.Series, output_model: Type[BaseModel] = None
    ) -> BaseModel:
        assert output_model
        name = _get_prop_from_series_schema(output_model)
        return output_model(**{name: value.tolist()})


class ArraySerializer(ObjectSerializer):
    @classmethod
    def deserialize(cls, value: CustomDeserializingModelT) -> pandas.DataFrame:
        return value.deserialize()

    @classmethod
    def serialize(
        cls, value: numpy.ndarray, output_model: Type[BaseModel] = None
    ) -> BaseModel:
        assert output_model
        if not isinstance(output_model, ModelMetaclass):
            return parse_obj_as(output_model, value.tolist())
        elif output_model.__name__.startswith(RestSchemaTypes.FLAT_ARRAY.value):
            return output_model(value=value.tolist())
        elif output_model.__name__.startswith(RestSchemaTypes.ARRAY.value):
            return output_model.parse_obj(value.tolist()).__root__
        elif output_model.__name__.startswith(RestSchemaTypes.SERIES.value):
            out_name = _get_prop_from_series_schema(output_model)
        else:
            out_name = "value"
        return output_model(**{out_name: value.tolist()})


class SequenceSerializer(ObjectSerializer):
    @classmethod
    def deserialize(cls, value: CustomDeserializingModelT) -> Any:
        return value

    @classmethod
    def serialize(
        cls, value: Union[Sequence, Dict], output_model: Type[BaseModel] = None
    ) -> Union[Dict, List[Dict]]:
        return [v for v in value]


class PassThroughSerializer(ObjectSerializer):
    @classmethod
    def deserialize(cls, value: CustomDeserializingModelT) -> Any:
        return value

    @classmethod
    def serialize(
        cls, value: BaseModel, output_model: Type[BaseModel] = None
    ) -> BaseModel:
        return value


def _get_prop_from_series_schema(schema):
    return list(schema.schema()["properties"].keys())[0]
