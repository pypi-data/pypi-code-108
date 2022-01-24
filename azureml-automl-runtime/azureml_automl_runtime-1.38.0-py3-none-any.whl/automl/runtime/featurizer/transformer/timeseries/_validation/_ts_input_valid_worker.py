# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Classes for TimeseriesInputValidationWorker."""
import warnings
from typing import cast, Dict, List, Optional, Union
import logging

import numpy as np
import pandas as pd
from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared import constants
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    NoValidDates,
    TimeseriesInvalidTimestamp,
    TimeseriesDfMissingColumn,
    TimeColumnValueOutOfRange,
    TimeseriesDfDuplicatedIndexTimeColTimeIndexColName,
    TimeseriesDfDuplicatedIndexTimeColTimeIndexNaT,
    TimeseriesDfDuplicatedIndexTimeColName)
from azureml.automl.core.shared._diagnostics.validation import Validation
from azureml.automl.core.shared.constants import TimeSeries
from azureml.automl.core.shared.exceptions import DataException, ValidationException
from azureml.automl.core.shared.forecasting_exception import ForecastingDataException
from azureml.automl.core.shared.logging_utilities import function_debug_log_wrapped
from azureml.automl.core.shared.reference_codes import ReferenceCodes

from azureml.automl.runtime import frequency_fixer
from azureml.automl.runtime.shared.forecasting_ts_utils import _construct_day_of_quarter_single_df_with_date
from azureml.automl.runtime.featurizer.transformer.timeseries._validation._timeseries_validation_common import (
    check_memory_limit, _get_df_or_raise)
from ._timeseries_validator import TimeseriesValidationParamName
from ._timeseries_validator import TimeseriesValidationParameter
from ._timeseries_validator import TimeseriesValidationWorkerBase


