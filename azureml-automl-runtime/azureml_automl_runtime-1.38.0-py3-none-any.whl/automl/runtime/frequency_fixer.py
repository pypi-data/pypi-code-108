# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""The utility functions to check the """
from typing import Dict, List, Optional, Tuple, Union, Set

import copy
import logging

import numpy as np
import pandas as pd

from pandas.tseries.frequencies import to_offset
from pandas.tseries.offsets import DateOffset, QuarterEnd, QuarterBegin
from uuid import uuid1

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.automl_base_settings import AutoMLBaseSettings
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    TimeseriesInvalidDateOffsetType,
    PandasDatetimeConversion,
    TimeseriesDfMissingColumn)
from azureml.automl.core.shared._diagnostics.validation import Validation
from azureml.automl.core.shared.constants import TimeSeries, TimeSeriesInternal, TimeSeriesWebLinks
from azureml.automl.core.shared.exceptions import ClientException, ConfigException, DataException
from azureml.automl.core.shared.forecasting_exception import ForecastingDataException
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared.types import GrainType
from azureml.automl.runtime._freq_aggregator import aggregate_dataset
from azureml.automl.runtime._time_series_data_config import TimeSeriesDataConfig
from azureml.automl.runtime.shared.time_series_data_frame import TimeSeriesDataFrame
from azureml.automl.runtime.shared.types import DataSingleColumnInputType
from azureml.automl.runtime.fixed_dataset import FixedDataSet

logger = logging.getLogger(__name__)

FREQUENCY_REJECT_TOLERANCE = 0.90
# We tolerate data grid inferred by TimeSeriesDataFrame if
# it is larger then the actual data set less then MISSING_DATA_TOLERANCE_TSDF
# times.
MISSING_DATA_TOLERANCE_TSDF = 3
FREQ = '__grain_freq__'
START = '__grain_start__'
COVERAGE = '__grain_coverage__'
_LOG_NO_TIMESTAMP = 'The data frame does not contain time stamps.'


