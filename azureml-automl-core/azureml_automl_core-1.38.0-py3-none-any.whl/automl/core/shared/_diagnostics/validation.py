# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from typing import Any, Union, Tuple, Optional

from azureml._common._error_definition import AzureMLError
from azureml._common._error_definition.user_error import ArgumentBlankOrEmpty
from azureml.automl.core.shared._diagnostics.automl_error_definitions import InvalidArgumentType
from azureml.automl.core.shared.exceptions import ValidationException

logger = logging.getLogger(__name__)


class Validation:
    """Class with helper methods to enforce and validate user provided arguments.

    The methods defined in this class will raise a ValidationException, with a user error classification, should
    the validations fail. The specific error codes are dependent on the type of validation. Please check the individual
    method's documentation to see what error code is being raised.
    """

    # Custom type aliases
    Numeric = Union[int, float]

    @staticmethod
    def validate_value(value: Any, name: str, reference_code: Optional[str] = None) -> None:
        """
        Validates that the value is non-null, fails otherwise. For also checking for empty strings or lists, please
        instead see :func:`validate_non_empty`.

        :param value: The object that should be evaluated for the null check.
        :param name: The name of the object.
        :param reference_code: A string that a developer or the user can use to get further context on the error.
        :return: None
        :raises ValidationException (with an 'ArgumentBlankOrEmpty' user error)
        """
        if value is None:
            logger.error("Argument validation failed. Expected argument {} to have a valid value.".format(name))

            raise ValidationException._with_error(AzureMLError.create(
                ArgumentBlankOrEmpty, argument_name=name, target=name, reference_code=reference_code)
            )

    @staticmethod
    def validate_non_empty(value: Any, name: str, reference_code: Optional[str] = None) -> None:
        """
        Validates that the value is non-null and non-empty (as defined by the len attribute), fails otherwise.

        :param value: The object that should be evaluated for the non-empty check.
        :param name: The name of the object.
        :param reference_code: A string that a developer or the user can use to get further context on the error.
        :return: None
        :raises ValidationException (with an 'ArgumentBlankOrEmpty' user error)
        """
        # Check for 'None' value
        Validation.validate_value(value, name, reference_code)

        # Check that value is non-empty, if there's no `len` defined, defaulting to False (i.e. it's a valid value)
        is_empty = len(value) == 0 if hasattr(value, '__len__') else False
        if is_empty:
            logger.error("Argument validation failed. Expected argument {} to have a valid and "
                         "non-empty value.".format(name))
            raise ValidationException._with_error(AzureMLError.create(
                ArgumentBlankOrEmpty, argument_name=name, target=name, reference_code=reference_code)
            )

    @staticmethod
    def validate_type(value: Any, name: str,
                      expected_types: Union[type, Tuple[type, ...]],
                      reference_code: Optional[str] = None) -> None:
        """
        Validates that the value data type is among those provided in expected_types.

        :param value: The object that should be evaluated for type checking
        :param name: The name of the object
        :param expected_types: The argument should adhere to the type (or a tuple of types) specified here.
        :param reference_code: A string that a developer or the user can use to get further context on the error.
        :return: None
        :raises ValidationException (with an 'ArgumentInvalid' user error)
        """
        if not isinstance(value, expected_types):
            logger.error("Argument validation failed. Expected argument {} of type {}, but is of type {}.".format(
                name, expected_types, type(value)))

            raise ValidationException._with_error(AzureMLError.create(
                InvalidArgumentType, target=name, argument=name, actual_type=type(value),
                expected_types=expected_types, reference_code=reference_code)
            )
