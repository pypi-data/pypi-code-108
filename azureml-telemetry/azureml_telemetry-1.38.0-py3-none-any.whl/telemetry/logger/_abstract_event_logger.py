# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Base class for all loggers."""
from abc import ABC, abstractmethod
from os import environ, getenv
import uuid

from azureml.telemetry.log_scope import LogScope as _LogScope
from azureml.telemetry.contracts import StandardFieldKeys, RequiredFieldKeys

HBI_WORKSPACE_JOB_KEY = 'HBI_WORKSPACE_JOB'
HBI_MODE = getenv(HBI_WORKSPACE_JOB_KEY, 'false').lower() != 'false'

try:
    from azureml._base_sdk_common import _ClientSessionId
    _telemetry_session_id = _ClientSessionId
except ImportError:
    _telemetry_session_id = 'l_' + str(uuid.uuid4())


class AbstractEventLogger(ABC):
    """Abstract event logger class."""

    @abstractmethod
    def log_event(self, telemetry_event, white_listed_properties=None):
        """
        Log event.

        :param telemetry_event: The event to be logged.
        :type telemetry_event: TelemetryObjectBase
        :param white_listed_properties: Properties that could be logged without redaction.
        :return: Event GUID.
        :rtype: str
        """
        raise NotImplementedError()

    @abstractmethod
    def log_metric(self, telemetry_metric, white_listed_properties=None):
        """
        Log metric.

        :param telemetry_metric: The metric to be logged.
        :type telemetry_metric: TelemetryObjectBase
        :param white_listed_properties: Properties that could be logged without redaction.
        :return: Metric GUID.
        :rtype: str
        """
        raise NotImplementedError()

    @abstractmethod
    def flush(self):
        """Flush the telemetry client."""
        raise NotImplementedError()

    SESSION_ID = "SessionId"
    SAMPLE_NOTEBOOK_NAME = "SampleNotebookName"

    @staticmethod
    def _redact_fill_props_with_context(telemetry_entry, white_listed_properties=None):
        """Fill telemetry props with context info.

        :param telemetry_entry: An event or metric.
        :param white_listed_properties: The list of property names from extension properties and context that
            should be skipped during redacting.
        :type telemetry_entry: TelemetryObjectBase
        :return properties with context info
        :rtype: dict
        """
        white_listed_properties = white_listed_properties or []
        if HBI_MODE:
            for key in _common_standard_redaction_fields:
                # deal with common fields that need to be redacted
                if key in telemetry_entry.standard_fields and key not in white_listed_properties:
                    telemetry_entry.standard_fields[key] = AbstractEventLogger._redact_string(
                        telemetry_entry.standard_fields[key])
            if telemetry_entry.extension_fields:
                # redact all not white-listed extension fields if needed
                for key in telemetry_entry.extension_fields.keys():
                    if key in white_listed_properties:
                        continue
                    telemetry_entry.extension_fields[key] = AbstractEventLogger._redact_string(
                        telemetry_entry.extension_fields[key])

        props = telemetry_entry.get_all_properties()
        ctx = _LogScope.get_current()
        # merge values from parent scope if any
        props = props if ctx is None else ctx.get_merged_props(props, HBI_MODE, white_listed_properties)
        # set global session id
        props[AbstractEventLogger.SESSION_ID] = _telemetry_session_id
        # set SampleNotebookName if any
        sample_notebook_name = getenv(AbstractEventLogger.SAMPLE_NOTEBOOK_NAME)
        if sample_notebook_name:
            props[AbstractEventLogger.SAMPLE_NOTEBOOK_NAME] = sample_notebook_name
        # set Run Information if any
        subscription_id = environ.get('AZUREML_ARM_SUBSCRIPTION', None)
        workspace_name = environ.get("AZUREML_ARM_WORKSPACE_NAME", None)
        experiment_name = environ.get("AZUREML_ARM_PROJECT_NAME", None)

        run_id = environ.get("AZUREML_RUN_ID", None)
        try:
            # fallback to the old way of getting run information
            if run_id is None:
                from azureml.core import Run
                run = Run.get_context(allow_offline=False)
                run_id = run.id
                subscription_id = run.experiment.workspace.subscription_id
                workspace_name = run.experiment.workspace.name
                experiment_name = run.experiment.name

            props[RequiredFieldKeys.SUBSCRIPTION_ID_KEY] = subscription_id
            props[RequiredFieldKeys.WORKSPACE_ID_KEY] = workspace_name
            props[StandardFieldKeys.RUN_ID_KEY] = run_id
            props['ExperimentName'] = experiment_name
        except Exception as e:
            props['RunContextFailure'] = str(e)

        return props

    @staticmethod
    def _redact_string(value_to_redact):
        return '[REDACTED]'


_common_standard_redaction_fields = [StandardFieldKeys.RUN_ID_KEY, StandardFieldKeys.PARENT_RUN_ID_KEY]