def get_tsdf_frequency_and_start(
        X: pd.DataFrame,
        y: Optional[DataSingleColumnInputType],
        time_column_Name: str,
        grain_column_names: Optional[Union[List[str], str]],
        user_frequency: Optional[pd.DateOffset] = None
) -> Optional[Tuple[pd.DateOffset, Union[pd.Timestamp, Dict[GrainType, pd.Timestamp]]]]:
    """
    Detect the frequency of a pandas data frame.

    :param X: The data frame used for the frequency inference.
    :param y: The labels for X.
    :param time_column_Name: The column denoting date time.
    :param grain_column_names: The columns defining multiple series.
    :param user_frequency: The frequency set by user.
    :returns: tuple, containing frequency and dictionary with starting time for each grain,
              if different grains have different frequencies or less then FREQUENCY_REJECT_TOLERANCE
              fraction of points can be fit into given frequency.
              If the data frame contain only one grain, the timestamp will be returned instead of a dictionary.
    :raises: DataException
    """
    if grain_column_names is not None \
            and not isinstance(grain_column_names, list):
        grain_column_names = [grain_column_names]
    if grain_column_names is not None and (FREQ in grain_column_names or START in grain_column_names):
        # If grain column names contain FREQ or START giving up.
        return None
    if y is not None:
        X[TimeSeriesInternal.DUMMY_TARGET_COLUMN] = y
    else:
        X[TimeSeriesInternal.DUMMY_TARGET_COLUMN] = np.NaN
    if grain_column_names is None or grain_column_names == []:
        X[TimeSeriesInternal.DUMMY_GRAIN_COLUMN] = TimeSeriesInternal.DUMMY_GRAIN_COLUMN
        grain_column_names = [TimeSeriesInternal.DUMMY_GRAIN_COLUMN]
    reverse_dict = {}  # type: Dict[str, str]
    if X.index.names[0] is not None:
        # Temporary rename the columns so that we will not fail on groupby
        # in pandas >= 0.24.0 if we have the same named columns in index.
        X, reverse_dict = _temp_rename_columns(
            X, set(X.index.names).intersection(set(X.columns)))
    try:
        tsdf = TimeSeriesDataFrame(
            X,
            time_colname=time_column_Name,
            grain_colnames=grain_column_names,
            ts_value_colname=TimeSeriesInternal.DUMMY_TARGET_COLUMN
        )
        # Make sure we have dropped NaT values even if we have a non ordinary
        # index composed from time and grain columns.
        time_colname_null = tsdf.time_index.isnull()
        if time_colname_null.any():
            tsdf.drop(tsdf.time_index[time_colname_null],
                      level=tsdf.time_colname, inplace=True)
    except BaseException:
        # We should not fail here if the data frame can not be created, we will fail
        # on the validation step.
        return None
    finally:
        # If we have renamed columns, we need to rename it back.
        X.rename(reverse_dict, axis=1, inplace=True)
        # Remove added columns.
        drop = [TimeSeriesInternal.DUMMY_TARGET_COLUMN]
        if grain_column_names == [TimeSeriesInternal.DUMMY_GRAIN_COLUMN]:
            drop.append(TimeSeriesInternal.DUMMY_GRAIN_COLUMN)
        X.drop(drop, axis=1, inplace=True)
    if tsdf.shape[0] == 0:
        # During the generation of a TimeSeriesDataFrame we remove the rows which contain null/NaT at the time
        # column. This theoretically may lead to the empty data frame. This situation should
        # be captured by the validation.
        return None
    tsdf.sort_index(inplace=True)
    freq_offset = tsdf.infer_freq(return_freq_string=False)
    # If frequency is inferred, we already have the solution.
    groupby_ob = tsdf.groupby_grain()
    fixed_frequencies = groupby_ob.apply(
        lambda x: improved_infer_freq_one_grain(
            x, freq_offset, x.name, user_frequency, FREQUENCY_REJECT_TOLERANCE)).reset_index(
        drop=True)
    fixed_frequencies_not_nan = fixed_frequencies[pd.notnull(fixed_frequencies[FREQ])]
    if fixed_frequencies_not_nan is None or len(fixed_frequencies_not_nan) == 0:
        # If all frequencies are NaN, give up.
        return None
    if len(fixed_frequencies_not_nan[FREQ].unique()) == 1:
        coverage = groupby_ob.apply(lambda x: check_coverage_one_grain(x, fixed_frequencies)).sum()
        if coverage / len(X) >= FREQUENCY_REJECT_TOLERANCE:
            dict_starts = {}
            for grain, df in groupby_ob:
                df = pd.merge(
                    pd.DataFrame(df),
                    fixed_frequencies,
                    on=df.grain_colnames,
                    how='left',
                    left_index=True,
                    right_index=False)
                df.reset_index(drop=True, inplace=True)
                dict_starts[grain] = df[START][0]
            if len(dict_starts.keys()) == 1 and TimeSeriesInternal.DUMMY_GRAIN_COLUMN in dict_starts.keys():
                return fixed_frequencies_not_nan[FREQ].iloc[0], dict_starts[TimeSeriesInternal.DUMMY_GRAIN_COLUMN]
            return fixed_frequencies_not_nan[FREQ].iloc[0], dict_starts
    return None


def check_coverage_one_grain(one_grain: TimeSeriesDataFrame, freqs: Union[pd.DataFrame, pd.Series]) -> int:
    """
    Get the number of points covered by the given frequency.

    :param one_grain: The data frame denoting one grain.
    :param freq: The proposed frequency of the grain.
    """
    if isinstance(freqs, pd.Series):
        freq = freqs[FREQ]
        start = freqs[START]
    else:
        df = pd.merge(
            pd.DataFrame(one_grain),
            freqs,
            on=one_grain.grain_colnames,
            how='left',
            left_index=True,
            right_index=False)
        df.reset_index(drop=True, inplace=True)
        freq = df[FREQ][0]
        start = df[START][0]
        if pd.isnull(freq) or pd.isnull(start):
            # If the frequency, returned for given grain is NaN, we can not build the
            # date grid and hence can not cover this frequency. Return coverage of 0.
            return 0
    date_grid = pd.date_range(start=start, end=one_grain.time_index.max(), freq=freq)
    return len([time for time in one_grain.time_index if time in date_grid])


