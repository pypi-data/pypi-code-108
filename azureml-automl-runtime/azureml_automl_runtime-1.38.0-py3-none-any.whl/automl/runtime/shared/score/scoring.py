# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Computation of AutoML model evaluation metrics."""
from typing import Any, Dict, List, Optional, Union

import logging
import numpy as np
import pandas as pd

from sklearn.base import TransformerMixin

from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared.constants import MetricExtrasConstants

from azureml.automl.runtime.shared.score import _scoring_utilities, _validation, constants, utilities
from azureml.automl.runtime.shared.score._metric_base import NonScalarMetric

logger = logging.getLogger(__name__)


def score_classification(
    y_test: np.ndarray,
    y_pred_probs: np.ndarray,
    metrics: List[str],
    class_labels: np.ndarray,
    train_labels: np.ndarray,
    sample_weight: Optional[np.ndarray] = None,
    y_transformer: Optional[TransformerMixin] = None,
    use_binary: bool = False,
    multilabel: Optional[bool] = False,
    positive_label: Optional[Any] = None
) -> Dict[str, Union[float, Dict[str, Any]]]:

    """
    Compute model evaluation metrics for a classification task.

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
    :param multilabel: Indicate if it is multilabel classification.
    :return: A dictionary mapping metric name to metric score.
    """
    if not multilabel:
        y_test = _validation.format_1d(y_test, 'y_test')

    _validation.validate_classification(y_test, y_pred_probs, metrics,
                                        class_labels, train_labels,
                                        sample_weight, y_transformer, multilabel=multilabel)
    _validation.log_classification_debug(y_test, y_pred_probs, class_labels,
                                         train_labels, sample_weight=sample_weight, multilabel=multilabel)

    scoring_dto = _scoring_utilities.ClassificationDataDto(y_test,
                                                           y_pred_probs,
                                                           class_labels,
                                                           train_labels,
                                                           sample_weight,
                                                           y_transformer,
                                                           multilabel=multilabel,
                                                           positive_label=positive_label)
    positive_label_encoded = scoring_dto.positive_label_encoded

    results = {}
    for name in metrics:
        try:
            metric_class = _scoring_utilities.get_metric_class(name)
            test_targets, pred_targets, labels, positive_label = scoring_dto.get_targets(
                encoded=utilities.is_scalar(name),
                classwise=utilities.is_classwise(name))

            metric = metric_class(
                test_targets, scoring_dto.y_pred_probs_padded, scoring_dto.y_test_bin,
                pred_targets, labels, sample_weight=sample_weight, use_binary=use_binary,
                positive_label_encoded=positive_label_encoded, multilabel=multilabel, y_transformer=y_transformer)

            results[name] = metric.compute()
        except MemoryError:
            raise
        except Exception as e:
            safe_name = _scoring_utilities.get_safe_metric_name(name)
            logger.error("Scoring failed for classification metric {}".format(safe_name))
            logging_utilities.log_traceback(e, logger, is_critical=False)
            if utilities.is_scalar(name):
                results[name] = np.nan
            else:
                results[name] = NonScalarMetric.get_error_metric()

    return results


def score_regression(
    y_test: np.ndarray,
    y_pred: np.ndarray,
    metrics: List[str],
    y_max: Optional[float] = None,
    y_min: Optional[float] = None,
    y_std: Optional[float] = None,
    sample_weight: Optional[np.ndarray] = None,
    bin_info: Optional[Dict[str, float]] = None
) -> Dict[str, Union[float, Dict[str, Any]]]:
    """
    Compute model evaluation metrics for a regression task.

    The optional parameters `y_min`, `y_min`, and `y_min` should be based on the
        target column y from the full dataset.

    - `y_max` and `y_min` should be used to control the normalization of
    normalized metrics. The effect will be division by max - min.
    - `y_std` is used to estimate a sensible range for displaying non-scalar
    regression metrics.

    If the metric is undefined given the input data, the score will show
        as nan in the returned dictionary.

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
    :param bin_info:
        The binning information for true values. This should be calculated from make_dataset_bins. Required for
        calculating non-scalar metrics.
    :return: A dictionary mapping metric name to metric score.
    """
    # Lenient on shape of y_test and y_pred
    y_test = _validation.format_1d(y_test, 'y_test')
    y_pred = _validation.format_1d(y_pred, 'y_pred')

    _validation.validate_regression(y_test, y_pred, metrics)
    _validation.log_regression_debug(y_test, y_pred, y_min, y_max, sample_weight=sample_weight)

    y_min = np.min(y_test) if y_min is None else y_min
    y_max = np.max(y_test) if y_max is None else y_max
    y_std = np.std(y_test) if y_std is None else y_std

    results = {}
    for name in metrics:
        safe_name = _scoring_utilities.get_safe_metric_name(name)
        try:
            metric_class = _scoring_utilities.get_metric_class(name)
            metric = metric_class(y_test, y_pred, y_min=y_min, y_max=y_max, y_std=y_std,
                                  bin_info=bin_info, sample_weight=sample_weight)
            results[name] = metric.compute()

            if utilities.is_scalar(name) and np.isinf(results[name]):
                logger.error("Found infinite regression score for {}, setting to nan".format(safe_name))
                results[name] = np.nan
        except MemoryError:
            raise
        except Exception as e:
            logger.error("Scoring failed for regression metric {}".format(safe_name))
            logging_utilities.log_traceback(e, logger, is_critical=False)
            if utilities.is_scalar(name):
                results[name] = np.nan
            else:
                results[name] = NonScalarMetric.get_error_metric()

    return results


