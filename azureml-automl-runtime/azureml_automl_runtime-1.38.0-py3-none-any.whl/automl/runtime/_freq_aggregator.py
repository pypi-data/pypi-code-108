# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""The methods to aggregate data by the frequency."""
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union, cast

import copy
import re
import uuid

import pandas as pd
import numpy as np

from pandas.tseries.frequencies import to_offset

from azureml._common._error_definition.azureml_error import AzureMLError
from azureml.automl.core.automl_base_settings import AutoMLBaseSettings
from azureml.automl.core.featurization.featurizationconfig import FeaturizationConfig
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    TimeseriesDsFreqLessThenFcFreq, PandasDatetimeConversion, NumericConversion)
from azureml.automl.core.shared.constants import TimeSeries, TimeSeriesWebLinks,\
    TimeSeriesInternal, AggregationFunctions
from azureml.automl.core.shared.forecasting_exception import ForecastingConfigException,\
    ForecastingDataException
from azureml.automl.core.shared.reference_codes import ReferenceCodes

from azureml.automl.runtime.column_purpose_detection._time_series_column_type_detection_result \
    import ColumnTypeAggDetectionResult
from azureml.automl.runtime._time_series_data_config import TimeSeriesDataConfig
from azureml.automl.runtime.column_purpose_detection import _time_series_column_helper
from azureml.automl.core.shared.types import GrainType

_INDEX = 'index'
_INDEX_MAX = _INDEX + '_max'
_INDEX_MIN = _INDEX + '_min'
_MODE = 'mode'


def sum_with_nan(x: pd.Series) -> float:
    """
    A custom way to sum a numric column that may contain nan.

    If the entire column is nan return nan, otherwise treat nan as 0
    and some numeric values.
    :param x: The series to be summed.
    :return: The sum of x.
    """
    if x.isnull().all():
        return np.nan
    return cast(float, pd.to_numeric(x).sum(skipna=True))


