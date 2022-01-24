# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Logging utilities for logging AutoML metrics to RunHistory."""
import logging

import numpy as np

from azureml._tracing._tracer_factory import get_tracer

from azureml.automl.core.shared import constants
from azureml.automl.runtime.shared.score import _scoring_utilities

from ._forecasting_logging_utilities import log_forecast_horizon_table
from ._aml_forecasting_horizon_metrics import ForecastTrainTableMetric, ForecastValidateTableMetric

logger = logging.getLogger(__name__)
tracer = get_tracer(__name__)


def log_metrics(child_run, scores, flush_metrics=False, log_binary=False):
    # Log scalar metrics before non-scalar metrics to take advantage of batched upload to Run History
    with tracer.start_as_current_span(
            constants.TelemetryConstants.SPAN_FORMATTING.format(
                constants.TelemetryConstants.COMPONENT_NAME, constants.TelemetryConstants.LOG_METRICS
            ),
            user_facing_name=constants.TelemetryConstants.LOG_METRICS_USER_FACING,
    ):
        scalar_scores = {}
        table_scores = {}
        nonscalar_scores = {}
        for name, score in scores.items():
            if score is None:
                continue
            if name in constants.Metric.SCALAR_FULL_SET:
                if name in constants.Metric.CLASSIFICATION_BINARY_SET and not log_binary:
                    logger.warning("Skipping logging uncomputed binary metric {}".format(name))
                else:
                    scalar_scores[name] = score
            elif _scoring_utilities.is_table_metric(name):
                table_scores[name] = score
            elif name in constants.Metric.NONSCALAR_FULL_SET:
                nonscalar_scores[name] = score
            elif name in constants.TrainingResultsType.ALL_TIME:
                # Filter out time metrics as we do not log these
                pass
            else:
                logger.warning("Unknown metric {}. Will not log.".format(name))

        # Log the scalar metrics. (Currently, these are stored in CosmosDB)
        for name, score in scalar_scores.items():
            try:
                child_run.log(name, score)
            except Exception:
                _log_metric_failure_warning(name, score)

        for name, score in table_scores.items():
            try:
                child_run.log_table(name, score)
            except Exception:
                _log_metric_failure_warning(name, score)

        # Log the non-scalar metrics. (Currently, these are all artifact-based.)
        for name, score in nonscalar_scores.items():
            try:
                if name == constants.Metric.AccuracyTable:
                    child_run.log_accuracy_table(name, score)
                elif name == constants.Metric.ForecastValidateTable:
                    log_forecast_horizon_table(child_run, ForecastValidateTableMetric, name, score)
                elif name == constants.Metric.ForecastTrainTable:
                    log_forecast_horizon_table(child_run, ForecastTrainTableMetric, name, score)
                elif name == constants.Metric.ConfusionMatrix:
                    child_run.log_confusion_matrix(name, score)
                elif name == constants.Metric.Residuals:
                    child_run.log_residuals(name, score)
                elif name == constants.Metric.PredictedTrue:
                    child_run.log_predictions(name, score)
                elif name in constants.Metric.NONSCALAR_FORECAST_SET:
                    # Filter out non-scalar forecasting metrics as we do not log these yet
                    pass
                else:
                    logger.warning("Unsupported non-scalar metric {}. Will not log.".format(name))
            except Exception:
                _log_metric_failure_warning(name, score)

        # Flush all queued run metrics to RH
        if flush_metrics:
            child_run.flush()


def _log_metric_failure_warning(metric_name: str, metric_value: str) -> None:
    logger.warning("Failed to log the metric {} with value {}.".format(metric_name, metric_value))


def log_metrics_info(scores, pipeline_id=None, run_id=None):
    reduced_scores = _get_reduced_scores(scores)
    log_fmt = "run_id:{}, pipeline_id:{},The following metrics have been logged for the child run: {}."
    logger.info(log_fmt.format(run_id, pipeline_id, reduced_scores))


def _get_reduced_scores(scores):
    reduced_scores = dict()
    for name, score in scores.items():
        is_score_NoneOrNumeric = score is None or isinstance(score, int) or isinstance(score, float)
        if name in constants.Metric.SCALAR_FULL_SET or is_score_NoneOrNumeric:
            reduced_scores[name] = score
        else:
            reduced_scores[name] = type(score)
    return reduced_scores
