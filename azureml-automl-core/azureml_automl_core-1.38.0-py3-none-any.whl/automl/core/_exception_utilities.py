# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
import sys
from functools import wraps
from typing import Any, Callable, Dict, Optional

from azureml._restclient.exceptions import ServiceException
from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared.logging_utilities import _CustomStackSummary
from azureml.automl.core.shared.logging_utilities import _get_pii_free_message as get_pii_free_message

logger = logging.getLogger(__name__)


def service_exception_handler(raise_exception: bool) -> "Callable[..., Callable[..., Any]]":
    """
    Decorator to handle any service exceptions resulting from a service error during a run update operation.

    :param raise_exception: If the exception should be raised, or just logged and passed.
    :return: Decorator for functions to log/raise exceptions coming out of HTTP calls to AzureML services
    """

    def handler(function: "Callable[..., Any]") -> "Callable[..., Any]":
        @wraps(function)
        def wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except ServiceException as e:
                logging_utilities.log_traceback(e, logger)
                if raise_exception:
                    raise

        return wrapper

    return handler


def ignore_exceptions(function: 'Callable[..., Any]') -> "Callable[..., Any]":
    """
    Decorator for functions to ignore any exceptions raised by any line of code inside it. The resulting exception is
    logged and passed.

    :return: A function decorator to ignore any underlying exceptions coming from the passed function.
    """

    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as e:
            logging_utilities.log_traceback(e, logger)
            return None

    return wrapper


@ignore_exceptions
def to_log_safe_sdk_error(exception: BaseException, error_name: str, is_critical: bool = True) -> Dict[str, Any]:
    """
    Convert an exception to a PII stripped version of itself, with some added metadata.

    This method returns dictionary representing a data model used by Jasmine to read off of a run's properties and
    store in telemetry.

    The schema returned will be:

        {
            "error_name": {
                "exception": <exception string>
                "traceback": <traceback string>
                "has_pii": <True/False>
                "is_critical": <True/False>
            }
        }

    The function is named as such (..._sdk_error) due to an equivalently named class in Jasmine.
    Ref: https://msdata.visualstudio.com/Vienna/_git/vienna?path=
    %2Fsrc%2Fazureml-api%2Fsrc%2FJasmine%2FJasmine.Common.ExceptionHandling%2FSdkError.cs

    :param exception: The exception object.
    :param error_name: The key for the error dictionary.
    :param is_critical: If the error is fatal.
    :return: A log safe representation of the exception. Any invalid values for 'exception' will return None.
    """
    result = {}     # type: Dict[str, Any]

    if not isinstance(exception, BaseException):
        return result

    exception_class_name = exception.__class__.__name__
    error_msg_without_pii = get_pii_free_message(exception)
    exception_details = {"message": error_msg_without_pii, "exception_class": exception_class_name}

    traceback_obj = exception.__traceback__ if hasattr(exception, "__traceback__") else sys.exc_info()[2]
    traceback_msg = _CustomStackSummary.get_traceback_message(traceback_obj, remove_pii=True)

    result[error_name] = {
        "exception": exception_details,
        "traceback": traceback_msg,
        "has_pii": False,
        "is_critical": is_critical,
    }

    return result
