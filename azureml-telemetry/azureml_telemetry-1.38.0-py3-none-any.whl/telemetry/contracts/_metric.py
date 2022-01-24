# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Metric object for telemetry."""
from typing import Any, Optional

from applicationinsights.channel.contracts import DataPointType

from ._telemetry_object_base import TelemetryObjectBase
from ._required_fields import RequiredFields
from ._standard_fields import StandardFields
from ._extension_fields import ExtensionFields


class Metric(TelemetryObjectBase):
    """
    Metric object for telemetry usage.

    Use metrics for collecting and aggregating data that can be best aggregated into buckets for analysis.

    :param name: The name of the metric captured.
    :type name: str
    :param value: The value of the metric captured.
    :type value: float
    :param required_fields: Required fields for the schema, also referred to as Part A.
    :type required_fields: azureml.telemetry.contracts.RequiredFields
    :param standard_fields: Standard fields for the schema, also referred to as Part B.
    :type standard_fields: azureml.telemetry.contracts.StandardFields
    :param extension_fields: Extension fields for the schema, referred to as Part C.
    :type extension_fields: azureml.telemetry.contracts.ExtensionFields
    :param metric_type: The type of the metric.
    :type metric_type: applicationinsights.channel.contracts.DataPointType
    :param count: The number of metrics that were aggregated into this data point.
    :type count: int
    :param metric_min: The minimum of all metrics collected that were aggregated into this data point.
    :type metric_min: float
    :param metric_max: The maximum of all metrics collected that were aggregated into this data point.
    :type metric_max: float
    :param std_dev: The standard deviation of all metrics collected that were aggregated into this data point.
    :type std_dev: float

    """

    def __init__(self, name: str, value: float, required_fields: RequiredFields,
                 standard_fields: StandardFields, extension_fields: Optional[ExtensionFields] = None,
                 metric_type: Optional[DataPointType] = None,
                 count: Optional[int] = None, metric_min: Optional[float] = None,
                 metric_max: Optional[float] = None, std_dev: Optional[float] = None,
                 *args: Any, **kwargs: Any):
        """
        Initialize a new instance of the Metric.

        :param name: The name of the metric captured.
        :type: str
        :param value: The value of the metric captured.
        :type: float
        :param required_fields: Required fields for the schema.
        :type: azureml.telemetry.contracts.RequiredFields
        :param standard_fields: Standard fields for the schema.
        :type: azureml.telemetry.contracts.StandardFields
        :param extension_fields: Extension fields a.k.a Part C.
        :type: list[azureml.telemetry.contracts.ExtensionFields, dict]
        :param metric_type: The type of the metric.
        :type: applicationinsights.channel.contracts.DataPointType
        :param count: The number of metrics that were aggregated into this data point.
        :type: int
        :param metric_min: The minimum of all metrics collected that were aggregated into this data point.
        :type: float
        :param metric_max: The maximum of all metrics collected that were aggregated into this data point.
        :type: float
        :param std_dev: The standard deviation of all metrics collected that were aggregated into this data point.
        :type: float
        """
        super(Metric, self).__init__(name, required_fields, standard_fields, extension_fields, *args, **kwargs)
        self.name = name
        self.value = value
        self.metric_type = metric_type
        self.count = count
        self.metric_min = metric_min
        self.metric_max = metric_max
        self.std_dev = std_dev