def aggregate_dataset(time_series_config: TimeSeriesDataConfig,
                      dataset_freq: Optional[pd.DateOffset],
                      force_aggregation: bool = False,
                      start_times: Optional[Dict[GrainType, pd.Timestamp]] = None,
                      column_types: Optional[ColumnTypeAggDetectionResult] = None
                      ) -> Tuple[pd.DataFrame, np.ndarray]:
    """
    Aggregate the time series data set to the new frequency.

    Example: We want to change the frequency from half an hour to two hours.
    Let us consider the data set (target is given in y column):
    +------------------+---------+-----+-----+
    |     DateTime     |   reg   | cat |  y  |
    +==================+=========+=====+=====+
    | 2020-01-01 00:00 |    1    | 'a' | 10  |
    +------------------+---------+-----+-----+
    | 2020-01-01 00:30 |    2    | 'a' | 11  |
    +------------------+---------+-----+-----+
    | 2020-01-01 01:00 |    3    | 'a' | 15  |
    +------------------+---------+-----+-----+
    | 2020-01-01 01:30 |    3    | 'b' | 20  |
    +------------------+---------+-----+-----+
    | 2020-01-01 02:00 |    5    | 'b' | 42  |
    +------------------+---------+-----+-----+
    | 2020-01-01 02:30 |    7    | 'b' | 77  |
    +------------------+---------+-----+-----+
    | 2020-01-01 02:30 |    7    | 'b' | 89  |
    +------------------+---------+-----+-----+
    | 2020-01-01 02:30 |    7    | 'a' |  9  |
    +------------------+---------+-----+-----+
    We will aggregate target with the sum operator and regressor
    with sum, min, max and mean. The non numerical values will be aggregated
    by the most frequent value:
    +------------------+----------+----------+----------+-----------+-----+-----+
    |     DateTime     |  reg_sum |  reg_min |  reg_max |  reg_mean | cat |  y  |
    +==================+==========+==========+==========+===========+=====+=====+
    | 2020-01-01 00:00 |    9     |    1     |    3     |    2.25   | 'a' | 56  |
    +------------------+----------+----------+----------+-----------+-----+-----+
    | 2020-01-01 02:00 |    26    |    5     |    7     |    6.50   | 'b' | 217 |
    +------------------+----------+----------+----------+-----------+-----+-----+
    :param time_series_config: The TimeSeriesDataConfig object, containing the needed settings and data.
    :param dataset_freq: The data set frequency detected by us.
                         If it is None, the data set will be aggregated
                         and no exceptions will be raised.
    :param force_aggregation: Force the aggregation even if the data seems regular.
                              Needed because we could do the aggregation in training time,
                              but in forecast/inference time the data may be regular in this case
                              we will run forecast on the columns we did not have in the training set
                              and it will lead to error.
    :param start_times: Used to set the phase. For example if the frequency is 4D we may want make
                        sure, that if we trained the model on data starting from 2001-01-01, the test data
                        will be aggregated so that it will contain dates in the 4D grid starting from 2001-01-01.
                        If set to none, the start dates of the data set will be used.
    :param column_types: The object holding detected types of the columns. If this object is absent, the type
                         will be inferred based on data.
    :raises: ForecastingConfigException if data set is more sparse then
             the desired frequency.
    """
    if time_series_config.target_aggregation_function is None:
        return time_series_config.data_x, time_series_config.data_y
    if time_series_config.freq is not None and dataset_freq is not None\
       and _get_frequency_nanos(time_series_config.freq) < _get_frequency_nanos(dataset_freq):
        forecast_freqstr = time_series_config.freq if isinstance(
            time_series_config.freq, str) else time_series_config.freq.freqstr
        raise ForecastingConfigException._with_error(
            AzureMLError.create(
                TimeseriesDsFreqLessThenFcFreq, target=TimeSeries.FREQUENCY,
                reference_code=ReferenceCodes._FORECASTING_PARAM_USER_FREQ,
                data_freq=dataset_freq.freqstr,
                forecast_freq=forecast_freqstr,
                freq_doc=TimeSeriesWebLinks.FORECAST_PARAM_DOCS
            )
        )
    # Sanity check if grain column name is in data frame.
    if time_series_config.time_series_id_column_names:
        # If grain is not in the data frame, do not do aggregation we will error out later
        # during the validation.
        for grain in time_series_config.time_series_id_column_names:
            if grain not in time_series_config.data_x.columns:
                return time_series_config.data_x, time_series_config.data_y
            # If the grain column contains missing values also return data frame, we will
            # give an error during validation.
            if time_series_config.data_x[grain].isnull().any():
                return time_series_config.data_x, time_series_config.data_y

    X_groupby = None
    if not force_aggregation and (dataset_freq is None or dataset_freq == to_offset(time_series_config.freq)):
        # We need to aggregate if we have the duplicated time-grain combinations.
        special_columns = [] if time_series_config.time_series_id_column_names is None else copy.deepcopy(
            time_series_config.time_series_id_column_names)
        special_columns.append(time_series_config.time_column_name)
        # If we do not have duplicates, we need to check the out of grid
        # data, but if we have duplicates, we will have to aggregate.
        if time_series_config.data_x.duplicated(subset=special_columns, keep=False).sum() == 0:
            # We need to check if grains are present and if so, check grid compliance by grain.
            if time_series_config.time_series_id_column_names:
                X_groupby = time_series_config.data_x.groupby(time_series_config.time_series_id_column_names)
                in_grid = True
                for grain, X_one in X_groupby:
                    X_one.dropna(subset=[time_series_config.time_column_name], inplace=True)
                    # Do not aggregate if there is no valid time stamps.
                    if X_one.shape[0] == 0:
                        continue
                    min_time = X_one[time_series_config.time_column_name].min()
                    if start_times and start_times.get(grain):
                        min_time = min(min_time, start_times.get(grain))
                    data_grid = pd.date_range(
                        min_time,
                        X_one[time_series_config.time_column_name].max(),
                        freq=time_series_config.freq)
                    if any(tm not in data_grid for tm in X_one[time_series_config.time_column_name]):
                        in_grid = False
                        break
                if in_grid:
                    return time_series_config.data_x, time_series_config.data_y
            else:
                min_time = time_series_config.data_x[time_series_config.time_column_name].min()
                if start_times:
                    for v in start_times.values():
                        min_time = min(min_time, v)
                data_grid = pd.date_range(
                    min_time,
                    time_series_config.data_x[time_series_config.time_column_name].max(),
                    freq=time_series_config.freq)
                if all(tm in data_grid for tm in time_series_config.data_x[time_series_config.time_column_name]):
                    return time_series_config.data_x, time_series_config.data_y

    if column_types is None:
        numeric_columns = _time_series_column_helper.get_numeric_columns(
            time_series_config.data_x, time_series_config.time_column_name,
            time_series_config.time_series_id_column_names, time_series_config.featurization)  # type: Set[Any]
        datetime_columns = _time_series_column_helper.get_datetime_columns(
            time_series_config.data_x, time_series_config.time_column_name,
            time_series_config.time_series_id_column_names, time_series_config.featurization)  # type: Set[Any]
    else:
        # If we provided column types in the training tyme we will
        # featurize the data accordingly.
        numeric_columns = column_types.numeric_columns
        datetime_columns = column_types.date_columns
    time_series_config.data_x[TimeSeriesInternal.DUMMY_TARGET_COLUMN] = time_series_config.data_y
    is_dummy_grain_added = False  # type: bool
    if X_groupby is None:
        grains = [TimeSeriesInternal.DUMMY_GRAIN_COLUMN] \
            if time_series_config.time_series_id_column_names is None \
            else time_series_config.time_series_id_column_names
        if grains == [TimeSeriesInternal.DUMMY_GRAIN_COLUMN] and\
                TimeSeriesInternal.DUMMY_GRAIN_COLUMN not in time_series_config.data_x.columns:
            time_series_config.data_x[TimeSeriesInternal.DUMMY_GRAIN_COLUMN] = TimeSeriesInternal.DUMMY_GRAIN_COLUMN
            is_dummy_grain_added = True
        X_groupby = time_series_config.data_x.groupby(grains)
    dfs = []
    try:
        for grain, X_one in X_groupby:
            X_one.dropna(subset=[time_series_config.time_column_name], inplace=True)
            # Do not aggregate if there is no valid time stamps.
            if X_one.shape[0] == 0:
                continue
            if is_dummy_grain_added:
                # We do not need the extra grain column, we have used it only for groupby.
                X_one.drop(TimeSeriesInternal.DUMMY_GRAIN_COLUMN, inplace=True, axis=1)
            # Add the phase only if the start time is present in the start_times
            # and it is less then minimal time point in the data set.
            X_one[TimeSeriesInternal.DUMMY_ORDER_COLUMN] = 1
            if start_times is not None and grain in start_times:
                data_start = X_one[time_series_config.time_column_name].min()
                real_start = start_times[grain]
                while real_start > data_start:
                    real_start -= to_offset(time_series_config.freq)
                if real_start < data_start:
                    # If we have the start time, we have to add the row corresponding to this time to the data set.
                    time_ix = np.where(X_one.columns.values == time_series_config.time_column_name)[0][0]
                    pad = [None] * (X_one.shape[1])
                    pad[time_ix] = real_start
                    X_one = pd.DataFrame([pad], columns=X_one.columns).append(
                        X_one)
            X_agg = _aggregate_one_grain(X_one, numeric_columns, datetime_columns, time_series_config, grain)

            # The mode will be applied to the DUMMY_ORDER_COLUMN, so that it will be renamed.
            mode_of_order_col = _get_mode_col_name(TimeSeriesInternal.DUMMY_ORDER_COLUMN)
            if mode_of_order_col in X_agg.columns:
                X_agg.dropna(subset=[mode_of_order_col], inplace=True)
                X_agg.drop(mode_of_order_col, axis=1, inplace=True)
            # If we have padded the data frame, we could add non desired early date.
            # For example if training set ends 2001-01-25, the frequency is 2D and trainig set
            # starts at 2001-01-26. The aggregation will add the non existing date 2001-01-25
            # to the test set and it will fail the run.
            # But if we have earlier dates, that means a user error and we should not correct it
            # and raise exception in forecast time.
            if start_times is not None:
                min_test_time = X_agg[time_series_config.time_column_name].min()
                if grain in start_times and start_times[grain] == min_test_time:
                    X_agg = X_agg[X_agg[time_series_config.time_column_name] != min_test_time]

            dfs.append(X_agg)
    finally:
        if is_dummy_grain_added:
            time_series_config.data_x.drop(TimeSeriesInternal.DUMMY_GRAIN_COLUMN, inplace=True, axis=1)
        if TimeSeriesInternal.DUMMY_TARGET_COLUMN in time_series_config.data_x.columns:
            time_series_config.data_x.drop(TimeSeriesInternal.DUMMY_TARGET_COLUMN, axis=1, inplace=True)
    # If we have nothing to concatenate (for example if all values are NaT) we are returning
    # the original data frame.
    if not dfs:
        return time_series_config.data_x, time_series_config.data_y
    X_agg = pd.concat(dfs, sort=True)
    X_agg.reset_index(drop=True, inplace=True)

    y = X_agg.pop(TimeSeriesInternal.DUMMY_TARGET_COLUMN).values
    return X_agg, cast(np.ndarray, y)


