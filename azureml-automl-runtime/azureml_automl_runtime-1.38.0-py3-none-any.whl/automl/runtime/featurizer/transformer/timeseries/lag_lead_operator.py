# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Create lags and leads (negative lags) of target and features."""
from typing import Any, Dict, Optional, List, Union, cast, Iterable
from warnings import warn, filterwarnings
import logging

import numpy as np
import pandas as pd
import re
from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared._diagnostics.automl_error_definitions import InvalidArgumentType, \
    TimeseriesColumnNamesOverlap, EmptyLagsForColumns
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    TimeseriesDfDuplicatedIndex,
    TimeseriesInputIsNotTimeseriesDf,
    TimeseriesDfColumnTypeNotSupported)
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.constants import TimeSeriesInternal
from azureml.automl.core.shared.exceptions import ConfigException, \
    ClientException, FitException
from azureml.automl.core.shared.forecasting_exception import (
    ForecastingDataException,
    ForecastingConfigException)
from azureml.automl.core.shared.logging_utilities import function_debug_log_wrapped
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.runtime.shared.forecasting_utils import flatten_list, invert_dict_of_lists
from azureml.automl.runtime.shared.forecasting_verify import is_list_oftype, is_iterable_but_not_string
from azureml.automl.runtime.shared.time_series_data_frame import TimeSeriesDataFrame
from azureml.automl.runtime.featurizer.transformer.timeseries.missingdummies_transformer import \
    MissingDummiesTransformer

from .forecasting_base_estimator import AzureMLForecastTransformerBase, _GrainBasedStatefulTransformer
from .forecasting_constants import ORIGIN_TIME_COLNAME_DEFAULT
from .max_horizon_featurizer import MaxHorizonFeaturizer
from .time_series_imputer import TimeSeriesImputer
from .transform_utils import OriginTimeMixin


