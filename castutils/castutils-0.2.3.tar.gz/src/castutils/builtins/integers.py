from typing import Any, Optional, Union

from castutils.builtins.strings import to_str
from castutils.types import GenericType


def as_int(obj: Any, /) -> int:
    if isinstance(obj, int):
        return obj
    else:
        raise TypeError("Object is not of instance int")


def as_int_or(obj: Any, fallback: GenericType, /) -> Union[int, GenericType]:

    try:
        return as_int(obj)
    except TypeError:
        return fallback


def to_int(
    obj: Any,
    /,
    encoding: Optional[str] = None,
    errors: Optional[str] = None,
) -> int:

    try:
        if isinstance(obj, int):
            return obj
        elif isinstance(obj, (str, bytes)):
            return int(to_str(obj, encoding=encoding, errors=errors))
        elif isinstance(obj, bool):
            return int(obj)
        return int(obj)
    except Exception as exception:
        raise ValueError("Object cannot transform to int") from exception


def to_int_or(
    obj: Any,
    fallback: GenericType,
    /,
    encoding: Optional[str] = None,
    errors: Optional[str] = None,
) -> Union[int, GenericType]:

    try:
        return to_int(obj, encoding=encoding, errors=errors)
    except ValueError:
        return fallback