def improved_infer_freq_one_grain(
        df_grain: TimeSeriesDataFrame,
        freq_offset: pd.DateOffset,
        grain: GrainType,
        user_frequency: Optional[pd.DateOffset] = None,
        custom_freq_reject_tolerance: float = FREQUENCY_REJECT_TOLERANCE) -> pd.Series:
    """
    Improved version of frequency inference which can be applied to one grain.

    In this algorithm we first try to use the TimeSeriesDataFrame mechanism if frequency detection,
    build the corresponding frequency grid and if the percentage of data which does not fit the
    grid is within the FREQUENCY_REJECT_TOLERANCE we return this frequency and start date for the given
    grain.
    In case if TimeSeriesDataFrame mechanism left a lot of data points outside the grid, we estimate
    timedeltas between the data points and take the mode of these values. This mode is then used to reconstruct
    the frequency. If the point groups having equal timedelta are separated by some other time interval, we
    consider it to be a different data grid.
    We construct multiple grids and select the dominant one with the percentage
    of non fitted points within FREQUENCY_REJECT_TOLERANCE. We also return the start point used for grid generation.
    If the tiomedeltas remind month, year or quarter we try if these DateOffset s can fit most of data points.
    If neither grid is good enough we return the previous frequency from TimeSeriesDataFrame mechanism.
    :param df_grain: The data frame representing one grain.
    :param freq_offset: The frequency determined by the TimeSeriesDataFrame mechanism.
    :param grain: The name of a given grain.
    :param user_frequency: The frequency set by user.
    :param custom_freq_reject_tolerance: The proportion of points which have to be covered by newly detected frequency
                                         for it to be selected.
    :returns: the series with frequency and start date.
              Example: pd.Series{freq=<Days * 7>, start='2019-01-01'}
    """
    # Pandas data frame try to take minimal date range between cells, but if this range is very small,
    # it will result in memory error.
    df_grain.sort_index(inplace=True)
    ix_time = df_grain.time_index
    if len(df_grain) == 1:
        # we can not detect frequency, giving up.
        # In this case we can not define the frequency of the grain and the freq_offset is obviously
        # the frequency of another grains in the data frame.
        return _series_freq_start_for_grain(df_grain, user_frequency, ix_time.min(), grain, 1)
    data_grid_too_big = False  # type: bool
    # If this parameter is set, we should not try the
    # frequency detected by the TSDF mechanism.
    if user_frequency is None:
        default_frequency = freq_offset  # type: pd.DateOffset
        try:
            time_grid = pd.date_range(start=df_grain.time_index.min(), end=df_grain.time_index.max(), freq=freq_offset)
            time_not_desired = [i for i in ix_time.to_series() if i not in time_grid]
            best_coverage = len(df_grain) - len(time_not_desired)  # type: int
            data_grid_too_big = len(time_grid) / len(df_grain) >= MISSING_DATA_TOLERANCE_TSDF
        except MemoryError:
            best_coverage = 0
    else:
        default_frequency = user_frequency
        best_coverage = 0
    # We will detect custom frequency only if detected frequency covers less then FREQUENCY_REJECT_TOLERANCE
    # points.
    # Note, this constant is used independent of aggregation status.
    if best_coverage / len(df_grain) <= FREQUENCY_REJECT_TOLERANCE or data_grid_too_big:
        # We (1) need another frequency (2) we can not establish the frequency.
        # We want to do subtraction without relation to index.
        timedeltas = (ix_time[1:] - ix_time[:-1]).to_series()
        td_mode = timedeltas.mode()[0]
        # Search for timedelta indexes, where delta is equal to
        # its mode.
        anchor_indexes = np.where(timedeltas == td_mode)[0]
        anchored_freq = None
        first_timestamp = None
        # If user has provided us a frequency, just try it, instead of getting choices.
        frequencues_to_try = get_frequencies_choices(
            td_mode, ix_time.to_series()) if user_frequency is None else [user_frequency]
        for frequency in frequencues_to_try:
            # Return freq_offset if dominant difference between points is less them millisecond.
            # In this case timedelta between two dates will be 0,
            # resulting in frequency:DateOffset(days=0).
            if frequency == DateOffset(days=0):
                return _series_freq_start_for_grain(df_grain, default_frequency, ix_time.min(), grain, best_coverage)
            if user_frequency is None and not has_dominant_frequency(
                    timedeltas, td_mode, frequency, 1 - custom_freq_reject_tolerance):
                continue
            # There are len(anchor_indexes) possible grids.
            # Theoretically we can have several sets of values separated by uneven time interval.
            # by using this iterations we try to handle this scenario.
            old_ix = -1
            set_checked_start_times = set()  # type: Set[pd.Timedelta]
            for i in range(len(anchor_indexes)):
                if old_ix == -1 or anchor_indexes[i] > old_ix + 1:
                    # If previous timedelta index differs by one, that
                    # means we already looked at this grid.
                    start = ix_time[anchor_indexes[i]]
                    if start in set_checked_start_times:
                        # If the start time is the same, we have already covered
                        # this anchor previously because the frequency is the same.
                        continue
                    else:
                        set_checked_start_times.add(start)
                    while df_grain.time_index.min() < start:
                        start -= frequency
                    date_grid = pd.date_range(start=start, end=df_grain.time_index.max(), freq=frequency)
                    if len(date_grid) < 3:
                        # Pandas mechanism of frequency detection does not work if the date grid
                        # is shorter then 3 time points. In this case we need to skip this frequency.
                        continue
                    covered_points = [i for i in range(len(ix_time)) if ix_time[i] in date_grid]
                    covered_number = len(covered_points)
                    if covered_number > best_coverage or (
                            data_grid_too_big and covered_number
                            / len(df_grain) > FREQUENCY_REJECT_TOLERANCE):
                        # The data_grid_too_big flag does not make sense anymore, because we used mode of a
                        # timedeltas.
                        data_grid_too_big = False
                        best_coverage = covered_number
                        anchored_freq = to_offset(pd.infer_freq(date_grid))
                        if anchored_freq is None:
                            # For some frequencies pandas mechanism does not work,
                            # the example is DateOffset(months=1) and the anchor
                            # is not the first or last day of the month pandas version 0.23.4.
                            anchored_freq = frequency
                        first_timestamp = ix_time[min(covered_points)]
                    if 2 * covered_number > len(ix_time):
                        # We break the inner loop because in this case we consider date grids
                        # are separated by non equal timedeltas. Given that another grid, using the same frequency
                        # can not cover more data points and hence should not be tried.
                        break
                old_ix = anchor_indexes[i]
        if anchored_freq is not None:
            return _series_freq_start_for_grain(df_grain, anchored_freq, first_timestamp, grain, best_coverage)
    # We were unable to find the better frequency, return what we have.
    return _series_freq_start_for_grain(df_grain, default_frequency, ix_time.min(), grain, best_coverage)


