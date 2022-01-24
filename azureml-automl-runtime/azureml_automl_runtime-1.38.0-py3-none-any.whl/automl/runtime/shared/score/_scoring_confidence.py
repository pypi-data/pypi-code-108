# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Computation of AutoML model evaluation metrics."""
import logging
import numpy as np
import time

from sklearn.base import TransformerMixin
from sklearn.utils import resample
from typing import Dict, List, Optional, Tuple, Type, Any, Union, cast

from azureml.automl.core.shared import logging_utilities

from azureml.automl.core.shared.constants import MetricExtrasConstants, TelemetryConstants
from azureml.automl.runtime.shared.score import _scoring_utilities, _validation, constants

logger = logging.getLogger(__name__)


def score_confidence_intervals_classification(
    y_test: np.ndarray,
    y_pred_probs: np.ndarray,
    metrics: List[str],
    class_labels: np.ndarray,
    train_labels: np.ndarray,
    sample_weight: Optional[np.ndarray] = None,
    y_transformer: Optional[TransformerMixin] = None,
    use_binary: bool = False,
    positive_label: Optional[Any] = None
) -> Dict[str, Dict[str, Any]]:
    """
    Compute confidence interval metrics for a classification task.

    All class labels for y should come
    as seen by the fitted model (i.e. if the fitted model uses a y transformer the labels
    should also come transformed).

    All metrics present in `metrics` will be present in the output dictionary with either
    the value(s) calculated or `nan` if the calculation failed.

    :param y_test: The target values (Transformed if using a y transformer)
    :param y_pred_probs: The predicted probabilities for all classes.
    :param metrics: Classification metrics to compute
    :param class_labels: All classes found in the full dataset (includes train/valid/test sets).
        These should be transformed if using a y transformer.
    :param train_labels: Classes as seen (trained on) by the trained model. These values
        should correspond to the columns of y_pred_probs in the correct order.
    :param sample_weight: Weights for the samples (Does not need
        to match sample weights on the fitted model)
    :param y_transformer: Used to inverse transform labels from `y_test`. Required for non-scalar metrics.
    :param use_binary: Compute metrics only on the true class for binary classification.
    :param positive_label: class designed as positive class in later binary classification metrics.
    :return: A dictionary mapping metric name to confidence interval.
    """

    y_test = _validation.format_1d(y_test, 'y_test')

    _validation.validate_classification(y_test, y_pred_probs, metrics,
                                        class_labels, train_labels,
                                        sample_weight, y_transformer)

    _validation.log_classification_debug(y_test, y_pred_probs, class_labels,
                                         train_labels, sample_weight=sample_weight)

    scoring_dto = _scoring_utilities.ClassificationDataDto(y_test,
                                                           y_pred_probs,
                                                           class_labels,
                                                           train_labels,
                                                           sample_weight,
                                                           y_transformer,
                                                           positive_label=positive_label)

    test_targets, pred_targets, labels, positive_label_encoded = scoring_dto.get_targets(encoded=True)

    metrics = [metric for metric in metrics if metric in constants.CLASSIFICATION_SCALAR_SET]

    computed_metrics = _generate_classification_confidence_intervals(metrics,
                                                                     test_targets, pred_targets, labels,
                                                                     scoring_dto.y_pred_probs_padded,
                                                                     scoring_dto.y_test_bin,
                                                                     sample_weight, use_binary,
                                                                     positive_label_encoded)

    return computed_metrics


