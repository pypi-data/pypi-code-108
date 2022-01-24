# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Pad the short grains based on column type and dataset frequency."""
from typing import List, Optional, Tuple, Set, Any, Union, Dict, cast

import numpy as np
import pandas as pd

from pandas.core.dtypes.dtypes import CategoricalDtype

from azureml._common._error_definition.azureml_error import AzureMLError
from azureml.automl.core.featurization.featurizationconfig import FeaturizationConfig
from azureml.automl.core.shared.constants import TimeSeriesInternal,\
    ShortSeriesHandlingValues
from azureml.automl.core.shared.utilities import get_min_points
from azureml.automl.core.constants import FeatureType
from azureml.automl.core.automl_base_settings import AutoMLBaseSettings
from azureml.automl.core.shared.types import GrainType
from azureml.automl.core.shared.exceptions import ClientException
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    GrainColumnsAndGrainNameMismatch, DateOutOfRangeDuringPadding, DateOutOfRangeDuringPaddingGrain,
    TimeseriesOnePointPerGrain)
from azureml.automl.core.shared.forecasting_exception import ForecastingDataException
from azureml.automl.runtime.column_purpose_detection import _time_series_column_helper
from azureml.automl.runtime.featurizer.transformer.timeseries import forecasting_heuristic_utils
from azureml.automl.runtime.shared.types import DataInputType
from azureml.automl.runtime.faults_verifier import VerifierManager


def pad_short_grains_or_raise(
        X: pd.DataFrame,
        y: np.ndarray,
        freq: pd.DateOffset,
        automl_settings: AutoMLBaseSettings,
        ref_code: str,
        verifier: Optional[VerifierManager] = None
) -> Tuple[pd.DataFrame, np.ndarray]:
    """
    The convenience method to pad the data and avoid exceptions from padding itself.

    Method raises the forecasting data exception if the freq is None. In the
    upstream code the only situation when freq can be none is that we have unique
    values for each of grain and user did not ptovided frequency.
    *Note:* If automl_settings.short_series_handling_configuration has value
    of 'drop' or None the data set will not be changed.
    :param X: The data frame to be analyzed for padding.
    :param y: The taget values.
    :param freq: The frequency of the data set.
    :param automl_settings: The settings object for the data.
    :param ref_code: The reference code to mark an exception if freq is None.
    :raises: ForecastingDataException
    :return: The data frame where all short grains are padded.
    """
    if (automl_settings.short_series_handling_configuration not in
        {ShortSeriesHandlingValues.SHORT_SERIES_HANDLING_AUTO,
         ShortSeriesHandlingValues.SHORT_SERIES_HANDLING_PAD}):
        # If padding is disabled, do not do anythong.
        return X, y

    if freq is None:
        # If we were unable to detect frequency and user did not provide it,
        # we may be working with the data frame where each grain has one value.
        if not automl_settings.grain_column_names:
            if len(X) > 1:
                # Silently fail, because we do not know the real reason of a failure.
                return X, y
        else:
            # Check if grain columns are in the data frame
            if any(grain not in X.columns for grain in automl_settings.grain_column_names):
                # Grain column is not in the data frame, fail silently here.
                return X, y
            # Finally check if grains are actually containing singular values.
            for _, df_one in X.groupby(automl_settings.grain_column_names):
                if len(df_one) > 1:
                    return X, y

        raise ForecastingDataException._with_error(
            AzureMLError.create(
                TimeseriesOnePointPerGrain, target='unique_timepoints',
                reference_code=ref_code
            )
        )
    try:
        return pad_short_grains(X, y, freq, automl_settings, verifier)
    except BaseException as e:
        forecasting_heuristic_utils._log_warn_maybe("Short grain padding has failed with exception.", e)
    return X, y