def _series_freq_start_for_grain(
        df_one_grain: TimeSeriesDataFrame,
        freq: pd.DateOffset,
        start: pd.Timestamp,
        grain: GrainType,
        n_points_in_grid: int) -> pd.Series:
    """
    The internal function to return frequency and start time in grain aware manner.

    :param df_grain: TimeSeriesDataFrame with only one grain.
    :param freq: The freqiency of this grain.
    :param start: the first timestamp to be used for date grid generation.
    :param grain: The name of a given grain.
    :param n_points_in_grid: The number of points within the time grid created using start and freq.
    :returns: The Series, containing grains, freq and start times.
    """
    dict_data = {FREQ: freq, START: start, COVERAGE: n_points_in_grid}

    if df_one_grain.grain_colnames is not None:
        if not isinstance(grain, tuple):
            dict_data[df_one_grain.grain_colnames[0]] = grain
        else:
            for ord, col in enumerate(df_one_grain.grain_colnames):
                dict_data[col] = grain[ord]
    return pd.Series(dict_data)


def get_frequencies_choices(delta: pd.Timedelta, df_time: pd.Series) -> List[pd.DateOffset]:
    """
    Return possible frequencies for the given timeselta.

    We need this function in case the frequency is special, for example it may
    be a monthly frequencies with some dates missing.
    :param delta: The dominant time delta between data points.
    :param df_time: The series, obtained from data frame time index.
    :returns: The list of frequencies to be tried.
    """
    from azureml.automl.runtime.featurizer.transformer.timeseries.forecasting_heuristic_utils \
        import timedelta_to_freq_safe
    # The default frequency
    frequencies = []
    dominant_day = df_time.apply(lambda x: x.day).mode()[0]
    dominant_month = df_time.apply(lambda x: x.month).mode()[0]
    if delta in {pd.Timedelta(days=30), pd.Timedelta(days=31)}:
        # Monthly frequency.
        if dominant_day in [30, 31]:
            frequencies.append(to_offset('M'))
        elif dominant_day == 1:
            frequencies.append(to_offset('MS'))
        else:
            frequencies.append(DateOffset(months=1))
    elif delta == pd.Timedelta(days=365):
        # Yearly frequency.

        if dominant_day == 1 and dominant_month == 1:
            frequencies.append(to_offset('YS'))
        elif dominant_day == 31 and dominant_month == 12:
            frequencies.append(to_offset('Y'))
        else:
            frequencies.append(DateOffset(years=1))
    elif delta == pd.Timedelta(days=92):
        # Quarterly frequency.
        start_month = df_time[0].month
        month_counts = df_time.apply(lambda x: x.month).value_counts()
        if start_month not in month_counts[0:4].index:
            start_month = dominant_month
        if dominant_day in [30, 31]:
            frequencies.append(QuarterEnd(startingMonth=start_month))
        elif dominant_day == 1:
            frequencies.append(QuarterBegin(startingMonth=start_month))
    # From timedelta we will get the unanchored frequency for example <7 * Days>.
    frequencies.append(timedelta_to_freq_safe(delta))
    return frequencies