def _generate_classification_confidence_intervals(
    metrics: List[str],
    test_targets: np.ndarray,
    pred_targets: np.ndarray,
    labels: np.ndarray,
    y_pred_probs_padded: np.ndarray,
    y_test_bin: np.ndarray,
    sample_weight: Optional[np.ndarray] = None,
    use_binary: bool = False,
    positive_label: Optional[Any] = None,
    iterations: int = 500,
) -> Dict[str, Dict[str, Any]]:
    """
    Bootstrap sampling on the pre-scored dataset to create confidence intervals on
    the metrics.

    Bootstrap sampling is used on the scoring dataset to create a confidence interval
    for all scalar metrics. The dataset prediction step is done exactly once, the predictions
    are bootstrapped N-times, metrics are calculated on these N bootstrap samples, the
    2.5th/97.5th percentile of the bootstrap metrics are the returned as the lower/upper 95th
    percentile confidence intervals

    :param metrics: Classification metrics to compute
    :param test_targets: The target values (Transformed if using a y transformer)
    :param pred_targets: The predicted class.
    :param labels: All classes found in the full dataset (includes train/valid/test sets).
        These should be transformed if using a y transformer.
    :param y_pred_probs_padded: the predicted classes padded
    :param y_test_bin: The actual class labels
    :param sample_weight: Weights for the samples (Does not need
        to match sample weights on the fitted model)
    :param use_binary: Compute metrics only on the true class for binary classification.
    :param positive_label: class designed as positive class in later binary classification metrics.
    :param iterations: number of bootstrap iterations to simulate the distribution of classification metrics.
    :return: A dictionary mapping metric name to confidence interval.
    """

    n, n_class = y_pred_probs_padded.shape
    n_samples = min(n, max(round(0.25 * n), 50 * n_class, 10000))

    with logging_utilities.log_activity(
        logger,
        activity_name=TelemetryConstants.BOOTSTRAP_STEPS,
    ):

        aggregated_metrics = None
        metric_values = _bootstrap_classification(metrics,
                                                  iterations,
                                                  test_targets,
                                                  pred_targets,
                                                  labels,
                                                  y_pred_probs_padded,
                                                  y_test_bin,
                                                  n_samples,
                                                  sample_weight,
                                                  use_binary,
                                                  positive_label)

        aggregated_metrics = _calculate_confidence_intervals(metric_values)

    return aggregated_metrics


def _bootstrap_classification(
    metrics: List[str],
    iterations: int,
    test_targets: np.ndarray,
    pred_targets: np.ndarray,
    labels: np.ndarray,
    y_pred_probs_padded: np.ndarray,
    y_test_bin: np.ndarray,
    n_samples: Optional[int],
    sample_weight: Optional[np.ndarray] = None,
    use_binary: bool = False,
    positive_label: Optional[Any] = None
) -> Dict[str, List[float]]:
    """
    Use bootstrap to estimate distributions for classification metrics with given data.

    :param metrics: Classification metrics to compute
    :param iterations: number of bootstrap iterations to simulate the distribution of classification metrics.
    :param test_targets: The target values (Transformed if using a y transformer)
    :param pred_targets: The predicted class.
    :param labels: All classes found in the full dataset (includes train/valid/test sets).
        These should be transformed if using a y transformer.
    :param y_pred_probs_padded: the predicted classes padded
    :param y_test_bin: The actual class labels
    :param n_samples: The number of samples to select with replacement for each bootstrap step
    :param sample_weight: Weights for the samples (Does not need
        to match sample weights on the fitted model)
    :param use_binary: Compute metrics only on the true class for binary classification.
    :param positive_label: class designed as positive class in later binary classification metrics.
    :return: A dictionary mapping metric name to its value distribution.
    """

    test_targets_orig = test_targets
    pred_targets_orig = pred_targets
    y_pred_probs_padded_orig = y_pred_probs_padded
    y_test_bin_orig = y_test_bin
    pred_targets_orig = pred_targets
    sample_weight_orig = sample_weight if sample_weight is not None else np.ones(test_targets.shape[0])

    time_for_metric_compute = 0.0
    time_for_resample = 0.0

    metric_values: Dict[str, List[float]] = dict(zip(metrics, [[] for _ in metrics]))
    error_times: Dict[str, int] = dict(zip(metrics, [0 for _ in metrics]))

    for i in range(iterations):
        resample_start_time = time.perf_counter()
        test_targets, pred_targets, y_pred_probs_padded, y_test_bin, sample_weight = \
            resample(test_targets_orig,
                     pred_targets_orig,
                     y_pred_probs_padded_orig,
                     y_test_bin_orig,
                     sample_weight_orig,
                     random_state=i,
                     n_samples=n_samples,
                     replace=True)
        time_for_resample += time.perf_counter() - resample_start_time

        for metric_name in metrics:

            metric_class = _scoring_utilities.get_metric_class(metric_name)
            safe_name = _scoring_utilities.get_safe_metric_name(metric_name)
            metric = metric_class(test_targets, y_pred_probs_padded, y_test_bin,
                                  pred_targets, labels, sample_weight=sample_weight,
                                  use_binary=use_binary, positive_label_encoded=positive_label)

            metric_compute_start_time = time.perf_counter()
            try:
                computed_metric = metric.compute()
            except MemoryError:
                raise
            except Exception as e:
                logger.error("Scoring failed for metric {} during bootstrap for confidence interval".format(safe_name))
                logging_utilities.log_traceback(e, logger, is_critical=False)
                computed_metric = np.nan
                error_times[metric_name] += 1
            time_for_metric_compute += time.perf_counter() - metric_compute_start_time
            metric_values[metric_name].append(computed_metric)

    logger.info('Bootstrap scoring metric compution for took {:0.4f} seconds'.format(time_for_metric_compute))
    logger.info('Bootstrap resample for took {:0.4f} seconds'.format(time_for_resample))
    for metric in metrics:
        if error_times[metric] > 0:
            logger.info("Bootstrap has {} times error out of {} tries for metric {}"
                        .format(error_times[metric], iterations, metric))

    return metric_values


