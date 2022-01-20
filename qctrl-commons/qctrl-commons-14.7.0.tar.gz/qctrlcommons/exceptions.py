# Copyright 2021 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#      https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.
"""Module for handling exceptions."""
import json
from functools import wraps
from typing import (
    Callable,
    Dict,
    List,
    Optional,
    Union,
)

import inflection


class QctrlException(Exception):
    """Base class for all qctrl-related errors."""


class QctrlGqlException(QctrlException):
    """Exception for GraphQL errors.

    Attributes
    ----------
    message: Union[List, str]
        exception messages.
    format_to_snake: bool
        option to format snake.


    """

    def __init__(self, message: Union[List, str], format_to_snake=False):

        super().__init__(message)
        self._errors = self._format_gql_errors(message)
        self._is_snake_case_format = format_to_snake

    def __str__(self):
        if not self._errors:
            return "An error occurred while executing the query"

        lines = ["The following errors occurred:"]

        for error in self._errors:
            if isinstance(error, dict) and self._is_snake_case_format:
                error = self.format_gql_error_type(error)
            lines.append(f"- {error}")

        return "\n".join(lines)

    @staticmethod
    def format_gql_error_type(error: Dict) -> Dict:
        """
        Convert the camelCase word to snake_case

        Parameters
        ----------
        error: Dict
            gql error

        Returns
        -------
        Dict
            formatted error
        """
        message = inflection.underscore(error["message"])
        fields = error.get("fields")
        if fields:
            fields = [inflection.underscore(field) for field in fields]
        return {"message": message, "fields": fields}

    @staticmethod
    def _format_gql_errors(message: Union[List, str]):
        """
        format all the gql errors.
        """

        if isinstance(message, list):
            return message.copy()

        # error message might be a list of errors
        try:
            errors = json.loads(message)
            assert isinstance(errors, list)

        # otherwise single error message
        except (json.JSONDecodeError, AssertionError):
            return [message]

        return errors


def wrap_with_qctrl_exception(func: Callable) -> Callable:
    """Wraps any occurring exception with a `QctrlException`. The original
    exception can be accessed through `QctrlException.__cause__`

    Parameters
    ----------
    func : Callable
        a callable object.

    Returns
    -------
    Callable
        the result of the callable.
    """

    @wraps(func)
    def exception_wrapped_f(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            raise QctrlException(f"{exc.__str__()}") from exc

    return exception_wrapped_f


class QctrlGraphIntegrityError(QctrlException):
    """Specialised exception which will be raised
    to handle `Graph` related errors."""


class QctrlArgumentsValueError(QctrlException, ValueError):
    """
    Exception thrown when one or more arguments provided to a method have incorrect values.

    Parameters
    ----------
    description : str
        Description of why the input error occurred.
    arguments : dict
        Dictionary containing the arguments of the method that contributed to the error.
    extras : dict
        Optional. Other variables that contributed to the error but are not arguments of the method.
    """

    def __init__(
        self, description: str, arguments: dict, extras: Optional[dict] = None
    ):
        message = description
        for key in arguments:
            message += "\n" + str(key) + "=" + repr(arguments[key])
        if extras:
            for key in extras:
                message += "\n" + str(key) + "=" + repr(extras[key])
        super().__init__(message)


class QctrlFieldError(QctrlException):
    """Error for input that does not meet validation criteria."""

    def __init__(self, message: str, fields: Optional[List[str]] = None):
        self.message = message
        self.fields = fields
        super().__init__(self.message)
