from abc import ABC, abstractmethod
from typing import Any, Dict, List, Sequence, Tuple, Type, _GenericAlias  # type: ignore

import numpy  # type: ignore
import pandas  # type: ignore
from cached_property import cached_property  # type: ignore
from pydantic import BaseModel
from pydantic.main import ModelMetaclass

from tktl.core.loggers import LOG
from tktl.core.serializers import to_pydantic
from tktl.core.serializers.base import CustomDeserializingModelT
from tktl.core.t import RestSchemaTypes
from tktl.core.utils import DelayedLoader, check_and_get_value
from tktl.registration.validation import (
    data_frame_convertible,
    input_pandas_representation,
    output_pandas_representation,
    series_convertible,
)

_SUPPORTS_ARROW_SAMPLE_DATA = [
    DelayedLoader,
    pandas.DataFrame,
    pandas.Series,
    numpy.ndarray,
    Sequence,
    dict,
]
_SUPPORTS_REST_SAMPLE_DATA = _SUPPORTS_ARROW_SAMPLE_DATA + [ModelMetaclass]
_SUPPORTED_TYPES = _SUPPORTS_REST_SAMPLE_DATA + [_GenericAlias]


def check_supported_inputs(value, types):
    return any([isinstance(value, t_) for t_ in types])


class EndpointSchema(ABC):
    KIND: str

    def __init__(
        self,
        value: Any,
        endpoint_kind: str,
        endpoint_name: str,
        user_defined_model: Type[BaseModel] = None,
    ):
        self.endpoint_kind = endpoint_kind
        self.value = value
        self.is_supported = check_supported_inputs(self.value, _SUPPORTED_TYPES)
        self.supports_rest_sample_data = check_supported_inputs(
            self.value, _SUPPORTS_REST_SAMPLE_DATA
        )
        self.supports_arrow_sample_data = check_supported_inputs(
            value, _SUPPORTS_ARROW_SAMPLE_DATA
        )
        if not self.is_supported:
            LOG.warning(
                f"Endpoint '{endpoint_name}': schema discovery not supported for inputs of type {type(value)}"
            )
        if user_defined_model:
            value = user_defined_model

        value = check_and_get_value(value, first_batch=True)
        self.pydantic: Type[CustomDeserializingModelT] = to_pydantic(
            value, unique_id=f"{endpoint_name}__{self.KIND}"
        )

    @cached_property
    @abstractmethod
    def pandas_convertible(self):
        raise NotImplementedError


class EndpointOutputSchema(EndpointSchema):
    KIND = "output"

    @cached_property
    def pandas_convertible(self):
        return series_convertible(self.value)

    @cached_property
    def names(self):
        if self.pandas_convertible:
            return self.pandas_representation.name
        else:
            return get_model_names(self.pydantic)

    @cached_property
    def pandas_representation(self):
        if self.pandas_convertible:
            return output_pandas_representation(self.value)
        else:
            return None


class EndpointInputSchema(EndpointSchema):
    KIND = "input"

    @cached_property
    def pandas_convertible(self):
        value = check_and_get_value(self.value, first_batch=True)
        return data_frame_convertible(value)

    @cached_property
    def names(self):
        if self.pandas_convertible:
            return list(self.pandas_representation.columns)
        else:
            return get_model_names(self.pydantic)

    @cached_property
    def pandas_representation(self):
        if self.pandas_convertible:
            return input_pandas_representation(self.value)
        else:
            return None


def get_model_names(model: CustomDeserializingModelT):
    schema = model.schema()
    if schema["title"] == RestSchemaTypes.DICT.value:
        return list(schema["properties"].keys())
    elif (
        schema["title"] == RestSchemaTypes.SEQUENCE.value
        or schema["title"] == RestSchemaTypes.ARRAY.value
    ):
        return get_nested_type_names(schema)
    else:
        raise ValueError(f"Schema named: {schema['title']} is not recognized")


def get_nested_type_names(schema) -> List[str]:
    schema, inner_type = walk_sequence_schema(schema)
    n_features = schema[0]
    if len(schema) == 1:
        shapes = ""
    else:
        shapes_str = "x".join([str(dim) for dim in schema[1:]])
        shapes = f" (Shape: {shapes_str})"
    return [f"Feature {i}{shapes}" for i in range(n_features)]


def walk_sequence_schema(schema: Dict, shapes=()) -> Tuple[Tuple[int], str]:
    if schema["type"] == "array":
        shapes += (schema["maxItems"],)
        return walk_sequence_schema(schema["items"], shapes=shapes)
    else:
        return shapes, schema["type"]
