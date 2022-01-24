# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Exceptions for the package."""

from azureml._common._error_response._error_response_constants import ErrorCodes
from azureml.exceptions import UserErrorException
from azureml.automl.core.shared import exceptions
from typing import Any


class AutoMLVisionRuntimeUserException(exceptions.UserException, UserErrorException):
    """Exception for user errors caught during model training."""


class AutoMLVisionValidationException(exceptions.DataException, UserErrorException):
    """Exception for any errors caught when validating inputs."""

    _error_code = ErrorCodes.VALIDATION_ERROR


class AutoMLVisionDataException(AutoMLVisionValidationException):
    """Exception related to data validations."""

    _error_code = ErrorCodes.INVALIDDATA_ERROR

    def __init__(self, message: str = "", **kwargs: Any) -> None:
        """Init function that accepts message argument.

        In the case of torch.utils.data.DataLoader with num_workers > 0, any exceptions raised in
        worker processes is reraised using this function
        https://github.com/pytorch/pytorch/blob/v1.7.1/torch/_utils.py#L413. If an exception raised
        in worker process has "message" in its properties, this function expects the __init__ method
        to have message argument. Adding it here as we raise AutoMLVisionDataException in
        _RobustCollateFn and it has "message" parameter.
        Please note that this behavior in torch can be changed in future versions
        and this __init__ method needs to be updated accordingly.
        """
        if "exception_message" in kwargs:
            message = kwargs.pop("exception_message")
        super().__init__(exception_message=message, **kwargs)


class AutoMLVisionSystemException(exceptions.AutoMLException):
    """Exception for internal errors that happen within the SDK."""

    _error_code = ErrorCodes.SYSTEM_ERROR


class AutoMLVisionExperimentException(AutoMLVisionSystemException):
    """Exception that happens during AutoML runtime."""


class AutoMLVisionTrainingException(AutoMLVisionExperimentException):
    """Exception for issues that arise during model training."""
