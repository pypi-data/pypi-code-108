from typing import Any, Optional, Union

from castutils.builtins.strings import to_str
from castutils.types import GenericType


# BOOL
def as_bool(obj: Any, /) -> bool:
    if isinstance(obj, bool):
        return obj
    else:
        raise TypeError("Object is not of instance bool")


def as_bool_or(obj: Any, fallback: GenericType, /) -> Union[bool, GenericType]:
    try:
        return as_bool(obj)
    except TypeError:
        return fallback


def to_bool(
    obj: Any,
    /,
    encoding: Optional[str] = None,
    errors: Optional[str] = None,
) -> bool:

    try:
        if isinstance(obj, bool):
            return obj
        elif isinstance(obj, (str, bytes)):
            obj = to_str(obj, encoding=encoding, errors=errors)
            if obj in ("y", "yes", "t", "true", "on", "word", "yah", "yay", "1"):
                return True
            elif obj in ("n", "no", "f", "false", "off", "nope", "nah", "nay", "0"):
                return False
        elif isinstance(obj, int):
            return bool(obj)
        return bool(obj)
    except Exception as exception:
        raise ValueError("Object cannot transform to bool") from exception


def to_bool_or(
    obj: Any,
    fallback: Optional[bool] = None,
    /,
    encoding: Optional[str] = None,
    errors: Optional[str] = None,
) -> Optional[bool]:

    try:
        return to_bool(obj, encoding=encoding, errors=errors)
    except ValueError:
        return fallback
