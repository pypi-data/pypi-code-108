# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Class for all the forecasting related parameters."""
from typing import Any, cast, Dict, List, Optional, Union
import logging
import warnings

from azureml._common._error_definition import AzureMLError
from azureml._common._error_definition.user_error import ArgumentBlankOrEmpty, ArgumentOutOfRange
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    InvalidArgumentType,
    InvalidArgumentWithSupportedValues,
    TimeseriesInvalidDateOffsetType,
    InvalidParameterSelection,
    TimeseriesAggNoFreq)
from azureml.automl.core.shared.constants import (TimeSeries,
                                                  TimeSeriesInternal,
                                                  TimeSeriesWebLinks,
                                                  ShortSeriesHandlingValues,
                                                  AggregationFunctions)
from azureml.automl.core.shared.exceptions import ConfigException
from azureml.automl.core.shared.reference_codes import ReferenceCodes

logger = logging.getLogger(__name__)


class ForecastingParameters:
    """
    Manage parameters used by forecasting tasks.

    :param time_column_name:
        The name of the time column. This parameter is required when forecasting to specify the datetime
        column in the input data used for building the time series and inferring its frequency.
    :type time_column_name: str
    :param forecast_horizon:
        The desired maximum forecast horizon in units of time-series frequency. The default value is 1.

        Units are based on the time interval of your training data, e.g., monthly, weekly that the forecaster
        should predict out. When task type is forecasting, this parameter is required. For more information on
        setting forecasting parameters, see `Auto-train a time-series forecast model <https://docs.microsoft.com/
        azure/machine-learning/how-to-auto-train-forecast>`_.
    :type forecast_horizon: int or str
    :param time_series_id_column_names:
        The names of columns used to group a timeseries.
        It can be used to create multiple series. If time series id column names is not defined or
        the identifier columns specified do not identify all the series in the dataset, the time series identifiers
        will be automatically created for your dataset.
    :type time_series_id_column_names: str or list(str)
    :param target_lags:
        The number of past periods to lag from the target column. By default the lags are turned off.

        When forecasting, this parameter represents the number of rows to lag the target values based
        on the frequency of the data. This is represented as a list or single integer. Lag should be used
        when the relationship between the independent variables and dependent variable do not match up or
        correlate by default. For example, when trying to forecast demand for a product, the demand in any
        month may depend on the price of specific commodities 3 months prior. In this example, you may want
        to lag the target (demand) negatively by 3 months so that the model is training on the correct
        relationship. For more information, see `Auto-train a time-series forecast model
        <https://docs.microsoft.com/azure/machine-learning/how-to-auto-train-forecast>`_.

        **Note on auto detection of target lags and rolling window size.
        Please see the corresponding comments in the rolling window section.**
        We use the next algorithm to detect the optimal target lag and rolling window size.

        #. Estimate the maximum lag order for the look back feature selection. In our case it is the number of
           periods till the next date frequency granularity i.e. if frequency is daily, it will be a week (7),
           if it is a week, it will be month (4). That values multiplied by two is the largest
           possible values of lags/rolling windows. In our examples, we will consider the maximum lag
           order of 14 and 8 respectively).
        #. Create a de-seasonalized series by adding trend and residual components. This will be used
           in the next step.
        #. Estimate the PACF - Partial Auto Correlation Function on the on the data from (2)
           and search for points, where the auto correlation is significant i.e. its absolute
           value is more then 1.96/square_root(maximal lag value), which correspond to significance of 95%.
        #. If all points are significant, we consider it being strong seasonality
           and do not create look back features.
        #. We scan the PACF values from the beginning and the value before the first insignificant
           auto correlation will designate the lag. If first significant element (value correlate with
           itself) is followed by insignificant, the lag will be 0 and we will not use look back features.
    :type target_lags: int, str, or list(int)
    :param feature_lags: Flag for generating lags for the numeric features with 'auto' or None.
    :type feature_lags: str or None
    :param target_rolling_window_size:
        The number of past periods used to create a rolling window average of the target column.

        When forecasting, this parameter represents `n` historical periods to use to generate forecasted values,
        <= training set size. If omitted, `n` is the full training set size. Specify this parameter
        when you only want to consider a certain amount of history when training the model.
        If set to 'auto', rolling window will be estimated as the last
        value where the PACF is more then the significance threshold. Please see target_lags section for details.
    :type target_rolling_window_size: int, str or None
    :param country_or_region_for_holidays: The country/region used to generate holiday features.
        These should be ISO 3166 two-letter country/region codes, for example 'US' or 'GB'.
    :type country_or_region_for_holidays: str or None
    :param use_stl: Configure STL Decomposition of the time-series target column.
                use_stl can take three values: None (default) - no stl decomposition, 'season' - only generate
                season component and season_trend - generate both season and trend components.
    :type use_stl: str or None
    :param seasonality: Set time series seasonality as an integer multiple of the series frequency.
                If seasonality is set to 'auto', it will be inferred.
                If set to None, the time series is assumed non-seasonal which is equivalent to seasonality=1.
    :type seasonality: int, str or None
    :param short_series_handling: Configure short series handling for forecasting tasks.
    :type short_series_handling: bool
    :param short_series_handling_configuration:
        The parameter defining how if AutoML should handle short time series.

        Possible values: 'auto' (default), 'pad', 'drop' and None.
        * **auto** short series will be padded if there are no long series,
        otherwise short series will be dropped.
        * **pad** all the short series will be padded.
        * **drop**  all the short series will be dropped".
        * **None** the short series will not be modified.
        If set to 'pad', the table will be padded with the zeroes and
        empty values for the regressors and random values for target with the mean
        equal to target value median for given time series id. If median is more or equal
        to zero, the minimal padded value will be clipped by zero:
        Input:

        +------------+---------------+----------+--------+
        | Date       | numeric_value | string   | target |
        +============+===============+==========+========+
        | 2020-01-01 | 23            | green    | 55     |
        +------------+---------------+----------+--------+

        Output assuming minimal number of values is four:

        +------------+---------------+----------+--------+
        | Date       | numeric_value | string   | target |
        +============+===============+==========+========+
        | 2019-12-29 | 0             | NA       | 55.1   |
        +------------+---------------+----------+--------+
        | 2019-12-30 | 0             | NA       | 55.6   |
        +------------+---------------+----------+--------+
        | 2019-12-31 | 0             | NA       | 54.5   |
        +------------+---------------+----------+--------+
        | 2020-01-01 | 23            | green    | 55     |
        +------------+---------------+----------+--------+

        **Note:** We have two parameters short_series_handling_configuration and
        legacy short_series_handling. When both parameters are set we are
        synchronize them as shown in the table below (short_series_handling_configuration and
        short_series_handling for brevity are marked as handling_configuration and handling
        respectively).

        +-----------+------------------------+--------------------+----------------------------------+
        |  handling | handling_configuration | resulting handling | resulting handling_configuration |
        +===========+========================+====================+==================================+
        | True      | auto                   | True               | auto                             |
        +-----------+------------------------+--------------------+----------------------------------+
        | True      | pad                    | True               | auto                             |
        +-----------+------------------------+--------------------+----------------------------------+
        | True      | drop                   | True               | auto                             |
        +-----------+------------------------+--------------------+----------------------------------+
        | True      | None                   | False              | None                             |
        +-----------+------------------------+--------------------+----------------------------------+
        | False     | auto                   | False              | None                             |
        +-----------+------------------------+--------------------+----------------------------------+
        | False     | pad                    | False              | None                             |
        +-----------+------------------------+--------------------+----------------------------------+
        | False     | drop                   | False              | None                             |
        +-----------+------------------------+--------------------+----------------------------------+
        | False     | None                   | False              | None                             |
        +-----------+------------------------+--------------------+----------------------------------+

    :type short_series_handling_configuration: str or None
    :param freq: Forecast frequency.

        When forecasting, this parameter represents the period with which the forecast is desired,
        for example daily, weekly, yearly, etc. The forecast frequency is dataset frequency by default.
        You can optionally set it to greater (but not lesser) than dataset frequency.
        We'll aggregate the data and generate the results at forecast frequency. For example,
        for daily data, you can set the frequency to be daily, weekly or monthly, but not hourly.
        The frequency needs to be a pandas offset alias.
        Please refer to pandas documentation for more information:
        https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#dateoffset-objects
    :type freq: str or None
    :param target_aggregation_function: The function to be used to aggregate the time series target
                                        column to conform to a user specified frequency. If the
                                        target_aggregation_function is set, but the freq parameter
                                        is not set, the error is raised. The possible target
                                        aggregation functions are: "sum", "max", "min" and "mean".
            * The target column values are aggregated based on the specified operation.
              Typically, sum is appropriate for most scenarios.
            * Numerical predictor columns in your data are aggregated by sum, mean, minimum value,
              and maximum value. As a result, automated ML generates new columns suffixed with the
              aggregation function name and applies the selected aggregate operation.
            * For categorical predictor columns, the data is aggregated by mode,
              the most prominent category in the window.
            * Date predictor columns are aggregated by minimum value, maximum value and mode.

            +----------------+-----------------------------+---------------------------------------------+
            |      freq      | target_aggregation_function |      Data regularity fixing mechanism       |
            +================+=============================+=============================================+
            | None (Default) | None (Default)              | The aggregation is not applied.             |
            |                |                             | If the valid frequency can not be           |
            |                |                             | determined the error will be raised.        |
            +----------------+-----------------------------+---------------------------------------------+
            | Some Value     | None (Default)              | The aggregation is not applied.             |
            |                |                             | If the number of data points compliant      |
            |                |                             | to given frequency grid is less then 90%    |
            |                |                             | these points will be removed, otherwise     |
            |                |                             | the error will be raised.                   |
            +----------------+-----------------------------+---------------------------------------------+
            | None (Default) | Aggregation function        | The error about missing frequency parameter |
            |                |                             | is raised.                                  |
            +----------------+-----------------------------+---------------------------------------------+
            | Some Value     | Aggregation function        | Aggregate to frequency using provided       |
            |                |                             | aggregation function.                       |
            +----------------+-----------------------------+---------------------------------------------+

    :type target_aggregation_function: str or None
    :param cv_step_size:
        Number of periods between the origin_time of one CV fold and the next fold. For
        example, if `n_step` = 3 for daily data, the origin time for each fold will be
        three days apart.
    :type cv_step_size: int
    :param validate_parameters: Configure to validate input parameters.
    :type validate_parameters: bool

    """

    DEPRECATED_DICT = {
        TimeSeries.MAX_HORIZON: TimeSeries.FORECAST_HORIZON,
        TimeSeries.GRAIN_COLUMN_NAMES: TimeSeries.TIME_SERIES_ID_COLUMN_NAMES,
        TimeSeries.COUNTRY_OR_REGION: TimeSeries.COUNTRY_OR_REGION_FOR_HOLIDAYS,
        TimeSeries.COUNTRY: TimeSeries.COUNTRY_OR_REGION_FOR_HOLIDAYS,
        TimeSeries.HOLIDAY_COUNTRY: TimeSeries.COUNTRY_OR_REGION_FOR_HOLIDAYS
    }

    DEFAULT_TIMESERIES_VALUE = {
        TimeSeries.FORECAST_HORIZON: TimeSeriesInternal.MAX_HORIZON_DEFAULT,
        TimeSeries.MAX_HORIZON: TimeSeriesInternal.MAX_HORIZON_DEFAULT,
        TimeSeries.TARGET_ROLLING_WINDOW_SIZE: TimeSeriesInternal.WINDOW_SIZE_DEFDAULT,
        TimeSeries.TARGET_LAGS: TimeSeriesInternal.TARGET_LAGS_DEFAULT,
        TimeSeries.FEATURE_LAGS: TimeSeriesInternal.FEATURE_LAGS_DEFAULT,
        TimeSeries.SEASONALITY: TimeSeriesInternal.SEASONALITY_VALUE_DEFAULT,
        TimeSeries.SHORT_SERIES_HANDLING: TimeSeriesInternal.SHORT_SERIES_HANDLING_DEFAULT,
        TimeSeries.USE_STL: TimeSeriesInternal.USE_STL_DEFAULT,
        TimeSeries.FREQUENCY: TimeSeriesInternal.FREQUENCY_DEFAULT,
        TimeSeries.SHORT_SERIES_HANDLING_CONFIG: TimeSeriesInternal.SHORT_SERIES_HANDLING_CONFIG_DEFAULT,
        TimeSeries.TARGET_AGG_FUN: TimeSeriesInternal.TARGET_AGG_FUN_DEFAULT,
        TimeSeries.CV_STEP_SIZE: TimeSeriesInternal.CV_STEP_SIZE_DEFAULT
    }

    _SHORT_GRAIN_HANDLING_DICT = {
        (True, ShortSeriesHandlingValues.SHORT_SERIES_HANDLING_AUTO):
            (True, ShortSeriesHandlingValues.SHORT_SERIES_HANDLING_AUTO),
        (True, ShortSeriesHandlingValues.SHORT_SERIES_HANDLING_PAD):
            (True, ShortSeriesHandlingValues.SHORT_SERIES_HANDLING_PAD),
        (True, ShortSeriesHandlingValues.SHORT_SERIES_HANDLING_DROP):
            (True, ShortSeriesHandlingValues.SHORT_SERIES_HANDLING_DROP),
        (True, None): (False, None),
        (False, ShortSeriesHandlingValues.SHORT_SERIES_HANDLING_AUTO):
            (False, None),
        (False, ShortSeriesHandlingValues.SHORT_SERIES_HANDLING_PAD):
            (False, None),
        (False, ShortSeriesHandlingValues.SHORT_SERIES_HANDLING_DROP):
            (False, None),
        (False, None):
            (False, None)
    }

    _SYNC_WARNING_TEXT = (
        'short_series_handling_configuration was set to None '
        'because ForecastingParameters was initialized with '
        'short_series_handling=False. Please instantiate this '
        'class with short_series_handling=True to set '
        'the short_series_handling_configuration.')

    EMPTY_TIME_COLUMN_NAME = "_EMPTY_TIME_COLUMN_NAME"
    MAX_LAG_LENGTH = 2000

    def __init__(
            self,
            time_column_name: Optional[str] = None,
            forecast_horizon: Union[str, int] = TimeSeriesInternal.MAX_HORIZON_DEFAULT,
            time_series_id_column_names: Optional[Union[str, List[str]]] = None,
            group_column_names: Optional[Union[str, List[str]]] = None,
            target_lags: Optional[Union[List[int], int, str]] = TimeSeriesInternal.TARGET_LAGS_DEFAULT,
            feature_lags: Optional[str] = TimeSeriesInternal.FEATURE_LAGS_DEFAULT,
            target_rolling_window_size: Optional[Union[str, int]] = TimeSeriesInternal.WINDOW_SIZE_DEFDAULT,
            holiday_country: Optional[str] = None,
            seasonality: Optional[Union[str, int]] = TimeSeriesInternal.SEASONALITY_VALUE_DEFAULT,
            country_or_region_for_holidays: Optional[str] = None,
            use_stl: Optional[str] = TimeSeriesInternal.USE_STL_DEFAULT,
            short_series_handling: bool = TimeSeriesInternal.SHORT_SERIES_HANDLING_DEFAULT,
            short_series_handling_configuration: Optional[str] =
            TimeSeriesInternal.SHORT_SERIES_HANDLING_CONFIG_DEFAULT,
            freq: Optional[str] = None,
            target_aggregation_function: Optional[str] = TimeSeriesInternal.TARGET_AGG_FUN_DEFAULT,
            cv_step_size: Optional[int] = TimeSeriesInternal.CV_STEP_SIZE_DEFAULT,
            validate_parameters: Optional[bool] = True,
            **kwargs: Any
    ):
        """
        Manage parameters used by forecasting tasks.

        :param time_column_name:
            The name of the time column. This parameter is required when forecasting to specify the datetime
            column in the input data used for building the time series and inferring its frequency.
        :type time_column_name: str
        :param forecast_horizon:
            The desired maximum forecast horizon in units of time-series frequency. The default value is 1.

            Units are based on the time interval of your training data, e.g., monthly, weekly that the forecaster
            should predict out. When task type is forecasting, this parameter is required. For more information on
            setting forecasting parameters, see `Auto-train a time-series forecast model <https://docs.microsoft.com/
            azure/machine-learning/how-to-auto-train-forecast>`_.
        :type forecast_horizon: int
        :param time_series_id_column_names:
            The names of columns used to group a timeseries.
            It can be used to create multiple series. If grain is not defined, the data set is assumed
            to be one time-series. This parameter is used with task type forecasting.
        :type time_series_id_column_names: str or list(str)
        :param target_lags:
            The number of past periods to lag from the target column. By default the lags are turned off.

            When forecasting, this parameter represents the number of rows to lag the target values based
            on the frequency of the data. This is represented as a list or single integer. Lag should be used
            when the relationship between the independent variables and dependent variable do not match up or
            correlate by default. For example, when trying to forecast demand for a product, the demand in any
            month may depend on the price of specific commodities 3 months prior. In this example, you may want
            to lag the target (demand) negatively by 3 months so that the model is training on the correct
            relationship. For more information, see `Auto-train a time-series forecast model
            <https://docs.microsoft.com/azure/machine-learning/how-to-auto-train-forecast>`_.

            **Note on auto detection of target lags and rolling window size (see below).**
            We use the next algorithm to detect the optimal target lag and rolling window size.

            #. Estimate the period, on which we consider look back features, in our case it is the number of
               periods till the next date frequency granularity i.e. if frequency is daily, it will be a week (7),
               if it is a week, it will be month (4). That values multiplied by two is the largest
               possible values of lags/rolling windows (for our examples it will be 14 and 8 respectively).
            #. Decompose the series into seasonal, trend and residual components and remove seasonal part.
            #. Estimate the PACF - Partial Auto Correlation Function on the on the data from (2)
               and search for points, where the auto correlation is significant i.e. its absolute
               value is more then 1.96/square_root(maximal lag value), which correspond to significance of 95%.
            #. If all points are significant, we consider it being strong seasonality
               and do not create look back features.
            #. We scan the PACF values from the beginning and the value before the first insignificant
               auto correlation will designate the lag. If first significant element (value correlate with
               itself) is followed by insignificant, the lag will be 0 and we will not use look back features.
            #. Rolling window size will be the last value where the PACF is more then the significance threshold.
        :type target_lags: int or list(int)
        :param feature_lags: Flag for generating lags for the numeric features with 'auto' or None.
        :type feature_lags: str or None
        :param target_rolling_window_size:
            The number of past periods used to create a rolling window average of the target column.

            When forecasting, this parameter represents `n` historical periods to use to generate forecasted values,
            <= training set size. If omitted, `n` is the full training set size. Specify this parameter
            when you only want to consider a certain amount of history when training the model.
        :type target_rolling_window_size: int
        :param holiday_country: The country/region used to generate holiday features.
            These should be ISO 3166 two-letter country/region codes, for example 'US' or 'GB'.
            To be deprecated. Please use country_or_region_for_holidays.
        :type country_or_region_for_holidays: str
        :param country_or_region_for_holidays: The country/region used to generate holiday features.
            These should be ISO 3166 two-letter country/region codes, for example 'US' or 'GB'.
        :type country_or_region_for_holidays: str
        :param use_stl: Configure STL Decomposition of the time-series target column.
                    use_stl can take three values: None (default) - no stl decomposition, 'season' - only generate
                    season component and season_trend - generate both season and trend components.
        :type use_stl: str
        :param seasonality: Set time series seasonality as an integer multiple of the series frequency.
                    If seasonality is set to 'auto', it will be inferred.
                    If set to None, the time series is assumed non-seasonal which is equivalent to seasonality=1.
        :type seasonality: int or str or None
        :param short_series_handling: Configure short series handling for forecasting tasks.
        :type short_series_handling: bool
        :param short_series_handling_configuration:
            The parameter defining how if AutoML should handle short time series.

            Possible values: 'auto' (default), 'pad', 'drop' and None.
            * **auto** short series will be padded if there are no long series,
            otherwise short series will be dropped.
            * **pad** all the short series will be padded.
            * **drop**  all the short series will be dropped".
            * **None** the short series will not be modified.
            If set to 'pad', the table will be padded with the zeroes and
            empty values for the regressors and random values for target with the mean
            equal to target value median for given time series id. If median is more or equal
            to zero, the minimal padded value will be clipped by zero:
            Input:

            +------------+---------------+----------+--------+
            | Date       | numeric_value | string   | target |
            +============+===============+==========+========+
            | 2020-01-01 | 23            | green    | 55     |
            +------------+---------------+----------+--------+

            Output assuming minimal number of values is four:

            +------------+---------------+----------+--------+
            | Date       | numeric_value | string   | target |
            +============+===============+==========+========+
            | 2019-12-29 | 0             | NA       | 55.1   |
            +------------+---------------+----------+--------+
            | 2019-12-30 | 0             | NA       | 55.6   |
            +------------+---------------+----------+--------+
            | 2019-12-31 | 0             | NA       | 54.5   |
            +------------+---------------+----------+--------+
            | 2020-01-01 | 23            | green    | 55     |
            +------------+---------------+----------+--------+

            **Note:** We have two parameters short_series_handling_configuration and
            legacy short_series_handling. When both parameters are set we are
            synchronize them as shown in the table below (short_series_handling_configuration and
            short_series_handling for brevity are marked as handling_configuration and handling
            respectively).

            +-----------+------------------------+--------------------+----------------------------------+
            |  handling | handling_configuration | resulting handling | resulting handling_configuration |
            +===========+========================+====================+==================================+
            | True      | auto                   | True               | auto                             |
            +-----------+------------------------+--------------------+----------------------------------+
            | True      | pad                    | True               | auto                             |
            +-----------+------------------------+--------------------+----------------------------------+
            | True      | drop                   | True               | auto                             |
            +-----------+------------------------+--------------------+----------------------------------+
            | True      | None                   | False              | None                             |
            +-----------+------------------------+--------------------+----------------------------------+
            | False     | auto                   | False              | None                             |
            +-----------+------------------------+--------------------+----------------------------------+
            | False     | pad                    | False              | None                             |
            +-----------+------------------------+--------------------+----------------------------------+
            | False     | drop                   | False              | None                             |
            +-----------+------------------------+--------------------+----------------------------------+
            | False     | None                   | False              | None                             |
            +-----------+------------------------+--------------------+----------------------------------+

        :type short_series_handling_configuration: str
        :param freq: Forecast frequency.

            When forecasting, this parameter represents the period with which the forecast is desired,
            for example daily, weekly, yearly, etc. The forecast frequency is dataset frequency by default.
            You can optionally set it to greater (but not lesser) than dataset frequency.
            We'll aggregate the data and generate the results at forecast frequency. For example,
            for daily data, you can set the frequency to be daily, weekly or monthly, but not hourly.
            The frequency needs to be a pandas offset alias.
            Please refer to pandas documentation for more information:
            https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#dateoffset-objects
        :type freq: str
        :param target_aggregation_function:
            The function to be used to aggregate the time series target
            column to conform to a user specified frequency. If the
            target_aggregation_function is set, but the freq parameter
            is not set, the error is raised. The possible target
            aggregation functions are: "sum", "max", "min" and "mean".
            * The target column values are aggregated based on the specified operation.
              Typically, sum is appropriate for most scenarios.
            * Numerical predictor columns in your data are aggregated by sum, mean, minimum value,
              and maximum value. As a result, automated ML generates new columns suffixed with the
              aggregation function name and applies the selected aggregate operation.
            * For categorical predictor columns, the data is aggregated by mode,
              the most prominent category in the window.
            * Date predictor columns are aggregated by minimum value, maximum value and mode.

            +----------------+-----------------------------+---------------------------------------------+
            |      freq      | target_aggregation_function |      Data regularity fixing mechanism       |
            +================+=============================+=============================================+
            | None (Default) | None (Default)              | The aggregation is not applied.             |
            |                |                             | If the valid frequency can not be           |
            |                |                             | determined the error will be raised.        |
            +----------------+-----------------------------+---------------------------------------------+
            | Some Value     | None (Default)              | The aggregation is not applied.             |
            |                |                             | If the number of data points compliant      |
            |                |                             | to given frequency grid is less then 90%    |
            |                |                             | these points will be removed, otherwise     |
            |                |                             | the error will be raised.                   |
            +----------------+-----------------------------+---------------------------------------------+
            | None (Default) | Aggregation function        | The error about missing frequency parameter |
            |                |                             | is raised.                                  |
            +----------------+-----------------------------+---------------------------------------------+
            | Some Value     | Aggregation function        | Aggregate to frequency using provided       |
            |                |                             | aggregation function.                       |
            +----------------+-----------------------------+---------------------------------------------+

        :type target_aggregation_function: str
        :param cv_step_size:
            Number of periods between the origin_time of one CV fold and the next fold. For
            example, if `n_step` = 3 for daily data, the origin time for each fold will be
            three days apart.
        :type cv_step_size: int
        :param validate_parameters: Configure to validate input parameters.
        :type validate_parameters: bool
        """
        self._time_column_name = time_column_name if time_column_name else self.EMPTY_TIME_COLUMN_NAME
        self._forecast_horizon = forecast_horizon
        self._time_series_id_column_names = time_series_id_column_names
        self._target_lags = target_lags
        self._feature_lags = feature_lags
        self._target_rolling_window_size = target_rolling_window_size
        self._group_column_names = group_column_names
        self._drop_column_names = None
        self._use_stl = use_stl
        self._short_series_handling = short_series_handling
        self._freq = freq  # type: Optional[str]
        self._cv_step_size = cv_step_size

        self._country_or_region_for_holidays = None
        if country_or_region_for_holidays is not None:
            self._country_or_region_for_holidays = country_or_region_for_holidays
            if holiday_country is not None:
                self._print_deprecated_neglected_message(
                    TimeSeries.HOLIDAY_COUNTRY, TimeSeries.COUNTRY_OR_REGION_FOR_HOLIDAYS)
        elif holiday_country is not None:
            self._country_or_region_for_holidays = holiday_country
            self._print_deprecated_message(TimeSeries.HOLIDAY_COUNTRY, TimeSeries.COUNTRY_OR_REGION_FOR_HOLIDAYS)

        self._formatted_target_lags = None  # type: Optional[Dict[str, List[Union[int, str]]]]
        self._formatted_id_column_names = None  # type: Optional[List[str]]
        self._formatted_drop_column_names = None  # type: Optional[List[str]]
        self._formatted_group_column_names = None  # type: Optional[List[str]]
        self._short_series_handling_configuration = short_series_handling_configuration  # type: Optional[str]
        self._target_aggregation_function = target_aggregation_function

        # Use property setter to ensure proper handling of None input
        # Mypy does not understand setter call here, so need to ignore the type error
        self.seasonality = seasonality  # type: ignore

        # Deprecation of drop_column_names.
        try:
            drop_column_names = kwargs.pop('drop_column_names')
            logging.warning(
                "Parameter 'drop_column_names' will be deprecated. Please drop columns from your "
                "datasets as part of your data preparation process before providing the datasets to AutoML.")
            self._drop_column_names = drop_column_names
        except KeyError:
            pass

        if validate_parameters:
            self.validate_parameters()
        self._sync_short_series_handling_params()

    def validate_parameters(self):
        """
        Validate the parameters in the ForecastingParameters class.
        """
        self._validate_time_column_name()
        self._validate_time_series_id_column_names()
        self._validate_forecast_horizon()
        self._validate_target_rolling_window_size()
        self._validate_target_lags()
        self._validate_feature_lags()
        self._validate_drop_columns()
        self._validate_freq(self._freq)
        self._validate_seasonality(self._seasonality)
        self._validate_short_series_handling(self._short_series_handling)
        self._validate_short_series_handling_config(self._short_series_handling_configuration)
        self._validate_target_aggregation_fun(self._target_aggregation_function)
        self._validate_cv_step_size()

    @property
    def forecast_horizon(self) -> Union[str, int]:
        """
        The desired maximum forecast horizon in units of time-series frequency. The default value is 1.
        Units are based on the time interval of your training data,
        e.g., monthly, weekly that the forecaster should predict out.
        """
        return self._forecast_horizon

    @forecast_horizon.setter
    def forecast_horizon(self, forecast_horizon: Union[str, int]) -> None:
        self._forecast_horizon = forecast_horizon
        self._validate_forecast_horizon()

    @property
    def formatted_time_series_id_column_names(self) -> Optional[List[str]]:
        """
        The names of columns used to group a timeseries. It can be used to create multiple series.
        If time_series_id_column_names is not defined, the data set is assumed to be one time-series.
        """
        if self._formatted_id_column_names is not None:
            return self._formatted_id_column_names

        self._formatted_id_column_names = self._make_column_names_list(
            self.time_series_id_column_names, use_empty_list=False)
        return self._formatted_id_column_names

    @property
    def time_series_id_column_names(self) -> Union[str, List[str], None]:
        """
        The names of columns used to group a timeseries. It can be used to create multiple series.
        If time_series_id_column_names is not defined, the data set is assumed to be one time-series.
        """
        return self._time_series_id_column_names

    @time_series_id_column_names.setter
    def time_series_id_column_names(self, time_series_id_column_names: Union[str, List[str], None]) -> None:
        self._time_series_id_column_names = time_series_id_column_names
        self._formatted_id_column_names = None
        self._validate_time_series_id_column_names()

    @property
    def time_column_name(self) -> str:
        """
        The name of the time column. This parameter is required when forecasting to specify the datetime
        column in the input data used for building the time series and inferring its frequency.
        """
        return self._time_column_name

    @time_column_name.setter
    def time_column_name(self, time_column_name: str) -> None:
        self._time_column_name = time_column_name
        self._validate_time_column_name()

    @property
    def formatted_target_lags(self) -> Optional[Dict[str, List[Union[int, str]]]]:
        """
        The formatted number of past periods to lag from the target column.
        """
        if self._formatted_target_lags is not None:
            return self._formatted_target_lags

        target_lags = None  # type: Optional[List[Union[int, str]]]

        if isinstance(self._target_lags, int) or isinstance(self._target_lags, list):
            if isinstance(self._target_lags, int):
                target_lags = [self._target_lags]
            else:
                # Get unique values and preserve order for unittests.
                target_lags = sorted(set(self._target_lags))
            if len(target_lags) == 0:
                target_lags = None
        elif self._target_lags == TimeSeries.AUTO:
            target_lags = [TimeSeries.AUTO]
        elif self._target_lags is None:
            target_lags = None

        # Convert target lags to dictionary or None.
        if target_lags is not None:
            lags = {
                TimeSeriesInternal.DUMMY_TARGET_COLUMN: target_lags
            }  # type: Optional[Dict[str, List[Union[int, str]]]]
        else:
            lags = None

        self._formatted_target_lags = lags

        return lags

    @property
    def target_lags(self) -> Union[List[int], int, str, None]:
        """
        The number of past periods to lag from the target column.
        """
        return self._target_lags

    @target_lags.setter
    def target_lags(self, target_lags: Union[List[int], int, str, None]) -> None:
        self._target_lags = target_lags
        self._formatted_target_lags = None
        self._validate_target_lags()

    @property
    def target_rolling_window_size(self) -> Optional[Union[str, int]]:
        return self._target_rolling_window_size

    @target_rolling_window_size.setter
    def target_rolling_window_size(self, target_rolling_window_size: Optional[Union[str, int]]) -> None:
        """The number of past periods used to create a rolling window average of the target column."""
        self._target_rolling_window_size = target_rolling_window_size
        self._validate_target_rolling_window_size()

    @property
    def holiday_country(self) -> Optional[str]:
        """
        The country/region used to generate holiday features.
        These should be ISO 3166 two-letter country/region code, for example 'US' or 'GB'.
        """
        self._print_deprecated_message(TimeSeries.HOLIDAY_COUNTRY, TimeSeries.COUNTRY_OR_REGION_FOR_HOLIDAYS)
        return self._country_or_region_for_holidays

    @property
    def country_or_region_for_holidays(self) -> Optional[str]:
        """
        The country/region used to generate holiday features.
        These should be ISO 3166 two-letter country/region code, for example 'US' or 'GB'.
        """
        return self._country_or_region_for_holidays

    @country_or_region_for_holidays.setter
    def country_or_region_for_holidays(self, country_or_region_for_holidays: Optional[str]) -> None:
        self._country_or_region_for_holidays = country_or_region_for_holidays

    @property
    def feature_lags(self) -> Optional[str]:
        """Flag for generating lags for the numeric features."""
        return self._feature_lags

    @feature_lags.setter
    def feature_lags(self, feature_lags: Optional[str]) -> None:
        self._feature_lags = feature_lags
        self._validate_feature_lags()

    @property
    def use_stl(self) -> Optional[str]:
        """
        Configure STL Decomposition of the time-series target column.
        use_stl can take three values: None (default) - no stl decomposition,
        'season' - only generate season component and season_trend - generate both season and trend components.
        """
        return self._use_stl

    @use_stl.setter
    def use_stl(self, use_stl: Optional[str]) -> None:
        self._use_stl = use_stl

    @property
    def formatted_drop_column_names(self) -> Optional[List[str]]:
        """
        The formatted names of columns to drop for forecasting tasks.
        """
        if self._formatted_drop_column_names is not None:
            return self._formatted_drop_column_names

        self._formatted_drop_column_names = self._make_column_names_list(
            self._drop_column_names, use_empty_list=True)
        return self._formatted_drop_column_names

    @property
    def drop_column_names(self) -> Optional[Union[str, List[str]]]:
        """
        The names of columns to drop for forecasting tasks.
        """
        # Deprecation of drop_column_names
        logging.warning(
            "Property 'drop_column_names' will be deprecated. Please drop columns from your "
            "datasets as part of your data preparation process before providing the datasets to AutoML.")
        return self._drop_column_names

    @drop_column_names.setter
    def drop_column_names(self, drop_column_names: Optional[Union[str, List[str]]]) -> None:
        # Deprecation of drop_column_names.
        logging.warning(
            "Property 'drop_column_names' will be deprecated. Please drop columns from your "
            "datasets as part of your data preparation process before providing the datasets to AutoML.")
        self._drop_column_names = drop_column_names
        self._validate_drop_columns()
        self._formatted_drop_column_names = None

    @property
    def formatted_group_column_names(self) -> Optional[List[str]]:
        if self._formatted_group_column_names is not None:
            return self._formatted_group_column_names

        self._formatted_group_column_names = self._make_column_names_list(
            self._group_column_names, use_empty_list=False)

        return self._formatted_group_column_names

    @property
    def group_column_names(self) -> Optional[Union[str, List[str]]]:
        return self._group_column_names

    @group_column_names.setter
    def group_column_names(self, group_column_names: Optional[Union[str, List[str]]]) -> None:
        self._group_column_names = group_column_names
        self._formatted_group_column_names = None

    @property
    def seasonality(self) -> Union[str, int]:
        """
        Time series seasonality as an integer multiple of the series frequency.
        """
        return self._seasonality

    @seasonality.setter
    def seasonality(self, seasonality: Optional[Union[str, int]]) -> None:
        seas_non_none = seasonality if seasonality is not None else TimeSeriesInternal.SEASONALITY_VALUE_NONSEASONAL
        self._validate_seasonality(seas_non_none)
        self._seasonality = seas_non_none

    @property
    def cv_step_size(self) -> Optional[int]:
        """
        Number of periods between the origin_time of one CV fold and the next fold. For
        example, if `n_step` = 3 for daily data, the origin time for each fold will be
        three days apart.
        """
        return self._cv_step_size

    @cv_step_size.setter
    def cv_step_size(self, cv_step_size: int) -> None:
        self._cv_step_size = cv_step_size
        self._validate_cv_step_size()

    @property
    def dropna(self) -> bool:
        """Configure dropna in timeseries data transformer."""
        return TimeSeriesInternal.DROP_NA_DEFAULT

    @property
    def overwrite_columns(self) -> bool:
        """Configure overwrite_columns in timeseries data transformer."""
        return TimeSeriesInternal.OVERWRITE_COLUMNS_DEFAULT

    @property
    def transform_dictionary(self) -> Dict[str, Any]:
        """Configure transform_dictionary in timeseries data transformer."""
        return TimeSeriesInternal.TRANSFORM_DICT_DEFAULT

    @staticmethod
    def from_parameters_dict(
            parameter_dict: Dict[str, Any],
            validate_params: bool,
            show_deprecate_warnings: Optional[bool] = True
    ) -> 'ForecastingParameters':
        """
        Construct ForecastingParameters class from a dict.

        :param parameter_dict: The dict contains all the forecasting parameters.
        :param validate_params: Whether validate input parameter or not.
        :param show_deprecate_warnings: Switch to show deprecated parameters warning.
        """
        # We will validate the parameters after we will set it.
        forecasting_params = ForecastingParameters(validate_parameters=False)
        for param in TimeSeries.ALL_FORECASTING_PARAMETERS:
            default_value = ForecastingParameters.DEFAULT_TIMESERIES_VALUE.get(param)
            if param in parameter_dict:
                # if any parameter found in deprecated dict, the corresponding new one needs set to be none to bypass
                # the updated one when retrieving that one.
                if param in ForecastingParameters.DEPRECATED_DICT.keys():
                    new_param = ForecastingParameters.DEPRECATED_DICT[param]
                    if new_param in parameter_dict and show_deprecate_warnings:
                        forecasting_params._print_deprecated_neglected_message(param, new_param)
                    else:
                        if show_deprecate_warnings:
                            forecasting_params._print_deprecated_message(param, new_param)
                        setattr(
                            forecasting_params,
                            forecasting_params._get_attribute_name(new_param),
                            parameter_dict.get(param, default_value)
                        )
                else:
                    setattr(
                        forecasting_params,
                        forecasting_params._get_attribute_name(param),
                        parameter_dict.get(param, default_value))

        if validate_params:
            forecasting_params.validate_parameters()

        return forecasting_params

    @property
    def freq(self) -> Optional[str]:
        """The frequency of the data set."""
        return self._freq

    @freq.setter
    def freq(self, val: Optional[str]) -> None:
        """Set the data set frequency"""
        self._validate_freq(val)
        self._freq = val

    @property
    def short_series_handling_configuration(self) -> Optional[str]:
        """Return if short grain should be padded."""
        return self._short_series_handling_configuration

    @short_series_handling_configuration.setter
    def short_series_handling_configuration(self, val: Optional[str]) -> None:
        """Set if short grain should be padded."""
        self._validate_short_series_handling_config(val)
        self._short_series_handling_configuration = val
        if val is not None and not self._short_series_handling:
            warnings.warn(ForecastingParameters._SYNC_WARNING_TEXT)
            logger.warning(ForecastingParameters._SYNC_WARNING_TEXT)
        self._sync_short_series_handling_params()

    @property
    def target_aggregation_function(self) -> Optional[str]:
        """Return the target aggregation function."""
        return self._target_aggregation_function

    @target_aggregation_function.setter
    def target_aggregation_function(self, val: Any) -> None:
        """Set the target aggregation function."""
        self._validate_target_aggregation_fun(val)
        self._target_aggregation_function = val

    def _sync_short_series_handling_params(self) -> None:
        """
        Convert the new string type parameter of short_series_handling_configuration to old short_series_handling.

        If val is invalid i.e. not in ShortSeriesHandlingValues, the _short_series_handling
        will remain unchanged.
        """
        self._short_series_handling, self._short_series_handling_configuration = \
            ForecastingParameters._SHORT_GRAIN_HANDLING_DICT.get(
                (self._short_series_handling, self._short_series_handling_configuration),
                (self._short_series_handling, self._short_series_handling_configuration))

    def _validate_time_column_name(self) -> None:
        if self.time_column_name is None or self.time_column_name == self.EMPTY_TIME_COLUMN_NAME:
            raise ConfigException._with_error(
                AzureMLError.create(
                    ArgumentBlankOrEmpty, target="time_column_name", argument_name="time_column_name",
                    reference_code=ReferenceCodes._FORECASTING_PARAM_TIME_COLUMN_MISSING
                )
            )

    def _validate_time_series_id_column_names(self) -> None:
        id_column_names = self._time_series_id_column_names
        expected_types = ', '.join(["str", "List[str]", "None"])
        if isinstance(id_column_names, list):
            for col in id_column_names:
                self._check_column_name_type(
                    col, TimeSeries.TIME_SERIES_ID_COLUMN_NAMES,
                    expected_types,
                    ReferenceCodes._FORECASTING_PARAM_ID_COL_NAMES_LIST_INVALID_TYPE)
        elif id_column_names is not None:
            self._check_column_name_type(
                id_column_names, TimeSeries.TIME_SERIES_ID_COLUMN_NAMES,
                expected_types,
                ReferenceCodes._FORECASTING_PARAM_ID_COL_NAMES_INVALID_TYPE)

    def _check_column_name_type(
            self, col_name: Any,
            target: str,
            expected_values: str,
            reference_code: str
    ) -> None:
        if not isinstance(col_name, str):
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentType, actual_type=type(col_name),
                    expected_types=expected_values,
                    target=target, argument="time_series_id_column_names ({})".format(str(col_name)),
                    reference_code=reference_code)
            )

    def _validate_target_rolling_window_size(self):
        ForecastingParameters._is_int_or_auto(
            self.target_rolling_window_size, TimeSeries.TARGET_ROLLING_WINDOW_SIZE,
            ReferenceCodes._FORECASTING_PARAM_TARGET_ROLLING_WINDOW_SIZE_INVALID_TYPE)

        if isinstance(self.target_rolling_window_size, int) and self.target_rolling_window_size < 2:
            raise ConfigException._with_error(
                AzureMLError.create(
                    ArgumentOutOfRange, target=TimeSeries.TARGET_ROLLING_WINDOW_SIZE,
                    argument_name=TimeSeries.TARGET_ROLLING_WINDOW_SIZE, min=2, max="inf",
                    reference_code=ReferenceCodes._TARGET_ROLLING_WINDOW_SMALL
                )
            )

    def _validate_target_lags(self) -> None:
        if self._target_lags is None or self._target_lags == TimeSeries.AUTO:
            return
        elif isinstance(self._target_lags, int):
            self._check_target_lags_range(self._target_lags)
        elif isinstance(self._target_lags, list):
            for lag in self._target_lags:
                if not isinstance(lag, int):
                    raise ConfigException._with_error(
                        AzureMLError.create(
                            InvalidArgumentType, target="target_lags", argument="target_lags ({})".format(lag),
                            actual_type=type(lag), expected_types="int",
                            reference_code=ReferenceCodes._FORECASTING_PARAM_TARGET_LAG_LIST_INVALID_TYPE)
                    )
                else:
                    self._check_target_lags_range(lag)
        else:
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentType, target="target_lags", argument="target_lags ({})".format(self._target_lags),
                    actual_type=type(self._target_lags), expected_types=", ".join(
                        ["int", "List[int]", TimeSeries.AUTO]),
                    reference_code=ReferenceCodes._FORECASTING_PARAM_TARGET_LAG_NOT_SUPPORTED)
            )

    def _check_target_lags_range(self, lag: int) -> None:
        if lag < 1 or lag > ForecastingParameters.MAX_LAG_LENGTH:
            raise ConfigException._with_error(
                AzureMLError.create(
                    ArgumentOutOfRange, target=TimeSeries.TARGET_LAGS,
                    argument_name="{} ({})".format(TimeSeries.TARGET_LAGS, lag),
                    min=1, max=ForecastingParameters.MAX_LAG_LENGTH,
                    reference_code=ReferenceCodes._FORECASTING_PARAM_TARGET_LAG_OUT_OF_RANGE
                )
            )

    def _validate_feature_lags(self) -> None:
        permitted_feature_lags_options = [TimeSeries.AUTO, TimeSeriesInternal.FEATURE_LAGS_DEFAULT]
        if self.feature_lags not in permitted_feature_lags_options:
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentWithSupportedValues, target=TimeSeries.FEATURE_LAGS,
                    arguments="{} ({})".format(TimeSeries.FEATURE_LAGS, self.feature_lags),
                    supported_values=", ".join([str(k) for k in permitted_feature_lags_options]),
                    reference_code=ReferenceCodes._FORECASTING_PARAM_FEATURE_LAGS_INVALID_TYPE
                )
            )

    def _validate_forecast_horizon(self) -> None:
        """Validation of the forecast_horizon"""
        ForecastingParameters._is_int_or_auto(
            self.forecast_horizon, TimeSeries.FORECAST_HORIZON,
            ReferenceCodes._FORECASTING_PARAM_HORIZON_INVALID_TYPE, False)
        if not isinstance(self.forecast_horizon, str) and self.forecast_horizon < 1:
            raise ConfigException._with_error(
                AzureMLError.create(
                    ArgumentOutOfRange, target=TimeSeries.FORECAST_HORIZON,
                    argument_name="{} ({})".format(TimeSeries.FORECAST_HORIZON, self.forecast_horizon),
                    min=1, max="inf", reference_code=ReferenceCodes._FORECASTING_HORIZON_INVALID, has_pii=True
                )
            )

    def _validate_freq(self, val: Any) -> None:
        """Validate the data set frequency parameter."""
        if val is not None and not isinstance(val, str):
            raise ConfigException._with_error(
                AzureMLError.create(
                    TimeseriesInvalidDateOffsetType, target=TimeSeries.FREQUENCY,
                    freq_url=TimeSeriesWebLinks.FORECAST_PARAM_DOCS,
                    reference_code=ReferenceCodes._FORECASTING_PARAM_FREQ_TYPE)
            )
        if val is None:
            self._validate_freq_agg(val, self.target_aggregation_function)

    def _validate_seasonality(self, val: Any) -> None:
        """Validate the seasonality parameter."""
        ForecastingParameters._is_int_or_auto(
            val, TimeSeries.SEASONALITY,
            ReferenceCodes._FORECASTING_PARAM_SEASONALITY_INVALID_TYPE, False)
        if isinstance(val, int) and val < 1:
            raise ConfigException._with_error(
                AzureMLError.create(
                    ArgumentOutOfRange, target=TimeSeries.SEASONALITY,
                    argument_name="{} ({})".format(TimeSeries.SEASONALITY, val),
                    min=1, max="inf", reference_code=ReferenceCodes._FORECASTING_PARAM_SEASONALITY_OUT_OF_RANGE,
                    has_pii=True
                )
            )

    def _validate_short_series_handling(self, val: Any) -> None:
        """
        Validate the type of short_series_handling.

        :param val: The value to be checked.
        :raises: ConfigException
        """
        if not isinstance(val, bool):
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentType, target=TimeSeries.SHORT_SERIES_HANDLING,
                    argument=TimeSeries.SHORT_SERIES_HANDLING,
                    actual_type=type(val),
                    expected_types='bool',
                    reference_code=ReferenceCodes._FORECASTING_PARAM_SHORT_GRAIN_HANDLING_INVALID)
            )

    def _validate_short_series_handling_config(self, val: Any) -> None:
        """
        Validate the value for the short grain padding.

        :param val: The value for the short_series_padding.
        :raises: ConfigException
        """
        self._validate_set_of_values_or_none(
            val,
            ShortSeriesHandlingValues.ALL,
            TimeSeries.SHORT_SERIES_HANDLING_CONFIG,
            ReferenceCodes._FORECASTING_PARAM_SHORT_GRAIN_CFG_INVALID
        )

    def _validate_drop_columns(self) -> None:
        """Validate drop columns in forecasting parameters."""
        expected_type_name = "str, List[str], None"
        is_invalid_type = False
        reference_code = None
        if self._drop_column_names is None:
            return
        if isinstance(self._drop_column_names, list):
            for val in self._drop_column_names:
                if not isinstance(val, str):
                    is_invalid_type = True
                    reference_code = ReferenceCodes._FORECASTING_PARAM_DROP_COLUMN_NOT_STR_LIST
                    break
        else:
            if not isinstance(self._drop_column_names, str):
                is_invalid_type = True
                reference_code = ReferenceCodes._FORECASTING_PARAM_DROP_COLUMN_NOT_STR
        if is_invalid_type:
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentType, target=TimeSeries.DROP_COLUMN_NAMES, reference_code=reference_code,
                    argument="{} ({})".format(TimeSeries.DROP_COLUMN_NAMES, self._drop_column_names),
                    actual_type=type(self._drop_column_names),
                    expected_types=expected_type_name))

    def _validate_target_aggregation_fun(self, val: Any) -> None:
        """Validate the target aggregation function literal."""
        self._validate_set_of_values_or_none(
            val,
            AggregationFunctions.ALL,
            TimeSeries.TARGET_AGG_FUN,
            ReferenceCodes._FORECASTING_PARAM_AGG_FUN
        )
        self._validate_freq_agg(self.freq, val)

    def _validate_freq_agg(self, freq: Optional[str],
                           target_aggregation_function: Optional[str]) -> None:
        """
        Validate the combination of freq and target_aggregation_function.

        :param freq: the value of freq parameter.
        :param target_aggregation_function:  the value of target_aggregation_function parameter
        :raises: ConfigException if target aggregation function is set,
                 but the freq is not.
        """
        if target_aggregation_function is not None and freq is None:
            raise ConfigException._with_error(
                AzureMLError.create(
                    TimeseriesAggNoFreq, target='aggregation_freq',
                    reference_code=ReferenceCodes._TS_AGG_WITHOUT_FREQ)
            )

    def _validate_cv_step_size(self) -> None:
        """Validation of the cross validation step size"""
        if self._cv_step_size is None:
            return
        elif isinstance(self._cv_step_size, int):
            if self._cv_step_size < 1:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        ArgumentOutOfRange, target=TimeSeries.CV_STEP_SIZE,
                        argument_name="{}".format(TimeSeries.CV_STEP_SIZE),
                        min=1, max="inf", reference_code=ReferenceCodes._FORECASTING_PARAM_CV_STEP_SIZE_OUT_OF_RANGE,
                        has_pii=True
                    )
                )
        else:
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentType, target=TimeSeries.CV_STEP_SIZE,
                    argument="{} ({})".format(TimeSeries.CV_STEP_SIZE, self._cv_step_size),
                    actual_type=type(self._cv_step_size),
                    expected_types='int',
                    reference_code=ReferenceCodes._FORECASTING_PARAM_CV_STEP_SIZE_INVALID_TYPE)
            )

    def _validate_set_of_values_or_none(
            self, val: Any, allowed_values: List[Any],
            parameter: str, ref_code: str,
            allow_nan: bool = True) -> None:
        """
        Test that parameter is within correct values set.

        :param val: The value to be validated.
        :param allowed_values: The list of allowed parameters.
        :param parameter: The name of a parameter, which should be checked.
        :param ref_code: The reference code to be given to the exception
                         if the val has non applicable value.
        """
        if val is not None and val not in allowed_values:
            possible_values = ", ".join(allowed_values)
            if allow_nan:
                possible_values += ' and None'
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidParameterSelection, target=parameter,
                    parameter=parameter,
                    values=possible_values,
                    reference_code=ref_code)
            )

    def _print_deprecated_message(self, old_parameter_name, new_parameter_name):
        msg = "Forecasting parameter {} will be deprecated in the future, " \
              "please use {} instead.".format(old_parameter_name, new_parameter_name)
        logging.warning(msg)
        logger.warning(msg)

    def _print_deprecated_neglected_message(self, old_parameter_name, new_parameter_name):
        msg = "Both forecasting parameter {} and {} are found from input. " \
              "The deprecated one {} " \
              "will be neglected.".format(old_parameter_name, new_parameter_name, old_parameter_name)
        logging.warning(msg)
        logger.warning(msg)

    def _set_default_value(self) -> None:
        for param in ForecastingParameters.DEFAULT_TIMESERIES_VALUE:
            if getattr(self, self._get_attribute_name(param), None) is None:
                setattr(self, self._get_attribute_name(param),
                        ForecastingParameters.DEFAULT_TIMESERIES_VALUE.get(param))

    def _get_attribute_name(self, forecasting_parameter_name: str) -> str:
        return "_" + forecasting_parameter_name

    def _make_column_names_list(
            self,
            column_names: Union[str, List[str], None],
            use_empty_list: Optional[bool] = False
    ) -> Optional[List[str]]:
        if column_names is None:
            return None if not use_empty_list else list()
        elif isinstance(column_names, list):
            if len(column_names) == 0 and not use_empty_list:
                return None
            return column_names
        else:
            return [column_names]

    @staticmethod
    def _is_int_or_auto(val: Optional[Any], val_name: str, reference_code: str, allow_none: bool = True) -> None:
        """
        Raise a ConfigException if value is not 'auto' or integer.

        :param val: The value to test.
        :param val_name: the name of a value to be displayed in the error message.
        :param allow_none: if true, the None value is allowed for val.
        :raises: ConfigException
        """
        if allow_none and val is None:
            return
        if not isinstance(val, int) and val != TimeSeries.AUTO:
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentType, target=val_name, reference_code=reference_code,
                    argument="{} ({})".format(val_name, val), actual_type=type(val),
                    expected_types=", ".join(['int', TimeSeries.AUTO]))
            )
