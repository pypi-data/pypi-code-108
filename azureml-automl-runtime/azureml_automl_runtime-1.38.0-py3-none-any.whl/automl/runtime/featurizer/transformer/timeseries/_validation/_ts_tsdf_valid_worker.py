# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Classes for TimeseriesDataFrameValidationWorker."""
import logging
from typing import Dict, cast, List, Optional, Set

import pandas as pd
from azureml._common._error_definition import AzureMLError
from azureml._common._error_definition.user_error import ArgumentOutOfRange
from azureml.automl.core.automl_base_settings import AutoMLBaseSettings
from azureml.automl.core.shared import constants
from azureml.automl.core.shared import utilities
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    TimeseriesInvalidTimestamp,
    TimeseriesDfFrequencyNotConsistentGrain,
    TimeseriesDfCannotInferFrequencyFromTSId,
    TimeseriesDfFrequencyGenericError,
    TimeseriesDfMultiFrequenciesDiff,
    TimeseriesDfUniqueTargetValueGrain,
    TimeseriesMaxHorizonWithTimeColumnValueOutOfRange,
    TimeseriesDfFrequencyChanged,
    TimeseriesDfTrainingValidDataNotContiguous,
    TimeseriesInsufficientData,
    TimeseriesGrainAbsentValidateTrainValidData)
from azureml.automl.core.shared.constants import (
    ShortSeriesHandlingValues,
    TimeSeries,
    TimeSeriesInternal,
    TimeSeriesWebLinks,
)
from azureml.automl.core.shared.exceptions import DataException, ValidationException
from azureml.automl.core.shared.forecasting_exception import ForecastingDataException
from azureml.automl.core.shared.logging_utilities import function_debug_log_wrapped
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared.types import GrainType
from pandas.tseries.frequencies import to_offset

from azureml.automl.runtime.featurizer.transformer.timeseries import timeseries_transformer
from azureml.automl.runtime.shared.time_series_data_frame import TimeSeriesDataFrame, construct_tsdf
from azureml.automl.runtime.shared.types import DataInputType
from ._timeseries_validator import TimeseriesValidationParamName
from ._timeseries_validator import TimeseriesValidationParameter
from ._timeseries_validator import TimeseriesValidationWorkerBase


