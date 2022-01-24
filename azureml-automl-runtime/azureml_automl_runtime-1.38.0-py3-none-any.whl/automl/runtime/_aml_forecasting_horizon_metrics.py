# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging

from azureml.core._metrics import ArtifactBackedMetric

module_logger = logging.getLogger(__name__)

# NEW ARTIFACT-BACKED METRICS
AZUREML_FORECAST_HORIZON_TABLE_METRIC_TYPE = "azureml.v2.forecast_horizon_table"

_metric_type_initializers = {}


class ForecastTrainTableMetric(ArtifactBackedMetric):
    def __init__(self, name, value, data_location, description=""):
        super(ForecastTrainTableMetric, self).__init__(name, value, data_location, description=description)
        self.metric_type = AZUREML_FORECAST_HORIZON_TABLE_METRIC_TYPE


_metric_type_initializers[AZUREML_FORECAST_HORIZON_TABLE_METRIC_TYPE] = ForecastTrainTableMetric


class ForecastValidateTableMetric(ArtifactBackedMetric):
    def __init__(self, name, value, data_location, description=""):
        super(ForecastValidateTableMetric, self).__init__(name, value, data_location, description=description)
        self.metric_type = AZUREML_FORECAST_HORIZON_TABLE_METRIC_TYPE


_metric_type_initializers[AZUREML_FORECAST_HORIZON_TABLE_METRIC_TYPE] = ForecastValidateTableMetric
