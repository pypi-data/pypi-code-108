# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Computation of available metrics."""
from typing import Any, cast, Dict, List, Optional, Tuple, Union
import logging

import numpy as np
import pandas as pd

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared._diagnostics.automl_error_definitions import AutoMLInternal
from sklearn.base import TransformerMixin

from azureml.automl.core.shared import constants
from azureml.automl.core.shared import utilities as core_utilities
from azureml.automl.core.shared.exceptions import ValidationException
from azureml.automl.runtime import _ml_engine
from azureml.automl.runtime.shared.score import scoring, utilities as metrics_utilities


logger = logging.getLogger(__name__)


METRICS_ERROR_TARGET = 'MetricsComputation'


def get_default_metric_with_objective(task):
    """This function is deprecated. Please use azureml.automl.core.shared.utilities."""
    return core_utilities.get_default_metric_with_objective(task)


def minimize_or_maximize(metric, task=None):
    """This function is deprecated. Please use azureml.automl.core.shared.utilities."""
    return core_utilities.minimize_or_maximize(metric, task=task)


def is_better(val1, val2, metric=None, task=None, objective=None):
    """This function is deprecated. Please use azureml.automl.runtime.shared.score functions."""
    return metrics_utilities.is_better(val1, val2, metric=metric, objective=objective)


def get_all_nan(task):
    """This function is deprecated. Please use azureml.automl.runtime.shared.score functions."""
    return metrics_utilities.get_all_nan(task)


def get_metric_ranges(task, for_assert_sane=False):
    """This function is deprecated. Please use azureml.automl.runtime.shared.score functions."""
    return metrics_utilities.get_metric_ranges(task)


def get_worst_values(task, for_assert_sane=False):
    """This function is deprecated. Please use azureml.automl.runtime.shared.score functions."""
    return metrics_utilities.get_worst_values(task)


def get_min_values(task):
    """This function is deprecated. Please use azureml.automl.runtime.shared.score functions."""
    return metrics_utilities.get_min_values(task)


def get_max_values(task, for_assert_sane=False):
    """This function is deprecated. Please use azureml.automl.runtime.shared.score functions."""
    return metrics_utilities.get_max_values(task)


def assert_metrics_sane(scores, task):
    """This function is deprecated. Please use azureml.automl.runtime.shared.score functions."""
    return metrics_utilities.assert_metrics_sane(scores, task)


def get_scalar_metrics(task):
    """This function is deprecated. Please use azureml.automl.runtime.shared.score functions."""
    return metrics_utilities.get_scalar_metrics(task)


def get_default_metrics(task):
    """This function is deprecated. Please use azureml.automl.runtime.shared.score functions."""
    return metrics_utilities.get_default_metrics(task)


def compute_metrics(y_pred: np.ndarray,
                    y_test: np.ndarray,
                    metrics: Optional[List[str]] = None,
                    task: str = constants.Tasks.CLASSIFICATION,
                    sample_weight: Optional[np.ndarray] = None,
                    num_classes: Optional[int] = None,
                    class_labels: Optional[np.ndarray] = None,
                    trained_class_labels: Optional[np.ndarray] = None,
                    y_transformer: Optional[TransformerMixin] = None,
                    y_max: Optional[float] = None,
                    y_min: Optional[float] = None,
                    y_std: Optional[float] = None,
                    bin_info: Optional[Dict[str, float]] = None,
                    horizons: Optional[np.ndarray] = None) -> Dict[str, Union[float, Dict[str, Any]]]:
    """This function is deprecated. Please use azureml.automl.runtime.shared.score.scoring."""
    if metrics is None:
        metrics = get_default_metrics(task)

    if task == constants.Tasks.CLASSIFICATION:
        return compute_metrics_classification(y_pred, y_test, metrics,
                                              num_classes=num_classes,
                                              sample_weight=sample_weight,
                                              class_labels=class_labels,
                                              trained_class_labels=trained_class_labels,
                                              y_transformer=y_transformer)
    elif task == constants.Tasks.REGRESSION:
        return compute_metrics_regression(y_pred, y_test, metrics,
                                          y_max, y_min, y_std,
                                          sample_weight=sample_weight,
                                          bin_info=bin_info)
    elif task == constants.Subtasks.FORECASTING:
        return compute_metrics_forecasting(y_pred, y_test, cast(np.ndarray, horizons), metrics,
                                           y_max, y_min, y_std,
                                           sample_weight=sample_weight,
                                           bin_info=bin_info)
    else:
        raise NotImplementedError


