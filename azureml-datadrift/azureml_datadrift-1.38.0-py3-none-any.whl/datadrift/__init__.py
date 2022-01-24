# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Contains functionality to detect when model training data has drifted from its scoring data.

In machine learning, *data drift* is the change in model input data that leads to model performance degradation.
It is one of the top reasons where model accuracy degrades over time, thus monitoring data drift helps detect
model performance issues. This package enables you detect and alert on data drift.

The :class:`azureml.datadrift.DataDriftDetector` class enables you to configure a data monitor object
which then can be run as a job to analyze data drift. Data drift jobs can be run interactively or
enabled to run on a schedule. You can set up alerts when data drift exceeds a threshold with the
:class:`azureml.datadrift.AlertConfiguration` class.
"""

from .datadriftdetector import DataDriftDetector
from .alert_configuration import AlertConfiguration
from ._datadiff import Metric, MetricType
from ._model_serving_dataset import ModelServingDataset
from azureml._base_sdk_common import __version__ as VERSION

__all__ = ["AlertConfiguration", "DataDriftDetector", "Metric", "MetricType", "ModelServingDataset"]
__version__ = VERSION
