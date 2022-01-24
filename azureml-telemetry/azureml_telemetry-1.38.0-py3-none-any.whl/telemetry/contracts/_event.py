# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Event object for telemetry."""
from typing import Any, Optional

from ._telemetry_object_base import TelemetryObjectBase
from ._required_fields import RequiredFields
from ._standard_fields import StandardFields
from ._extension_fields import ExtensionFields


class Event(TelemetryObjectBase):
    """
    Event object for telemetry usage.

    Use events for collecting events with a defined schema.

    :param name: The name of the event.
    :type name: str
    :param required_fields: Required fields or Part A of the schema.
    :type required_fields: azureml.telemetry.contracts.RequiredFields
    :param standard_fields: Standard fields or Part B of the schema.
    :type standard_fields: azureml.telemetry.contracts.StandardFields
    :param extension_fields: Extension fields or Part C of the schema.
    :type extension_fields: azureml.telemetry.contracts.ExtensionFields
    """

    def __init__(self, name: str, required_fields: RequiredFields,
                 standard_fields: Optional[StandardFields] = None,
                 extension_fields: Optional[ExtensionFields] = None,
                 *args: Any, **kwargs: Any):
        """
        Initialize a new instance of the Event.

        :param name: Name of the event.
        :type name: str
        :param required_fields: Required fields or Part A of the schema.
        :type required_fields: azureml.telemetry.contracts.RequiredFields
        :param standard_fields: Standard fields or Part B of the schema.
        :type standard_fields: azureml.telemetry.contracts.StandardFields
        :param extension_fields: Extension fields or Part C of the schema.
        :type extension_fields: azureml.telemetry.contracts.ExtensionFields
        """
        super(Event, self).__init__(name=name, required_fields=required_fields,
                                    standard_fields=standard_fields,
                                    extension_fields=extension_fields, *args, **kwargs)
