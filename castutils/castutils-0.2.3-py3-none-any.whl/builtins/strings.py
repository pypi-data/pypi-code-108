from typing import Any, Optional, Union
from uuid import UUID

from castutils.types import GenericType


def as_str(obj: Any, /) -> str:
    if isinstance(obj, str):
        return obj
    else:
        raise TypeError("Object is not of instance str")


def as_str_or(obj: Any, fallback: GenericType, /) -> Union[str, GenericType]:
    try:
        return as_str(obj)
    except TypeError:
        return fallback


def to_str(
    obj: Any,
    /,
    encoding: Optional[str] = None,
    errors: Optional[str] = None,
    form: Optional[str] = None,
) -> str:

    encoding = encoding or "utf-8"
    errors = errors or "strict"

    try:
        if isinstance(obj, str):
            return obj
        elif isinstance(obj, bytes):
            return obj.decode(encoding, errors)
        elif isinstance(obj, UUID):
            if form == "short":
                return obj.hex
        return str(obj)
    except Exception as exception:
        raise ValueError("Object cannot transform to str") from exception


def to_str_or(
    obj: Any,
    fallback: GenericType,
    /,
    encoding: Optional[str] = None,
    errors: Optional[str] = None,
    form: Optional[str] = None,
) -> Union[str, GenericType]:

    try:
        return to_str(obj, encoding=encoding, errors=errors, form=form)
    except ValueError:
        return fallback
