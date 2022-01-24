# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Validation for AutoML metrics."""
import logging
import numpy as np
from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared._diagnostics.automl_error_definitions import AutoMLInternal
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.reference_codes import ReferenceCodes

from sklearn.base import TransformerMixin
from typing import Dict, List, Optional, Any

from azureml.automl.runtime.shared.score import constants, utilities
from azureml.automl.runtime.shared.score._metric_base import NonScalarMetric
from azureml.automl.core.shared.exceptions import ValidationException


logger = logging.getLogger(__name__)


def validate_classification(y_test: np.ndarray,
                            y_pred_probs: np.ndarray,
                            metrics: List[str],
                            class_labels: np.ndarray,
                            train_labels: np.ndarray,
                            sample_weight: Optional[np.ndarray],
                            y_transformer: Optional[TransformerMixin],
                            multilabel: Optional[bool] = False) -> None:
    """
    Validate the inputs for scoring classification.

    :param y_test: Target values.
    :param y_pred_probs: The predicted probabilities for all classes.
    :param metrics: Metrics to compute.
    :param class_labels: All classes found in the full dataset.
    :param train_labels: Classes as seen (trained on) by the trained model.
    :param sample_weight: Weights for the samples.
    :param y_transformer: Used to inverse transform labels.
    :param multilabel: Indicate if it is multilabel classification.
    """
    for metric in metrics:
        Contract.assert_true(
            metric in constants.CLASSIFICATION_SET, "Metric {} not a valid classification metric".format(metric),
            target="metric", reference_code=ReferenceCodes._METRIC_INVALID_CLASSIFICATION_METRIC
        )

    _check_array_type(y_test, 'y_test')
    _check_array_type(y_pred_probs, 'y_pred_probs')
    _check_array_type(class_labels, 'class_labels')
    _check_array_type(train_labels, 'train_labels')
    _check_array_type(sample_weight, 'sample_weight', ignore_none=True)

    _check_arrays_first_dim(y_test, y_pred_probs, 'y_test', 'y_pred_probs')

    _check_arrays_same_type({
        'class_labels': class_labels,
        'train_labels': train_labels,
        'y_test': y_test,
    }, check_numeric_type=False)

    _check_dim(class_labels, 'class_labels', 1)
    _check_dim(train_labels, 'train_labels', 1)

    if not multilabel:
        _check_dim(y_test, 'y_test', 1)
    else:
        _check_dim(y_test, 'y_test', 2)

    _check_dim(y_pred_probs, 'y_pred_probs', 2)

    _check_array_values(class_labels, 'class_labels')
    _check_array_values(train_labels, 'train_labels')
    _check_array_values(y_test, 'y_test')
    _check_array_values(y_pred_probs, 'y_pred_probs')

    if sample_weight is not None:
        _check_array_values(sample_weight, 'sample_weight')

    unique_classes = np.unique(class_labels)
    Contract.assert_true(unique_classes.shape[0] >= 2,
                         message="Number of classes must be at least 2 for classification (got {})".format(
                             unique_classes.shape[0]),
                         target="num_unique_classes", log_safe=True)

    if sample_weight is not None:
        Contract.assert_true(sample_weight.dtype.kind in set('fiu'),
                             message="Type of sample_weight must be numeric (got type {})".format(sample_weight.dtype),
                             target="sample_weight", log_safe=True)

        Contract.assert_true(y_test.shape[0] == sample_weight.shape[0],
                             message="Number of samples does not match in y_test ({}) and sample_weight ({})".format(
                                 y_test.shape[0], sample_weight.shape[0]),
                             target="sample_weight", log_safe=True)

    Contract.assert_true(train_labels.shape[0] == y_pred_probs.shape[1],
                         message="train_labels.shape[0] ({}) does not match y_pred_probs.shape[1] ({}).".format(
                             train_labels.shape[0], y_pred_probs.shape[1]), log_safe=True)
    if multilabel:
        Contract.assert_true(train_labels.shape[0] == y_test.shape[1],
                             message="train_labels.shape[0] ({}) does not match y_test.shape[1] ({}).".format(
            train_labels.shape[0], y_test.shape[1]), log_safe=True)

    set_diff = np.setdiff1d(train_labels, class_labels)
    if set_diff.shape[0] != 0:
        logger.error("train_labels contains values not present in class_labels")
        message = "Labels {} found in train_labels are missing from class_labels.".format(set_diff)
        raise ValidationException._with_error(
            AzureMLError.create(
                AutoMLInternal, target="train_labels",
                reference_code=ReferenceCodes._METRIC_VALIDATION_EXTRANEOUS_TRAIN_LABELS, error_details=message)
        )

    # This validation is not relevant for multilabel as the y_test is in one-hot encoded format.
    if not multilabel:
        set_diff = np.setdiff1d(np.unique(y_test), class_labels)
        if set_diff.shape[0] != 0:
            logger.error("y_test contains values not present in class_labels")
            message = "Labels {} found in y_test are missing from class_labels.".format(set_diff)
            raise ValidationException._with_error(
                AzureMLError.create(
                    AutoMLInternal, target="y_test",
                    reference_code=ReferenceCodes._METRIC_VALIDATION_EXTRANEOUS_YTEST_LABELS, error_details=message)
            )


