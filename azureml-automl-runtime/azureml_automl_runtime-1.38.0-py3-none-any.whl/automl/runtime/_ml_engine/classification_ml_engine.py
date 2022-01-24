# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Methods specific to a Classification task type."""

from typing import Any, Dict, List, Optional, Union

import logging
import numpy as np
from sklearn.base import TransformerMixin

from azureml.automl.runtime.shared.score import scoring, _scoring_confidence
from azureml.automl.core.shared import constants, logging_utilities
from azureml.automl.core.shared.constants import Metric, MetricExtrasConstants

logger = logging.getLogger(__name__)


def evaluate_classifier(
        y_test: np.ndarray,
        y_pred_probs: np.ndarray,
        metrics: List[str],
        class_labels: np.ndarray,
        train_labels: np.ndarray,
        sample_weight: Optional[np.ndarray] = None,
        y_transformer: Optional[TransformerMixin] = None,
        use_binary: bool = False,
        enable_metric_confidence: bool = False,
        positive_label: Optional[Any] = None,
        confidence_metrics: Optional[List[str]] = None
) -> Dict[str, Union[float, Dict[str, Any]]]:
    """
    Given the scored data, generate metrics for classification task

    All class labels for y should come as seen by the fitted model (i.e. if the fitted model uses a
    y transformer the labels should also come transformed).

    All metrics present in `metrics` will be present in the output dictionary with either
    the value(s) calculated or `nan` if the calculation failed.

    :param y_test: The target values (Transformed if using a y transformer)
    :param y_pred_probs: The predicted probabilities for all classes.
    :param metrics: Classification metrics to compute point estimates
    :param class_labels: All classes found in the full dataset (includes train/valid/test sets).
        These should be transformed if using a y transformer.
    :param train_labels: Classes as seen (trained on) by the trained model. These values
        should correspond to the columns of y_pred_probs in the correct order.
    :param sample_weight: Weights for the samples (Does not need
        to match sample weights on the fitted model)
    :param y_transformer: Used to inverse transform labels from `y_test`. Required for non-scalar metrics.
    :param use_binary: Compute metrics only on the true class for binary classification.
    :param enable_metric_confidence: Allow classfication metric calculation to include confidence intervals
        This is currently defaulted to False, and will have an automl config setting to enable
    :param positive_label: class designed as positive class in binary classification metrics.
    :param confidence_metrics: The list of metrics to compute confidence interval.
        If None, it will take the value of `metrics`
        If not None, must be a subset of `metrics`.
        metrics in this list but not in `metircs` will be ignored
    :return: A dictionary mapping metric name to metric score.
    """
    scored_metrics = scoring.score_classification(y_test,
                                                  y_pred_probs,
                                                  metrics,
                                                  class_labels,
                                                  train_labels,
                                                  sample_weight,
                                                  y_transformer,
                                                  use_binary=use_binary,
                                                  positive_label=positive_label)

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
                _scoring_confidence.score_confidence_intervals_classification(y_test,
                                                                              y_pred_probs,
                                                                              confidence_metrics,
                                                                              class_labels,
                                                                              train_labels,
                                                                              sample_weight,
                                                                              y_transformer,
                                                                              use_binary,
                                                                              positive_label)

    joined_metrics = {}  # type: Dict[str, Any]
    for metric in scored_metrics.keys():

        computed_metric = scored_metrics[metric]
        joined_metrics[metric] = computed_metric

        if metric in scored_confidence_intervals:
            ci_metric = scored_confidence_intervals[metric]  # type: Dict[str, Any]
            ci_metric[MetricExtrasConstants.VALUE] = computed_metric
            joined_metrics[MetricExtrasConstants.MetricExtrasFormat.format(metric)] = ci_metric

    return joined_metrics