def score_forecasting(
    y_test: np.ndarray,
    y_pred: np.ndarray,
    metrics: List[str],
    horizons: np.ndarray,
    y_max: Optional[float] = None,
    y_min: Optional[float] = None,
    y_std: Optional[float] = None,
    sample_weight: Optional[np.ndarray] = None,
    bin_info: Optional[Dict[str, float]] = None,
    X_test: Optional[pd.DataFrame] = None,
    X_train: Optional[pd.DataFrame] = None,
    y_train: Optional[np.ndarray] = None,
    grain_column_names: Optional[List[str]] = None,
    time_column_name: Optional[str] = None
) -> Dict[str, Union[float, Dict[str, Any]]]:
    """
    Compute model evaluation metrics for a forecasting task.

    `y_max`, `y_min`, and `y_std` should be based on `y_test` information unless
    you would like to compute multiple metrics for comparison (ex. cross validation),
    in which case, you should use a common range and standard deviation. You may
    also pass in `y_max`, `y_min`, and `y_std` if you do not want it to be calculated.

    All metrics present in `metrics` will be present in the output dictionary with either
    the value(s) calculated or `nan` if metric calculation failed.

    :param y_test: The target values.
    :param y_pred: The predicted values.
    :param metrics: List of metric names for metrics to calculate.
    :type metrics: list
    :param horizons: The horizon of each prediction. If missing or not relevant, pass None.
    :param y_max: The max target value.
    :param y_min: The min target value.
    :param y_std: The standard deviation of targets value.
    :param sample_weight:
        The sample weight to be used on metrics calculation. This does not need
        to match sample weights on the fitted model.
    :param bin_info:
        The binning information for true values. This should be calculated from make_dataset_bins. Required for
        calculating non-scalar metrics.
    :param X_test: The inputs which were used to compute the predictions.
    :param X_train: The inputs which were used to train the model.
    :param y_train: The targets which were used to train the model.
    :param grain_column_names: The grain column name.
    :param time_column_name: The time column name.
    :return: A dictionary mapping metric name to metric score.
    """
    # Lenient on shape of y_test, y_pred, and horizons
    y_test = _validation.format_1d(y_test, 'y_test')
    y_pred = _validation.format_1d(y_pred, 'y_pred')
    horizons = _validation.format_1d(horizons, 'horizons')

    _validation.validate_forecasting(y_test, y_pred, horizons, metrics)
    _validation.log_forecasting_debug(y_test, y_pred, horizons, y_min, y_max, sample_weight=sample_weight)

    y_std = np.std(y_test) if y_std is None else y_std

    results = {}
    for name in metrics:
        if name in constants.FORECASTING_NONSCALAR_SET:
            try:
                metric_class = _scoring_utilities.get_metric_class(name)
                metric = metric_class(y_test, y_pred, horizons,
                                      y_std=y_std, bin_info=bin_info,
                                      X_test=X_test, X_train=X_train, y_train=y_train,
                                      grain_column_names=grain_column_names,
                                      time_column_name=time_column_name)
                results[name] = metric.compute()
            except MemoryError:
                raise
            except Exception as e:
                safe_name = _scoring_utilities.get_safe_metric_name(name)
                logger.error("Scoring failed for forecasting metric {}".format(safe_name))
                logging_utilities.log_traceback(e, logger, is_critical=False)
                if utilities.is_scalar(name):
                    results[name] = np.nan
                else:
                    results[name] = NonScalarMetric.get_error_metric()
    return results


def aggregate_scores(
    scores: List[Dict[str, Any]],
    metrics: List[str]
) -> Dict[str, Union[float, Dict[str, Any]]]:
    """
    Compute mean scores across validation folds.

    :param scores: List of results from scoring functions.
    :param metrics: List of metrics to aggregate.
    :return: Dictionary containing the aggregated scores.
    """
    means = {}      # type: Dict[str, Union[float, Dict[str, Any]]]
    for name in metrics:
        if name not in scores[0]:
            logger.warning("Tried to aggregate metric {}, but {} was not found in scores".format(name, name))
            continue

        split_results = [score[name] for score in scores if name in score]
        _validation.log_failed_splits(split_results, name)
        metric_class = _scoring_utilities.get_metric_class(name)
        try:
            means[name] = metric_class.aggregate(split_results)
        except Exception as e:
            safe_name = _scoring_utilities.get_safe_metric_name(name)
            logger.error("Score aggregation failed for metric {}".format(safe_name))
            logging_utilities.log_traceback(e, logger, is_critical=False)
            means[name] = NonScalarMetric.get_error_metric()

        try:
            name_extras = MetricExtrasConstants.MetricExtrasFormat.format(name)
            split_results_extras = [score[name_extras] for score in scores if name_extras in score]

            if len(split_results_extras) > 0:
                means_name_extras = {}  # type: Dict[str, List[float]]

                stats = split_results_extras[0].keys()
                for stat in stats:
                    means_name_extras[stat] = \
                        metric_class.aggregate([score[stat] for score in split_results_extras])

                means[name_extras] = means_name_extras

        except Exception as e:
            safe_name = _scoring_utilities.get_safe_metric_name(name)
            logger.error("Score aggregation failed for metric extras {}".format(safe_name))
            logging_utilities.log_traceback(e, logger, is_critical=False)

    for train_type in constants.ALL_TIME:
        train_times = [res[train_type] for res in scores if train_type in res]
        if train_times:
            means[train_type] = float(np.mean(train_times))

    return means