def score_confidence_intervals_regression(
    y_test: np.ndarray,
    y_pred: np.ndarray,
    metrics: List[str],
    y_max: Optional[float] = None,
    y_min: Optional[float] = None,
    y_std: Optional[float] = None,
    sample_weight: Optional[np.ndarray] = None
) -> Dict[str, Dict[str, Any]]:
    """
    Compute model evaluation metrics confidence interval for a regression task.

    The optional parameters `y_min`, `y_min`, and `y_min` should be based on the
        target column y from the full dataset.

    - `y_max` and `y_min` should be used to control the normalization of
    normalized metrics. The effect will be division by max - min.
    - `y_std` is used to estimate a sensible range for displaying non-scalar
    regression metrics.

    If the metric is undefined given the input data, its confidence interval
        will be meaningless and will not be returned

    :param y_test: The target values.
    :param y_pred: The predicted values.
    :param metrics: List of metric names for metrics to calculate.
    :type metrics: list
    :param y_max: The max target value.
    :param y_min: The min target value.
    :param y_std: The standard deviation of targets value.
    :param sample_weight:
        The sample weight to be used on metrics calculation. This does not need
        to match sample weights on the fitted model.
    :return: A dictionary mapping metric name to confidence interval.
    """

    y_test = _validation.format_1d(y_test, 'y_test')
    y_pred = _validation.format_1d(y_pred, 'y_pred')

    _validation.validate_regression(y_test, y_pred, metrics)
    _validation.log_regression_debug(y_test, y_pred, y_min, y_max, sample_weight=sample_weight)

    y_min = np.min(y_test) if y_min is None else y_min
    y_max = np.max(y_test) if y_max is None else y_max
    y_std = np.std(y_test) if y_std is None else y_std

    metrics = [metric for metric in metrics if metric in constants.REGRESSION_SCALAR_SET]

    computed_metrics = _generate_regression_confidence_intervals(metrics,
                                                                 y_test, y_pred,
                                                                 y_max, y_min, y_std,
                                                                 sample_weight=sample_weight)

    return computed_metrics


def _generate_regression_confidence_intervals(
    metrics: List[str],
    y_test: np.ndarray,
    y_pred: np.ndarray,
    y_max: Optional[float] = None,
    y_min: Optional[float] = None,
    y_std: Optional[float] = None,
    sample_weight: Optional[np.ndarray] = None,
    iterations: int = 500,
) -> Dict[str, Dict[str, Any]]:
    """
    Bootstrap sampling on the pre-scored dataset to create confidence intervals on
    the metrics.

    Bootstrap sampling is used on the scoring dataset to create a confidence interval
    for all scalar metrics. The dataset prediction step is done exactly once, the predictions
    are bootstrapped N-times, metrics are calculated on these N bootstrap samples, the
    2.5th/97.5th percentile of the bootstrap metrics are the returned as the lower/upper 95th
    percentile confidence intervals

    :param metrics: Regression metrics to compute
    :param y_test: True labels for the test set.
    :param y_pred: Predictions for each sample.
    :param y_max: Maximum target value.
    :param y_min: Minimum target value.
    :param y_std: Standard deviation of the targets.
    :param sample_weight: Weighting of each sample in the calculation.
    :param iterations: number of bootstrap iterations to simulate the distribution of classification metrics.
    :return: A dictionary mapping metric name to confidence interval.
    """

    n = y_test.shape[0]
    n_samples = min(n, max(round(0.25 * n), 10000))

    with logging_utilities.log_activity(
        logger,
        activity_name=TelemetryConstants.BOOTSTRAP_STEPS,
    ):

        aggregated_metrics = None
        metric_values = _bootstrap_regression(metrics,
                                              iterations,
                                              y_test,
                                              y_pred,
                                              y_max,
                                              y_min,
                                              y_std,
                                              n_samples,
                                              sample_weight)

        aggregated_metrics = _calculate_confidence_intervals(metric_values)

    return aggregated_metrics


