# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import logging
from typing import Any, Dict, Optional, Tuple

import azureml.automl.core._exception_utilities as exception_utilities
from azureml.automl.core._logging.event_logger import EventLogger
from azureml.automl.core._run import AbstractRun, RunType
from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared import utilities as common_utilities
from azureml.automl.core.shared._diagnostics.automl_events import AutoMLBaseEvent, RunFailed
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.core import Run

logger = logging.getLogger(__name__)


@exception_utilities.service_exception_handler(raise_exception=False)
def log_warning_message(run: RunType, warning_message: str) -> None:
    """
    Log a warning on the Run object.
    These would show up as the little yellow boxes on the UI run page.

    Any ServiceExceptions as a result of the call to fail the run are logged and silently ignored.

    :param run: The run object.
    :type run: azureml.automl.core._run.RunType
    :param warning_message: Warning message.
    :type warning_message: str
    :return: None
    """
    Contract.assert_value(run, "run")
    Contract.assert_non_empty(warning_message, "warning_message")
    Contract.assert_type(run, "run", expected_types=(AbstractRun, Run))

    if isinstance(run, AbstractRun):
        logger.warning("Abstract runs don't currently support logging a warning message on the run.")
    else:
        run._client.run.post_event_warning("Run", warning_message)


@exception_utilities.service_exception_handler(raise_exception=False)
def start_run(run: RunType) -> None:
    """
    Mark the run as started.

    Any ServiceExceptions as a result of the call to fail the run are logged and silently ignored.

    :param run: The Run object that needs to transition to a 'Started' state
    :type azureml.automl.core._run.RunType
    :return: None
    """
    Contract.assert_value(run, "run")
    Contract.assert_type(run, "run", expected_types=(AbstractRun, Run))

    logger.info("Marking run {} as Started.".format(run.id))
    run.start()


@exception_utilities.service_exception_handler(raise_exception=False)
def complete_run(run: RunType) -> None:
    """
    Mark the run as Completed.

    Any ServiceExceptions as a result of the call to fail the run are logged and silently ignored.

    :param run: The Run object that needs to transition to a 'Completed' state
    :type azureml.automl.core._run.RunType
    :return: None
    """
    Contract.assert_value(run, "run")
    Contract.assert_type(run, "run", expected_types=(AbstractRun, Run))

    logger.info("Marking run {} as Completed.".format(run.id))
    run.complete()


@exception_utilities.service_exception_handler(raise_exception=False)
def cancel_run(run: RunType, warning_string: Optional[str] = None) -> None:
    """
    Mark the run as Cancelled, with an optional warning string specifying the reason to cancel the run.

    Any ServiceExceptions as a result of the call to fail the run are logged and silently ignored.

    :param run: The Run object that needs to transition to a 'Completed' state
    :param warning_string: An optional message specifying the reason to cancel the run
    :type azureml.automl.core._run.RunType
    :return: None
    """
    Contract.assert_value(run, "run")
    Contract.assert_type(run, "run", expected_types=(AbstractRun, Run))

    if warning_string:
        log_warning_message(run, warning_string)

    logger.info("Marking run {} as Canceled.".format(run.id))
    run.cancel()


@exception_utilities.service_exception_handler(raise_exception=False)
def fail_run(
        run: RunType, exception: BaseException, is_aml_compute: bool = True, update_run_properties: bool = False,
        failure_event: Optional[AutoMLBaseEvent] = None
) -> None:
    """
    Fail the run with the error contained within the exception.

    If the exception is not an instance of AzureMLException, then it is interpreted into one, defaulting to a
    System error code.

    Use the `is_aml_compute` parameter to interpret certain errors, such as client side HTTP issues, as
    user errors. For instance, runs that are not managed by execution service often need to interpret
    such errors as user caused.

    Any ServiceExceptions as a result of the call to fail the run are logged and silently ignored.

    :param run: The run object to fail.
    :type azureml.automl.core._run.RunType
    :param exception: The exception to be used to fail the run.
    :type BaseException
    :param is_aml_compute: If the run is managed by Execution Service and running on an AML Compute
    :type bool
    :param update_run_properties: If the run's properties should be updated with a PII stripped version of exception
    :type bool
    :param failure_event: The failure event. If it is None, we will failover to use the default failure event.
    :type Optional[AutoMLBaseEvent]
    :return: None
    """
    Contract.assert_value(run, "run")
    Contract.assert_type(run, "run", expected_types=(AbstractRun, Run))
    Contract.assert_value(exception, "exception")

    logger.error("Marking Run {} as Failed.".format(run.id))
    logging_utilities.log_traceback(exception, logger)

    # Convert potentially unknown exception type into an interpretable one, so that we can get the
    # right error responses and error codes
    interpreted_exception = common_utilities.interpret_exception(exception, is_aml_compute)
    error_code = common_utilities.get_error_code(interpreted_exception)

    _log_error_event(run, interpreted_exception, failure_event)

    if update_run_properties:
        _update_run_with_log_safe_properties(run, exception)
    run.fail(error_details=interpreted_exception, error_code=error_code)


@exception_utilities.ignore_exceptions
def _log_error_event(
        run: RunType, exception: BaseException, failure_event: Optional[AutoMLBaseEvent] = None) -> None:
    """Log an AutoML RunFailed event in client telemetry"""
    event_logger = EventLogger(run)
    if failure_event is None:
        error_code, error_str = _get_error_code_and_error_str(exception)
        failure_event = RunFailed(run_id=run.id, error_code=error_code, error=error_str)
    event_logger.log_event(failure_event)


def _get_error_code_and_error_str(exception: BaseException) -> Tuple[str, str]:
    """Get error code and error str."""
    error_code = common_utilities.get_error_code(exception, as_hierarchy=True)
    sdk_error_dict = exception_utilities.to_log_safe_sdk_error(exception, error_name="run_error")
    error_str = json.dumps(sdk_error_dict)
    return error_code, error_str


@exception_utilities.ignore_exceptions
def _update_run_with_log_safe_properties(run: RunType, exception: BaseException) -> None:
    """
    Upload a log safe version of exception (message, stacktrace) to the Run DTO, behind the key "errors"

    This is a no-op for an invalid exception type.

    :param run: The run object whose properties to update.
    :param exception: The exception from which to get error details.
    :return: None
    """
    sdk_error_dict = exception_utilities.to_log_safe_sdk_error(exception, error_name="run_error")
    if sdk_error_dict:
        error_dict = {
            "errors": json.dumps(sdk_error_dict)
        }
        run.add_properties(error_dict)
