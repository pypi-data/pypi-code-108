from collections.abc import Iterable, Sequence
from functools import singledispatch
from typing import (  # type: ignore
    Any,
    Dict,
    List,
    Optional,
    Type,
    Union,
    _GenericAlias,
    _SpecialForm,
)

import numpy  # type: ignore
import pandas  # type: ignore
from pandas.core.dtypes.inference import is_sequence  # type: ignore
from pydantic import create_model
from pydantic.main import ModelMetaclass

from tktl.core.exceptions.base import TaktileRuntimeError, TaktileSdkError
from tktl.core.serializers.base import CustomDeserializingModelT
from tktl.core.serializers.rest.schema import (
    get_array_model,
    get_custom_model,
    get_dataframe_model,
    get_flat_array_model,
    get_mapping_model,
    get_nested_sequence_model,
    get_series_model,
    get_single_value_model,
)
from tktl.core.serializers.rest.utils import pandas_to_python_type
from tktl.core.t import RestSchemaTypes


@singledispatch
def to_pydantic(
    value: Any, name: str = RestSchemaTypes.SINGLE_VALUE.value, unique_id: str = None
) -> Union[Type[CustomDeserializingModelT], Type[_GenericAlias], _GenericAlias]:
    """
    Single dispatch function for serializing values of each of the supported kinds. Each
    of the dispatched functions' implementation is tailored for one of Taktile's supported
    input types. All the implementations return a custom Pydantic model that implements
    a `deserialize` method to be used when deserializing incoming data as a REST request

    Parameters
    ----------
    value : Any
        Input value to be serialized
    name : str
        Name of the model
    unique_id : str
        Unique identifier of the model

    Returns
    -------
    single_value_model : CustomDeserializingModelT
        The Pydantic-based model
    """
    single_value_model = get_single_value_model(value)
    single_value_model.__name__ = get_model_unique_name(name=name, unique_id=unique_id)
    return single_value_model


@to_pydantic.register
def _custom(
    value: ModelMetaclass,
    name: str = RestSchemaTypes.CUSTOM_MODEL.value,
    unique_id: str = None,
):
    model = get_custom_model(value)
    model.__name__ = get_model_unique_name(name=name, unique_id=unique_id)
    return model


@to_pydantic.register
def _df(
    value: pandas.DataFrame,
    name: str = RestSchemaTypes.DATAFRAME.value,
    unique_id: str = None,
    nullable=True,
):
    type_map = {}
    example_map = {}

    for col in value.columns:
        var_type = pandas_to_python_type(value[col])
        if var_type is None:
            types = (type(v) for _, v in value[col].iteritems() if not pandas.isna(v))
            try:
                var_type = next(types)  # type of first item that is not None
            except StopIteration:
                raise TaktileSdkError(
                    f"Column {col} contains all null values and unable to infer its type with .dtype"
                )

        if nullable:
            var_type = Optional[var_type]

        type_map[col] = (var_type, ...)

        # Make nxt_val (pandas.isna is recursive so need to check for iterable first)
        vals = (
            v
            for _, v in value[col].iteritems()
            if isinstance(v, Iterable) or not pandas.isna(v)
        )

        try:
            nxt_val = next(vals)
        except StopIteration:
            nxt_val = None  # python built-in version of NaN

        example_map[col] = nxt_val

    index_type = type(next((t for t in value.index)))
    type_map["index"] = (index_type, None)  # type: ignore

    base_model = create_model(name, **type_map)  # type: ignore
    inner_model_unique_id = get_model_unique_name(
        name, unique_id=f"{unique_id}__dt_validate"
    )
    dataframe_model = get_dataframe_model(
        base_model=base_model, example=[example_map], unique_id=inner_model_unique_id
    )
    dataframe_model.__name__ = get_model_unique_name(name=name, unique_id=unique_id)
    return dataframe_model