def _bootstrap_regression(
    metrics: List[str],
    iterations: int,
    y_test: np.ndarray,
    y_pred: np.ndarray,
    y_max: Optional[float] = None,
    y_min: Optional[float] = None,
    y_std: Optional[float] = None,
    n_samples: Optional[int] = None,
    sample_weight: Optional[np.ndarray] = None,
) -> Dict[str, List[float]]:
    """
    Use bootstrap to estimate distributions for regression metrics with given data.

    :param metrics: Regression metrics to compute
    :param iterations: number of bootstrap iterations to simulate the distribution of classification metrics.
    :param y_test: True labels for the test set.
    :param y_pred: Predictions for each sample.
    :param y_max: Maximum target value.
    :param y_min: Minimum target value.
    :param y_std: Standard deviation of the targets.
    param n_samples: The number of samples to select with replacement for each bootstrap step
    :param sample_weight: Weighting of each sample in the calculation.
    :return: A dictionary mapping metric name to its value distribution.
    """

    y_test_orig = y_test
    y_pred_orig = y_pred
    sample_weight_orig = sample_weight if sample_weight is not None else np.ones(y_test.shape)

    time_for_metric_compute = 0.0
    time_for_resample = 0.0

    metric_values: Dict[str, List[float]] = dict(zip(metrics, [[] for _ in metrics]))
    error_times: Dict[str, int] = dict(zip(metrics, [0 for _ in metrics]))

    for i in range(iterations):
        resample_start_time = time.perf_counter()
        y_test, y_pred, sample_weight = resample(y_test_orig,
                                                 y_pred_orig,
                                                 sample_weight_orig,
                                                 random_state=i,
                                                 n_samples=n_samples,
                                                 replace=True)
        time_for_resample += time.perf_counter() - resample_start_time

        for metric_name in metrics:

            metric_class = _scoring_utilities.get_metric_class(metric_name)
            safe_name = _scoring_utilities.get_safe_metric_name(metric_name)
            metric = metric_class(y_test, y_pred, y_min, y_max, y_std, sample_weight=sample_weight)

            metric_compute_start_time = time.perf_counter()
            try:
                computed_metric = metric.compute()
            except MemoryError:
                raise
            except Exception as e:
                logger.error("Scoring failed for metric {} during bootstrap for confidence interval".format(safe_name))
                logging_utilities.log_traceback(e, logger, is_critical=False)
                computed_metric = np.nan
                error_times[metric_name] += 1
            time_for_metric_compute += time.perf_counter() - metric_compute_start_time
            metric_values[metric_name].append(computed_metric)

    logger.info('Bootstrap scoring metric compution for took {:0.4f} seconds'.format(time_for_metric_compute))
    logger.info('Bootstrap resample for took {:0.4f} seconds'.format(time_for_resample))
    for metric in metrics:
        if error_times[metric] > 0:
            logger.info("Bootstrap has {} times error out of {} tries for metric {}"
                        .format(error_times[metric], iterations, metric))

    return metric_values


def _calculate_confidence_intervals(
    metric_values: Dict[str, List[float]],
) -> Dict[str, Dict[str, Any]]:
    """
    Compute aggregate model evaluation metrics from the bootstrap scoring

    All metrics present in `metrics` will be present in the output dictionary with either
    the value(s) calculated or `nan` if metric calculation failed.

    :param metrics_values:
        A dictionary mapping metric name to its value distribution.
    :return: A dictionary mapping metric name to confidence interval.
    """
    metrics_extras: Dict[str, Dict[str, Any]] = {}
    for metric in metric_values.keys():
        values = metric_values[metric]
        if all(np.isnan(values)):
            logger.warning("metric {} values are all nan in confidence interval computing".format(metric))
            continue
        metrics_extras[metric] = {}
        metrics_extras[metric][MetricExtrasConstants.LOWER_95_PERCENTILE] = np.nanpercentile(values, 2.5)
        metrics_extras[metric][MetricExtrasConstants.UPPER_95_PERCENTILE] = np.nanpercentile(values, 97.5)

    return metrics_extras
