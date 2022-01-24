# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Exceptions thrown by limit function call implementations.

Adapted from https://github.com/sfalkner/pynisher
"""
from azureml.automl.core.shared._error_response_constants import ErrorCodes
from azureml.automl.core.shared.constants import ClientErrors
from azureml.automl.core.shared.exceptions import ClientException, ResourceException


class CpuTimeoutException(ResourceException):
    """Exception to raise when the cpu time exceeded."""

    _error_code = ErrorCodes.EARLYTERMINATION_ERROR

    def __init__(self, exception_message=None, target=None, **kwargs):
        """Constructor."""
        message = ClientErrors.EXCEEDED_TIME_CPU if exception_message is None else exception_message
        super().__init__(message, target, **kwargs)


class TimeoutException(ResourceException):
    """Exception to raise when the total execution time exceeded."""

    _error_code = ErrorCodes.EARLYTERMINATION_ERROR

    def __init__(self, exception_message=None, target=None, **kwargs):
        """Constructor.

        :param value: time consumed
        """
        message = ClientErrors.EXCEEDED_TIME if exception_message is None else exception_message
        super().__init__(message, target, **kwargs)


class SubprocessException(ClientException):
    """Exception to raise when subprocess terminated."""

    _error_code = ErrorCodes.PROCESSKILLED_ERROR

    def __init__(self, exception_message=None, target=None, **kwargs):
        """Constructor.

        :param exception_message: Exception message.
        :param target: The target.
        """
        message = ClientErrors.SUBPROCESS_ERROR if exception_message is None else exception_message
        super().__init__(message, target, **kwargs)
