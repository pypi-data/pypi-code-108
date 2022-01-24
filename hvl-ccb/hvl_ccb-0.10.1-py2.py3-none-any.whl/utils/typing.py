#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Additional Python typing module utilities
"""
import logging
import sys
from typing import Union, List, Dict, Tuple

import numpy.typing as npt
from typeguard import origin_type_checkers  # type: ignore

if sys.version_info >= (3, 9):
    from types import GenericAlias  # PEP 585

logger = logging.getLogger(__name__)


def is_generic_type_hint(type_):
    """
    Check if class is a generic type, for example `Union[int, float]`,  `List[int]`, or
    `List`.

    :param type_: type to check
    """

    if not (sys.version_info >= (3, 9) and isinstance(type_, GenericAlias)):

        if not hasattr(type_, "__module__"):
            return False

        # check if the class inherits from any `typing` class
        if type_.__module__ != "typing":
            if not any(t.__module__ == "typing" for t in type_.mro()):
                return False

    origin = getattr(type_, "__origin__", type_)  # Note: List.__origin__ == list

    return origin in origin_type_checkers


def check_generic_type(value, type_, name="instance"):
    """
    Check if `value` is of a generic type `type_`. Raises `TypeError` if it's not.

    :param name: name to report in case of an error
    :param value: value to check
    :param type_: generic type to check against
    """
    if not hasattr(type_, "__origin__") or type_.__origin__ not in origin_type_checkers:
        raise ValueError(f"Type {type_} is not a generic type.")
    origin_type_checkers[type_.__origin__](name, value, type_, None)


Number = Union[int, float]
"""Typing hint auxiliary for a Python base number types: `int` or `float`."""

ConvertableTypes = Union[
    int, float, List[Number], Tuple[Number], Dict[str, Number], npt.NDArray
]
"""Typing hint for data type that can be used in conversion"""