def _aggregate_one_grain(X_one: pd.DataFrame,
                         numeric_columns: Set[Any],
                         datetime_columns: Set[Any],
                         time_series_config: TimeSeriesDataConfig,
                         time_series_id: Optional[GrainType] = None) -> pd.DataFrame:
    """
    Aggregate the data based on the new frequency.

    :param X_one: The data frame with one grain.
    :param numeric_columns: The numeric columns in the data frame.
    :param datetime_columns: The datetime columns in the data frame.
    :param time_series_config: The TimeSeriesDataConfig object, containing the needed settings and data.
    :param time_series_id: The name of a time time series id.
    :return: The data frame with data aggregated to the new frequency.
    """
    X_one.sort_values(by=[time_series_config.time_column_name], inplace=True)
    special_column_names = {time_series_config.time_column_name}  # type: Set[str]
    if time_series_config.time_series_id_column_names is not None:
        special_column_names = special_column_names.union(set(time_series_config.time_series_id_column_names))
    all_columns = set(X_one.columns)  # type: Set[Any]
    cat_columns = all_columns - special_column_names.union(
        numeric_columns, datetime_columns) - {TimeSeriesInternal.DUMMY_TARGET_COLUMN}  # type: Set[Any]
    # We know, that we must have the target column.
    # We also add index, columns, which we will then use to aggregate categories.
    target_agg_fun = \
        cast(str, time_series_config.target_aggregation_function)  # type: Union[str, Callable[[Any], float]]
    if target_agg_fun == AggregationFunctions.SUM:
        target_agg_fun = sum_with_nan
    X_return = _resample_numeric_features(
        X_one,
        time_series_config,
        {TimeSeriesInternal.DUMMY_TARGET_COLUMN},
        [target_agg_fun])  # type: pd.DataFrame
    agg_target_col_name = set(X_return.columns) - {time_series_config.time_column_name}
    X_return.rename({list(agg_target_col_name)[0]: TimeSeriesInternal.DUMMY_TARGET_COLUMN},
                    axis=1, inplace=True)
    # Additional regressors are optional.
    # Aggregate numeric columns if any.
    if numeric_columns:
        X_one_num = _resample_numeric_features(
            X_one,
            time_series_config,
            numeric_columns,
            AggregationFunctions.ALL)  # type: pd.DataFrame
        X_return = X_return.merge(X_one_num, on=time_series_config.time_column_name)
    # Aggregate categorical columns if any.
    if cat_columns or datetime_columns:
        # Pandas handles different edge cases of aggregation.
        # We will save min and max indices of values being aggregated.
        # The data set is already sorted, and we are safe to use min and max
        # indices as a range.
        index_df = pd.DataFrame({
            time_series_config.time_column_name: X_one[time_series_config.time_column_name],
            _INDEX: np.arange(X_one.shape[0])})
        index_df = _resample_numeric_features(
            index_df,
            time_series_config,
            {_INDEX},
            [AggregationFunctions.MIN, AggregationFunctions.MAX])
        index_df.dropna(subset=[_INDEX_MIN, _INDEX_MAX], inplace=True)
        if cat_columns:
            X_one_cat = _resample_cat_features(
                index_df,
                X_one,
                time_series_config.time_column_name,
                list(cat_columns))  # type: pd.DataFrame
            X_return = X_return.merge(X_one_cat, on=time_series_config.time_column_name)
        if datetime_columns:
            X_one_dt = _resample_datetime_features(
                index_df,
                X_one,
                time_series_config,
                datetime_columns)  # type: pd.DataFrame
            X_return = X_return.merge(X_one_dt, on=time_series_config.time_column_name)
    # We need to recover grains, because we have dropped it
    # during aggregation.
    if time_series_config.time_series_id_column_names:
        grain_ord = 0
        time_series_id_iterable = time_series_id if isinstance(
            time_series_id,
            tuple) or isinstance(
            time_series_id,
            list) else (
            time_series_id,
        )
        for grain in time_series_config.time_series_id_column_names:
            X_return[grain] = time_series_id_iterable[grain_ord]
            grain_ord += 1
    return X_return