def log_classification_debug(y_test: np.ndarray,
                             y_pred_probs: np.ndarray,
                             class_labels: np.ndarray,
                             train_labels: np.ndarray,
                             sample_weight: Optional[np.ndarray] = None,
                             multilabel: Optional[bool] = False) -> None:
    """
    Log shapes of classification inputs for debugging.

    :param y_pred_probs: The predicted probabilities for all classes.
    :param class_labels: All classes found in the full dataset.
    :param train_labels: Classes as seen (trained on) by the trained model.
    :param sample_weight: Weights for the samples.
    :param multilabel: Indicate if it is multilabel classification.
    """

    unique_y_test = np.unique(y_test)
    debug_data = {
        'y_test': y_test.shape,
        'y_pred_probs': y_pred_probs.shape,
        'unique_y_test': unique_y_test.shape,
        'class_labels': class_labels.shape,
        'train_labels': train_labels.shape,
        'n_missing_train': np.setdiff1d(class_labels, train_labels).shape[0],
        'n_missing_valid': np.setdiff1d(class_labels, unique_y_test).shape[0],
        'sample_weight': None if sample_weight is None else sample_weight.shape
    }

    if not multilabel:
        unique_y_test = np.unique(y_test)
        debug_data.update({'unique_y_test': unique_y_test.shape,
                           'n_missing_valid': np.setdiff1d(class_labels, unique_y_test).shape[0]})
    else:
        # Log the difference in the no of labels between class_labels and y_test
        debug_data.update({'n_missing_valid': class_labels.shape[0] - y_test.shape[1]})

    logger.info("Classification metrics debug: {}".format(debug_data))


def validate_regression(y_test: np.ndarray,
                        y_pred: np.ndarray,
                        metrics: List[str]) -> None:
    """
    Validate the inputs for scoring regression.

    :param y_test: Target values.
    :param y_pred: Target predictions.
    :param metrics: Metrics to compute.
    """
    for metric in metrics:
        Contract.assert_true(
            metric in constants.REGRESSION_SET, "Metric {} not a valid regression metric".format(metric),
            target="metric", reference_code=ReferenceCodes._METRIC_INVALID_REGRESSION_METRIC
        )

    _check_array_type(y_test, 'y_test')
    _check_array_type(y_pred, 'y_pred')

    _check_arrays_first_dim(y_test, y_pred, 'y_test', 'y_pred')
    _check_array_values(y_test, 'y_test')
    _check_array_values(y_pred, 'y_pred')