class LagLeadOperator(AzureMLForecastTransformerBase, OriginTimeMixin, _GrainBasedStatefulTransformer):
    """
    A transformation class for computing lags and leads for values.
    Work for general time series data sets, sparse or non-sparse.
    Has two lag options: "lag_by_time" or "lag_by_occurrence"
    default: "lag_by_occurrence"
    "lag_by_time" is good for (almost) evenly spaced time series data, while
    "lag_by_occurrence" is a better option for non-evenly spaced data
    This module will automatically select the right one by checking
    data sparsity.

    .. py:class:: LagLeadOperator

    .. _pandas.Series.shift: https://pandas.pydata.org/pandas-docs/stable/
                            generated/pandas.Series.shift.html

    This will be used as a featurization step inside the forecast pipeline.

    :param lags:
        dictionary of the form {'column_to_lag' : [lag_order1, lag_order2]}.
        Dictionary keys must be names of columns in the data frame to which
        the transform is applied. Dictionary values are either integers or
        lists of integers indicating what lags must be constructed.
        Negative values are allowed, and indicate 'leads' i.e. moving into
        the future values of time series.
    :type lags: dict

    :param max_horizon:
        how many steps ahead do you intend to predict the series later. This
        is used to construct a full grid of `time` and `origin_time` to make
        sure that output is compatible with multi-step forecasting featurizers
        downstream. This argument is ignored if the input data has
        `origin_time_column_name` set, because it is assumed that the job of
        setting up multi-horizon data structure had already been performed.
        Defaults to 1 to produce expected behavior for most users.
    :type max_horizon: int

    :param dropna:
        should missing values from lag creation be dropped? Defaults to False.
        Note that the missing values from the test data are not dropped but
        are instead 'filled in' with values from training data.
    :type dropna: bool

    :param origin_time_column_name:
        how to name the `origin_time` column when the input does not contain
        one. Must be a single string. This argument is ignored if the input
        data has `origin_time_column_name` set, because it is assumed that the job
        of setting up multi-horizon data structure had already been performed.
        Defaults to "origin".
    :type origin_time_column_name: str

    :param overwrite_columns:
        Flag that permits the transform to overwrite existing columns in the
        input TimeSeriesDataFrame for features that are already present in it.
        If True, prints a warning and overwrites columns.
        If False, throws a RuntimeError.
        Defaults to False to protect user data.
    :type overwrite_columns: bool

    :param backfill_cache:
                         Back fill the chache to avoid NaNs to prevent the output data
                         frame shape degradation.
    :type backfill_cache: bool

    Example 1 (Evenly Spaced Time Series Data, Will Use Lag_By_Time):
    Construct a small TimeSeriesDataFrame:

    >>> raw_data = {'store': ['storeA'] * 3 + ['storeB'] * 4,
    ...             'date' : pd.to_datetime(
    ...                 ['2017-01-01', '2017-02-01', '2017-03-01'] * 2 +
    ...                 ['2017-04-01'] ),
    ...             'sales': range(8, 15)}
    >>> tsdf = TimeSeriesDataFrame(
    ...    data=pd.DataFrame(raw_data),
    ...    grain_colnames=['store'], time_colname=['date'],
    ...    ts_value_colname='sales')
    >>> tsdf = tsdf.set_index(['store', 'date']).sort_index()
    >>> tsdf
                            sales
    store      date
    storeA     2017-01-01      8
               2017-02-01      9
               2017-03-01     10
    storeB     2017-01-01     11
               2017-02-01     12
               2017-03-01     13
               2017-04-01     14
    >>> tsdf=MaxHorizonFeaturizer(1).fit_transform(tsdf)
                                     sales  horizon_origin
    store      date       origin
    storeA     2017-01-01 2016-12-01     8               1
               2017-02-01 2017-01-01     9               1
               2017-03-01 2017-02-01    10               1
    storeB     2017-01-01 2016-12-01    11               1
               2017-02-01 2017-01-01    12               1
               2017-03-01 2017-02-01    13               1
               2017-04-01 2017-03-01    14               1
    >>> make_lags = LagLeadOperator(
    ...                 lags_to_construct={'sales': [-1, 1]})
    >>> make_lags.fit(tsdf)
    >>> result = make_lags.transform(tsdf)
    >>> result
                                     sales  horizon_origin  sales_lead1  sales_lag1
    store      date       origin
    storeA     2017-01-01 2016-12-01     8               1         9.00         nan
               2017-02-01 2017-01-01     9               1        10.00        8.00
               2017-03-01 2017-02-01    10               1          nan        9.00
    storeB     2017-01-01 2016-12-01    11               1        12.00         nan
               2017-02-01 2017-01-01    12               1        13.00       11.00
               2017-03-01 2017-02-01    13               1        14.00       12.00
               2017-04-01 2017-03-01    14               1          nan       13.00

    Example 2 (Non-evenly Spaced Time Series Data, Will Use Lag_By_Occurrence):
    Construct a small TimeSeriesDataFrame:

    >>> raw_data = {'store': ['storeA'] * 3 + ['storeB'] * 4,
    ...             'date' : pd.to_datetime(
    ...                 ['2017-01-01', '2017-02-01', '2017-04-01'] * 2 +
    ...                 ['2017-07-01'] ),
    ...             'sales': range(8, 15)}
    >>> tsdf = TimeSeriesDataFrame(
    ...    data=pd.DataFrame(raw_data),
    ...    grain_colnames=['store'], time_colname=['date'],
    ...    ts_value_colname='sales')
    >>> tsdf = tsdf.set_index(['store', 'date']).sort_index()
    >>> tsdf
                            sales
    store      date
    storeA     2017-01-01      8
               2017-02-01      9
               2017-04-01     10
    storeB     2017-01-01     11
               2017-02-01     12
               2017-04-01     13
               2017-07-01     14
    >>> tsdf=MaxHorizonFeaturizer(1).fit_transform(tsdf)
    >>> tsdf
                                     sales  horizon_origin
    store      date       origin
    storeA     2017-01-01 2016-12-01     8               1
               2017-02-01 2017-01-01     9               1
               2017-04-01 2017-03-01    10               1
    storeB     2017-01-01 2016-12-01    11               1
               2017-02-01 2017-01-01    12               1
               2017-04-01 2017-03-01    13               1
               2017-07-01 2017-06-01    14               1
    >>> make_lags = LagLeadOperator(
    ...                 lags_to_construct={'sales': [1]})
    >>> make_lags.fit(tsdf)
    >>> result = make_lags.transform(tsdf)
    >>> result
                                     sales  horizon_origin   sales_occurrence_lag1  date_occurrence_lag1_timeDiffDays
    store      date       origin
    storeA     2017-01-01 2016-12-01     8               1                     nan                                nan
               2017-02-01 2017-01-01     9               1                    8.00                                 31
               2017-04-01 2017-03-01    10               1                    9.00                                 59
    storeB     2017-01-01 2016-12-01    11               1                     nan                                nan
               2017-02-01 2017-01-01    12               1                   11.00                                 31
               2017-04-01 2017-03-01    13               1                   12.00                                 59
               2017-07-01 2017-06-01    14               1                   13.00                                 91
    """

    LAG_BY_TIME = 'lag_by_time'
    LAG_BY_OCCURRENCE = 'lag_by_occurrence'
    LAG_POSTFIX = 'lag'
    LEAD_POSTFIX = 'lead'
    OCCURRENCE_POSTFIX = 'occurrence'
    POSTFIX_SEP = '_'
    SPARSITY_THRESHOLD = 0.02  # threshold parameter to decide between lag by time and occurrence options

    def __init__(self,
                 lags: Dict[str, Union[int, List[int]]],
                 max_horizon: int = 1, dropna: bool = False,
                 origin_time_column_name: str = ORIGIN_TIME_COLNAME_DEFAULT,
                 overwrite_columns: bool = False,
                 backfill_cache: bool = False) -> None:
        """Create a LagLeadOperator."""
        super().__init__()
        self.lags_to_construct = lags
        self.max_horizon = max_horizon
        self.dropna = dropna
        self.origin_time_colname = origin_time_column_name
        self.overwrite_columns = overwrite_columns
        self.backfill_cache = backfill_cache

        # lag options: "lag_by_time" or "lag_by_occurrence"
        # default: "lag_by_occurrence"
        # "lag_by_time" is good for (almost) evenly spaced time series data, while
        # "lag_by_occurrence" is a better option for non-evenly spaced data
        self.lag_option = LagLeadOperator.LAG_BY_OCCURRENCE

        # iniitialize fitted status - to False, obviously
        self._is_fit = False
        self._cache = None
        self._ts_freq = None
        # set the flag for train and test set
        self._in_fit_transform = False

        # feature flag for inclusion of order column in input dataframe
        # This flag is used to preserve compatibility between SDK versions
        self._no_original_order_column = True

        # feature flag for addition of occurrence origin column to output dataframe
        # This flag is used to preserve compatibility between SDK versions
        self._add_occurrence_origin_column = True

        # Save column names generated from lag_lead operator to be added to timeseries_param_dict later
        # down the pipeline in _featurization_execution_timeseries.py, so that those columns can be removed
        # later for classical forecasting models and Prophet in _multi_grain_forecast_base.py,
        # since those learners doesn't need those columns, and in fact need to remove them in order
        # to elimitate duplex time index generated from lookback features (lags/rolling windows).
        self._lag_columns = []  # type: List[Union[str, Any]]

    def get_params(self, deep=True):
        params = super().get_params(deep)
        params.update({
            "lags": self.lags_to_construct,
            "origin_time_column_name": self.origin_time_colname
        })
        return params

    ############################################################################
    # Housekeeping - use properties to rule out incorrect inputs from users
    ############################################################################
    @property
    def lags_to_construct(self) -> Dict[str, Union[int, List[int]]]:
        """Get the dictionary of column names to lists of lags/leads to construct."""
        return self._lags_to_construct

    # set value of _lags_to_constuct, and check for incorrect user input
    @lags_to_construct.setter
    def lags_to_construct(self, value: Dict[str, Union[int, List[int]]]) -> None:
        # check if input value is a dict
        if not isinstance(value, dict):
            raise ForecastingConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentType, target="lags_to_construct",
                    argument="lags_to_construct", actual_type=type(value), expected_types="dict",
                    reference_code=ReferenceCodes._LAG_LEAD_LAG_TYPE
                )
            )
        # check if all keys are strings
        try:
            is_list_oftype(list(value.keys()), str)
        except FitException:
            raise ForecastingConfigException._with_error(
                AzureMLError.create(TimeseriesDfColumnTypeNotSupported, target='value',
                                    reference_code=ReferenceCodes._LAG_LEAD_COLUMN_TYPE,
                                    col_name='list of columns',
                                    supported_type='string')
            )
        # check if every value is either list of ints or an int
        for v in value.values():
            if np.issubdtype(type(v), np.signedinteger):
                pass
            elif is_iterable_but_not_string(v):
                # This assert is to pass through mypy check, the condition above handles it.
                Contract.assert_true(
                    isinstance(v, Iterable),
                    "The value should be an iterable.",
                    log_safe=True
                )
                v = cast(List[int], v)
                if len(v) == 0:
                    raise ForecastingConfigException._with_error(
                        AzureMLError.create(
                            EmptyLagsForColumns, target="target_lags",
                            reference_code=ReferenceCodes._LAG_LEAD_LAG_EMPTY
                        )
                    )
                for val in v:
                    if not np.issubdtype(type(val), np.signedinteger):
                        raise ForecastingConfigException._with_error(
                            AzureMLError.create(
                                InvalidArgumentType, target="lags_to_construct",
                                argument="lags_to_construct", actual_type=type(val), expected_types="int",
                                reference_code=ReferenceCodes._LAG_LEAD_LAG_TYPE_INT_LIST
                            )
                        )
            else:
                raise ForecastingConfigException._with_error(
                    AzureMLError.create(
                        InvalidArgumentType, target="lags_to_construct",
                        argument="lags_to_construct", actual_type=type(v), expected_types="int, List[int]",
                        reference_code=ReferenceCodes._LAG_LEAD_LAG_TYPE_INT
                    )
                )
        # all checks passed, can assign
        self._lags_to_construct = value

    @property
    def dropna(self) -> bool:
        """See `dropna` parameter."""
        return self._dropna

    @dropna.setter
    def dropna(self, value: bool) -> None:
        if not isinstance(value, bool):
            error_message = ("Input 'dropna' must be True or False.")
            raise ClientException(error_message, has_pii=False,
                                  reference_code=ReferenceCodes._LAG_LEAD_DROPNA)
        self._dropna = value

    @property
    def max_horizon(self) -> int:
        """See `max_horizon` parameter."""
        return self._max_horizon

    @max_horizon.setter
    def max_horizon(self, value: int) -> None:
        self.verify_max_horizon_input(value)
        self._max_horizon = value

    @property
    def origin_time_colname(self) -> str:
        """See `origin_time_column_name` parameter."""
        return self._origin_time_colname

    @origin_time_colname.setter
    def origin_time_colname(self, value: str) -> None:
        if not isinstance(value, str):
            raise ForecastingConfigException._with_error(
                AzureMLError.create(TimeseriesDfColumnTypeNotSupported, target='value',
                                    reference_code=ReferenceCodes._LAG_LEAD_ORIGIN,
                                    col_name='origin_time_column_name',
                                    supported_type='string')
            )
        self._origin_time_colname = value

    @property
    def overwrite_columns(self) -> bool:
        """See `overwrite_columns` parameter."""
        return self._overwrite_columns

    @overwrite_columns.setter
    def overwrite_columns(self, value: bool) -> None:
        if not isinstance(value, bool):
            error_message = ("Input 'overwrite_column' must be True or "
                             "False, instead received {}")
            raise ClientException(
                error_message.format(value),
                reference_code=ReferenceCodes._LAG_LEAD_OVERWRITE_COL).with_generic_msg(
                error_message.format('[MASKED]'))
        self._overwrite_columns = value

    ############################################################################
    # Private methods: all the work is done through them
    ############################################################################

    def _no_original_order_column_safe(self):
        return hasattr(self, '_no_original_order_column') and self._no_original_order_column

    def _add_occurrence_origin_column_safe(self):
        return hasattr(self, '_add_occurrence_origin_column') and self._add_occurrence_origin_column

    def _check_columns_to_lag(self, X: TimeSeriesDataFrame) -> Dict[str, List[int]]:
        """
        Check from which columns user wants to construct lags.

        Exclude columns that are not in X or are properties of X.

        :param X: is a TimeSeriesDataFrame

        :return: list of valid column labels which will be lagged.
        """
        # get a list of TSDF property columns, except ts_value_colname
        property_cols = set(flatten_list([getattr(X, attr) for attr in X._metadata]))
        property_cols.remove(X.ts_value_colname)

        # if asked to lag system cols, refuse and warn
        columns_to_lag = set(self.lags_to_construct.keys())
        columns_not_to_lag = columns_to_lag.intersection(property_cols)
        if len(columns_not_to_lag) > 0:
            warning_message = ("Some of the requested columns will not be "
                               "lagged, since they are internal to TimeSeriesDataFrame! "
                               "Will not lag: {}".format(columns_not_to_lag))
            columns_to_lag = columns_to_lag - columns_not_to_lag
            warn(warning_message, UserWarning)
        # if asked to lag columns that are not in TSDF, refuse and warn
        columns_not_in_df = columns_to_lag.difference(set(X.columns))
        if len(columns_not_in_df) > 0:
            warning_message = (
                "Some of the requested columns will not be "
                "lagged, since they are not present in the input "
                "TimeSeriesDataFrame.! Will not lag: {}".format(columns_not_in_df)
            )
            columns_to_lag = columns_to_lag - columns_not_in_df
            warn(warning_message, UserWarning)
        # clean up the dict of arguments by turning values of ints into
        # a singleton list of ints
        lags_to_construct_safe = dict()
        for column, lag_orders in self.lags_to_construct.items():
            if column in columns_to_lag:
                lag_orders_list = lag_orders if isinstance(lag_orders, list) \
                    else [lag_orders]
                lags_to_construct_safe[column] = lag_orders_list
        return lags_to_construct_safe

    def _generate_new_column_names(self) -> List[str]:
        """Generate all new column names from a dictionary of inputs."""
        new_colnames = []
        for colname, lag_orders in self.lags_to_construct.items():
            if isinstance(lag_orders, int):
                lag_orders = [lag_orders]
            for order in lag_orders:
                # append "occurrence" to lag name to match names in "_construct_one_lag..." functions
                post_fix = LagLeadOperator._get_lag_col_common_postfix(
                    order, self.lag_option == self.LAG_BY_OCCURRENCE)
                post_fix += str(abs(order))
                if self._ts_freq:
                    try:
                        post_fix += self._ts_freq.name
                    except NotImplementedError:
                        post_fix += self._ts_freq.freqstr
                new_colname = colname + post_fix
                new_colnames.append(new_colname)
        return (new_colnames)

    def _check_for_column_overwrites(self, X: TimeSeriesDataFrame) -> None:
        """
        Check for whether existing TSDF columns are getting overwritten.

        Either a warning is printed or an exception is
        raised, depending on settings.
        """
        new_colnames = set(self._generate_new_column_names())
        input_colnames = set(X.columns)
        columns_to_overwrite = input_colnames.intersection(new_colnames)
        if len(columns_to_overwrite) > 0:
            warning_message = ('Some of the columns that are about to be '
                               'created by LagLeadOperator already exist in the input '
                               'TimeSeriesDataFrame: {}. ')
            if self.overwrite_columns:
                warning_message = warning_message.format(columns_to_overwrite)
                warning_message += 'They will be overwritten!'
                warn(warning_message, UserWarning)
            else:
                raise ForecastingConfigException._with_error(
                    AzureMLError.create(
                        TimeseriesColumnNamesOverlap, target="TimeSeriesDataFrame",
                        class_name='LagLeadOperator',
                        column_names=", ".join(columns_to_overwrite),
                        reference_code=ReferenceCodes._LAG_LEAD_COLUMN_EXISTS)
                )

    ############################################################################
    # And the below logic handles lag_by_time features on inputs
    # with origin_time
    ############################################################################

    def _check_one_lag_inputs(self,
                              X: TimeSeriesDataFrame,
                              lag_var: str,
                              lag_order: int) -> None:
        """
        Validate that data frame, lag variable and lag order are valid.

        :param X: The data frame to generate lag on.
        :param lag_var: The name of lagging variable.
        :lag_order: the order of a lag.
        :raises: ForecastingConfigException,
                 ForecastingDataException
        """
        if not isinstance(lag_var, str):
            raise ForecastingConfigException._with_error(
                AzureMLError.create(TimeseriesDfColumnTypeNotSupported, target='lag_var',
                                    reference_code=ReferenceCodes._LAG_LEAD_COLUMN_TYPE_CONSTRUCT,
                                    col_name='lag_var',
                                    supported_type='string')
            )
        if not isinstance(lag_order, int):
            raise ForecastingConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentType, target="lag_order",
                    argument="lag_order", actual_type=type(lag_order), expected_types="int",
                    reference_code=ReferenceCodes._LAG_LEAD_LAG_TYPE_CONSTRUCT)
            )
        if not isinstance(X, TimeSeriesDataFrame):
            raise ForecastingDataException._with_error(
                AzureMLError.create(TimeseriesInputIsNotTimeseriesDf, target='X',
                                    reference_code=ReferenceCodes._LAG_LEAD_NOT_TSDF)
            )

    def _construct_one_lag_by_time_with_origin(self,
                                               X: TimeSeriesDataFrame,
                                               lag_var: str,
                                               lag_order: int) -> TimeSeriesDataFrame:
        """
        Construct a single lag of a single variable.

        Should only be used on an argument with origin_time set.
        Returns a unindexed pandas DataFrame with a single column.
        """
        # check inputs
        self._check_one_lag_inputs(X, lag_var, lag_order)
        if X.origin_time_colname is None:
            error_message = \
                ('This method should only be called on a '
                 'TimeSeriesDataFrame in which `origin_time_colname` is set!')
            raise ClientException(
                error_message,
                reference_code=ReferenceCodes._LAG_LEAD_NO_ORIGIN,
                has_pii=False)
        # prepare pretty lag endings: foo_lagX
        lag_postfix = LagLeadOperator._get_lag_col_common_postfix(lag_order)
        lag_postfix += str(abs(lag_order))
        if self._ts_freq:
            try:
                lag_postfix += self._ts_freq.name
            except NotImplementedError:
                lag_postfix += self._ts_freq.freqstr
        # when origin_time is not present, we have to artificially create one
        temp_df = pd.DataFrame(X).reset_index()
        lag_order_freq = cast(int, self._ts_freq)
        if lag_order == 1:
            # pandas bug: https://github.com/pandas-dev/pandas/issues/33683
            # may result in weird behavior when freq * 0 is applied. For that reason,
            # we will rely directly on the lagged origin column and not subtract
            # multiply by freq * 0.
            temp_df['lag_time'] = temp_df[X.origin_time_colname]
        else:
            temp_df['lag_time'] = (temp_df[X.origin_time_colname] - lag_order_freq * (lag_order - 1))
        true_grain = list(X.grain_colnames)
        index_cols = list(flatten_list([X.time_colname] + true_grain))
        # now turn tdsf into a time series
        ts = X._extract_time_series(lag_var).reset_index()
        left_join_keys = ['lag_time'] + true_grain
        right_join_keys = index_cols
        # join creates all the lags and NaNs in the appropriate places
        temp_df = temp_df[left_join_keys]
        result = temp_df.merge(ts, how='left', left_on=left_join_keys,
                               right_on=right_join_keys)
        df_with_lags = result[[lag_var]]
        df_with_lags.columns = [lag_var + lag_postfix]
        return cast(TimeSeriesDataFrame, df_with_lags)

    def _pre_check_data(self, X: TimeSeriesDataFrame) -> None:
        """
        Pre check data prior to generating lags for all columns.

        :param X: The time series data frame to be checked.
        :raises: ForecastingDataException, DataException
        """
        if not isinstance(X, TimeSeriesDataFrame):
            raise ForecastingDataException._with_error(
                AzureMLError.create(TimeseriesInputIsNotTimeseriesDf, target='X',
                                    reference_code=ReferenceCodes._LAG_LEAD_NOT_TSDF_ALL)
            )

    def _construct_all_lags_by_time_with_origin(self, X: TimeSeriesDataFrame) -> TimeSeriesDataFrame:
        """Call _construct_one_lag in a loop over lags_to_construct."""
        # quick check that X is indeed a tsdf
        self._pre_check_data(X)
        if X.origin_time_colname is None:
            error_message = ('This method should only be called on a '
                             'TimeSeriesDataFrame in which `origin_time_colname` is set!')
            raise ClientException(error_message, has_pii=False,
                                  reference_code=ReferenceCodes._LAG_LEAD_NO_ORIGIN_ALL)
        tsdf_with_lags = X.copy()
        # make sure we are not lagging columns that should not be lagged
        lags_to_construct_safe = self._check_columns_to_lag(X)
        columns_to_keep = []
        for lag_var, all_lag_orders in lags_to_construct_safe.items():
            for lag_order in all_lag_orders:
                lag = self._construct_one_lag_by_time_with_origin(X, lag_var, lag_order)
                lag_name = lag.columns[0]
                tsdf_with_lags[lag_name] = lag[lag_name].values
                columns_to_keep.append(lag_name)
        # we need to return only lag columns to unify processing
        return cast(TimeSeriesDataFrame, tsdf_with_lags[columns_to_keep])

    ############################################################################
    # And the below logic handles lag_by_occurrence features generation
    # on inputs with horizon_origin
    ############################################################################

    def _construct_one_lag_by_occurrence_with_horizon_origin(self,
                                                             X: TimeSeriesDataFrame,
                                                             lag_var: str,
                                                             lag_order: int) -> TimeSeriesDataFrame:
        """
        Construct a single lag_by_occurrence of a single variable.

        Returns a unindexed pandas DataFrame with a single column.
        """
        # check inputs
        self._check_one_lag_inputs(X, lag_var, lag_order)
        if (TimeSeriesInternal.HORIZON_NAME not in X.columns):
            error_message = \
                ('This method should only be called on a '
                 'TimeSeriesDataFrame in which horizon_origin is set!')
            raise ClientException(
                error_message,
                reference_code=ReferenceCodes._LAG_LEAD_NO_HORIZON,
                has_pii=False)

        # prepare pretty lag endings: foo_occurrence_lagX
        lag_postfix = LagLeadOperator._get_lag_col_common_postfix(lag_order, True)
        lag_postfix += str(abs(lag_order))
        if self._ts_freq:
            try:
                lag_postfix += self._ts_freq.name
            except NotImplementedError:
                lag_postfix += self._ts_freq.freqstr

        temp_df = pd.DataFrame(X).reset_index()

        true_grain = list(X.grain_colnames)
        index_cols = list(flatten_list([X.time_colname] + true_grain))

        not_imputed_val = MissingDummiesTransformer.MARKER_VALUE_NOT_MISSING
        if not self._no_original_order_column_safe():
            # When TimeSeriesInternal.DUMMY_ORDER_COLUMN column is available,
            # we will rely on this column to remove imputed rows before
            # generating lag_by_occurrence features.
            # This is deprecated behavior and is only included for backwards compatibility
            if (TimeSeriesInternal.DUMMY_ORDER_COLUMN in X.columns):
                if self._in_fit_transform:
                    target_dummies_name = \
                        MissingDummiesTransformer.get_column_name(TimeSeriesInternal.DUMMY_TARGET_COLUMN)
                    X = X[X[TimeSeriesInternal.DUMMY_ORDER_COLUMN].notnull()
                          | (X[target_dummies_name] == not_imputed_val)]
                else:
                    X = X[X[TimeSeriesInternal.DUMMY_ORDER_COLUMN].notnull()]
        else:
            dummies_name = MissingDummiesTransformer.get_column_name(lag_var)
            if dummies_name in X.columns:
                X = X[X[dummies_name] == not_imputed_val]

        # We will produce the occurrence lags from a version of the data where missing/imputed
        # values are removed - call this "ts"
        ts_cols = [lag_var, TimeSeriesInternal.HORIZON_NAME]
        ts = pd.DataFrame(X[ts_cols])
        # We will recompute the origin times anyway, so these can be dropped entirely
        ts.reset_index(level=X.origin_time_colname, drop=True, inplace=True)
        ts.reset_index(inplace=True)

        # Enumerate the rows of ts in each time-sorted grain-horizon group
        # This sequence index will be a join key that  forms the lags
        true_grain = list(X.grain_colnames) + list([TimeSeriesInternal.HORIZON_NAME])
        index_cols = list(flatten_list([X.time_colname] + true_grain))
        ts.sort_values(by=[X.time_colname], inplace=True, ascending=True)
        ts['temp_seq_record_index'] = ts.groupby(true_grain).cumcount() + 1

        # Left join ts's sequence index into the original input data by grain-horizon
        temp_df = temp_df.merge(ts[['temp_seq_record_index'] + index_cols], how='left',
                                left_on=index_cols, right_on=index_cols)

        # Missing/imputed rows will not have a filled sequence index
        # If not filled, they will have missing values for lag features and be dropped from the data altogether
        # In order to maintain the data contract, try to impute sequence indices for these rows
        if temp_df['temp_seq_record_index'].isnull().values.any():
            # The correct filling strategy for the sequence index is to sort by time
            # within each grain-horizon group and then backfill missing values.
            # The backfill ensures that imputed rows receive the same index as the next
            # valid row - which will eventually lag back to the *previous* valid row
            max_index_by_grain = {tsid_h: ts_one['temp_seq_record_index'].max() + 1
                                  for tsid_h, ts_one in ts.groupby(true_grain)}
            df_list = []
            for tsid_h, temp_df_one in temp_df.groupby(true_grain):
                temp_df_one_sorted = temp_df_one.sort_values(by=[X.time_colname])
                if pd.isnull(temp_df_one_sorted['temp_seq_record_index'].iloc[-1]):
                    # Due to the backfill, need to manually fill the latest value in temp_df_one if
                    # it is missing/imputed
                    temp_df_one_sorted['temp_seq_record_index'].values[-1] = max_index_by_grain.get(tsid_h, np.nan)
                temp_df_one_sorted['temp_seq_record_index'].fillna(method='bfill', inplace=True)
                df_list.append(temp_df_one_sorted)

            temp_df = pd.concat(df_list)
            # temp_df rows could be shuffled - put them back in their original order
            temp_df.sort_index(inplace=True)

        # Backward shift the sequence index in temp_df - after this operation, the sequence index
        # is part of a join key that will bring in lagged values
        temp_df['temp_seq_record_index'] = \
            temp_df['temp_seq_record_index'] - (temp_df[TimeSeriesInternal.HORIZON_NAME] - 1) - lag_order
        left_join_keys = ['temp_seq_record_index'] + true_grain
        right_join_keys = ['temp_seq_record_index'] + true_grain

        # join creates all the lags and NaNs in the appropriate places
        temp_df = temp_df[left_join_keys]
        result = temp_df.merge(ts, how='left', left_on=left_join_keys,
                               right_on=right_join_keys)
        # The dates in the result DataFrame are the dates corresponding to the lagged values
        # Return these dates since they can be useful i.e. as by-occurrence origin times
        df_with_lags = result[[lag_var, X.time_colname]]
        df_with_lags.rename(columns={lag_var: lag_var + lag_postfix}, inplace=True)

        return cast(TimeSeriesDataFrame, df_with_lags)

    def _construct_all_lags_by_occurrence_with_horizon_origin(self, X: TimeSeriesDataFrame) -> TimeSeriesDataFrame:
        """Call _construct_one_lag in a loop over lags_to_construct."""
        # quick check that X is indeed a tsdf
        self._pre_check_data(X)
        if (TimeSeriesInternal.HORIZON_NAME not in X.columns):
            error_message = ('This method should only be called on a '
                             'TimeSeriesDataFrame in which `horizon_origin` is set!')
            raise ClientException(error_message, has_pii=False,
                                  reference_code=ReferenceCodes._LAG_LEAD_NO_HORIZON_ALL)
        tsdf_with_lags = X.copy()

        # make sure we are not lagging columns that should not be lagged
        lags_to_construct_safe = self._check_columns_to_lag(X)
        columns_to_keep = []
        new_origins = None
        for lag_var, all_lag_orders in lags_to_construct_safe.items():
            for lag_order in all_lag_orders:
                lag = self._construct_one_lag_by_occurrence_with_horizon_origin(X, lag_var, lag_order)
                if lag_var == X.ts_value_colname and lag_order == 1:
                    new_origins = pd.DatetimeIndex(lag[X.time_colname])
                lag_name = lag.columns[0]
                tsdf_with_lags[lag_name] = lag[lag_name].values
                columns_to_keep.append(lag_name)

        if self._add_occurrence_origin_column_safe():
            if new_origins is None:
                # If we need new origin times compute them from the lag-1 on the target column
                lag = \
                    self._construct_one_lag_by_occurrence_with_horizon_origin(X, X.ts_value_colname, 1)
                new_origins = pd.DatetimeIndex(lag[X.time_colname])
            tsdf_with_lags[TimeSeriesInternal.ORIGIN_TIME_OCCURRENCE_COLUMN_NAME] = new_origins
            columns_to_keep.append(TimeSeriesInternal.ORIGIN_TIME_OCCURRENCE_COLUMN_NAME)

        # we need to return only lag columns to unify processing
        return cast(TimeSeriesDataFrame, tsdf_with_lags[columns_to_keep])

    def _set_lag_option(self, X: TimeSeriesDataFrame) -> None:
        """
        Set lag option such that it is determined in the fit()
        """
        lags_to_construct_safe = self._check_columns_to_lag(X)
        if len(lags_to_construct_safe) > 0:
            for lag_col in self.lags_to_construct.keys():
                target_dummies_name = MissingDummiesTransformer.get_column_name(lag_col)
                is_imputed_val = MissingDummiesTransformer.MARKER_VALUE_MISSING
                if target_dummies_name not in X.columns:
                    num_missing_values = 0
                else:
                    num_missing_values = \
                        (X[target_dummies_name].isna() | X[target_dummies_name] == is_imputed_val).sum()
                if num_missing_values / X.shape[0] < self.SPARSITY_THRESHOLD:
                    # Data is (almost) evenly spaced, we will do lag_by_time
                    self.lag_option = LagLeadOperator.LAG_BY_TIME
                else:
                    # Data is not evenly spaced, we will do lag_by_occurrence
                    self.lag_option = LagLeadOperator.LAG_BY_OCCURRENCE
                    break

    def _cache_trailing_training_data(self, X: TimeSeriesDataFrame) -> 'LagLeadOperator':
        """
        Cache the tail end of the training data.

        When transforming test data, we should not have NaNs at the start
        because we can use tail bits of training data to obtain them.
        """
        # quick check that X is indeed a tsdf
        if not isinstance(X, TimeSeriesDataFrame):
            raise ForecastingDataException._with_error(
                AzureMLError.create(TimeseriesInputIsNotTimeseriesDf, target='X',
                                    reference_code=ReferenceCodes._LAG_LEAD_NOT_TSDF_CACHE)
            )

        # find largest lag value that needs to be constructed
        lags_to_construct_safe = self._check_columns_to_lag(X)
        if len(lags_to_construct_safe) > 0:
            lags_inverse_dict = invert_dict_of_lists(lags_to_construct_safe)
            max_lag_order = max(lags_inverse_dict.keys())

            # Internal function to get trailing data for a single grain
            def get_trailing_by_grain(gr, Xgr):
                h_max = self.max_horizon_from_key_safe(gr, self.max_horizon)
                last_obs_for_cache = max_lag_order + h_max + 1
                val_series = Xgr.ts_value.sort_index(level=Xgr.time_colname)
                tail_series = val_series.iloc[-last_obs_for_cache:]
                tail_start = (tail_series.index
                              .get_level_values(Xgr.time_colname).min())
                return Xgr[Xgr.time_index >= tail_start]

            # ------------------------------------------------------------
            if self.lag_option == LagLeadOperator.LAG_BY_OCCURRENCE:
                # Find a selection of rows for which at least one of the variables to be lagged is not imputed
                sel_not_imputed = pd.Series(False, index=X.index)
                not_imputed_val = MissingDummiesTransformer.MARKER_VALUE_NOT_MISSING
                for lag_col in lags_to_construct_safe.keys():
                    missing_dummies_name = MissingDummiesTransformer.get_column_name(lag_col)
                    if missing_dummies_name in X.columns:
                        # Turn on the selection for rows marked as not imputed
                        sel_not_imputed |= (X[missing_dummies_name] == not_imputed_val)
                    else:
                        # In this case, assume nothing is imputed
                        sel_not_imputed |= True
                        break

                # Remove rows where all variables to be lagged are imputed
                # No reason to keep these in the cache for lag-by-occurrence
                X = X[sel_not_imputed]

            # take last max_lag_order obs per grain
            if X.grain_colnames is not None:
                self._cache = X.groupby_grain().apply(
                    lambda Xgr: get_trailing_by_grain(Xgr.name, Xgr))
            else:
                self._cache = get_trailing_by_grain('', X)

            # For generating lag_by_time features, if cache contains the
            # missing value, it will result in the degradation of
            # a shape of transformed data on the data set
            # missing y values.
            # We backfill these values if backfill_cache is true.
            if (self.lag_option == LagLeadOperator.LAG_BY_TIME):
                if self._cache is not None and self.backfill_cache:
                    ts_imputer = TimeSeriesImputer(input_column=self._cache.ts_value_colname,
                                                   option='fillna',
                                                   method='bfill',
                                                   freq=self._ts_freq)
                    self._cache = ts_imputer.transform(self._cache)
        else:
            self._cache = None

        return self

    ############################################################################
    # Last, we have publicly facing fit and predict methods
    ############################################################################

    # fit method performs caching of tail bits of training data, this way
    # lags on test data are populated with non-missing values from train
    @function_debug_log_wrapped(logging.INFO)
    def fit(self, X: TimeSeriesDataFrame, y: Optional[Any] = None) -> 'LagLeadOperator':
        """
        Fit the lag/lead transform.

        This method performs caching of tail bits of training data, this way
        lags on test data are populated with non-missing values from train

        :param X: Input data
        :type X: azureml.automl.runtime.shared.time_series_data_frame.TimeSeriesDataFrame

        :param y: Ignored. Included for pipeline compatibility

        :return: Fitted transform
        :rtype: azureml.automl.runtime.featurizer.transformer.timeseries.lag_lead_operator.LagLeadOperator
        """
        self._ts_freq = X.infer_freq(return_freq_string=False)
        self._set_lag_option(X)
        self._check_for_column_overwrites(X)
        self._cache_trailing_training_data(X)
        self._is_fit = True

        return self

    @function_debug_log_wrapped(logging.INFO)
    def transform(self, X: TimeSeriesDataFrame) -> TimeSeriesDataFrame:
        """
        Construct lag columns in TimeSeriesDataFrame X.

        :param X: Input data
        :type X: azureml.automl.runtime.shared.time_series_data_frame.TimeSeriesDataFrame

        :return: Data frame with lag/lead columns
        :rtype: azureml.automl.runtime.shared.time_series_data_frame.TimeSeriesDataFrame
        """
        if not self._is_fit:
            error_message = ("For the LagOperator to work correctly, fit() "
                             "must be called before transform()!")
            raise ClientException(error_message, has_pii=False,
                                  reference_code=ReferenceCodes._LAG_LEAD_NO_FIT)

        # logic:
        #   1) create copy of input data
        #   2) attempt to prepend the cache to it (will fail for training data)
        #   3) call method to do lags in a loop
        #   4) left join back to original data to trim off the early rows

        output = X.copy()
        # this should work without errors when applied to test data
        # under the assumption that test comes after train :)
        if self._no_original_order_column_safe() and self.lag_option == LagLeadOperator.LAG_BY_OCCURRENCE and \
           self._cache is not None:
            # If we're not using the order column and we're lagging by occurrence,
            # make sure we have missing indicator columns for every column we're lagging
            # Otherwise, the concat call could add a missing indicator to X and fill it with NaN
            # this can have unwanted consequences
            lags_to_construct_safe = self._check_columns_to_lag(X)
            for lag_col in lags_to_construct_safe.keys():
                missing_dummies_name = MissingDummiesTransformer.get_column_name(lag_col)
                if missing_dummies_name in self._cache.columns:
                    Contract.assert_true(missing_dummies_name in X.columns,
                                         'Cache contains a missing value indicator, but input data does not',
                                         log_safe=True)
        try:
            # Default behavior when axis isn't provided was to sort in pandas 0.23.
            # In order to preserve this behavior and upgrade to pandas 0.25, this sort
            # was added to suppress warnings and keep behavior.
            temp_output = pd.concat([self._cache, output], sort=True)
        # exception will be thrown when applied to train data since TSDF
        # will not allow to prepend a part of it to itself
        except ForecastingDataException as ex:
            if ex.error_code == TimeseriesDfDuplicatedIndex().code:
                # Check if the error code is TimeseriesDfDuplicatedIndex.
                temp_output = output.copy()
            else:
                # Otherwise raise the exception.
                raise

        if self.lag_option == LagLeadOperator.LAG_BY_OCCURRENCE:
            if TimeSeriesInternal.HORIZON_NAME not in X.columns:
                temp_output = MaxHorizonFeaturizer(self.max_horizon).fit_transform(temp_output)
            # actual lags implemented in a separate internal method
            interim_output = self._construct_all_lags_by_occurrence_with_horizon_origin(temp_output)

            # this join makes sure that all rows that were not in the input TSDF
            # get eliminated by left join semantics
            # small step: avoiding duplicating columns
            # must take feature columns from right
            feature_columns = interim_output.columns
            non_feature_columns = output.columns.difference(feature_columns)
            # also suppress warnings from joins
            filterwarnings('ignore')
            result = output[non_feature_columns].merge(
                interim_output[feature_columns], how='left',
                left_index=True, right_index=True)
            filterwarnings('default')

            # we need to do a little more work if dropna is True
            # don't want to drop rows where NaNs are not caused by the LagOperator
            if self.dropna:
                notnull_by_column = result[feature_columns].notnull().values
                not_null_all_cols = np.apply_along_axis(all, 1, notnull_by_column)
                result = result[not_null_all_cols]

        if (self.lag_option == LagLeadOperator.LAG_BY_TIME):
            if X.origin_time_colname is None:
                temp_output = self.create_origin_times(
                    temp_output, self.max_horizon, freq=self._ts_freq,
                    origin_time_colname=self.origin_time_colname)
            # Set the flag for train and test set for backwards compatibility only
            # Can be safely deleted after the next stable SDK is rolled out.
            IN_FIT_TRANSFORM = '_in_fit_transform'
            if not hasattr(self, IN_FIT_TRANSFORM):
                setattr(self, IN_FIT_TRANSFORM, False)

            # actual lags implemented in a separate internal method
            interim_output = self._construct_all_lags_by_time_with_origin(temp_output)

            # this join makes sure that all rows that were not in the input TSDF
            # get eliminated by left join semantics
            # small step: avoiding duplicating columns
            # must take feature columns from right
            feature_columns = interim_output.columns
            non_feature_columns = output.columns.difference(feature_columns)
            # also suppress warnings from joins
            filterwarnings('ignore')
            result = output[non_feature_columns].merge(
                interim_output[feature_columns], how='left',
                left_index=True, right_index=True)
            filterwarnings('default')

            # we need to do a little more work if dropna is True
            # don't want to drop rows where NaNs are not caused by the LagOperator
            if self.dropna:
                notnull_by_column = result[feature_columns].notnull().values
                not_null_all_cols = np.apply_along_axis(all, 1, notnull_by_column)
                result = result[not_null_all_cols]

        return cast(TimeSeriesDataFrame, result)

    @function_debug_log_wrapped(logging.INFO)
    def fit_transform(
            self,
            X: TimeSeriesDataFrame,
            y: Optional[np.ndarray] = None,
            **fit_params: Any) -> TimeSeriesDataFrame:
        """ When fit_transform() is called, perform it and set the '_in_fit_transform' flag to False.
        This flag signals that we are in the test set. This is needed for generating lags by occurrence.
        """
        self._in_fit_transform = True
        rv = super(LagLeadOperator, self).fit_transform(X, y, **fit_params)  # type: TimeSeriesDataFrame
        self._in_fit_transform = False
        return rv

    def preview_column_names(self, tsdf: TimeSeriesDataFrame, with_origin: bool = False) -> List[str]:
        """
        Get the lag lead features names that would be made if the transform were applied to X.

        :param tsdf: The TimeSeriesDataFrame to generate column names for.
        :type tsdf: azureml.automl.runtime.shared.time_series_data_frame.TimeSeriesDataFrame
        :param with_origin: Return 'origin' column name if it was created.
        :type with_origin: bool

        :return: lag lead feature names
        :rtype: list[str]

        """
        self._ts_freq = tsdf.infer_freq(return_freq_string=False)
        # set appropriate lag_by option if the function is called directly
        if not self._is_fit:
            self._set_lag_option(tsdf)
        new_cols = self._generate_new_column_names()
        if with_origin:
            new_cols.append(self.origin_time_colname)
        self._lag_columns = new_cols
        return new_cols

    @staticmethod
    def _get_lag_col_common_postfix(lag_order: int, has_occurrence: Optional[bool] = False) -> str:
        """Get the common part in the postfix of the columns generated by LagLeadOperator."""
        post_fix = LagLeadOperator.LAG_POSTFIX if lag_order > 0 else LagLeadOperator.LEAD_POSTFIX
        post_fix = LagLeadOperator.POSTFIX_SEP + post_fix
        if has_occurrence:
            post_fix = LagLeadOperator.POSTFIX_SEP + LagLeadOperator.OCCURRENCE_POSTFIX + post_fix
        return post_fix

    @staticmethod
    def get_col_internal_type(col_name: str) -> Optional[str]:
        """
        Get the type of a column if it is generated by lag lead operator.

        :param col_name: The column name.
        :return: If column is generated by lag lead operator, return lag/lead/occurrence_lag/occurrence_lead,
                 else None.
        """
        for has_occurrence in [True, False]:
            for order in [-1, 1]:
                lag_postfix = LagLeadOperator._get_lag_col_common_postfix(order, has_occurrence)
                if re.search("{}[0-9a-zA-Z-]+$".format(lag_postfix), col_name) is not None:
                    return lag_postfix[1:]
        return None
