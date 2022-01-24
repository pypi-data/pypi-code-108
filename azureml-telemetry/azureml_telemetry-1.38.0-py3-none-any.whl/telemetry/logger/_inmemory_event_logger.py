# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Represents an in-memory event logger."""
import json

from ._abstract_event_logger import AbstractEventLogger


class InMemoryEventLogger(AbstractEventLogger):
    """Represents an in-memory event logger."""

    def __init__(self):
        """Initialize in memory event logger."""
        self.logs = []

    def log_event(self, telemetry_event, white_listed_properties=None):
        """Store the event in the dictionary.

        :param telemetry_event: The event to be logged.
        :type telemetry_event: TelemetryObjectBase
        :param white_listed_properties: Properties that could be logged without redaction.
        :return: Event GUID.
        :rtype: str
        """
        logged = InMemoryEventLogger._redact_fill_props_with_context(
            telemetry_event,
            white_listed_properties)
        logged["EventName"] = telemetry_event.name
        print(logged)
        self.logs.append(logged)
        return telemetry_event.required_fields.event_id

    def log_metric(self, telemetry_metric, white_listed_properties=None):
        """Store the metric into the dictionary.

        :param telemetry_metric: The metric to be logged.
        :type telemetry_metric: TelemetryObjectBase
        :param white_listed_properties: Properties that could be logged without redaction.
        :return: Metric GUID.
        :rtype: str
        """
        logged = InMemoryEventLogger._redact_fill_props_with_context(
            telemetry_metric,
            white_listed_properties)
        print(logged)
        self.logs.append(logged)
        return telemetry_metric.required_fields.event_id

    def flush(self):
        """Flush the events."""
        json.dumps(self.logs)
