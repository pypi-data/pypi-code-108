# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Base class for telemetry objects."""
from typing import Any, Dict, Optional

from datetime import datetime
import uuid

from ._required_fields import RequiredFields, RequiredFieldKeys
from ._standard_fields import StandardFields

EVENT_SCHEMA_VERSION_KEY = "EventSchemaVersion"
EVENT_SCHEMA_VERSION_VALUE = "0.1"


class TelemetryObjectBase(dict):
    """Defines the base class for collecting schematized telemetry events and metrics.

    Use :class:`azureml.telemetry.contracts.Metric` for collecting and aggregating data, and
    :class:`azureml.telemetry.contracts.Event` for collecting low volume events with a defined schema use events.
    Both types of telemetry use a schema instead of free text for logging the data. The schema defines required,
    standard, and extension fields.

    :param required_fields: Required fields or Part A of the schema.
    :type required_fields: azureml.telemetry.contracts.RequiredFields
    :param standard_fields: Standard fields or Part B of the schema.
    :type standard_fields: azureml.telemetry.contracts.StandardFields
    :param extension_fields: Extension fields or Part C of the schema.
    :type extension_fields: azureml.telemetry.contracts.ExtensionFields
    :param args: Optional arguments for formatting messages.
    :type args: list
    :param kwargs: Optional keyword arguments for adding additional information to messages.
    :type kwargs: dict
    """

    def __init__(self,
                 name: str,
                 required_fields: RequiredFields,
                 standard_fields: Optional[StandardFields] = None,
                 extension_fields: Optional[Dict[str, Any]] = None,
                 *args: Any, **kwargs: Any):
        """
        Initialize telemetry object base.

        :param required_fields: Required fields or Part A of the schema.
        :type required_fields: azureml.telemetry.contracts.RequiredFields
        :param standard_fields: Standard fields or Part B of the schema.
        :type standard_fields: azureml.telemetry.contracts.StandardFields
        :param extension_fields: Extension fields or Part C of the schema.
        :type extension_fields: azureml.telemetry.contracts.ExtensionFields
        :param args: Optional arguments for formatting messages.
        :type args: list
        :param kwargs: Optional keyword arguments for adding additional information to messages.
        :type kwargs: dict
        """
        super(TelemetryObjectBase, self).__init__(*args, **kwargs)
        assert required_fields is not None and len(required_fields) > 0, "Required fields cannot be empty or None."
        assert name is not None and len(name) > 0
        self[EVENT_SCHEMA_VERSION_KEY] = EVENT_SCHEMA_VERSION_VALUE
        self.required_fields = required_fields
        self.standard_fields = standard_fields or StandardFields()
        self.extension_fields = extension_fields
        self.name = name
        self.required_fields[RequiredFieldKeys.EVENT_ID_KEY] = str(uuid.uuid4())
        self.required_fields[RequiredFieldKeys.EVENT_TIME_KEY] = str(datetime.utcnow())

    def get_all_properties(self):
        """Retrieve all the properties from the metric.

        :return: The properties.
        :rtype: dict
        """
        properties = {
            EVENT_SCHEMA_VERSION_KEY: EVENT_SCHEMA_VERSION_VALUE
        }

        properties.update(self.required_fields)
        properties.update(self.standard_fields)
        if self.extension_fields and len(self.extension_fields) > 0:
            properties.update(self.extension_fields)
        return properties

    def __str__(self):
        return self.get_all_properties().__str__()