def _in_allowed_deltas(delta: pd.Timedelta, allowed_deltas: Set[pd.Timedelta]) -> bool:
    """
    Define if the delta is in allowed set of deltas.

    :param delta: The timedelta to be checked.
    :param allowed_deltas: The set of timedeltas allowed.
    """
    if delta in allowed_deltas:
        return True
    # If we have several allowed deltas the calculation if
    # delta is the sum of allowed deltas will have exponential
    # difficulty, that is why we are giving up here.
    if len(allowed_deltas) > 1:
        return False
    # If allowed_deltas is represented by one value, we will check
    # if delta is multiple of this value.
    for val in allowed_deltas:
        if delta % val == pd.Timedelta(days=0):
            return True
    return False


def has_dominant_frequency(
        timedeltas: pd.Series,
        delta_mode: pd.Timedelta,
        dominant_frequency: pd.DateOffset,
        tolerance: float) -> bool:
    """
    Determine if the data set can comply with dominant_frequency.

    *Note:* In this quick test we just test if data set can comply to the frequency according to given
    timedeltas, but it is not guaranteed and actual check if most of data points are in the frequency
    grid should happen afterwards.
    :param timedeltas: The timedeltas from the single series.
    :param delta_mode: The most frequent timedelta in the series.
    :param frequency: The detected dominant frequency to be tested.
    :param tolerance: The allowed percentage of outliers from the expected timedeltas.
    :returns: True if data set can be in this frequency grid, False otherwise.
    """
    allowed_deltas = get_dominant_timedeltas(dominant_frequency, delta_mode)
    non_coompliant = sum(not _in_allowed_deltas(delta, allowed_deltas) for delta in timedeltas)
    return non_coompliant / len(timedeltas) <= tolerance


