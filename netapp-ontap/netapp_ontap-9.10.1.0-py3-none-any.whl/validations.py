"""

Copyright &copy; 2021 NetApp Inc.
All rights reserved.

This module holds validation functions that can be used for field level validation

"""

from typing import Callable, List, TypeVar

from marshmallow import ValidationError  # type: ignore
from netapp_ontap import config


T = TypeVar("T")  # pylint: disable=invalid-name


def enum_validation(choices: List[T]) -> Callable[[T], None]:
    """Verifies that the provided value is one of the possible choices

    Args:
        choices: The list of choices

    Returns:
        A callable function which validates its input value as being part of the set of choices.
    """

    def _validate(value: T) -> None:
        if not config.ENABLE_VALIDATIONS:
            return

        lower_choices = [str(c).lower() for c in choices]
        lower_value = str(value).lower()
        if lower_value not in lower_choices:
            raise ValidationError(f'"{lower_value}" is not one of {lower_choices}')

    return _validate


def len_validation(minimum: int = 0, maximum: int = None) -> Callable[[str], None]:
    """Verify the given string is within the acceptable length limits

    Args:
        minimum: The minimum length the string can be
        maximum: The maximum length the string can be. If unset, maximum is not checked.

    Returns:
        A callable function which validates its input as being between minimum and maximum.
    """

    def _validate(value: str) -> None:
        if not config.ENABLE_VALIDATIONS:
            return

        if not minimum <= len(value):
            raise ValidationError(
                f'"{value}" must be greater than or equal to {minimum} characters.'
            )
        if maximum is not None:
            if not len(value) <= maximum:
                raise ValidationError(
                    f'"{value}" must be less than or equal to {maximum} characters.'
                )

    return _validate

def integer_validation(minimum: int = None, maximum: int = None) -> Callable[[int], None]:
    """Verify that the given value is within the acceptable range

    Args:
        minimum: The minimum value the integer can be
        maximum: The maximum value the integer can be

    Returns:
        A callable function which validates its inputs as being between minimum and maximum.
    """

    def _validate(value: int) -> None:
        if not config.ENABLE_VALIDATIONS:
            return

        if minimum is not None:
            if not minimum <= value:
                raise ValidationError(
                    f'"{value}" must be greater than or equal to {minimum}.'
                )
        if maximum is not None:
            if not value <= maximum:
                raise ValidationError(
                    f'"{value}" must be less than or equal to {maximum}.'
                )

    return _validate