@to_pydantic.register
def _series(
    value: pandas.Series,
    name: str = RestSchemaTypes.SERIES.value,
    unique_id: str = None,
) -> Type[CustomDeserializingModelT]:
    nullable = True if value.isna().sum() > 0 else False
    type_name = "Outcome" if not value.name else value.name
    type_map = {}

    try:
        nxt_val = next(
            v
            for v in value.to_dict().values()
            if isinstance(v, Iterable) or not pandas.isna(v)
        )
    except StopIteration:
        nxt_val = None

    example_map = {type_name: [nxt_val]}

    types = (type(v) for k, v in value.to_dict().items() if not pandas.isna(v))
    var_type = next(types)  # type of first item that is not None
    if var_type == bool:
        var_type = Union[var_type, float]  # type: ignore
    if nullable:
        var_type = Optional[var_type]  # type: ignore
    type_map[type_name] = (List[var_type], None)  # type: ignore
    base_model = create_model(name, **type_map)  # type: ignore
    series_model = get_series_model(
        series=value, base_model=base_model, example=example_map
    )
    series_model.__name__ = get_model_unique_name(name=name, unique_id=unique_id)
    return series_model


@to_pydantic.register
def _array(
    value: numpy.ndarray, name: str = RestSchemaTypes.ARRAY.value, unique_id: str = None
) -> Type[CustomDeserializingModelT]:
    as_list = value.tolist()
    if len(value.shape) == 1:
        first_non_empty = next(v for v in as_list if not pandas.isna(v))
        array_model = get_flat_array_model(
            type(first_non_empty), example=[first_non_empty]
        )
        name = RestSchemaTypes.FLAT_ARRAY.value
        array_model.__name__ = name if not unique_id else f"{name}__{unique_id}"
    else:
        example = replace_nans_and_infs(value[0]).tolist()
        list_model = get_nested_sequence_model(as_list)
        array_model = get_array_model(list_model, example=[example])
        array_model.__name__ = get_model_unique_name(name=name, unique_id=unique_id)
    return array_model


@to_pydantic.register
def _sequence(
    value: Sequence, name: str = RestSchemaTypes.SEQUENCE.value, unique_id: str = None
) -> Type[CustomDeserializingModelT]:
    if isinstance(value, list) or isinstance(value, tuple):
        if len(value) > 0:
            first = value[0]
            if isinstance(first, list):
                sequence_model = get_nested_sequence_model(first)
                sequence_model.__name__ = get_model_unique_name(
                    name=name, unique_id=unique_id
                )

            elif isinstance(first, dict):
                mapping_model = _dict_model(
                    value=first, name=RestSchemaTypes.DICT.value
                )
                sequence_model = get_mapping_model(base_model=mapping_model)
                sequence_model.__name__ = get_model_unique_name(
                    name=name, unique_id=unique_id
                )
            # more specific than numpy's is_sequence implementation
            elif not is_sequence(first):
                sequence_model = get_single_value_model(first)
                sequence_model.__name__ = get_model_unique_name(
                    name=name, unique_id=unique_id
                )
            else:
                raise TaktileRuntimeError
        else:
            raise ValueError("Input must be non-empty")
    else:
        raise TaktileRuntimeError
    return sequence_model


@to_pydantic.register
def _dict(
    value: dict, name: str = RestSchemaTypes.DICT.value, unique_id: str = None
) -> Type[CustomDeserializingModelT]:
    mapping_model = _dict_model(value=value, name=name)
    dict_model = get_mapping_model(mapping_model)
    dict_model.__name__ = get_model_unique_name(name=name, unique_id=unique_id)
    return dict_model


@to_pydantic.register
def _generic(
    value: _GenericAlias, name: str = RestSchemaTypes.ANY.value, unique_id: str = None,
) -> Type[_GenericAlias]:
    return value


@to_pydantic.register
def _any(
    value: _SpecialForm, name: str = RestSchemaTypes.ANY.value, unique_id: str = None,
) -> _GenericAlias:
    return Union[Dict, List, Any]


def _dict_model(value, name):
    types = {k: (type(v), v) for k, v in value.items()}
    return create_model(name, **types)


def _get_df_example(example_map):
    class Config:
        schema_extra = {"example": example_map}

    return Config


def get_model_unique_name(name: str, unique_id: Optional[str]) -> str:
    return name if not unique_id else f"{name}__{unique_id}"


def replace_nans_and_infs(array) -> numpy.ndarray:
    as_float = numpy.isnan(array.astype(numpy.float64))
    as_inf = numpy.isinf(array.astype(numpy.float64))
    replaced_nans = numpy.where(as_float, None, array)
    return numpy.where(as_inf, 0.0, replaced_nans)