def get_dominant_timedeltas(frequency: pd.DateOffset, default: pd.Timedelta) -> Set[pd.Timedelta]:
    """
    Get the dominant timedelta for the given frequency.

    :param frequency: The frequency for which the timedelta needs to be estimated.
    :param default: The median time delta present on all returned sets.
    :returns: Dominant timedeltas for given timedelta.
    """
    # Pandas has its own function pd.to_timedelta, but it does not handle frequencies,
    # which does not have 'delta' attribute.
    timedeltas = set()  # type: Set[pd.Timedelta]
    if hasattr(frequency, 'delta'):
        timedeltas = {frequency.delta}
    elif isinstance(frequency, pd.offsets.Week) or frequency == DateOffset(weeks=1):
        timedeltas = {pd.Timedelta(days=7)}
    elif isinstance(frequency, pd.offsets.BusinessDay):
        timedeltas = {pd.Timedelta(days=1), pd.Timedelta(days=3)}
    elif isinstance(frequency, pd.offsets.MonthOffset) or frequency == DateOffset(months=1):
        timedeltas = {pd.Timedelta(days=30), pd.Timedelta(days=31),
                      pd.Timedelta(days=28), pd.Timedelta(days=29)}
    elif isinstance(frequency, pd.offsets.YearOffset) or frequency == DateOffset(years=1):
        timedeltas = {pd.Timedelta(days=365), pd.Timedelta(days=366)}
    elif isinstance(frequency, pd.offsets.QuarterOffset):
        timedeltas = {pd.Timedelta(days=90), pd.Timedelta(days=91), pd.Timedelta(days=92)}
    timedeltas.add(default)
    return timedeltas


def fix_df_frequency(X: pd.DataFrame,
                     time_column_name: str,
                     grain_column_names: Optional[GrainType],
                     start_times: Union[pd.Timestamp, Dict[GrainType, pd.Timestamp]],
                     freq: Optional[pd.DateOffset]) -> pd.DataFrame:
    """
    Remove outlier data points from the data frame which does not comply with the given frequency.

    :param X: The data frame used for the frequency inference.
    :param time_column_Name: The column denoting date time.
    :param grain_column_names: The columns defining multiple series.
    :param start_times: The start times for time series. If data set contains multiple grains,
                        it must be a dictionary with start times for each grain. If data set
                        does not contain grains, it is a single timestamp.
    :returns: pd.DateOffset is frequency can be inferred or None otherwise.
    :raises: ClientException
    """
    if (grain_column_names is None) != isinstance(start_times, pd.Timestamp):
        raise ClientException('If the data frame contains multiple data time series, the start times '
                              'should be represented by a dictionary in case of a single '
                              'series, it must be a pd.Timestamp.', has_pii=False)
    if isinstance(grain_column_names, str):
        grain_column_names = [grain_column_names]
    X = convert_to_datetime(X, time_column_name)
    if grain_column_names is None:
        start_times = _correct_start_time(X, time_column_name, start_times, freq)
        return fix_frequency_one_grain(X, freq, start_times, time_column_name)
    dfs = []

    # Pandas groupby no longer allows `by` to contain keys which are both column and index values (0.24)
    # pandas.pydata.org/pandas-docs/stable/whatsnew/v0.24.0.html#removal-of-prior-version-deprecations-changes
    # One way around this is to use the Grouper.
    groupers = []
    for key in grain_column_names:
        groupers.append(pd.Grouper(key=key, axis=0))
    for grain, df in X.groupby(groupers, as_index=False, group_keys=False):
        if grain not in start_times.keys():
            # If we do not know the start time we can not fix the data frame.
            dfs.append(df)
        else:
            start_time = start_times[grain]
            start_time = _correct_start_time(df, time_column_name, start_time, freq)
            dfs.append(fix_frequency_one_grain(
                df,
                freq,
                start_time,
                time_column_name))
    if dfs:
        return_df = pd.concat(dfs, sort=False)
        return_df.reset_index(inplace=True, drop=True)
        return return_df
    # Return the empty data frame if all data were filtered.
    return X[:0]


def _correct_start_time(one_grain: pd.DataFrame,
                        time_column_name: str,
                        start: pd.Timestamp,
                        freq: Optional[pd.DateOffset]) -> pd.Timestamp:
    """
    Get the estimated start time for the data frame, given its frequency.

    Example: min date of X is 2001-01-01 15:30:42 freq='D' then 2000-12-31 15:30:42 will be returned.
    **Note:** This function is NOT grain aware.
    :param one_grain: The data frame.
    :param time_column_name: The name of a datetime column.
    :param start: The initially proposed start time.
    :param freq: The frequency of a time series data frame.
    :return: The proposed start of a datetime grid.
    """
    min_time = one_grain[time_column_name].min()
    if pd.isnull(freq):
        return min_time
    while start > min_time:
        start -= freq
    return start


