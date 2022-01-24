# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Methods specific to a Timeseries task type."""

from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd

from azureml.automl.core.automl_base_settings import AutoMLBaseSettings
from azureml.automl.runtime._data_definition import RawExperimentData
from azureml.automl.runtime.shared.score import scoring

from .validation.timeseries_raw_experiment_data_validator import TimeseriesRawExperimentDataValidator


def validate_timeseries(raw_experiment_data: RawExperimentData,
                        automl_settings: AutoMLBaseSettings) -> None:
    """
    Checks whether data is ready for a Timeseries (forecasting) machine learning task

    :param raw_experiment_data: Object which provides access to the training (and/or validation) dataset(s).
    :param automl_settings: The settings for the experiment.
    :return: None
    """
    experiment_data_validator = TimeseriesRawExperimentDataValidator(automl_settings)
    experiment_data_validator.validate(raw_experiment_data)


def evaluate_timeseries(
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
    return scoring.score_forecasting(y_test, y_pred, metrics, horizons, y_max, y_min, y_std, sample_weight, bin_info,
                                     X_test, X_train, y_train, grain_column_names, time_column_name)
