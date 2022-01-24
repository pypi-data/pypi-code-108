# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Represents a class used to log events and metrics to Application Insights.."""
import logging

from applicationinsights import TelemetryClient
from applicationinsights.channel import SynchronousQueue, TelemetryChannel, TelemetryContext
from azureml.telemetry.logging_handler import _RetrySynchronousSender
from ._abstract_event_logger import AbstractEventLogger, _ClientSessionId


class ApplicationInsightsEventLogger(AbstractEventLogger):
    """Represents a class used to log events and metrics to Application Insights.

    For more information see,
    `What is Application Insights? <https://docs.microsoft.com/azure/azure-monitor/app/app-insights-overview>`_.

    .. remarks::

        For more information see,
        `What is Application Insights? <https://docs.microsoft.com/azure/azure-monitor/app/app-insights-overview>`_.

    :param instrumentation_key: The Application Insights instrumentation key to use for sending telemetry.
    :param args: Optional arguments for formatting messages.
    :type args: list
    :param kwargs: Optional keyword arguments for adding additional information to messages.
    :type kwargs: dict
    """

    def __init__(self, instrumentation_key, *args, **kwargs):
        """
        Initialize a new instance of the ApplicationInsightsLogger.

        :param instrumentation_key: The Application Insights instrumentation key to use for sending telemetry.
        :type instrumentation_key: str
        :param args: Optional arguments for formatting messages.
        :type args: list
        :param kwargs: Optional keyword arguments for adding additional information to messages.
        :type kwargs: dict
        """
        self.logger = logging.getLogger(__name__)
        self._sender = _RetrySynchronousSender
        self.telemetry_client = TelemetryClient(instrumentation_key,
                                                self._create_synchronous_channel(TelemetryContext()))
        # flush telemetry every 30 seconds (assuming we don't hit max_queue_item_count first)
        self.telemetry_client.channel.sender.send_interval_in_milliseconds = 30 * 1000
        # flush telemetry if we have 10 or more telemetry items in our queue
        self.telemetry_client.channel.queue.max_queue_length = 10
        self.telemetry_client.context.session.id = _ClientSessionId
        super(ApplicationInsightsEventLogger, self).__init__(*args, **kwargs)

    def log_event(self, telemetry_event, white_listed_properties=None):
        """
        Log an event to Application Insights.

        :param telemetry_event: The telemetry event to log.
        :type telemetry_event: azureml.telemetry.contracts.Event
        :param white_listed_properties: A list of properties that could be logged without redaction.
        :type white_listed_properties: list
        :return: The event GUID.
        :rtype: str
        """
        self.telemetry_client.track_event(
            telemetry_event.name,
            ApplicationInsightsEventLogger._redact_fill_props_with_context(
                telemetry_event,
                white_listed_properties)
        )
        return telemetry_event.required_fields.event_id

    def log_metric(self, telemetry_metric, white_listed_properties=None):
        """Log a metric to Application Insights.

        :param telemetry_metric: The telemetry metric to log.
        :type telemetry_metric: azureml.telemetry.contracts.Metric
        :param white_listed_properties: A list of properties that could be logged without redaction.
        :type white_listed_properties: list
        :return: The metric GUID.
        :rtype: str
        """
        self.telemetry_client.track_metric(
            name=telemetry_metric.name,
            value=telemetry_metric.value,
            count=telemetry_metric.count,
            type=telemetry_metric.metric_type,
            max=telemetry_metric.metric_max,
            min=telemetry_metric.metric_min,
            std_dev=telemetry_metric.std_dev,
            properties=ApplicationInsightsEventLogger._redact_fill_props_with_context(
                telemetry_metric,
                white_listed_properties)
        )
        return telemetry_metric.required_fields.event_id

    def _create_synchronous_channel(self, context):
        """Create a synchronous app insight channel.

        :param context: The Application Insights context.
        :return: TelemetryChannel
        """
        channel = TelemetryChannel(context=context, queue=SynchronousQueue(self._sender(self.logger)))
        return channel

    def flush(self):
        """Flush the telemetry client."""
        self.telemetry_client.flush()
