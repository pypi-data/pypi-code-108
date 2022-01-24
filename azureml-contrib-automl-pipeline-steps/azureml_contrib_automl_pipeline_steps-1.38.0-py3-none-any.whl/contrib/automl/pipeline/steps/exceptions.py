# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Exceptions thrown by AutoMLBuilder."""

from azureml._common._error_response._error_response_constants import ErrorCodes
from azureml.exceptions import UserErrorException


class ConflictingTimeoutException(UserErrorException):
    """
    An exception indicating that both run_invocation_timeout and experiment_timeout_hours were incorrectly passed.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.CONFLICTINGSETTINGS_ERROR