def fix_frequency_one_grain(X: pd.DataFrame,
                            freq: Optional[pd.DateOffset],
                            start: pd.Timestamp,
                            time_column_name: str) -> pd.DataFrame:
    """
    Remove outlier data points from the data frame which does not comply with the given frequency.

    :param X: Tha time series data frame to be used during fitting.
    :param freq: The frequency to be used for fixing X.
    :param start: The starting point of grid to tilter data frame.
    :param time_column_name: The column denoting date time.
    :returns: the dataframe with corrected frequency.
    """
    if freq is None or pd.isnull(start):
        logger.info(_LOG_NO_TIMESTAMP)
        return X
    X = convert_to_datetime(X, time_column_name)
    # Make a date grid in the time frame of a data frame X.
    data_grid = pd.date_range(start=start, end=X[time_column_name].max(), freq=freq)
    grid_df = data_grid.to_frame(index=False)
    grid_df.rename({grid_df.columns[0]: time_column_name}, axis=1, inplace=True)
    # Do an inner join to remove all outliers.
    if time_column_name in X.index.names and time_column_name in X.columns:
        # In the pandas >=0.24.0 we can not merge two data frames if the column
        # used as a merging key is also in index.
        # We will temporary rename this column.
        X, rev_dict = _temp_rename_columns(X, {time_column_name})
        X_fixed = grid_df.merge(X, 'inner', on=time_column_name)
        # We have to drop the date column from the fixed data frame, because we used the date
        # index to correct the data.
        X_fixed.drop(list(rev_dict.keys())[0], axis=1, inplace=True)
        # We have also modified the original data frame and need to fix it.
        X.rename(rev_dict, axis=1, inplace=True)
        return X_fixed
    return grid_df.merge(X, 'inner', on=time_column_name)


def check_types(X: pd.DataFrame,
                y: Optional[DataSingleColumnInputType]) -> None:
    """
    Raise the exception if X or y has incorrect type, also convert y to np.ndarray.

    :param X: The data frame used for the frequency inference.
    :param y: The labels for X.
    :returns: tuple with X and y.
    :raises: ValidationException
    """
    Validation.validate_type(X, "X", expected_types=pd.DataFrame)
    if y is not None:
        Validation.validate_type(y, "y", expected_types=np.ndarray)


def fix_data_set_regularity_may_be(
        X: pd.DataFrame,
        y: Optional[np.ndarray],
        automl_settings: AutoMLBaseSettings,
        freq_ref_code: str
) -> FixedDataSet:
    """
    The helper function to fix the data frame frequency.

    :param X: The data frame used for the frequency inference.
    :param y: The labels for X.
    :param automl_settings: The AutoMLSettings object.
    :param freq_ref_code: The error ref code to be set if user frequency can not
                          be converted to pd.Offset
    :return: The FixedDataSet object , containing the corrected data frame,
              corresponding y, two flags showing
              if the frequency inference failed and if data set was modified and
              the date offset. The date offset is not None only
              if the valid frequency was detected.
    """
    user_freq = str_to_offset_safe(automl_settings.freq, freq_ref_code)
    aggregation_enabled = automl_settings.target_aggregation_function is not None and automl_settings.freq is not None
    # At this point we already converted y to np.ndarray.
    check_types(X, y)
    try:
        # If we can not convert time column to the date time, we will silently fail.
        # The downstream code should show the correct exception.
        X = convert_to_datetime(X, automl_settings.time_column_name)
    except BaseException:
        return FixedDataSet(X, y, True, False, user_freq)
    results = get_tsdf_frequency_and_start(
        X, y,
        automl_settings.time_column_name,
        automl_settings.grain_column_names,
        # We do not need user frequency if the data set will be aggregated.
        None if aggregation_enabled else user_freq)
    if results is None and not aggregation_enabled:
        # We are unable to get frequency, giving up.
        # Do not print any guard rails because we will fail later on data set verification.
        return FixedDataSet(X, y, True, False, user_freq)

    if results is not None:
        new_freq, starts = results
    else:
        new_freq = None
    y_fixed = None  # type: Optional[np.ndarray]
    # If user set an aggregation parameter, aggregate data set and return it.
    if aggregation_enabled:
        ts_data = TimeSeriesDataConfig.from_settings(X, y, automl_settings)
        X_fixed, y_fixed = aggregate_dataset(ts_data, new_freq)
        was_aggregated = X_fixed.shape != X.shape
        return FixedDataSet(
            X_fixed, y_fixed, False, was_aggregated, user_freq)

    if y is not None:
        # If y was provided, align it with X.
        X[TimeSeriesInternal.DUMMY_TARGET_COLUMN] = y
    X_fixed = fix_df_frequency(X,
                               automl_settings.time_column_name,
                               automl_settings.grain_column_names,
                               starts,
                               new_freq)
    if y is not None:
        X.drop(TimeSeriesInternal.DUMMY_TARGET_COLUMN, inplace=True, axis=1)
        y_fixed = X_fixed.pop(TimeSeriesInternal.DUMMY_TARGET_COLUMN).values
    return FixedDataSet(
        X_fixed, y_fixed, False, X_fixed.shape[0] != X.shape[0], new_freq)


