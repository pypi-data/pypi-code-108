# Copyright (c) Qotto, 2021

"""
Record errors
"""

from typing import Any, Union

__all__ = [
    'RecordAttributeError',
    'RecordAttributeTypeError',
    'RecordAttributeValueError',
]


class RecordAttributeError(Exception):
    """
    Base class for Record related errors
    """


class RecordAttributeTypeError(RecordAttributeError):
    """
    Record attribute has wrong type
    """

    def __init__(self, attribute: str, expected_type: Union[str, type], value: Any) -> None:
        super().__init__(
            f'Record attribute "{attribute}" should be of type "{expected_type}", '
            f'value was "{value}" of type {type(value)}'
        )


class RecordAttributeValueError(RecordAttributeError):
    """
    Record attribute has wrong value
    """

    def __init__(self, attribute: str, value: Any, message: str = None) -> None:
        super().__init__(
            f'Record attribute "{attribute}" has incorrect value "{value}" of type {type(value)}'
            f' (cause: {message or "unspecified"})'
        )
