# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Methods specific to a Regression task type."""

from typing import Any, Dict, List, Optional, Union

import logging
import numpy as np

from azureml.automl.runtime.shared.score import scoring, _scoring_confidence
from azureml.automl.core.shared import constants, logging_utilities
from azureml.automl.core.shared.constants import Metric, MetricExtrasConstants

logger = logging.getLogger(__name__)


def evaluate_regressor(
        y_test: np.ndarray,
        y_pred: np.ndarray,
        metrics: List[str],
        y_max: Optional[float] = None,
        y_min: Optional[float] = None,
        y_std: Optional[float] = None,
        sample_weight: Optional[np.ndarray] = None,
        bin_info: Optional[Dict[str, float]] = None,
        enable_metric_confidence: bool = False,
        confidence_metrics: Optional[List[str]] = None
) -> Dict[str, Union[float, Dict[str, Any]]]:
    """
    Given the scored data, generate metrics for classification task.
    The optional parameters `y_max`, `y_min`, and `y_std` should be based on the target column y from the
    full dataset.

    - `y_max` and `y_min` should be used to control the normalization of
    normalized metrics. The effect will be division by max - min.
    - `y_std` is used to estimate a sensible range for displaying non-scalar
    regression metrics.

    If the metric is undefined given the input data, the score will show
        as nan in the returned dictionary.

    :param y_test: The target values.
    :param y_pred: The predicted values.
    :param metrics: List of metric names for metrics to calculate.
    :param y_max: The max target value.
    :param y_min: The min target value.
    :param y_std: The standard deviation of targets value.
    :param sample_weight:
        The sample weight to be used on metrics calculation. This does not need
        to match sample weights on the fitted model.
    :param bin_info:
        The binning information for true values. This should be calculated from make_dataset_bins. Required for
        calculating non-scalar metrics.
    :param enable_metric_confidence: Allow classfication metric calculation to include confidence intervals
        This is currently defaulted to False, and will have an automl config setting to enable
    :param confidence_metrics: The list of metrics to compute confidence interval.
        If None, it will take the value of `metrics`
        If not None, must be a subset of `metrics`.
        metrics in this list but not in `metircs` will be ignored
    :return: A dictionary mapping metric name to metric score.
    """
    scored_metrics = scoring.score_regression(y_test, y_pred, metrics, y_max, y_min, y_std, sample_weight, bin_info)

    scored_confidence_intervals = {}
    if enable_metric_confidence:
        if confidence_metrics is None:
            confidence_metrics = metrics
        else:
            ignored_metrics = [metric for metric in confidence_metrics if metric not in metrics]
            if ignored_metrics:
                message = "Found metrics {} in `confidence_metrics` but not in `metrics`."
                message += "These metrics will be ignored for confidence interval computation."
                message.format(ignored_metrics)
                logger.warning(message)
            confidence_metrics = [metric for metric in confidence_metrics if metric in metrics]

        with logging_utilities.log_activity(
            logger,
            activity_name=constants.TelemetryConstants.COMPUTE_CONFIDENCE_METRICS,
        ):
            scored_confidence_intervals = \
                _scoring_confidence.score_confidence_intervals_regression(y_test,
                                                                          y_pred,
                                                                          confidence_metrics,
                                                                          y_max,
                                                                          y_min,
                                                                          y_std,
                                                                          sample_weight)

    joined_metrics = {}  # type: Dict[str, Any]
    for metric in scored_metrics.keys():

        computed_metric = scored_metrics[metric]
        joined_metrics[metric] = computed_metric

        if metric in scored_confidence_intervals:
            ci_metric = scored_confidence_intervals[metric]  # type: Dict[str, Any]
            ci_metric[MetricExtrasConstants.VALUE] = computed_metric
            joined_metrics[MetricExtrasConstants.MetricExtrasFormat.format(metric)] = ci_metric

    return joined_metrics
