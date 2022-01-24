# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import copy
from typing import Any, Dict, Tuple, cast

import pandas as pd
from azureml.automl.core.constants import FeatureType
from azureml.automl.core.featurization import FeaturizationConfig
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.constants import TimeSeriesInternal
from azureml.automl.core.shared.types import GrainType
from azureml.train.automl._azureautomlsettings import AzureAutoMLSettings
from azureml.train.automl.runtime._worker_initiator import EXPERIMENT_STATE_PLUGIN
from azureml.train.automl.runtime._partitioned_dataset_utils import _get_dataset_for_grain
from distributed import get_worker

from azureml.automl.runtime._data_definition import RawExperimentData
from azureml.automl.runtime._freq_aggregator import _aggregate_one_grain, _get_mode_col_name
from azureml.automl.runtime._ml_engine import timeseries_ml_engine
from azureml.automl.runtime._time_series_data_config import TimeSeriesDataConfig
from azureml.automl.runtime.frequency_fixer import _correct_start_time, convert_to_datetime, fix_frequency_one_grain
from azureml.automl.runtime.short_grain_padding import _pad_one_grain


class GrainPreprocessResult:
    def __init__(
        self,
        is_aggregated: bool,
        is_padded: bool,
        is_frequency_fixed: bool,
        name: GrainType
    ):
        self.is_aggregated = is_aggregated
        self.is_padded = is_padded
        self.is_frequency_fixed = is_frequency_fixed
        self.name = name


def _preprocess_grain(
    X: pd.DataFrame,
    grain_key_values: Dict[str, Any],
    new_frequency: pd.offsets,
    max_horizon: int,
    start_time: pd.Timestamp,
    min_points_per_grain: int,
    automl_settings: AzureAutoMLSettings,
    should_aggregate: bool,
    should_pad: bool
) -> Tuple[pd.DataFrame, pd.DataFrame, GrainPreprocessResult]:
    """
    preprocess includes 3 steps
    1. preparation
    2. splitting
    3. validation
    """
    prepared_grain_data, grain_preprocess_result = _prepare_grain(
        X,
        grain_key_values,
        automl_settings,
        should_aggregate,
        should_pad,
        new_frequency,
        start_time,
        min_points_per_grain
    )
    grain_train_data, grain_validation_data = _split_grain(prepared_grain_data, max_horizon, automl_settings)
    automl_settings_for_validation = copy.deepcopy(automl_settings)
    if should_aggregate:
        # reset the featurization config in cases of aggregation VSO: 1326498
        automl_settings_for_validation.featurization = FeaturizationConfig().__dict__

    _validate_grain(grain_train_data, grain_validation_data, automl_settings_for_validation)
    return grain_train_data, grain_validation_data, grain_preprocess_result


def _validate_grain_by_dataset(grain_keys_values: Dict[str, Any]) -> None:
    worker = get_worker()
    experiment_state_plugin = worker.plugins[EXPERIMENT_STATE_PLUGIN]

    training_dataset_for_grain = _get_dataset_for_grain(grain_keys_values, experiment_state_plugin.training_dataset)
    valid_dataset_for_grain = _get_dataset_for_grain(grain_keys_values, experiment_state_plugin.validation_dataset)

    _validate_grain(training_dataset_for_grain.to_pandas_dataframe(),
                    valid_dataset_for_grain.to_pandas_dataframe(),
                    experiment_state_plugin.automl_settings)


def _validate_grain(grain_train_data: pd.DataFrame,
                    grain_validation_data: pd.DataFrame,
                    automl_settings: AzureAutoMLSettings) -> None:

    grain_train_X = grain_train_data.copy(deep=True)
    grain_train_y = grain_train_X.pop(automl_settings.label_column_name).values

    grain_validation_X = grain_validation_data.copy(deep=True)
    grain_validation_y = grain_validation_X.pop(automl_settings.label_column_name).values

    raw_experiment_Data = RawExperimentData(X=grain_train_X,
                                            y=grain_train_y,
                                            X_valid=grain_validation_X,
                                            y_valid=grain_validation_y)
    timeseries_ml_engine.validate_timeseries(raw_experiment_Data, automl_settings)


def _split_grain(grain_data: pd.DataFrame,
                 max_horizon: int,
                 automl_settings: AzureAutoMLSettings) -> Tuple[pd.DataFrame, pd.DataFrame]:

    grain_data[automl_settings.time_column_name] = pd.to_datetime(grain_data[automl_settings.time_column_name])
    grain_data.sort_values(by=automl_settings.time_column_name, inplace=True)
    grain_train_data = grain_data.head(len(grain_data) - max_horizon)
    grain_validation_data = grain_data.tail(max_horizon)
    return grain_train_data, grain_validation_data


