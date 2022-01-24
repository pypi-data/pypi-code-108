# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Automatically detect the time series id column names that eliminates all duplicate time index."""
from typing import List, Optional, Any, Union, Dict, cast
import logging

import pandas as pd

from azureml.automl.core.featurization.featurizationconfig import FeaturizationConfig
from azureml.automl.core.automl_base_settings import AutoMLBaseSettings
from azureml.automl.runtime.faults_verifier import VerifierManager
from azureml.automl.core.constants import FeatureType as _FeatureType
from azureml.automl.core.shared.constants import TimeSeriesInternal
from azureml.automl.runtime._ml_engine.featurizer_suggestion._suggest_featurizers import\
    _update_customized_feature_types
from azureml.automl.runtime.column_purpose_detection import (StatsAndColumnPurposeType, ColumnPurposeDetector)
from azureml.automl.core.shared.forecasting_exception import ForecastingDataException
from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared._diagnostics.automl_error_definitions import\
    TimeseriesDfDuplicatedIndexAutoTimeSeriesIDDetection

_logger = logging.getLogger(__name__)


def get_candidate_time_series_id_columns(X_train: pd.DataFrame,
                                         featurization_dict: Union[str, Dict[str, Any]]) -> List[str]:
    """
    Candidate time series id columns must be categorical columns, and does not have any missing values.

    :param X_train: Training data.
    :param featurization: The featurization config object.
    """
    candidate_time_series_id_columns = []

    # list of (raw_stats, feature_type_detected, column_name).
    stats_and_columns = ColumnPurposeDetector.get_raw_stats_and_column_purposes(X_train, True)

    if isinstance(featurization_dict, dict):
        featurization_config = FeaturizationConfig()
        featurization_config._from_dict(featurization_dict)

        # Eliminate all categorical columns that is in drop_columns and
        # update feature type defined in featurizationConfig
        _update_customized_feature_types(featurization_config, stats_and_columns)

    # Categorical columns list that do not contain NaN values
    # Categorical columns that have missing values can not be part of time series id column names.
    candidate_time_series_id_columns = [stat[2] for stat in stats_and_columns
                                        if (stat[1] == _FeatureType.Categorical and stat[0].num_na == 0)]
    _logger.info("Number of categorical candidate columns for auto time series detection: " +
                 str(len(candidate_time_series_id_columns)))
    return candidate_time_series_id_columns


def check_automatic_time_series_id_columns(X_train: pd.DataFrame,
                                           automl_settings_obj: AutoMLBaseSettings) -> bool:
    """
    Detect time series id column names that eliminate the duplicate time index if it exists.

    :param X_train: Training data.
    :param automl_settings_obj: The AutoML settings.
    """

    is_time_series_id_columns_detected = False
    featurization = automl_settings_obj.featurization
    time_column_name = automl_settings_obj.time_column_name
    detected_time_series_id_columns = []     # type: List[str]
    # If there is any duplicate in time index, check candidate of time series id column names exists
    candidate_columns = get_candidate_time_series_id_columns(X_train, featurization)

    curr_ngroups = X_train.groupby([time_column_name]).ngroups
    while candidate_columns and \
            len(detected_time_series_id_columns) < TimeSeriesInternal.MAX_TIME_SERIES_ID_COLUMN_NUMBER:

        # To get categorical column that makes max uniqueness, dictionary is used to keep {category col: ngroups}
        category_group_dict = {
            col: X_train.groupby([time_column_name] + detected_time_series_id_columns + [col]).ngroups
            for col in candidate_columns
        }

        if category_group_dict:
            # candidate is the categorical column that has the maximum uniqueness
            candidate, new_ngroups = max(category_group_dict.items(), key=lambda x: x[1])
            candidate_columns.remove(candidate)
            if(curr_ngroups < new_ngroups):
                curr_ngroups = new_ngroups
                detected_time_series_id_columns.append(candidate)
                if X_train.shape[0] == curr_ngroups:
                    is_time_series_id_columns_detected = True
                    break
            else:
                # there is no more column that can improve the uniqueness of the date index.
                break
        else:
            break

    if(len(detected_time_series_id_columns) != 0):
        if len(detected_time_series_id_columns) >= TimeSeriesInternal.MAX_TIME_SERIES_ID_COLUMN_NUMBER:
            # In this case, there is still duplicates in dataset with currently detected time series id column names.
            raise ForecastingDataException._with_error(
                AzureMLError.create(
                    TimeseriesDfDuplicatedIndexAutoTimeSeriesIDDetection,
                    target='time_column_name',
                    reference_code=ReferenceCodes._TSDF_DUPLICATED_INDEX_WITH_AUTO_TIMESERIES_ID_DETECTION,
                    detected_time_series_id_columns=detected_time_series_id_columns)
            )
        # Here, number of columns in detected_time_series_id_columns are less than MAX_TIME_SERIES_ID_COLUMN_NUMBER.
        if is_time_series_id_columns_detected:
            # post processing of time series id column names that removes extra column
            # that does not change ngroups of duplicate date index if exists.
            _logger.info("Post-processing for auto time series id detection has started.")
            for i in range(len(detected_time_series_id_columns) - 1, -1, -1):
                rest = detected_time_series_id_columns[:i] + detected_time_series_id_columns[i + 1:]
                if(X_train.shape[0] == X_train.groupby([time_column_name] + rest).ngroups):
                    del detected_time_series_id_columns[i]

            automl_settings_obj.grain_column_names = detected_time_series_id_columns
            _logger.info("Post-processing for auto time series id detection has ended.")

    return is_time_series_id_columns_detected


