"""
This module exposes functions to perform validation according to given type or annotation.
It relies mainly on pydantic, and also exposes a function to parse a pydantic BaseModel from almost any python object.
"""
from __future__ import annotations

from collections.abc import Iterable as _Iterable
from inspect import _empty  # type: ignore[attr-defined]

# I don't know why but importing typevar T from mypy works and defining it ourself does not work 😐
from typing import T  # type: ignore[attr-defined]
from typing import (
    Any,
    Iterable,
    Tuple,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
    overload,
)

from pydantic import BaseModel, create_model
from pydantic.main import BaseConfig

ModelT = TypeVar("ModelT", bound=BaseModel)
DataT = TypeVar("DataT")
DefaultT = TypeVar("DefaultT")


class JSONModel(BaseModel):
    body: Any


@overload
def validate(
    _type: Type[DataT],
    data: Any,
) -> DataT:
    ...  # pragma: no cover


@overload
def validate(
    _type: Type[DataT],
    data: None,
    default: DefaultT,
) -> DefaultT:
    ...  # pragma: no cover


@overload
def validate(
    _type: Type[DataT],
    data: Any,
    default: DefaultT,
) -> DataT:
    ...  # pragma: no cover


@overload
def validate(
    _type: T,
    data: Any,
) -> T:
    ...  # pragma: no cover


@overload
def validate(_type: T, data: Any, default: DefaultT) -> T:
    ...  # pragma: no cover


def validate(_type: Any, data: Any, default: Any = ..., encoding: str = "utf-8") -> Any:
    """Perform validation according to given type"""
    is_optional, data_type = _check_optional(_type)
    # Make sure there is a default value for optional parameters
    if is_optional and default in (_empty, ...):
        default = None
    # Handle some simple cases
    if isinstance(data, bytes) and data_type is bytes:
        return data
    elif isinstance(data, bytes) and data_type is str:
        return data.decode(encoding)
    elif isinstance(data, str) and data_type is str:
        return data
    elif isinstance(data, str) and data_type is bytes:
        return data.encode(encoding)
    # If "Any" is used, don't bother to validate
    elif data_type is Any:
        return data
    # Handle case when annotation is optional
    # Default value is always used when provided
    elif data in (None, b""):
        # Handle case when default is available
        if default not in (_empty, ...):
            return default
    # In all other case we must try to parse the given data into data_type
    # Handle case when data_type is a pydantic model
    if _check_pydantic_model(data_type):
        return parse_model(data_type, data)
    # Handle all other cases by generating a dynamic model
    # At this point we can dynamically create a pydantic model
    DataModel: Type[BaseModel] = create_model(
        "DataModel", __root__=(_type, ...), __config__=_BaseConfig
    )
    # We can reuse the parse_model function and return __root__ attribute
    return parse_model(DataModel, data).__root__


def parse_model(
    model: Type[ModelT],
    data: Any = None,
) -> ModelT:
    """Get a pydantic model with given type from message.

    Arguments:
        model: a BaseModel class that should be used to parse the data
        data: data to parse, can be of any type

    Returns:
        An instance of the model class given as argument

    Raises:
        ValidationError: When given data cannot be parsed into desired pydantic model
    """
    if data in (b"", None):
        return model()
    # Handle bytes and strings
    if isinstance(data, (bytes, str)):
        return model.parse_raw(data)
    # Handle mapping and sequences
    elif isinstance(data, (_Iterable, Iterable)):
        return model.parse_obj(data)
    # Handle objects
    return model.from_orm(data)


class _BaseConfig(BaseConfig):
    arbitrary_types_allowed = True


def _check_optional(annotation: Any) -> Tuple[bool, Any]:
    """Check if an annotation is optional"""
    if get_origin(annotation) is Union:
        args = get_args(annotation)
        if type(None) in args:
            return True, annotation
    return False, annotation


def _check_pydantic_model(annotation: Any) -> bool:
    """Check that given object is a valid pydantic model class."""
    try:
        return issubclass(annotation, BaseModel)
    except TypeError:
        return False


__all__ = ["validate", "parse_model"]
