# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import logging

from azureml.automl.runtime._run_history.offline_automl_run.offline_automl_run import OfflineAutoMLRun
from azureml.exceptions import UserErrorException
from azureml.core import Run
module_logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)


def log_forecast_horizon_table(child_run, metric_class, name, value, description=""):
    """Log forecast train/validate table as a metric score"""
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.decoder.JSONDecodeError:
            raise UserErrorException("Invalid JSON provided")
    metric = metric_class(name, value, None, description=description)
    # log AutoML runs
    if isinstance(child_run, Run):
        child_run._client._log_metric_v2(metric)
    # log offline runs or many model runs
    elif isinstance(child_run, OfflineAutoMLRun):
        child_run.log_horzion_table(name, value)
