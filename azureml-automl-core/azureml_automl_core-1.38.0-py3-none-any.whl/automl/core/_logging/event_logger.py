# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Optional
import copy
import platform
import uuid

from azureml import telemetry
from azureml.core import Run
from azureml.core import __version__ as version
from azureml.telemetry.contracts import (RequiredFields, StandardFields, Event)
from azureml.automl.core.shared._diagnostics.automl_events import AutoMLBaseEvent


class EventLogger:
    """
    An entry point to log events to AzureML telemetry.
    """
    def __init__(self, run: Optional[Run] = None):
        """
        Construct an event logger. If the run is not provided, a default one is grabbed from the context if possible.
        This is used to collect general information about the event, such as:
            - Workspace ID
            - Subscription ID
            - Region
        Other information about the host machine is automatically collected and logged (such as session ID,
        OS architecture, SDK version)

        :param run: An AzureML run.
        """
        workspace_id = None  # type: Optional[str]
        subscription_id = None  # type: Optional[str]
        location = None  # type: Optional[str]
        run_id = None  # type: Optional[str]
        parent_run_id = None  # type: Optional[str]

        if run is None:
            # Init a run from context, if one exists
            run = Run.get_context()

        if isinstance(run, Run) and run.experiment is not None and run.experiment.workspace is not None:
            workspace_id = run.experiment.workspace._workspace_id
            subscription_id = run.experiment.workspace.subscription_id
            location = run.experiment.workspace.location
            run_id = run.id
            parent_run_id = run.parent.id if run.parent is not None else None

        self._req = RequiredFields(
            client_type='SDK',
            client_version=version,
            component_name='automl',
            correlation_id=str(uuid.uuid4()),
            subscription_id=subscription_id,
            workspace_id=workspace_id
        )
        self._std = StandardFields(
            client_os=platform.system(),
            run_id=run_id,
            parent_run_id=parent_run_id,
            workspace_region=location
        )
        self._logger = telemetry.get_event_logger()

    def log_event(self, automl_event: AutoMLBaseEvent) -> None:
        """
        Flush the event to the telemetry.

        :param automl_event: The AutoMLBaseEvent.
        """
        if not isinstance(automl_event, AutoMLBaseEvent) or not automl_event.should_emit:
            return

        std = copy.deepcopy(self._std)
        std.task_result = automl_event.task_result
        std.failure_reason = automl_event.failure_reason
        event = Event(
            name=automl_event.event_name,
            required_fields=self._req,
            standard_fields=std,
            extension_fields=automl_event.extension_fields,
        )
        self._logger.log_event(event)
        self._logger.flush()
