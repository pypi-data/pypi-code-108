"""
Utilities for the Cognite Wells SDK
This module provides helper methods and different utilities for the Cognite Wells SDK
This module is protected and should not be used by end-users.
"""
from typing import Callable


def to_camel_case(snake_case_string: str):
    components = snake_case_string.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def extend_class(cls) -> Callable:
    """Decorator be used for creating extension function on already existing classes

    Args:
        cls: class to be extended
    @return: the extended class
    """
    return lambda f: (setattr(cls, f.__name__, f) or f)  # type: ignore