def log_regression_debug(y_test: np.ndarray,
                         y_pred: np.ndarray,
                         y_min: Optional[float],
                         y_max: Optional[float],
                         sample_weight: Optional[np.ndarray] = None) -> None:
    """
    Log shapes of regression inputs for debugging.

    :param y_test: Target values.
    :param y_pred: Predicted values.
    :param y_min: Minimum target value.
    :param y_max: Maximum target value.
    :param sample_weight: Weights for the samples.
    """
    min_max_equal = None if None in [y_min, y_max] else y_min == y_max
    debug_data = {
        'y_test': y_test.shape,
        'y_pred': y_pred.shape,
        'y_test_unique': np.unique(y_test).shape[0],
        'y_pred_unique': np.unique(y_pred).shape[0],
        'y_test_has_negative': (y_test < 0).sum() > 0,
        'y_pred_has_negative': (y_pred < 0).sum() > 0,
        'min_max_equal': min_max_equal,
        'sample_weight': None if sample_weight is None else sample_weight.shape
    }

    logger.info("Regression metrics debug: {}".format(debug_data))


def validate_forecasting(y_test: np.ndarray,
                         y_pred: np.ndarray,
                         horizons: np.ndarray,
                         metrics: List[str]) -> None:
    """
    Validate the inputs for scoring forecasting.

    :param y_test: Target values.
    :param y_pred: Target predictions.
    :param horizons: Forecast horizons per sample.
    :param metrics: Metrics to compute.
    """
    for metric in metrics:
        Contract.assert_true(
            metric in constants.FORECASTING_SET, "Metric {} not a valid forecasting metric".format(metric),
            target="metric", reference_code=ReferenceCodes._METRIC_INVALID_FORECASTING_METRIC
        )

    _check_array_type(y_test, 'y_test')
    _check_array_type(y_pred, 'y_pred')
    _check_array_type(horizons, 'horizons')

    _check_arrays_first_dim(y_test, y_pred, 'y_test', 'y_pred')
    _check_arrays_first_dim(y_test, horizons, 'y_test', 'horizons')
    _check_array_values(y_test, 'y_test')
    _check_array_values(y_pred, 'y_pred')
    _check_array_values(horizons, 'horizons', validate_type=False)


def log_forecasting_debug(y_test: np.ndarray,
                          y_pred: np.ndarray,
                          horizons: np.ndarray,
                          y_min: Optional[float],
                          y_max: Optional[float],
                          sample_weight: Optional[np.ndarray] = None) -> None:
    """
    Log shapes of forecasting inputs for debugging.

    :param y_test: Target values.
    :param y_pred: Predicted values.
    :param horizons: Forecast horizons per sample.
    :param y_min: Minimum target value.
    :param y_max: Maximum target value.
    :param sample_weight: Weights for the samples.
    """
    min_max_equal = None if None in [y_min, y_max] else y_min == y_max
    debug_data = {
        'y_test': y_test.shape,
        'y_pred': y_pred.shape,
        'horizons': horizons.shape,
        'y_test_unique': np.unique(y_test).shape[0],
        'y_pred_unique': np.unique(y_pred).shape[0],
        'y_test_has_negative': (y_test < 0).sum() > 0,
        'y_pred_has_negative': (y_pred < 0).sum() > 0,
        'min_max_equal': min_max_equal,
        'sample_weight': None if sample_weight is None else sample_weight.shape
    }

    logger.info("Forecasting metrics debug: {}".format(debug_data))


def _check_arrays_first_dim(array_a: np.ndarray,
                            array_b: np.ndarray,
                            array_a_name: str,
                            array_b_name: str) -> None:
    """
    Validate that two arrays have the same shape in the first dimension.

    :array_a: First array.
    :array_b: Second array.
    :array_a_name: First array name.
    :array_b_name: Second array name.
    """
    Contract.assert_value(array_a, array_a_name)
    Contract.assert_value(array_b, array_b_name)
    message = "Number of samples does not match in {} ({}) and {} ({})".format(
        array_a_name, array_a.shape[0], array_b_name, array_b.shape[0])
    Contract.assert_true(array_a.shape[0] == array_b.shape[0], message=message, log_safe=True)


