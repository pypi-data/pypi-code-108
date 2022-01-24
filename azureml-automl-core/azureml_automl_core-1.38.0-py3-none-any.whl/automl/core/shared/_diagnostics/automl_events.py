# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""The base class to hold all the AutoML events."""
from abc import ABC
from typing import Any, Dict, Optional
import copy

from azureml.automl.core.shared._error_response_constants import ErrorCodes
from azureml.telemetry.contracts import ExtensionFields
from azureml.telemetry.contracts._standard_fields import FailureReason, TaskResult


class AutoMLBaseEvent(ABC):
    """
    Base class for all AutoML events. Subclasses can override `extension_fields` to log custom fields along with the
    events.The event name defaults to the name of the sub-class.
    """
    SHOULD_EMIT = "should_emit"

    def __init__(self, additional_fields: Optional[Dict[str, Any]] = None) -> None:
        """
        Constructor for AutoML Base Event class.

        :param additional_fields: The additional fields that needs to be added to the ext fields.
        """
        additional_fields = copy.deepcopy(additional_fields)
        self._should_emit = True if not additional_fields else additional_fields.pop(
            AutoMLBaseEvent.SHOULD_EMIT, True)
        self._additional_ext_fields = {} if not additional_fields else additional_fields

    @property
    def event_name(self) -> str:
        """
        The name of the event - same as the class name.
        """
        return self.__class__.__name__

    @property
    def extension_fields(self) -> ExtensionFields:
        """
        The custom properties that describe the event. This is logged in the telemetry under 'custom_dimensions'
        """
        return ExtensionFields(self._additional_ext_fields)

    @property
    def task_result(self) -> TaskResult:
        """
        The task result, describing if the event resulted in a successful or failed operation. Defaults to a neutral
        result (represented by TaskResult.Others, an enum with a value equal to 100)
        """
        return TaskResult.Others

    @property
    def failure_reason(self) -> Optional[FailureReason]:
        """
        If the task result was a failure, the failure reason indicates if the error was User or System caused.
        """
        return None

    @property
    def should_emit(self) -> bool:
        """
        If the event will should be emitted by event logger.
        """
        # We will emit the log in the case that self._should_emit is True, "True", None, "None"
        should_emit = self._should_emit is None or self._should_emit == "None"
        return should_emit or self._should_emit == "True" or (self._should_emit is True)


class RunFailed(AutoMLBaseEvent):
    """
    An AutoML run failure event. This is logged for all AutoML runs, with general information on the error.
    """

    def __init__(
            self,
            run_id: str,
            error_code: str,
            error: str,
            additional_fields: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Constructor for creating a RunFailed Event
        :param run_id: The run identifier for the event.
        :param error_code: The complete error hierarchy
        :param error: A telemetry-friendly (log safe) representation of the error. May include stack traces.
        """
        super(RunFailed, self).__init__(additional_fields)
        self._run_id = run_id
        self._error_code = error_code
        self._error = error

    @property
    def extension_fields(self) -> ExtensionFields:
        ext_fields = super(RunFailed, self).extension_fields
        ext_fields.update(
            {
                "run_id": self._run_id,
                "error_code": self._error_code,
                "error": self._error,
            }
        )
        return ext_fields

    @property
    def failure_reason(self) -> Optional[FailureReason]:
        if ErrorCodes.USER_ERROR in self._error_code:
            return FailureReason.UserError
        else:
            return FailureReason.SystemError

    @property
    def task_result(self) -> TaskResult:
        return TaskResult.Failure


class RunSucceeded(AutoMLBaseEvent):
    """
    An AutoML run succeeded event. This is logged for all AutoML runs, with general information on the error.
    """

    def __init__(self, run_id: str, additional_fields: Optional[Dict[str, Any]] = None) -> None:
        """
        Constructor for creating a RunFailed Event

        :param run_id: The run identifier for the event.
        :param additional_fields: The additional fields that needs to be added to the ext fields.
        """
        super(RunSucceeded, self).__init__(additional_fields)
        self._run_id = run_id

    @property
    def extension_fields(self) -> ExtensionFields:
        ext_fields = super(RunSucceeded, self).extension_fields
        ext_fields.update({"run_id": self._run_id})
        return ext_fields

    @property
    def task_result(self) -> TaskResult:
        return TaskResult.Success