def convert_to_datetime(X: pd.DataFrame, time_column_name: str) -> pd.DataFrame:
    """
    Convert time column to datetime only if it is not in this format already.

    **Note:** This function does not create a copy of data frame.
    :param X: The affected data frame.
    :param time_column_name: The name of a time column name.
    :return: The data frame, for which time_column_name us guaranteed to be a datetime.
    """
    if time_column_name not in X.columns:
        raise ForecastingDataException._with_error(
            AzureMLError.create(TimeseriesDfMissingColumn,
                                target=TimeSeries.TIME_COLUMN_NAME,
                                reference_code=ReferenceCodes._FREQUENCY_FIXER_CONVERT_COLUMN_NOT_FOUND,
                                column_names=time_column_name)
        )
    # If the time column dtype is pd.Categorical np.issubdtype will fail
    # because it is pandas dtype. In this case we can apply pd.to_datetime
    # directly.
    if not isinstance(X[time_column_name].dtype, np.dtype) or \
            not np.issubdtype(X[time_column_name].dtype, np.datetime64):
        try:
            X[time_column_name] = pd.to_datetime(X[time_column_name])
        except Exception as e:
            raise DataException._with_error(
                AzureMLError.create(PandasDatetimeConversion, target="X", column=time_column_name,
                                    column_type=X[time_column_name].dtype,
                                    reference_code=ReferenceCodes._FREQUENCY_FIXER_CONVERT_INVALID_VALUE),
                inner_exception=e
            ) from e
    return X


def str_to_offset_safe(freq: Optional[str],
                       ref_code: Optional[str] = None) -> pd.DateOffset:
    """
    Safely call the pandas to_offset function to gate date offset.

    :param freq: The string reoresentation of a frequency to be converted to pd.DateOffset.
    :param ref_code: The reference code to be used in case if exception is to be raised.
    :return: The frequency corresponding to string.
    :raises: ConfigException if the frequency can not be converted to the pd.DateOffset.
    """
    try:
        return to_offset(freq)
    except BaseException:
        raise ConfigException._with_error(
            AzureMLError.create(
                TimeseriesInvalidDateOffsetType, target="freq",
                freq_url=TimeSeriesWebLinks.FORECAST_PARAM_DOCS,
                reference_code=ref_code)
        )


def _temp_rename_columns(X: pd.DataFrame,
                         col_set: Set[str]) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """
    Rename columns, return the modified data frame and dictionary to revert renaming.

    *Note:* This function renames data frame inplace and return it for convenience only.
    :param X: The data frame to rename.
    :param col_set: The set of columns to rename.
    :return: Tuple with the modified data frame and dictionary to revert changes.
    """
    reverse_dict = {}
    rename_dict = {}
    for col in col_set:
        new_name = "{}{}".format(col, str(uuid1()))
        rename_dict[col] = new_name
        reverse_dict[new_name] = col
    X.rename(rename_dict, axis=1, inplace=True)
    return X, reverse_dict