def _resample_numeric_features(X_one: pd.DataFrame,
                               time_series_config: TimeSeriesDataConfig,
                               numeric_columns: Set[Any],
                               aggregation_functions: List[Any]
                               ) -> pd.DataFrame:
    """
    Do the aggregation of a numeric features.

    **Note:** This function drops grains
    :param X_one_num: The data frame to apply the aggregation.
    :param time_series_config: The TimeSeriesDataConfig object, containing the needed settings and data.
    :param numeric_columns: The columns to use in the aggregation.
    :param aggregation_functions: The list of aggregation functions
                                  to be applied to the data frame.
    :return: The data frame with the aggregated numeric columns.
    """
    # Replace sum with our custom aggregation function.
    # We will work on the copy of the list to avoid modifying
    # the constant.
    aggregation_functions = copy.deepcopy(aggregation_functions)
    for i in range(len(aggregation_functions)):
        if aggregation_functions[i] == AggregationFunctions.SUM:
            aggregation_functions[i] = sum_with_nan
    X_one = X_one.set_index(time_series_config.time_column_name)
    drop_cols = list(set(X_one.columns) - numeric_columns)
    X_one.drop(drop_cols, axis=1, inplace=True)
    # Sometimes the column type is being lost at this stage.
    # We are making sure to restore it.
    for col in X_one.columns:
        is_y = col == TimeSeriesInternal.DUMMY_TARGET_COLUMN
        try:
            X_one[col] = X_one[col].astype('float')
        except BaseException as e:
            raise ForecastingDataException._with_error(
                AzureMLError.create(
                    NumericConversion, target="y" if is_y else "X",
                    column="y" if is_y else str(col),
                    reference_code=ReferenceCodes._FREQUENCY_AGGREGATION_NUMBER_Y_CONVERSION
                    if is_y else ReferenceCodes._FREQUENCY_AGGREGATION_NUMBER_X_CONVERSION),
                inner_exception=e
            ) from e

    X_resample = X_one.resample(rule=time_series_config.freq)
    X_one = X_resample.aggregate(aggregation_functions)
    # The resampling has moved the time column to index,
    # we have to restore the regular range index.
    _convert_column_names(X_one)
    X_one.reset_index(inplace=True, drop=False)
    return X_one