def compute_metrics_classification(y_pred_probs: Union[np.ndarray, pd.DataFrame],
                                   y_test: np.ndarray,
                                   metrics: List[str],
                                   num_classes: Optional[int] = None,
                                   sample_weight: Optional[np.ndarray] = None,
                                   class_labels: Optional[np.ndarray] = None,
                                   trained_class_labels: Optional[np.ndarray] = None,
                                   y_transformer: Optional[TransformerMixin] = None,
                                   logger: Optional[logging.Logger] = None) -> Dict[str, Union[float, Dict[str, Any]]]:
    """This function is deprecated. Please use azureml.automl.runtime.shared.score.scoring.score_classification."""
    logging.warning("azureml.automl.runtime.shared.metrics.compute_metrics_classification is deprecated. "
                    "Please use azureml.automl.runtime.shared.score.scoring.score_classification")

    if isinstance(y_pred_probs, pd.DataFrame):
        y_pred_probs = y_pred_probs.values

    class_labels, trained_class_labels = _infer_classification_inputs(class_labels, trained_class_labels,
                                                                      y_test, y_pred_probs)

    return _ml_engine.evaluate_classifier(y_test, y_pred_probs, metrics,
                                          class_labels, trained_class_labels,
                                          sample_weight=sample_weight, y_transformer=y_transformer,
                                          use_binary=False)


def _infer_classification_inputs(
    class_labels: Optional[np.ndarray],
    trained_class_labels: Optional[np.ndarray],
    y_test: np.ndarray,
    y_pred_probs: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """
    This passthrough will attempt to infer missing arguments, but is not expected to work in general.

    We cannot assume:
      - the model was trained on all class_labels
      - the model is being evaluated on all class_labels
      - class_labels are consecutive integers from 0 to num_classes - 1
    """
    n_train_labels = y_pred_probs.shape[1]

    if class_labels is None:
        test_labels = np.unique(y_test)
        if test_labels.shape[0] >= n_train_labels:
            class_labels = test_labels
        else:
            message = "class_labels are required to compute classification metrics"
            logger.error(message)
            raise ValidationException._with_error(
                AzureMLError.create(AutoMLInternal, target="class_labels", error_details=message)
            )

    if trained_class_labels is None:
        if class_labels.shape[0] > n_train_labels:
            trained_class_labels = class_labels[:n_train_labels]
        elif class_labels.shape[0] < n_train_labels:
            message = "trained_class_labels are required to compute classification metrics"
            logger.error(message)
            raise ValidationException._with_error(
                AzureMLError.create(AutoMLInternal, target="trained_class_labels", error_details=message)
            )
        else:
            trained_class_labels = class_labels
    return class_labels, trained_class_labels


def compute_metrics_regression(y_pred: np.ndarray,
                               y_test: np.ndarray,
                               metrics: List[str],
                               y_max: Optional[float] = None,
                               y_min: Optional[float] = None,
                               y_std: Optional[float] = None,
                               sample_weight: Optional[np.ndarray] = None,
                               bin_info: Optional[Dict[str, float]] = None,
                               logger: Optional[logging.Logger] = None) -> Dict[str, Union[float, Dict[str, Any]]]:
    """This function is deprecated. Please use azureml.automl.runtime.shared.score.scoring.score_regression."""
    logging.warning("azureml.automl.runtime.shared.metrics.compute_metrics_regression is deprecated. "
                    "Please use azureml.automl.runtime.shared.score.scoring.score_regression")

    return scoring.score_regression(y_test, y_pred, metrics,
                                    y_max=y_max, y_min=y_min, y_std=y_std,
                                    sample_weight=sample_weight, bin_info=bin_info)


def compute_metrics_forecasting(y_pred: np.ndarray,
                                y_test: np.ndarray,
                                horizons: np.ndarray,
                                metrics: List[str],
                                y_max: Optional[float] = None,
                                y_min: Optional[float] = None,
                                y_std: Optional[float] = None,
                                sample_weight: Optional[np.ndarray] = None,
                                bin_info: Optional[Dict[str, float]] = None,
                                logger: Optional[logging.Logger] = None,
                                X_test: Optional[pd.DataFrame] = None,
                                X_train: Optional[pd.DataFrame] = None,
                                y_train: Optional[np.ndarray] = None,
                                grain_column_names: Optional[List[str]] = None
                                ) -> Dict[str, Union[float, Dict[str, Any]]]:
    """This function is deprecated. Please use azureml.automl.runtime.shared.score.scoring.score_forecasting."""
    logging.warning("azureml.automl.runtime.shared.metrics.compute_metrics_forecasting is deprecated. "
                    "Please use azureml.automl.runtime.shared.score.scoring.score_forecasting")

    return scoring.score_forecasting(y_test, y_pred, metrics, horizons,
                                     y_max=y_max, y_min=y_min, y_std=y_std,
                                     sample_weight=sample_weight, bin_info=bin_info,
                                     X_test=X_test, X_train=X_train, y_train=y_train,
                                     grain_column_names=grain_column_names)


def compute_mean_cv_scores(
        scores: List[Dict[Any, Any]],
        metrics: List[str],
        logger: Optional[logging.Logger] = None) -> Dict[str, Union[float, Dict[str, Any]]]:
    """This function is deprecated. Please use azureml.automl.runtime.shared.score.scoring.aggregate_scores."""
    logging.warning("azureml.automl.runtime.shared.metrics.compute_mean_cv_scores is deprecated. "
                    "Please use azureml.automl.runtime.shared.score.scoring.aggregate_scores")

    return scoring.aggregate_scores(scores, metrics)
