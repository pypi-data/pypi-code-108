from typing import Any, Optional, Union

from castutils.builtins.strings import to_str
from castutils.types import GenericType


def as_float(obj: Any, /) -> float:
    if isinstance(obj, float):
        return obj
    else:
        raise TypeError("Object is not of instance float")


def as_float_or(obj: Any, fallback: GenericType, /) -> Union[float, GenericType]:

    try:
        return as_float(obj)
    except TypeError:
        return fallback


def to_float(
    obj: Any,
    /,
    encoding: Optional[str] = None,
    errors: Optional[str] = None,
) -> float:

    try:
        if isinstance(obj, float):
            return obj
        elif isinstance(obj, (str, bytes)):
            return float(to_str(obj, encoding=encoding, errors=errors))
        elif isinstance(obj, bool):
            return float(obj)
        return float(obj)
    except Exception as exception:
        raise ValueError("Object cannot transform to float") from exception


def to_float_or(
    obj: Any,
    fallback: GenericType,
    /,
    encoding: Optional[str] = None,
    errors: Optional[str] = None,
) -> Union[float, GenericType]:

    try:
        return to_float(obj, encoding=encoding, errors=errors)
    except ValueError:
        return fallback
