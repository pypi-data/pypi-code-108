# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Classe for TimeseriesAutoParamValidationWorker."""
from typing import cast, List, Tuple, Union
import logging

import pandas as pd
from azureml._common._error_definition import AzureMLError
from azureml.automl.core.automl_base_settings import AutoMLBaseSettings
from azureml.automl.core.shared import constants
from azureml.automl.core.shared import utilities
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    TimeseriesInsufficientDataValidateTrainData)
from azureml.automl.core.shared.constants import TimeSeriesInternal
from azureml.automl.core.shared.forecasting_exception import ForecastingDataException
from azureml.automl.core.shared.logging_utilities import function_debug_log_wrapped
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared.constants import TimeSeries

from azureml.automl.runtime import _common_training_utilities
from azureml.automl.runtime.featurizer.transformer.timeseries import forecasting_heuristic_utils
from azureml.automl.runtime.shared.types import DataInputType
from ._timeseries_validator import TimeseriesValidationParamName
from ._timeseries_validator import TimeseriesValidationParameter
from ._timeseries_validator import TimeseriesValidationWorkerBase


class TimeseriesAutoParamValidationWorker(TimeseriesValidationWorkerBase):
    """Validation worker for the auto parameter."""

    def __init__(self) -> None:
        pass

    @function_debug_log_wrapped(logging.INFO)
    def validate(self, param: TimeseriesValidationParameter) -> None:
        """
        Abstract method that validate the auto gen parameter and the train/valid pair.
        """
        automl_settings = param.params[TimeseriesValidationParamName.AUTOML_SETTINGS]
        X = param.params[TimeseriesValidationParamName.X]
        y = param.params[TimeseriesValidationParamName.Y]
        X_valid = param.params[TimeseriesValidationParamName.X_VALID]
        y_valid = param.params[TimeseriesValidationParamName.Y_VALID]

        lags, window_size, forecast_horizon = TimeseriesAutoParamValidationWorker._get_auto_parameters_maybe(
            automl_settings, X, y)
        min_points = utilities.get_min_points(window_size,
                                              lags,
                                              forecast_horizon,
                                              automl_settings.n_cross_validations,
                                              automl_settings.cv_step_size
                                              )
        self._post_auto_param_gen_validation(X, y, X_valid, y_valid,
                                             automl_settings, forecast_horizon,
                                             window_size=window_size, lags=lags,
                                             min_points=min_points)

        # Set the lags, window_size, forecast_horizon, and min_points to the parameter.
        param.params[TimeseriesValidationParamName.LAGS] = lags
        param.params[TimeseriesValidationParamName.WINDOW_SIZE] = window_size
        param.params[TimeseriesValidationParamName.FORECAST_HORIZON] = forecast_horizon
        param.params[TimeseriesValidationParamName.MIN_POINTS] = min_points

    @staticmethod
    def _get_auto_parameters_maybe(automl_settings: AutoMLBaseSettings,
                                   X: pd.DataFrame,
                                   y: DataInputType) -> Tuple[List[int], int, int]:
        """
        Return the parameters which should be estimated heuristically.

        Now 09/18/2019 it is lags, window_size and max_horizon.
        :param automl_settings: The settings of the run.
        :param X: The input data frame. If the type of input is not a data frame no heursitics will be estimated.
        :param y: The expected data.
        """
        # quick check of the data, no need of tsdf here.
        window_size = automl_settings.window_size if automl_settings.window_size is not None else 0
        lags = automl_settings.lags[constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN] \
            if automl_settings.lags is not None else [0]  # type: List[Union[str, int]]
        # We need to get the heuristics to estimate the minimal number of points needed for training.
        max_horizon = automl_settings.max_horizon
        # Estimate heuristics if needed.
        if max_horizon == constants.TimeSeries.AUTO:
            max_horizon = forecasting_heuristic_utils.get_heuristic_max_horizon(
                X,
                automl_settings.time_column_name,
                automl_settings.grain_column_names)
        if window_size == constants.TimeSeries.AUTO or lags == [constants.TimeSeries.AUTO]:
            X[TimeSeriesInternal.DUMMY_TARGET_COLUMN] = y
            heuristics_lags, heuristics_rw = forecasting_heuristic_utils.analyze_pacf_per_grain(
                X,
                automl_settings.time_column_name,
                TimeSeriesInternal.DUMMY_TARGET_COLUMN,
                automl_settings.grain_column_names)
            # Make sure we have removed the y back from the data frame.
            X.drop(TimeSeriesInternal.DUMMY_TARGET_COLUMN, axis=1, inplace=True)
            if window_size == constants.TimeSeries.AUTO:
                window_size = heuristics_rw
            if lags == [constants.TimeSeries.AUTO]:
                lags = [heuristics_lags]
        return cast(List[int], lags), cast(int, window_size), cast(int, max_horizon)

    def _post_auto_param_gen_validation(
            self,
            X: pd.DataFrame,
            y: DataInputType,
            X_valid: pd.DataFrame,
            y_valid: DataInputType,
            automl_settings: AutoMLBaseSettings,
            forecast_horizon: int,
            window_size: int,
            lags: List[int],
            min_points: int) -> None:
        """
        The set of validations, whic can run only after we have detected the auto parameters.

        :param X: The data frame with features.
        :param y: The array with targets/labels.
        :param X_valid: The validation data set.
        :param y_valid: The target
        :param automl_settings: The settings to be used.
        :param forecast_horizon : The max horizon used (after the heuristics were applied).
        :param window_size: The actual window size, provided by the user or detected.
        :param lags: Tje actual lags, provided by the user or detected.
        :param min_points: The minimal number of points necessary to train the model.
        """
        do_check_for_insufficient_data = True
        if hasattr(automl_settings, 'forecasting_dnn_models_only'):
            if hasattr(automl_settings, TimeSeries.SHORT_SERIES_HANDLING_CONFIG):
                """
                short series handling can be resolved 3 ways - pad/drop/do-nothing
                if resolved as padding - this check will never be true because padding happens before this point
                if resolved as dropping - this check should not be done, since dropping happens after this point
                so we only do this check when short series handling is set as None
                The case if all series being short is handled seperately in global validation
                """
                do_check_for_insufficient_data = automl_settings.short_series_handling_configuration is None
            else:
                do_check_for_insufficient_data = not automl_settings.short_series_handling

        if do_check_for_insufficient_data:
            if X.shape[0] < min_points:
                raise ForecastingDataException._with_error(
                    AzureMLError.create(TimeseriesInsufficientDataValidateTrainData, target='X.shape',
                                        reference_code=ReferenceCodes._TS_WRONG_SHAPE_DATA_VALIDATE_TRAIN_DATA,
                                        min_points=min_points,
                                        n_cross_validations=automl_settings.n_cross_validations,
                                        cv_step_size=automl_settings.cv_step_size,
                                        max_horizon=forecast_horizon,
                                        lags=lags,
                                        window_size=window_size,
                                        shape=X.shape[0])
                )
        _common_training_utilities.check_target_uniqueness(y, constants.Subtasks.FORECASTING)