class TimeseriesDataFrameValidationWorker(TimeseriesValidationWorkerBase):
    """Validation worker for the generated tsdf after the post auto parameter gen."""

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
        min_points = param.params[TimeseriesValidationParamName.MIN_POINTS]

        lags = param.params[TimeseriesValidationParamName.LAGS]
        window_size = param.params[TimeseriesValidationParamName.WINDOW_SIZE]
        forecast_horizon = param.params[TimeseriesValidationParamName.FORECAST_HORIZON]

        tsdf = TimeseriesDataFrameValidationWorker._get_and_validate_tsdf(
            X, y, automl_settings, forecast_horizon, min_points, is_validation_data=False)
        tsdf_valid = None
        if X_valid is not None:
            tsdf_valid = TimeseriesDataFrameValidationWorker._get_and_validate_tsdf(
                X_valid,
                y_valid,
                automl_settings,
                forecast_horizon,
                min_points=0,
                is_validation_data=True)
            TimeseriesDataFrameValidationWorker._validate_timeseries_train_valid_tsdf(
                tsdf, tsdf_valid, bool(window_size + max(lags)))

    @staticmethod
    def _get_and_validate_tsdf(
            X: pd.DataFrame,
            y: DataInputType,
            automl_settings: AutoMLBaseSettings,
            forecast_horizon: int,
            min_points: int = 0,
            is_validation_data: bool = False
    ) -> TimeSeriesDataFrame:
        """
        Generate the TimeSeriesDataFrame and run validations on it.

        :param X: The data frame with features.
        :param y: The array with targets/labels.
        :param automl_settings: The settings to be used.
        :param forecast_horizon : The max horizon used (after the heuristics were applied).
        :param min_points: The minimal number of points necessary to train the model.
        :param is_validation_data: True if this is a validation data set.
        :return: TimeSeriesDataFrame with the data from the X and y.

        """
        # We cast timeseries_param_dict to dictionary, because we have already checked that it is not None
        # before in the _check_timeseries_input method.
        timeseries_param_dict = cast(Dict[str, str], utilities._get_ts_params_dict(automl_settings))
        grains = timeseries_param_dict.get(TimeSeries.GRAIN_COLUMN_NAMES)
        if grains is None:
            grains = [TimeSeriesInternal.DUMMY_GRAIN_COLUMN]  # type: ignore
        if isinstance(grains, str):
            grains = [grains]  # type: ignore
        tsdf = construct_tsdf(
            X,
            y,
            TimeSeriesInternal.DUMMY_TARGET_COLUMN,
            timeseries_param_dict.get(TimeSeries.TIME_COLUMN_NAME),  # type: ignore
            timeseries_param_dict.get(
                TimeSeriesInternal.ORIGIN_TIME_COLUMN_NAME,
                TimeSeriesInternal.ORIGIN_TIME_COLNAME_DEFAULT),
            grains,  # type: ignore
            timeseries_transformer.get_boolean_col_names(X)
        )
        tsdf.sort_index(inplace=True)
        frequencies_grain_names = {}  # type: Dict[pd.DateOffset, List[GrainType]]
        short_grains = set()
        if automl_settings.grain_column_names is not None:
            # to deal the problem that user has no input grain
            try:
                freq_by_grain = None  # type: pd.Series
                if automl_settings.freq is None:
                    freq_by_grain = tsdf.infer_freq_by_grain()
                for data_tuple in tsdf.groupby_grain():
                    grain_name_str = data_tuple[0]
                    tsdf_grain = data_tuple[1]
                    data_points = tsdf_grain.shape[0]

                    if not is_validation_data or tsdf_grain.shape[0] > 1:
                        # if validation data is only one data point, no need to check freq.
                        # If frequency is provided, check if it is consistent.
                        if automl_settings.freq is None:
                            freq = freq_by_grain[grain_name_str]
                        else:
                            freq = to_offset(automl_settings.freq)
                        if tsdf_grain.shape[0] != 1:
                            # We can not establish the frequency only if tsdf_grain has only one value.
                            if freq is None:
                                raise ForecastingDataException._with_error(
                                    AzureMLError.create(
                                        TimeseriesDfCannotInferFrequencyFromTSId, target='tsdf_grain',
                                        reference_code=ReferenceCodes._TSDF_CANNOT_INFER_FREQ_FROM_TS_ID,
                                        grain_name_str=grain_name_str)
                                )
                            # Check alignment with the inferred frequency
                            TimeseriesDataFrameValidationWorker._check_timeseries_alignment_single_grain(
                                grain_name_str, tsdf_grain, freq)

                            if freq in frequencies_grain_names:
                                frequencies_grain_names[freq].append(grain_name_str)
                            else:
                                frequencies_grain_names[freq] = [grain_name_str]
                        # check min data points for train and forecast_horizon  for validation
                        data_points = tsdf_grain.ts_value.count()
                        if not is_validation_data:
                            if data_points < min_points:
                                short_grains.add(grain_name_str)
                            TimeseriesDataFrameValidationWorker._check_grain_min_points(
                                data_points, min_points, automl_settings, grain_name=grain_name_str)
                            if tsdf_grain.shape[0] != 1:
                                TimeseriesDataFrameValidationWorker._check_cv_gap_exist(
                                    tsdf_grain,
                                    forecast_horizon,
                                    automl_settings.n_cross_validations,
                                    grain_name_str, freq)
                            # check if individual grain has more than 1 unique observation
                            if (not automl_settings.short_series_handling or grain_name_str not in short_grains) and \
                                    (tsdf_grain.ts_value.nunique(dropna=True) <= 1):
                                raise ForecastingDataException._with_error(
                                    AzureMLError.create(
                                        TimeseriesDfUniqueTargetValueGrain,
                                        target="grain_target",
                                        grain=grain_name_str,
                                        reference_code=ReferenceCodes._TSDF_UNIQUE_VALUE_IN_GRAIN)
                                )

                    if is_validation_data:
                        if data_points < forecast_horizon:
                            print(("WARNING: Validation set has fewer data points ({}) "
                                   "than forecast_horizon  ({}) for one of time series identifiers. "
                                   "We will be unable to estimate error and predictive quantiles at some horizons. "
                                   "Please consider increasing the validation data to the length of max horizon.").
                                  format(data_points, forecast_horizon))
                        elif data_points > forecast_horizon:
                            print(("WARNING: Validation set has more data points {} "
                                   "than forecast_horizon  {} for one of time series identifiers. "
                                   "Not all validation data will be used in the training. "
                                   "Please consider decreasing the validation data to the length of max horizon.").
                                  format(data_points, forecast_horizon))

            except DataException:
                # If we already have a descriptive Exception, raise it.
                raise
            except Exception as me:
                # If not, raise generic exception.
                raise ForecastingDataException._with_error(
                    AzureMLError.create(
                        TimeseriesDfFrequencyGenericError, target='ts_freq_generic',
                        reference_code=ReferenceCodes._TSDF_FREQUENCY_GENERIC_ERROR
                    ), inner_exception=me
                ) from me

            TimeseriesDataFrameValidationWorker._check_tsdf_frequencies(frequencies_grain_names, short_grains)

        # check all the tsdf at the end.
        if not is_validation_data:
            if automl_settings.freq is None:
                tsdf_freq = tsdf.infer_freq()
            else:
                tsdf_freq = to_offset(automl_settings.freq)
            number_of_data_points = tsdf.ts_value.count()
            TimeseriesDataFrameValidationWorker._check_grain_min_points(number_of_data_points, min_points,
                                                                        automl_settings)
            TimeseriesDataFrameValidationWorker._check_cv_gap_exist(tsdf, forecast_horizon,
                                                                    automl_settings.n_cross_validations,
                                                                    freq=tsdf_freq)
        return tsdf

    @staticmethod
    def _validate_timeseries_train_valid_tsdf(tsdf_train: TimeSeriesDataFrame,
                                              tsdf_valid: TimeSeriesDataFrame,
                                              has_lookback_features: bool) -> None:
        """
        Validate train-valid pair in the time series task.

        :param tsdf_train: The training data set.
        :param tsdf_valid: The validation data set.
        :param has_lookback_features: True if rolling window or lag lead is switched on.
        """
        train_grain_data_dict = {grain: tsdf for grain, tsdf in tsdf_train.groupby_grain()}
        valid_grain_data_dict = {grain: tsdf for grain, tsdf in tsdf_valid.groupby_grain()}
        train_grain = set(train_grain_data_dict.keys())
        valid_grain = set(valid_grain_data_dict.keys())
        # check grain is the same for train and valid.
        grain_difference = train_grain.symmetric_difference(valid_grain)
        if len(grain_difference) > 0:
            grain_in_train_not_in_valid = train_grain.intersection(grain_difference)
            grain_in_valid_not_in_train = valid_grain.intersection(grain_difference)
            if len(grain_in_train_not_in_valid) > 0:
                grains = ",".join(["[{}]".format(grain) for grain in grain_in_train_not_in_valid])
                dataset_contain = "training"
                dataset_not_contain = "validation"
            if len(grain_in_valid_not_in_train) > 0:
                grains = ",".join(["[{}]".format(grain) for grain in grain_in_valid_not_in_train])
                dataset_contain = "validation"
                dataset_not_contain = "training"
            raise ForecastingDataException._with_error(
                AzureMLError.create(TimeseriesGrainAbsentValidateTrainValidData, target='grain_difference',
                                    reference_code=ReferenceCodes._TS_GRAIN_ABSENT_VALIDATE_TRAIN_VALID,
                                    grains=grains,
                                    dataset_contain=dataset_contain,
                                    dataset_not_contain=dataset_not_contain)
            )
        # check per grain contiguous and frequency.
        for grain, tsdf in train_grain_data_dict.items():
            tsdf_valid = valid_grain_data_dict[grain]
            train_freq = tsdf.infer_freq()
            if train_freq is None:
                # The only reason we cannot determine the frequency is because we have a grain'
                # with one value, or two values, one of which is pd.NaT.
                # In this case we have a short grain, which should be dropped, or we should raise the exception later.
                continue
            if has_lookback_features and tsdf.time_index.max() + tsdf.infer_freq() != tsdf_valid.time_index.min():
                raise ForecastingDataException._with_error(
                    AzureMLError.create(TimeseriesDfTrainingValidDataNotContiguous, target='tsdf_valid',
                                        reference_code=ReferenceCodes._TSDF_TRAINING_VALID_DATA_NOT_CONTIGUOUS,
                                        grain=str(grain))
                )
            if tsdf_valid.shape[0] > 1:
                valid_freq = tsdf_valid.infer_freq()
                if train_freq != valid_freq:
                    raise ForecastingDataException._with_error(
                        AzureMLError.create(TimeseriesDfFrequencyChanged, target='train_freq',
                                            reference_code=ReferenceCodes._TSDF_FREQUENCY_CHANGED,
                                            grain=str(grain),
                                            train_freq=train_freq,
                                            valid_freq=valid_freq)
                    )

    @staticmethod
    def _check_grain_min_points(number_of_data_points: int,
                                min_points: int,
                                automl_settings: AutoMLBaseSettings,
                                grain_name: Optional[GrainType] = None) -> None:
        """
        Check if each of the grain(series) contains minimal number of the data points.

        :param number_of_data_points: The number of data points in one grain.
        :param min_points: The minimal number of points required for training.
        :param automl_settings: The autoML settings.
        :param grain_name: The name of a grain being checked.
        :raises: DataException
        """
        # First check if we have the short series handling configuration and then fall back
        # to the legacy mechanism.
        has_config = hasattr(automl_settings,
                             TimeSeries.SHORT_SERIES_HANDLING_CONFIG)
        config_val = automl_settings.short_series_handling_configuration if has_config else None
        if (has_config
                and config_val == ShortSeriesHandlingValues.SHORT_SERIES_HANDLING_AUTO
                or config_val == ShortSeriesHandlingValues.SHORT_SERIES_HANDLING_DROP):
            # If we are going to remove short series, do not validate for it.
            # If all series are too short, grain dropper will throw an error.
            return
        if (not has_config
                and hasattr(automl_settings, TimeSeries.SHORT_SERIES_HANDLING)
                and getattr(automl_settings, TimeSeries.SHORT_SERIES_HANDLING)):
            # If we are going to remove short series, do not validate for it.
            # If all series are too short, grain dropper will throw an error.
            return

        if number_of_data_points < min_points:
            window_size = automl_settings.window_size if automl_settings.window_size is not None else 0
            lags = automl_settings.lags[constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN] \
                if automl_settings.lags is not None else 0
            if grain_name is None:
                raise DataException._with_error(AzureMLError.create(
                    TimeseriesInsufficientData, target="X", grains=grain_name,
                    num_cv=automl_settings.n_cross_validations,
                    max_horizon=automl_settings.max_horizon, lags=str(lags), window_size=window_size,
                    cv_step_size=automl_settings.cv_step_size)
                )
            if not isinstance(grain_name, list) and not isinstance(grain_name, tuple):
                grain_name = [grain_name]

            raise DataException._with_error(AzureMLError.create(
                TimeseriesInsufficientData, target="X", grains=str(grain_name),
                num_cv=automl_settings.n_cross_validations, max_horizon=automl_settings.max_horizon, lags=str(lags),
                window_size=window_size, cv_step_size=automl_settings.cv_step_size)
            )

    @staticmethod
    def _check_timeseries_alignment_single_grain(grain_level: GrainType, tsdf: TimeSeriesDataFrame,
                                                 freq: pd.DateOffset) -> None:
        """
        Check if single timeseries (single grain) is aligned to the given frequency.

        :param grain_level: The name of a grain.
        :param tsdf: The time series dataframe to be tested.
        :param freq: Frequency to check alignment against.
        """
        time_index = tsdf.time_index
        if not isinstance(time_index[0], pd.Timestamp):
            raise ValidationException._with_error(AzureMLError.create(TimeseriesInvalidTimestamp, target="X"))

        onfreq_time = pd.date_range(start=time_index.min(), end=time_index.max(), freq=freq)
        if not set(time_index).issubset(onfreq_time):
            raise ForecastingDataException._with_error(
                AzureMLError.create(TimeseriesDfFrequencyNotConsistentGrain,
                                    target='_check_timeseries_alignment_single_grain.time_index',
                                    reference_code=ReferenceCodes._TSDF_FREQUENCY_NOT_CONSISTENT_SINGLE_GRAIN,
                                    grain_level=str(grain_level),
                                    freq=str(freq),
                                    forecasting_config=TimeSeriesWebLinks.FORECAST_CONFIG_DOC))

    @staticmethod
    def _check_cv_gap_exist(tsdf: TimeSeriesDataFrame,
                            max_horizon: int,
                            n_cross_validations: Optional[int] = None,
                            grain_name: Optional[str] = None,
                            freq: Optional[pd.DateOffset] = None) -> None:
        """
        Check if one of the cross validation splits lacks the data.

        :param tsdf: One grain of a time series data frame.
        :param max_horizon: The maximal horizon, used for prediction.
        :param n_cross_validations: The number of cross validations.
        :param grain_name: The grain being analyzed if any.
        :param freq: The frequency of the data in the time series data frame.
        """
        if n_cross_validations is not None:
            if freq is None:
                freq = tsdf.infer_freq()
            for i in range(n_cross_validations):
                # In this code we are estimating the number of missing values in the cross
                # validation fold.
                # if this amount is bigger then some arbitrary number, currently 25%
                # the validation is considered to be failed.
                max_time = tsdf.time_index.max()
                # pandas bug: https://github.com/pandas-dev/pandas/issues/33683
                # may result in weird behavior when freq * 0 is applied. For that reason,
                # end time will have special handling. Start time will always have multiplier
                # of at least one since max_horizon must be >= 1
                end_time = max_time if i != 0 else max_time - i * freq
                try:
                    expected_dates = pd.date_range(start=max_time - (i + max_horizon) * freq,
                                                   end=end_time,
                                                   freq=freq)
                except pd.errors.OutOfBoundsDatetime as e:
                    raise ForecastingDataException._with_error(
                        AzureMLError.create(
                            TimeseriesMaxHorizonWithTimeColumnValueOutOfRange,
                            target="max_horizon",
                            max_horizon=str(max_horizon),
                            reference_code=ReferenceCodes._FORECASTING_HORIZON_INVALID_WITH_TIMECOLUMN_VALUES,
                            inner_exception=e
                        )
                    ) from e
                # Compare the expected dates with the real dates.
                missing_dates = sorted([str(val) for val in set(expected_dates).difference(set(tsdf.time_index))])
                n_absent_in_cv = len(missing_dates)
                # Currently we have commented out the exceptions, because the check is strict.
                # In future we want to replace the exceptions by guard rails.
                if n_absent_in_cv == max_horizon:
                    missing_dates_str = ", ".join(missing_dates)
                    if grain_name is None:
                        exception_msg = (
                            "Missing timestamp(s) {} in data. "
                            "One of the validation folds will be empty "
                            "because the data at the end of time series are missing")
                        exception_msg = exception_msg.format(missing_dates_str)
                        # deEx = DataException(
                        #    exception_msg.format(missing_dates_str)).with_generic_msg(
                        #        exception_msg.format(MASKED))
                    else:
                        exception_msg = ("Missing timestamp(s) {} in data in series {}. "
                                         "One of the validation folds will be empty "
                                         "because the data at the end of time series are missing")
                        exception_msg = exception_msg.format(missing_dates_str, grain_name)
                        # deEx = DataException(
                        #    exception_msg.format(missing_dates_str, grain_name)).with_generic_msg(
                        #        exception_msg.format(MASKED, MASKED))
                    # raise deEx
                    # Warning is commented, because the warning text may be logged.
                    # warnings.warn(exception_msg)

    @staticmethod
    def _check_tsdf_frequencies(frequencies_grain_names: Dict[pd.DateOffset, List[GrainType]],
                                short_grains: Set[GrainType]) -> None:
        """
        Check if all series in the training set have only one frequency.

        :param frequencies_grain_names: The dictionary, containing frequencies and grain names.
        :param short_grains: The grains, which should not be used in this analysis as they
                             will be dropped.
        """
        # pd.DateOffset can not compare directly. need a start time.
        if len(frequencies_grain_names) == 0:
            return
        date_offsets = set()
        for k, v in frequencies_grain_names.items():
            if len(set(v) - short_grains) > 0:
                date_offsets.add(k)
        if len(date_offsets) > 1:
            raise ForecastingDataException._with_error(
                AzureMLError.create(TimeseriesDfMultiFrequenciesDiff, target='date_offsets',
                                    reference_code=ReferenceCodes._TSDF_MULTI_FREQUENCIES_DIFF)
            )