def _check_array_values(arr: np.ndarray,
                        name: str,
                        validate_type: bool = True) -> None:
    """
    Check the array for correct types and reasonable values.

    :param arr: Array to check.
    :param name: Array name.
    :param validate_type: Whether to validate the array type.
    """
    # Convert object types
    if arr.dtype == object:
        if isinstance(arr[0], (int, float)):
            arr = arr.astype(float)
        elif isinstance(arr[0], str):
            arr = arr.astype(str)

    if arr.dtype.kind in set('bcfiu'):
        message = "Elements of {} cannot be {}"
        Contract.assert_true(~np.isnan(arr).any(), message=message.format(name, 'NaN'), log_safe=True)
        Contract.assert_true(np.isfinite(arr).all(), message=message.format(name, 'infinite'), log_safe=True)
    elif np.issubdtype(arr.dtype, np.str_):
        pass
    else:
        if validate_type:
            message = ("{} should have numeric or string type, found type {}. "
                       "Elements have type {}").format(name, arr.dtype, type(arr[0]))
            logger.error(message)


def _check_array_type(arr: Any, name: str, ignore_none: bool = False) -> None:
    """
    Check that the input is a numpy array.

    :param arr: Array object to validate.
    :param name: Name of array to use in error message.
    :param validate_none: Whether to validate the array as None-type.
    """
    if ignore_none and arr is None:
        return

    Contract.assert_value(arr, name)

    try:
        arr.dtype
    except AttributeError:
        message = "Argument {} must be a numpy array, not {}".format(name, type(arr))
        Contract.assert_true(False, message=message, log_safe=True)


def _check_arrays_same_type(array_dict: Dict[str, np.ndarray], check_numeric_type: bool = True) -> None:
    """
    Check that multiple arrays have the same types.

    :param array_dict: Dictionary from array name to array.
    :param check_numeric_type: whether to compare numeric arrays
    """
    items = list(array_dict.items())
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            i_type, j_type = items[i][1].dtype, items[j][1].dtype
            i_name, j_name = items[i][0], items[j][0]

            # Handle equivalent types like int32/int64 integers, U1/U2 strings
            if check_numeric_type:
                # check if two numeric types are equivalent types
                if np.issubdtype(i_type, np.integer) and np.issubdtype(j_type, np.integer):
                    continue
                if np.issubdtype(i_type, np.floating) and np.issubdtype(j_type, np.floating):
                    continue
            else:
                # if they are both numeric, then continue
                if np.issubdtype(i_type, np.number) and np.issubdtype(j_type, np.number):
                    continue
            if np.issubdtype(i_type, np.str_) and np.issubdtype(j_type, np.str_):
                continue

            # Handle all other types
            Contract.assert_true(i_type == j_type,
                                 message="{} ({}) does not have the same type as {} ({})".format(
                                     i_name, i_type, j_name, j_type),
                                 log_safe=True)


def _check_dim(arr: np.ndarray,
               name: str,
               n_dim: int) -> None:
    """
    Check the number of dimensions for the given array.

    :param arr: Array to check.
    :param name: Array name.
    :param n_dim: Expected number of dimensions.
    """
    Contract.assert_true(arr.ndim == n_dim, message="{} must be an ndarray with {} dimensions, found {}".format(
        name, n_dim, arr.ndim), target=name, log_safe=True)


def format_1d(arr: np.ndarray,
              name: str) -> np.ndarray:
    """
    Format an array as 1d if possible.

    :param arr: The array to reshape.
    :param name: Name of the array to reshape.
    :return: Array of shape (x,).
    """
    _check_array_type(arr, name)

    if arr.ndim == 2 and (arr.shape[0] == 1 or arr.shape[1] == 1):
        arr = np.ravel(arr)
    return arr


def log_failed_splits(scores, metric):
    """
    Log if a metric could not be computed for some splits.

    :scores: The scores over all splits for one metric.
    :metric: Name of the metric.
    """
    n_splits = len(scores)

    failed_splits = []
    for score_index, score in enumerate(scores):
        if utilities.is_scalar(metric):
            if np.isnan(score):
                failed_splits.append(score_index)
        else:
            if NonScalarMetric.is_error_metric(score):
                failed_splits.append(score_index)
    n_failures = len(failed_splits)
    failed_splits_str = ', '.join([str(idx) for idx in failed_splits])

    if n_failures > 0:
        warn_args = metric, n_failures, n_splits, failed_splits_str
        warn_msg = "Could not compute {} for {}/{} validation splits: {}"
        logger.warning(warn_msg.format(*warn_args))
