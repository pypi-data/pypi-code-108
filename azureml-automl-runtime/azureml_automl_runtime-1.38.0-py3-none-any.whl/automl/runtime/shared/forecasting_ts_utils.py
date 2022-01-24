# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utility functions for manipulating data in a TimeSeriesDataFrame object."""
from typing import Tuple, TYPE_CHECKING, cast, Dict
from warnings import warn

import numpy as np
import pandas as pd
from azureml._common._error_definition import AzureMLError
from azureml._common._error_definition.user_error import ArgumentOutOfRange
from azureml.automl.core.shared._diagnostics.automl_error_definitions import GrainShorterThanTestSize
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    InvalidArgumentType,
    InvalidSeriesForStl,
    TimeseriesInputIsNotTimeseriesDf)
from azureml.automl.core.shared._diagnostics.validation import Validation
from azureml.automl.core.shared.exceptions import DataException, ValidationException
from azureml.automl.core.shared.forecasting_exception import ForecastingDataException
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.runtime.shared import forecasting_utils, forecasting_verify as verify

# NOTE:
# Do not import TimeSeriesDataFrame or ForecastDataFrame at the top of this
# file, because both of them import this file as well, and circular references
# emerge. It is OK to import TSDF or FDF inside a function instead.
# Here we import type checking only for type checking time.
# during runtime TYPE_CHECKING is set to False.
if TYPE_CHECKING:
    from azureml.automl.runtime.shared.time_series_data_frame import TimeSeriesDataFrame

SEASONAL_DETECT_FFT_THRESH_SIZE = 1024
SEASONAL_DETECT_MIN_OBS = 5


def detect_seasonality(ts_values: np.ndarray) -> int:
    """
    Detect a dominant seasonality in a scalar valued time-series.

    A "seasonality" refers to a lag value with a significant peak
    in the autocorrelation function of the series.
    :param ts_values: series values sorted by ascending time
    :type ts_values: numpy.ndarray
    :return:
        Lag value associated with the strongest autocorrelation peak.
        If no significant peaks can be found, then the function returns
        the value 1
    :rtype: int

    """
    from statsmodels.tsa.tsatools import detrend
    from statsmodels.tsa.stattools import acf

    # Don't bother trying to find a seasonality for very short series
    ts_len = len(ts_values)
    if ts_len < SEASONAL_DETECT_MIN_OBS:
        return 1

    # Define the autocorr threshold above which a lag is considered "seasonal"
    # Here, we use a combination of a statistical significance level
    #  (stat_thresh) and a constant correlation value (min_thresh):
    #  thresh = max(stat_thresh, min_thresh)
    # Null hypothesis for stat_thresh assumes a white noise, gaussian process.
    # The constant, min_thresh, was subjectively determined to be a reasonable
    #  threshold (it is used in the .NET seasonality detector as well)
    z_95 = 1.96
    z_thresh = z_95 / np.sqrt(ts_len)
    min_thresh = 0.45
    autocorr_thresh = z_thresh if z_thresh > min_thresh else min_thresh

    # Compute autocorr for lags up to half the data size
    # i.e. Shannon-Nyquist Sampling Theorem
    nlags = int(np.floor(ts_len / 2.0))

    # If the data has trend, this biases the autocorr estimate
    # Attempt to remove any linear trend in the series
    ts_values_detrend = detrend(ts_values, order=1)

    # Compute the autocorr function
    # Plain autocorr is n^2, FFT is nlog(n). So use FFT for long series
    use_FFT = ts_len > SEASONAL_DETECT_FFT_THRESH_SIZE
    ts_values_acf = acf(ts_values_detrend, nlags=nlags, fft=use_FFT)

    # Find the lag (other than 0) with the maximum autocorr
    max_acf_lag = np.argmax(ts_values_acf[1:]) + 1
    max_acf = ts_values_acf[max_acf_lag]

    return cast(int, max_acf_lag if max_acf >= autocorr_thresh else 1)


