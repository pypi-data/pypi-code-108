from functools import partial
from typing import Any, Callable, TypeVar

Transform = Callable[[Any], Any]

T = TypeVar("T")


def IDENTITY(value: T) -> T:
    return value


def IDENTITY_FACTORY(value: T) -> Callable[[], T]:
    return partial(IDENTITY, value)