def _resample_datetime_features(
        index_ranges: pd.DataFrame,
        X_one_date: pd.DataFrame,
        time_series_config: TimeSeriesDataConfig,
        datetime_columns: Set[Any]) -> pd.DataFrame:
    """
    Resample the datetime features.

    **Note:** This function drops grains
    We need to apply the separate approach to the datetime columns, they
    natively support min and max, we will also add mode.
    :param X_one_date: The data frame to apply the aggregation.
    :param time_series_config: The TimeSeriesDataConfig object, containing the needed settings and data.
    :param datetime_columns: The columns to use in the aggregation.
    :return: The data frame with the aggregated datetime columns.
    """
    X_one_date = X_one_date.set_index(time_series_config.time_column_name)
    drop_cols = list(set(X_one_date.columns) - datetime_columns)
    X_one_date.drop(drop_cols, axis=1, inplace=True)
    # Sometimes the column type is being lost at this stage.
    # We are making sure to restore it.
    for col in datetime_columns:
        try:
            X_one_date[col] = pd.to_datetime(X_one_date[col])
        except BaseException as e:
            raise ForecastingDataException._with_error(
                AzureMLError.create(
                    PandasDatetimeConversion, target="X", column=col,
                    column_type=X_one_date[col].dtype,
                    reference_code=ReferenceCodes._FREQUENCY_AGGREGATION_CONVERT_INVALID_VALUE),
                inner_exception=e
            ) from e
    X_resample = X_one_date.resample(rule=time_series_config.freq)
    X_one_date_min_max = X_resample.aggregate(AggregationFunctions.DATETIME)
    # The resampling has moved the time column to index,
    # we have to restore the regular range index.
    _convert_column_names(X_one_date_min_max)
    X_one_date_min_max.reset_index(inplace=True, drop=False)
    X_one_date.reset_index(inplace=True, drop=False)
    X_one_date_mode = _resample_cat_features(index_ranges,
                                             X_one_date,
                                             time_series_config.time_column_name,
                                             list(datetime_columns))
    # We have converted all the columns to string to count mode safely.
    # We can avoid it in the latest versions of pandas >= 0.25.1, but in the
    # elder versions this mode operation will be unsafe for dates.
    # As we know that the data already was converted to date, modes also can be converted
    # without precautions.
    for col in X_one_date_mode.columns:
        X_one_date_mode[col] = pd.to_datetime(X_one_date_mode[col])
    return X_one_date_min_max.merge(X_one_date_mode, on=time_series_config.time_column_name)