def pad_short_grains(X: pd.DataFrame,
                     y: np.ndarray,
                     freq: pd.DateOffset,
                     automl_settings: AutoMLBaseSettings,
                     verifier: Optional[VerifierManager] = None) -> Tuple[pd.DataFrame, np.ndarray]:
    """
    Pad the data frame with the NaNs and zeroes.

    :param X: The data frame to be analyzed for padding.
    :param y: The taget values.
    :param freq: The frequency of the data set.
    :param automl_settings: The settings object for the data.
    :return: The data frame where all short grains are padded.
    """
    if automl_settings.grain_column_names:
        for col in automl_settings.grain_column_names:
            if X[col].isnull().any():
                return X, y
    fc = FeaturizationConfig()  # type: FeaturizationConfig
    if isinstance(automl_settings.featurization, dict):
        fc._from_dict(automl_settings.featurization)
    numeric_col = _time_series_column_helper.get_numeric_columns(
        X, automl_settings.time_column_name,
        automl_settings.grain_column_names, fc)
    lags, window_size, max_horizon = forecasting_heuristic_utils.try_get_auto_parameters(
        automl_settings, X, y)
    min_points = get_min_points(
        window_size, lags, max_horizon, automl_settings.n_cross_validations, automl_settings.cv_step_size)
    X[TimeSeriesInternal.DUMMY_TARGET_COLUMN] = y
    # Note: we can not rely on the freq setting in AutoMLBaseSettings,
    # because user may not set it.
    padding_needed = True  # type: bool
    grains_padded = []
    if automl_settings.grain_column_names is not None:
        dfs = []
        groupby_obj = X.groupby(automl_settings.grain_column_names)
        if automl_settings.short_series_handling_configuration == ShortSeriesHandlingValues.SHORT_SERIES_HANDLING_AUTO:
            # Pre check if we have short grains.
            for _, df in groupby_obj:
                if _get_effective_length(df, automl_settings.time_column_name) >= min_points:
                    padding_needed = False
                    break
        if padding_needed:
            for grain, df in groupby_obj:
                df_padded = _pad_one_grain(df, freq,
                                           min_points,
                                           numeric_col,
                                           automl_settings.time_column_name,
                                           automl_settings.grain_column_names,
                                           grain)
                if len(df_padded) > len(df):
                    grains_padded.append(grain)
                dfs.append(df_padded)
            X_new = pd.concat(dfs)
            X_new.reset_index(drop=True, inplace=True)
        else:
            # If padding is 'auto' and there is at least one long grain
            # we do not pad the data. Consequently we will drop short
            # grains during time series transformation.
            X_new = X
    else:
        X_new = _pad_one_grain(X, freq,
                               min_points, numeric_col,
                               automl_settings.time_column_name,
                               automl_settings.grain_column_names)
        if len(X_new) > len(X):
            grains_padded.append(TimeSeriesInternal.USER_FRIENDLY_DEFAULT_GRAIN)
    y_new = X_new.pop(TimeSeriesInternal.DUMMY_TARGET_COLUMN).values

    if verifier is not None and padding_needed:
        verifier.update_data_verifier_short_grain_handling(grains_padded, [])
    # We need to check if _pad_one_grain returned non modified X
    if X is not X_new:
        X.drop(TimeSeriesInternal.DUMMY_TARGET_COLUMN, axis=1, inplace=True)
    return X_new, y_new