def _prepare_grain(
    X: pd.DataFrame,
    grain_key_values: Dict[str, Any],
    automl_settings: AzureAutoMLSettings,
    should_aggregate: bool,
    should_pad: bool,
    new_frequency: pd.offsets,
    start_time: pd.Timestamp,
    min_points_per_grain: int
) -> Tuple[pd.DataFrame, GrainPreprocessResult]:
    """
    Preparation includes 3 kinds of data mutations, each being optional
    1. Fixing non compliant points
    2. Aggregate
    3. Pad short grains
    #1 and #2 are mutually exclusive
    """
    # Check if aggregation enabled
    # if yes, do agg
    # if no, fix
    y_grain = X[automl_settings.label_column_name].values
    X_grain_no_target = X.copy(deep=True)
    X_grain_no_target.pop(automl_settings.label_column_name)
    ts_config = TimeSeriesDataConfig.from_settings(X_grain_no_target, y_grain, automl_settings)

    is_aggregated = False
    is_padded = False
    is_frequency_fixed = False

    grains = cast(GrainType, tuple([key for _, key in grain_key_values.items()]))
    if should_aggregate:
        # If we are here we must have an aggregation funciton
        Contract.assert_value(ts_config.target_aggregation_function, "target_aggregation_function")
        df = _aggregate_grain(ts_config.data_x, ts_config, grains)
        is_aggregated = df.shape[0] != ts_config.data_x.shape[0]

        # we must renamed the resulting dataframe's target column back to the original name.
        df.rename({TimeSeriesInternal.DUMMY_TARGET_COLUMN: automl_settings.label_column_name}, axis=1, inplace=True)
    else:
        df = _fix_frequency(X, automl_settings.time_column_name, new_frequency, start_time)
        is_frequency_fixed = df.shape[0] != X.shape[0]

    if should_pad:
        featurization_config = ts_config.featurization
        column_purposes = featurization_config.column_purposes or {}
        numeric_columns = set(
            col_name for col_name, purpose in column_purposes.items() if purpose == FeatureType.Numeric
        )
        df, is_padded = _pad_grain(df, grains, new_frequency, min_points_per_grain, numeric_columns, automl_settings)
    else:
        is_padded = False
    friendly_grains = TimeSeriesInternal.USER_FRIENDLY_DEFAULT_GRAIN \
        if grains[0] == TimeSeriesInternal.DUMMY_GRAIN_COLUMN else grains
    return df, GrainPreprocessResult(is_aggregated, is_padded, is_frequency_fixed, friendly_grains)


def _pad_grain(df, grains, freq, min_points_per_grain, numeric_columns, automl_settings):
    df_padded = _pad_one_grain(
        df,
        freq,
        min_points_per_grain,
        numeric_columns,
        automl_settings.time_column_name,
        automl_settings.grain_column_names,
        grains
    )

    return df_padded, len(df_padded) > len(df)


def _fix_frequency(
    X: pd.DataFrame,
    time_column_name: str,
    new_frequency: pd.offsets,
    start_time: pd.Timestamp
) -> pd.DataFrame:
    X = convert_to_datetime(X, time_column_name)
    start_time_corrected = _correct_start_time(X, time_column_name, start_time, new_frequency)
    return fix_frequency_one_grain(X, new_frequency, start_time_corrected, time_column_name)


def _aggregate_grain(
    X_one: pd.DataFrame,
    time_series_config: TimeSeriesDataConfig,
    time_series_ids: GrainType
) -> pd.DataFrame:
    # TODO: This should be done in a more global place
    X_one.dropna(subset=[time_series_config.time_column_name], inplace=True)
    if X_one.shape[0] == 0:
        # TODO: we really don't need this check here if na time cols are already dropped.
        return pd.DataFrame()

    X_one[TimeSeriesInternal.DUMMY_ORDER_COLUMN] = 1
    # ######## This section only applies at inference time ##############
    # TODO: should we keep this and secion below?
    # Add the phase only if the start time is present in the start_times
    # and it is less then minimal time point in the data set.
    # if start_times is not None and grain in start_times:
    #     data_start = X_one[time_series_config.time_column_name].min()
    #     real_start = start_times[grain]
    #     while real_start > data_start:
    #         real_start -= to_offset(time_series_config.freq)
    #     if real_start < data_start:
    #         # If we have the start time, we have to add the row corresponding to this time to the data set.
    #         time_ix = np.where(X_one.columns.values == time_series_config.time_column_name)[0][0]
    #         pad = [None] * (X_one.shape[1])
    #         pad[time_ix] = real_start
    #         X_one = pd.DataFrame([pad], columns=X_one.columns).append(X_one)
    # #########################################################################
    # Get numeric and datetime columns from featurization
    featurization_config = time_series_config.featurization
    column_purposes = featurization_config.column_purposes or {}
    numeric_columns = set(col_name for col_name, purpose in column_purposes.items() if purpose == FeatureType.Numeric)
    datetime_columns = set(
        col_name for col_name, purpose in column_purposes.items() if purpose == FeatureType.DateTime
    )

    # Set target on dataframe
    X_one[TimeSeriesInternal.DUMMY_TARGET_COLUMN] = time_series_config.data_y

    X_agg = _aggregate_one_grain(X_one, numeric_columns, datetime_columns, time_series_config, time_series_ids)

    # The mode will be applied to the DUMMY_ORDER_COLUMN, so that it will be renamed.
    mode_of_order_col = _get_mode_col_name(TimeSeriesInternal.DUMMY_ORDER_COLUMN)
    if mode_of_order_col in X_agg.columns:
        X_agg.dropna(subset=[mode_of_order_col], inplace=True)
        X_agg.drop(mode_of_order_col, axis=1, inplace=True)

    # ######## This section only applies at inference time ##############
    # TODO: should we keep this and section above?
    # If we have padded the data frame, we could add non desired early date.
    # For example if training set ends 2001-01-25, the frequency is 2D and trainig set
    # starts at 2001-01-26. The aggregation will add the non existing date 2001-01-25
    # to the test set and it will fail the run.
    # But if we have earlier dates, that means a user error and we should not correct it
    # and raise exception in forecast time.
    # if start_times is not None:
    #     min_test_time = X_agg[time_series_config.time_column_name].min()
    #     if grain in start_times and start_times[grain] == min_test_time:
    #         X_agg = X_agg[X_agg[time_series_config.time_column_name] != min_test_time]
    # #########################################################################

    X_agg.reset_index(drop=True, inplace=True)
    return X_agg