def detect_seasonality_tsdf(X: 'TimeSeriesDataFrame') -> int:
    """
    Return the dominant seasonality in the dataframe.

    If different grains have different seasonality the warning is shown and
    the most frequent seasonality will be returned.
    :param X: The dataset.
    :type X: azureml.automl.runtime.shared.time_series_data_frame.TimeSeriesDataFrame
    :returns: The seasonality.
    :rtype: int

    """
    from azureml.automl.runtime.shared.time_series_data_frame import TimeSeriesDataFrame

    verify.type_is_one_of(type(X), [np.dtype(TimeSeriesDataFrame)], "Input")

    # seasonality->number of grains with it.
    seasonality_dict = dict()  # type: Dict[int, int]
    dom_seasonality = -1
    max_series = 0
    for grain, df_one in X.groupby_grain():
        seasonality = detect_seasonality(df_one.ts_value)
        if seasonality not in seasonality_dict:
            seasonality_dict[seasonality] = 0
        seasonality_dict[seasonality] += 1
        if seasonality_dict[seasonality] > max_series:
            max_series = seasonality_dict[seasonality]
            dom_seasonality = seasonality
    if len(seasonality_dict.keys()) > 1:
        warn(
            'Different grains have different seasonality, '
            'the mode seasonality of {} will be used.'.format(seasonality))
    return dom_seasonality