def _resample_cat_features(index_ranges: pd.DataFrame,
                           X_one_cat: pd.DataFrame,
                           time_column_name: str,
                           categorical_columns: List[Any]) -> pd.DataFrame:
    """
    Resample and data frame with categorical features and concatenate it with numeric.

    **Note:** This function drops grains
    :param index_ranges: The data frame, containing new index and index ranges,
                         used for aggregation.
    :param X_one_cat: Not aggregated, sorted data frame with categorical values sorted by date.
    :param time_column_name: The name of the time column.
    :param special_columns: The time and grain columns.
    :return: the aggregated data frame.
    """
    # create a time column with the aggregated dates.
    new_time = 'time_{}'.format(uuid.uuid1())
    X_one_cat = X_one_cat[[time_column_name] + categorical_columns]
    # We will convert the data to strings to safely calculate
    # the modes.
    for cat_col in categorical_columns:
        if cat_col != TimeSeriesInternal.DUMMY_ORDER_COLUMN:
            nulls = X_one_cat[cat_col].isnull()
            X_one_cat[cat_col] = X_one_cat[cat_col].astype(str)
            X_one_cat[cat_col][nulls] = None
    X_one_cat[new_time] = pd.NaT
    # Split the data to the time intervals from the aggregated time index
    # and aggregate categorical features.
    # Dates before the new index starts.
    for i in range(len(index_ranges)):
        # For each row in aggregated dates in already aggregated
        # numeric column, we take subset of dates greater or equal then begin
        # up to the one less then the next one and do the aggregation.
        cat_index = np.arange(
            index_ranges[_INDEX_MIN].iloc[i],
            index_ranges[_INDEX_MAX].iloc[i] + 1).astype(int)
        X_one_cat = _replace_categories_with_mode(
            X_one_cat, indices=cat_index,
            new_time_column_name=new_time,
            new_date=index_ranges[time_column_name].iloc[i],
            categorical_columns=categorical_columns)
    # Swap the old time_column_name and rename the new aggregated one.
    X_one_cat.drop(time_column_name, axis=1, inplace=True)
    rename_dict = {new_time: time_column_name}
    for cat_col in categorical_columns:
        rename_dict[cat_col] = _get_mode_col_name(cat_col)
    X_one_cat.rename(rename_dict, axis=1, inplace=True)
    # In some cases we can have a tails of non aggregated data, for
    # example, when forecasting frequency is not multiple of data set
    # frequency. In this case the values after last aggregated time point
    # will be dropped.
    X_one_cat.dropna(subset=[time_column_name], inplace=True)
    # At this point we have multiple duplicated rows. We need to remove it.
    X_one_cat.drop_duplicates(inplace=True)
    # If the dates have the time zone information, the X_one_cat[time_column_name] will be of an object type.
    # because pd.NaT does not have the tz info.
    if X_one_cat[time_column_name].dtype == np.dtype('object'):
        # We can use pandas conversion as we are confident that we are working
        # with dates here.
        X_one_cat[time_column_name] = pd.to_datetime(X_one_cat[time_column_name])
    return X_one_cat


