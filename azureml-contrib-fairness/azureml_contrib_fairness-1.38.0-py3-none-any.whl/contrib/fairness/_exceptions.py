# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Custom exceptions for AzureML Fairness package."""

# For detailed info on error handling design, see spec:
# https://msdata.visualstudio.com/Vienna/_git/specs?path=%2FErrorHandling%2Ferror-handling-in-azureml-sdk.md
# For error codes see:
# <root>\src\azureml-core\azureml\_common\_error_response\_generate_constants\error_codes.json
from azureml._common._error_response._error_response_constants import ErrorCodes
from azureml.exceptions import UserErrorException


class DashboardValidationException(UserErrorException):
    """An exception raised when a problem is found with a supplied Dashboard dictionary."""

    _error_code = ErrorCodes.VALIDATION_ERROR
