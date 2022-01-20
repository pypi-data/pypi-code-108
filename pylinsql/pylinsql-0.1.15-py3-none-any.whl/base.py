import dataclasses
import typing
from typing import (
    Any,
    Dict,
    Optional,
    Protocol,
    Type,
    TypeVar,
    Union,
)

T = TypeVar("T")
T1 = TypeVar("T1")
T2 = TypeVar("T2")
T3 = TypeVar("T3")
T4 = TypeVar("T4")
T5 = TypeVar("T5")
T6 = TypeVar("T6")


def is_lambda(v) -> bool:
    "True if (and only if) argument holds a lambda function."

    LAMBDA = lambda: None
    return isinstance(v, type(LAMBDA)) and v.__name__ == LAMBDA.__name__


def is_optional_type(typ: Type[Any]) -> bool:
    "True if the type is an optional type (e.g. Optional[T] or Union[T1,T2,None])."

    if typing.get_origin(typ) is Union:  # Optional[T] is represented as Union[T, None]
        return type(None) in typing.get_args(typ)

    return False


def unwrap_optional_type(typ: Type[Optional[T]]) -> Type[T]:
    "Extracts the type qualified as optional (e.g. returns T for Optional[T])."

    # Optional[T] is represented internally as Union[T, None]
    if typing.get_origin(typ) is not Union:
        raise TypeError("optional type must have un-subscripted type of Union")

    # will automatically unwrap Union[T] into T
    return Union[
        tuple(filter(lambda item: item is not type(None), typing.get_args(typ)))
    ]  # type: ignore


def cast_if_not_none(typ: Type[T], value: Optional[Any]) -> Optional[T]:
    "Coerces an optional value into the specified type unless the value is None."

    if value is None:
        return None
    else:
        return typ(value)


class DataClass(Protocol[T]):
    "Identifies a type as a dataclass type."

    __dataclass_fields__: Dict


def is_dataclass_type(typ) -> bool:
    "True if the argument corresponds to a data class type (but not an instance)."

    return isinstance(typ, type) and dataclasses.is_dataclass(typ)


def is_dataclass_instance(obj) -> bool:
    "True if the argument corresponds to a data class instance (but not a type)."

    return not isinstance(obj, type) and dataclasses.is_dataclass(obj)