def _get_mode_col_name(col: Any) -> str:
    """
    Return the name of a column containing modes.

    :param col: The initial name of column.
    :return: The name of a column containing modes.
    """
    return "{}_{}".format(col, _MODE)


def _replace_categories_with_mode(X_one: pd.DataFrame,
                                  indices: np.ndarray,
                                  new_time_column_name: str,
                                  new_date: pd.Timestamp,
                                  categorical_columns: List[Any]) -> pd.DataFrame:
    """
    Replace categories in the indices range.

    :param X_one: The data frame with categorical values, one grain.
    :param indices: The indices of rows, containing the time range of interest.
    :param new_time_column_name: The new time column name, which will become
                                 time column name after aggregation.
    :param new_date: The new date to be set for given indices.
    :param categorical_columns:
    :return: The new data frame where categories at given indices are replaced
             by their mode.
    """
    X_one[new_time_column_name].iloc[indices] = new_date
    for col in categorical_columns:
        X_one[col].iloc[indices] = _get_mode_safe(X_one[col], indices)
    return X_one


def _get_mode_safe(series: pd.Series, indices: np.ndarray) -> Optional[str]:
    """
    Safely get the mode of a series.

    :param series: The source series.
    :param indices: The indices to consider while calculating the mode.
    :return: The median of the series.
    """
    sub_series = series.iloc[indices]
    mode_series = sub_series.mode()
    # If the series contains only None mode_series will be empty.
    if len(mode_series) > 0:
        # We have converted all non-null values to strings, so we
        # know, that mode will be a string in this case.
        return cast(str, mode_series.iloc[0])
    return None


def _convert_column_names(data: pd.DataFrame) -> pd.DataFrame:
    """
    Resampling of data frame leads to two level column name. Here we flatten it.

    **Note:** This method modify the data frame in place, it returns the same object.
    :param data: The data frame to rename columns in.
    :return: The modified data frame.
    """
    new_colnames = []
    for col in data.columns:
        if isinstance(col, tuple):
            if len(col) == 2 and col[1] == sum_with_nan.__name__:
                new_colnames.append('_'.join([col[0], AggregationFunctions.SUM]))
            else:
                new_colnames.append('_'.join(list(col)))
        else:
            new_colnames.append(col)
    data.columns = new_colnames
    return data


def _get_frequency_nanos(freq: Union[str, pd.DateOffset]) -> int:
    """
    Get the number of nanoseconds in 10 time periods.

    We get the number of nanoseconds in 10 periods to make the difference
    representative. For example we can not say what is bigger DateOffset(days=30)
    or to_offset('M') because months can have different lengths.
    :param freq: The data set frequency.
    :return: the number of nanoseconds in 10 date periods.
    """
    if isinstance(freq, str):
        freq = to_offset(freq)
    # To calculate the number of nanoseconds we are building a grid starting from 2018-01-01.
    # This is an arbitrary date where the year starts from Monday.
    date_grid = pd.date_range('2018-01-01', freq=freq, periods=11)
    return cast(int, (date_grid[-1] - date_grid[0]).delta)