class TimeseriesInputValidationWorker(TimeseriesValidationWorkerBase):
    """Validation worker for the input data."""

    def __init__(self,
                 x_param_name: TimeseriesValidationParamName,
                 y_param_name: TimeseriesValidationParamName) -> None:
        self._x_param_name = x_param_name
        self._y_param_name = y_param_name

    @function_debug_log_wrapped(logging.INFO)
    def validate(self, param: TimeseriesValidationParameter) -> None:
        """Abstract method that validate the timeseries config/data."""
        automl_settings = param.params[TimeseriesValidationParamName.AUTOML_SETTINGS]
        X = param.params[self._x_param_name]
        y = param.params[self._y_param_name]
        x_raw_column_names = param.params[TimeseriesValidationParamName.X_RAW_COLUMN_NAMES]

        # If the X is X_valid and it's none, or y is y_valid and it's none, we do nothing.
        if ((X is None and self._x_param_name == TimeseriesValidationParamName.X_VALID)
                or (y is None and self._y_param_name == TimeseriesValidationParamName.Y_VALID)):
            return
        X = _get_df_or_raise(X, x_raw_column_names)
        # Check if we have enough memory.
        check_memory_limit(X, y)

        # The timeseries_param_dict must be setuped in the TimeseriesParametersValidationWorker.
        timeseries_param_dict = param.params.get(TimeseriesValidationParamName.TIMESERIES_PARAM_DICT)
        Validation.validate_value(timeseries_param_dict, "timeseries_param_dict")
        timeseries_param_dict = cast(Dict[str, str], timeseries_param_dict)
        TimeseriesInputValidationWorker._check_columns_present(X, timeseries_param_dict)

        # Check that we contain the actual time stamps in the DataFrame
        if X[automl_settings.time_column_name].count() == 0:
            raise ForecastingDataException._with_error(
                AzureMLError.create(
                    NoValidDates,
                    time_column_name=automl_settings.time_column_name,
                    reference_code=ReferenceCodes._TSDF_TM_COL_CONTAINS_NAT_ONLY,
                    target=TimeSeries.TIME_COLUMN_NAME)
            )

        # Convert time column to datetime only if all columns are already present.
        time_param = timeseries_param_dict.get(TimeSeries.TIME_COLUMN_NAME)
        if isinstance(time_param, str):
            frequency_fixer.convert_to_datetime(X, time_param)

        # Check not supported datatypes and warn
        TimeseriesInputValidationWorker._check_supported_data_type(X)
        TimeseriesInputValidationWorker._check_time_index_duplication(X, automl_settings.time_column_name,
                                                                      automl_settings.grain_column_names)
        TimeseriesInputValidationWorker._check_valid_pd_time(X, automl_settings.time_column_name)

        # Set the X or X_valid back to the validation parameter, for later worker use.
        param.params[self._x_param_name] = X

    @staticmethod
    def _check_time_index_duplication(df: pd.DataFrame,
                                      time_column_name: str,
                                      grain_column_names: Optional[List[str]] = None) -> None:
        """
        Check if the data frame contain duplicated timestamps within the one grain.

        :param df: The data frame to be checked.
        :param time_column_name: the name of a time column.
        :param grain_column_names: the names of grain columns.
        """
        group_by_col = [time_column_name]
        if grain_column_names is not None:
            if isinstance(grain_column_names, str):
                grain_column_names = [grain_column_names]
            group_by_col.extend(grain_column_names)
        duplicateRowsDF = df[df.duplicated(subset=group_by_col, keep=False)]
        # customer has NaT or NaN in the data.
        if pd.isnull(duplicateRowsDF[time_column_name]).sum() > 0:
            raise ForecastingDataException._with_error(
                AzureMLError.create(TimeseriesDfDuplicatedIndexTimeColTimeIndexNaT,
                                    target='time_column_name',
                                    reference_code=ReferenceCodes._TSDF_DUPLICATED_INDEX_TM_COL_TM_IDX_NAT,
                                    time_column_name=time_column_name)
            )

        if duplicateRowsDF.shape[0] > 0:
            if grain_column_names is not None and len(grain_column_names) > 0:
                raise ForecastingDataException._with_error(
                    AzureMLError.create(TimeseriesDfDuplicatedIndexTimeColTimeIndexColName,
                                        target='time_column_name',
                                        reference_code=ReferenceCodes._TSDF_DUPLICATED_INDEX_TM_COL_TM_IDX_COL_NAME,
                                        time_column_name=time_column_name,
                                        grain_column_names=grain_column_names)
                )
            else:
                raise ForecastingDataException._with_error(
                    AzureMLError.create(TimeseriesDfDuplicatedIndexTimeColName,
                                        target='time_column_name',
                                        reference_code=ReferenceCodes._TSDF_DUPLICATED_INDEX_TM_COL_NAME,
                                        time_column_name=time_column_name)
                )

    @staticmethod
    def _check_columns_present(df: pd.DataFrame, timeseries_param_dict: Dict[str, str]) -> None:
        """
        Determine if df has the correct column names for time series.

        :param df: The data frame to be analyzed.
        :param timeseries_param_dict: The parameters specific to time series.
        """

        def check_a_in_b(a: Union[str, List[str]], b: List[str]) -> List[str]:
            """
            checks a is in b.

            returns any of a not in b.
            """
            if isinstance(a, str):
                a = [a]

            set_a = set(a)
            set_b = set(b)
            return list(set_a - set_b)

        missing_col_names = []  # type: List[str]
        # check time column in df
        col_name = timeseries_param_dict.get(constants.TimeSeries.TIME_COLUMN_NAME)
        if col_name is not None:
            missing_col_names = check_a_in_b(col_name, df.columns)
        # raise if missing
        if len(missing_col_names) != 0:
            raise ForecastingDataException._with_error(
                AzureMLError.create(TimeseriesDfMissingColumn,
                                    target=TimeseriesDfMissingColumn.TIME_COLUMN,
                                    reference_code=ReferenceCodes._TST_NO_TIME_COLNAME_TRAIN_UTIL,
                                    column_names=constants.TimeSeries.TIME_COLUMN_NAME)
            )

        # check grain column(s) in df
        col_names = timeseries_param_dict.get(constants.TimeSeries.GRAIN_COLUMN_NAMES)
        if col_names is not None:
            missing_col_names = check_a_in_b(col_names, df.columns)
        # raise if missing
        if len(missing_col_names) != 0:
            raise ForecastingDataException._with_error(
                AzureMLError.create(TimeseriesDfMissingColumn,
                                    target=TimeseriesDfMissingColumn.GRAIN_COLUMN,
                                    reference_code=ReferenceCodes._TST_CHECK_PHASE_NO_GRAIN_CHK_COLS,
                                    column_names=constants.TimeSeries.TIME_SERIES_ID_COLUMN_NAMES)
            )

        # check drop column(s) in df
        missing_drop_cols = []  # type: List[str]
        col_names = timeseries_param_dict.get(constants.TimeSeries.DROP_COLUMN_NAMES)
        if col_names is not None:
            missing_drop_cols += check_a_in_b(col_names, df.columns)

        # warn if missing
        if len(missing_drop_cols) != 0:
            warnings.warn("The columns to drop were not found and will be ignored.")

    @staticmethod
    def _check_supported_data_type(df: pd.DataFrame) -> None:
        """
        Check if the data frame contains non supported data types.

        :param df: The data frame to be analyzed.
        """
        supported_datatype = set([np.number, np.dtype(object), pd.Categorical.dtype, np.datetime64])
        unknown_datatype = set(df.infer_objects().dtypes) - supported_datatype
        if (len(unknown_datatype) > 0):
            warnings.warn("Following datatypes: {} are not recognized".
                          format(unknown_datatype))

    @staticmethod
    def _check_valid_pd_time(df: pd.DataFrame, time_column_name: str) -> None:
        """
        Check the validity of data in the date column.

        :param df: The data frame to be checked.
        :param time_column_name: the name of a time column.
        """
        try:
            time_df = pd.to_datetime(df[time_column_name])
            # for the padding case, the data may contains pd.NaT here and we need to neglect it.
            _construct_day_of_quarter_single_df_with_date(
                pd.DataFrame({'date': time_df[pd.notnull(time_df)]}), 'date')
        except pd.errors.OutOfBoundsDatetime as e:
            raise DataException._with_error(
                AzureMLError.create(TimeColumnValueOutOfRange, target=time_column_name, column_name=time_column_name,
                                    min_timestamp=pd.Timestamp.min, max_timestamp=pd.Timestamp.max),
                inner_exception=e
            ) from e
        except ValueError as ve:
            raise ValidationException._with_error(
                AzureMLError.create(TimeseriesInvalidTimestamp, target="X"), inner_exception=ve
            ) from ve