def _pad_one_grain(X_one: pd.DataFrame,
                   freq: pd.DateOffset,
                   min_points: int,
                   numeric_col: Set[Any],
                   time_column_name: str,
                   grain_column_names: Optional[List[str]],
                   name: Optional[GrainType] = None) -> pd.DataFrame:
    """
    Pad one grain if needed.

    :param X_one: The grain to be padded.
    :param freq: The frequency of the data set.
    :param min_points: The minimal required number of points.
    :param numeric_col: The set of numeric columns.
    :param time_column_name: The date time column name.
    :param grain_column_names: the optional parameter of grain column names.
    :return: The data frame where all short grains are padded.
    """
    periods = min_points - _get_effective_length(X_one, time_column_name)
    if periods <= 0:
        return X_one
    if pd.isnull(X_one[time_column_name].min()):
        return X_one

    data = np.empty((periods, X_one.shape[1]))
    data[:] = np.NaN
    df_pad = pd.DataFrame(data, columns=X_one.columns.values)
    for col in X_one.columns:
        if not type(X_one[col].dtype).__module__.startswith('pandas'):
            if np.issubdtype(X_one[col].dtype, np.int):
                # If the column to be padded is an integer, we need to convert it to float
                # as np.nan is of a float type.
                X_one[col] = X_one[col].astype('float')
            elif np.issubdtype(X_one[col].dtype, np.datetime64):
                # We will pad the column with the minimal date timestamp from the existing data.
                df_pad[col] = X_one[col].min()
            elif np.issubdtype(X_one[col].dtype, np.dtype('object')):
                # To avoid creating the column, containing only NaN during cross validation
                # we will fill the object column with empty strings instead of NaNs.
                if not X_one[col].isna().all():
                    df_pad[col] = ""
        elif isinstance(X_one[col].dtype, CategoricalDtype):
            # We need to make sure new categories are the same as in X_one
            if not X_one[col].isna().all():
                df_pad[col] = X_one[col].dtype.categories[0]
            df_pad[col] = pd.Categorical(df_pad[col], categories=X_one[col].dtype.categories)
        if col in numeric_col:
            df_pad[col] = 0

    if(TimeSeriesInternal.DUMMY_TARGET_COLUMN in df_pad.columns):
        df_pad[TimeSeriesInternal.DUMMY_TARGET_COLUMN] = _get_target_values_for_padding(
            X_one[TimeSeriesInternal.DUMMY_TARGET_COLUMN],
            len(df_pad))
    try:
        df_pad[time_column_name] = pd.date_range(
            end=X_one[time_column_name].min() - freq, freq=freq, periods=periods)
    except (pd.errors.OutOfBoundsDatetime, OverflowError):
        if name is not None:
            raise ForecastingDataException._with_error(
                AzureMLError.create(
                    DateOutOfRangeDuringPaddingGrain,
                    target='date',
                    reference_code=ReferenceCodes._SHORT_GRAIN_PADDING_INVALID_DATE_GRAIN,
                    grain=name,
                    freq=freq.freqstr,
                    start=X_one[time_column_name].min(),
                    min=pd.Timestamp.min))
        else:
            raise ForecastingDataException._with_error(
                AzureMLError.create(
                    DateOutOfRangeDuringPadding,
                    target='date',
                    reference_code=ReferenceCodes._SHORT_GRAIN_PADDING_INVALID_DATE,
                    freq=freq.freqstr,
                    start=X_one[time_column_name].min(),
                    min=pd.Timestamp.min))
    if grain_column_names is not None and name is not None:
        col_num = 0
        if name is not None and not isinstance(name, tuple) and not isinstance(name, list):
            name = (name,)
        if len(name) != len(grain_column_names):
            # We raise here the Client exception because
            #
            raise ClientException._with_error(
                AzureMLError.create(
                    GrainColumnsAndGrainNameMismatch,
                    target='grain_names',
                    reference_code=ReferenceCodes._SHORT_GRAIN_PADDING_INVALID_GRAIN))
        for grain_col in grain_column_names:
            df_pad[grain_col] = name[col_num]
            col_num += 1

    X_one = X_one.append(df_pad)
    X_one.sort_values(by=time_column_name, inplace=True)
    X_one.reset_index(inplace=True, drop=True)
    return X_one


def _get_target_values_for_padding(target: pd.Series, size: int) -> np.ndarray:
    # Add the Gaussian noise with center being the median
    # and standard deviation is median * 5e-05.
    if target.isnull().all():
        median = 0.0  # type: float
    else:
        median = target.median()
    # We know that np.random.normal will not return scalar, because
    # we have supplied the non None size parameter.
    noise = np.random.normal(
        loc=median,
        scale=1.0 * 5e-05 if median == 0 else abs(median) * 5e-05,
        size=size)
    if median >= 0:
        noise[noise < 0] = 0
    return cast(np.ndarray, noise)


def _get_effective_length(X_one: pd.DataFrame,
                          time_column_name: str,
                          target_column_name: str = TimeSeriesInternal.DUMMY_TARGET_COLUMN) -> int:
    """
    Get the effective size of the data frame.

    Do not count rows with NaNs in time and target columns.
    **NOTE:** This function is NOT grain aware.
    :param X: The data frame to count effective rows for.
    :param time_column_name: The name of a time columns.
    :param target_column_name: The name of a target column.
    :return: The number of rows after data frame cleanup.
    """
    if target_column_name not in X_one.columns:
        return 0
    return cast(int, len(X_one) - (X_one[time_column_name].isna() | X_one[target_column_name].isna()).sum())