def get_columns_before_agg(columns: List[Any]) -> Set[str]:
    """
    Get column names before the aggregation.

    :param columns: The list of columns.
    :return: Return the set of columns before aggregation.
    """
    agg_functions = copy.deepcopy(AggregationFunctions.ALL)
    agg_functions.append(_MODE)
    suffix = re.compile(
        "|".join(["(_{}$)".format(suffix) for suffix in agg_functions]))
    return {
        col if not isinstance(col, str) else suffix.sub('', col) for col in columns}


def get_column_types(
        columns_train: List[Any],
        columns_test: List[Any],
        time_column_name: str,
        grain_column_names: Optional[List[str]]
) -> ColumnTypeAggDetectionResult:
    """
    Get the column types based on the column suffices in the training set.

    :param columns_train: The set of columns in the training set.
    :param columns_test: The column names from the test set.
    :param time_column_name: The time column name.
    :param grain_column_names: The name of a grain column.
    :return: The object with the detected columns and flag designating failure.
    """
    # We will generate two sets of columns: the original one and the one with
    # aggregation suffices removed.
    columns_agg = set(columns_train)
    columns_agg.discard(TimeSeriesInternal.DUMMY_ORDER_COLUMN)
    columns = set(columns_test)
    # Discard the special columns which should not be aggregated.
    columns.discard(time_column_name)
    columns_agg.discard(time_column_name)
    if grain_column_names:
        for grain in grain_column_names:
            columns.discard(grain)
            columns_agg.discard(grain)
    # If some of non special columns do not contain the suffix,
    # then the aggregation was not applied.
    if columns_agg.intersection(columns):
        return ColumnTypeAggDetectionResult(set(), set(), set(), detection_failed=True)
    # If the frequency aggregation has happened, each column will have specific suffix:
    # numeric: {col}_min, {col}_max, {col}_sum and {col}_mean
    # date: {col}_min, {col}_max and {col}_mode
    # categorical: {col}_mode
    # Here we will check if there are only these sets of suffices applied to the column.
    # if there is other set of suffices, we will assume that the aggregation was not
    # applied.
    # Note: This function is called from the code which already knows that the training
    # set contains columns different from forecast set, so we know: it is a user error,
    # or the result of an aggregation. If another aggregation type has happened before,
    # training and forecasting set will have the same sets of columns.
    datetime_suffices = {AggregationFunctions.MIN, AggregationFunctions.MAX, _MODE}
    numeric_columns = set()
    date_columns = set()
    categorical_columns = set()
    for col in columns:
        # Numeric?
        col_agg_set = {'{}_{}'.format(col, agg) for agg in AggregationFunctions.ALL}
        if not col_agg_set.difference(columns_agg):
            numeric_columns.add(col)
            columns_agg -= col_agg_set
        # Datetime?
        col_agg_set = {'{}_{}'.format(col, agg) for agg in datetime_suffices}
        if not col_agg_set.difference(columns_agg):
            date_columns.add(col)
            columns_agg -= col_agg_set
        # Categorical?
        mode_col = '{}_{}'.format(col, _MODE)
        if mode_col in columns_agg:
            categorical_columns.add(col)
            columns_agg.discard(mode_col)
        # If the column was not aggregated and was not present in the training set,
        # it is OK, it will nor result in the error during forecasting.
    # If the training column set still contains columns not present in the test set,
    # we assume that the data set was not aggregated. Downstream this will cause the
    # user error.
    if columns_agg:
        return ColumnTypeAggDetectionResult(set(), set(), set(), detection_failed=True)
    return ColumnTypeAggDetectionResult(
        numeric_columns, date_columns, categorical_columns, detection_failed=False)