def get_stl_decomposition(ts_values: np.ndarray, seasonality: int = 1) \
        -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute a Seasonal and Trend decomposition using Loess smoothing.

    This function computes the "STL decomposition" of a 1-D array, returning a tuple containing
    the seasonal, trend, and residual components as 1-D arrays. The trend is determined via Loess smoothing
    and the seasonal component is periodic with a periodicity of the input seasonality.
    The decomposition is additive, so the returned components sum to the original values:
    ts_values = seasonal + trend + residual.

    :param ts_values: 1-D time series to decompose
    :type ts_values: numpy.ndarray
    :param seasonality: Seasonality of the input series
    :type seasonality: int
    :return: Components of the STL decomposition
    :rtype: tuple(numpy.ndarray, numpy.ndarray, numpy.ndarray)
    """
    from statsmodels.nonparametric.smoothers_lowess import lowess

    if np.any(pd.isnull(ts_values)):
        raise DataException._with_error(AzureMLError.create(InvalidSeriesForStl, target="X"))

    endog = ts_values.squeeze()

    # Step 1 - estimate trend via LOWESS regression
    exog = np.arange(len(endog))
    trend = lowess(endog, exog, is_sorted=True, missing='drop', return_sorted=False)

    # Step 2 - detrend the signal
    endog_detrend = endog - trend

    if len(endog) >= seasonality:
        # Step 3 - calculate seasonality strided means and then center the result
        period_means = np.fromiter((np.mean(endog_detrend[p::seasonality]) for p in range(seasonality)), float)
        period_means -= np.mean(period_means)

        # Step 4 - create the seasonal component by tiling the period averages
        nseasons = int(np.ceil(len(endog) / seasonality))
        seasonal = np.tile(period_means, nseasons)[:len(endog)]
    else:
        # If seasonality is longer than series length, cannot safely compute a seasonal component
        # Default to zeros in this case
        seasonal = np.zeros(len(endog))

    # Step 5 - get the residual
    residual = endog_detrend - seasonal

    return seasonal, trend, residual


def last_n_periods_split(tsdf: 'TimeSeriesDataFrame',
                         test_size: int) -> Tuple['TimeSeriesDataFrame', 'TimeSeriesDataFrame']:
    """
    Split input dataset into training and testing datasets.

    The split is such that, for each grain, this function
    assign last ``test_size`` number of data points into a test dataset and
    hold off the initial data points for training dataset.
    If origin_time is not set in ``tsdf``, then each data point corresponds to
    a single time step (period).

    :param tsdf:
        Input dataset to generate the test dataset from.
    :type tsdf:
        azureml.automl.runtime.shared.time_series_data_frame.TimeSeriesDataFrame.
    :param test_size:
        The number of data points per grain to set aside for test dataset.
    :type test_size:
        int.
    :return:
        A 2-tuple of TimeSeriesDataFrames, first element is training dataset and
        second element is test dataset.
    """
    from azureml.automl.runtime.shared.time_series_data_frame import TimeSeriesDataFrame

    # checking inputs
    if not verify.type_is_numeric(type(test_size), '', should_raise=False):
        raise ValidationException._with_error(
            AzureMLError.create(
                InvalidArgumentType, target="test_size",
                argument="test_size ({})".format(test_size), actual_type=type(test_size),
                expected_types="Numeric")
        )

    Validation.validate_type(tsdf, "timeseriesdataframe", TimeSeriesDataFrame)

    if test_size <= 0:
        raise ValidationException._with_error(AzureMLError.create(
            ArgumentOutOfRange, target="test_size", argument_name="test_size ({})".format(test_size), min=1, max="inf"
        ))

    grouped_data = tsdf.groupby_grain()

    # check if test_size is too small
    min_rows_per_grain = grouped_data.size().min()
    if test_size > min_rows_per_grain - 1:
        raise ValidationException._with_error(AzureMLError.create(
            GrainShorterThanTestSize, target="test_size", test_size=test_size, min_rows_per_grain=min_rows_per_grain
        ))

    # continue with the split
    train_data = grouped_data.apply(lambda x: x[:(len(x) - test_size)])

    # Call deduplicate just in case groupby/apply duplicated grain index levels
    train_data.deduplicate_index(inplace=True)

    test_data = grouped_data.apply(lambda x: x[(len(x) - test_size):])
    test_data.deduplicate_index(inplace=True)

    return train_data, test_data


def _construct_day_of_quarter_single_df_with_date(df: pd.DataFrame, time_col: str) -> pd.DataFrame:
    """
    Compute day of quarter from a DataFrame with one time column time_col.

    Also compute information that could be derived from
    ``time_index`` column, e.g., year, quarter, first day of the quarter.

    :param df:
        Input dataframe with time_col to compute day of quarter on.
    :type df:
        pd.DataFrame.
    :return:
        A data frame containing a ```day_of_quarter``` column and a few
        other time related columns used for computing ```day_of_quarter```.
    """
    df['year'] = df[time_col].dt.year
    df['quarter'] = df[time_col].dt.quarter
    df['first_month_of_quarter'] = (df['quarter'] - 1) * 3 + 1
    df['first_day_of_quarter'] = pd.to_datetime(
        df['year'].map(str) + "/"
        + df['first_month_of_quarter'].map(str) + "/1")
    # must set time zone to day_of_quarter, else date arithmetic fails
    # when index is tz-aware
    df['first_day_of_quarter'] = df['first_day_of_quarter'].dt.tz_localize(df[time_col].dt.tz)
    df['day_of_quarter'] = (df[time_col] - df['first_day_of_quarter']).dt.days + 1

    return df


def construct_day_of_quarter(X: 'TimeSeriesDataFrame') -> pd.DataFrame:
    """
    Compute day of quarter from the time index in the input.

    Also compute information that could be derived from
    ``time_index`` column, e.g., year, quarter, first day of the quarter.

    :param X:
        Input dataframe to compute day of quarter on.
    :type X:
        azureml.automl.runtime.shared.time_series_data_frame.TimeSeriesDataFrame.
    :return:
        A data frame containing a ```day_of_quarter``` column and a few
        other time related columns used for computing ```day_of_quarter```.
    """
    from azureml.automl.runtime.shared.time_series_data_frame import TimeSeriesDataFrame

    if not isinstance(X, TimeSeriesDataFrame):
        raise ForecastingDataException._with_error(
            AzureMLError.create(TimeseriesInputIsNotTimeseriesDf, target='X',
                                reference_code=ReferenceCodes._TS_INPUT_IS_NOT_TSDF_TM_TS_UTIL)
        )
    df = pd.DataFrame({'date': X.time_index})

    return _construct_day_of_quarter_single_df_with_date(df, 'date')


def datetime_is_date(x):
    """
    Test if input datetime object has any hour/minute/second components.

    :param x: Input datetime object to be checked.
    :type x: pandas.core.indexes.datetimes.DatetimeIndex
    :return:
        Return ``True``  if an input date is without any hour/minute/second components otherwise return ``False``.
    """
    result = forecasting_utils._range((x - x.normalize()).values).astype(int) == 0
    return result