def get_duplicated_time_index(df: pd.DataFrame,
                              time_column_name: str,
                              time_series_id_column_names: List[str] = []) -> int:
    """
    Return if the data frame contain duplicated timestamps.

    :param df: The data frame to be checked.
    :param time_column_name: the name of a time column.
    :param time_series_id_column_names: The names of columns used to group a timeseries.
    """
    duplicate_num = 0
    group_by_col = [time_column_name]
    if time_series_id_column_names is not None and len(time_series_id_column_names) != 0:
        _logger.info("time_series_id_column_names were provided.")
        if isinstance(time_series_id_column_names, str):
            time_series_id_column_names = [time_series_id_column_names]
        group_by_col.extend(time_series_id_column_names)
    duplicate_num = df[df.duplicated(subset=group_by_col, keep=False)].shape[0]
    return duplicate_num


def detect_time_series_id_if_exists(X_train: pd.DataFrame,
                                    automl_settings_obj: AutoMLBaseSettings,
                                    verifier: Optional[VerifierManager]) -> bool:
    """
    Detect time series id column names that removes the duplicate time index if it exists.

    :param X_train: Training data.
    :param automl_settings_obj: The AutoML settings.
    :param verifier: The verifier to be used to add/update guardrails.
    """

    _logger.info("Auto time series id detection has started.")
    is_time_series_id_columns_detected = False
    duplicate_num = get_duplicated_time_index(X_train,
                                              automl_settings_obj.time_column_name,
                                              cast(List[str], automl_settings_obj.grain_column_names))

    # If there exists duplicate time index, we override time-series-id-column-names whether it is user defined or not.
    if(duplicate_num != 0):
        _logger.info("The data has duplicate time index: " + str(duplicate_num))
        # Automatic time series id column detection is triggered since data has duplicate time indexes.
        is_time_series_id_columns_detected = check_automatic_time_series_id_columns(
            X_train,
            automl_settings_obj
        )
        if is_time_series_id_columns_detected:
            _logger.info("Auto time series id detection has succeeded.")
        else:
            _logger.info("Auto time series id detection has failed.")

    if verifier is not None:
        verifier.update_data_verifier_time_series_id_detection_handling(cast(List[str],
                                                                             automl_settings_obj.grain_column_names),
                                                                        duplicate_num,
                                                                        is_time_series_id_columns_detected)

    _logger.info("Auto time series id detection completed.")

    return is_time_series_id_columns_detected
