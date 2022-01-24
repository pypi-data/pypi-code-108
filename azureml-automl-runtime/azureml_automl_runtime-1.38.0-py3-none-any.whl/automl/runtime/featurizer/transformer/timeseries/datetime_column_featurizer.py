# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Class for featurizing datetime columns in timeseries datasets."""
from typing import cast, List, Dict, Optional
import logging

import pandas as pd
from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared._diagnostics.automl_error_definitions import \
    PandasDatetimeConversion, MissingColumnsInData
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.exceptions import DataErrorException
from azureml.automl.core.shared.logging_utilities import function_debug_log_wrapped
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.runtime.shared.time_series_data_frame import TimeSeriesDataFrame
from azureml.automl.runtime.shared.types import DataSingleColumnInputType

from .forecasting_base_estimator import AzureMLForecastTransformerBase


class DatetimeColumnFeaturizer(AzureMLForecastTransformerBase):
    """
    Transform that creates calendrical features for datetime-typed columns.
    This tranform contrasts with the TimeIndexFeaturizer which creates features for the time axis
    of a timeseries. Unlike the time axis, datetime columns/features do not necessarily have
    well defined frequencies, so the featurization does not include any pruning.
    """

    _FEATURE_SUFFIXES = ['Year', 'Month', 'Day', 'DayOfWeek',
                         'DayOfYear', 'QuarterOfYear', 'WeekOfMonth',
                         'Hour', 'Minute', 'Second']  # type: List[str]

    def __init__(self, datetime_columns: Optional[List[str]] = None) -> None:
        Contract.assert_true(
            (datetime_columns is None) or (isinstance(datetime_columns, list)),
            "Expected datetime_columns input to be None or a list.",
            log_safe=True
        )
        dt_cols = []  # type: List[str]
        if isinstance(datetime_columns, list):
            dt_cols = datetime_columns
        self.datetime_columns = dt_cols

    def _get_feature_names_one_column(self, input_column_name: str) -> List[str]:
        return ['{}_{}'.format(input_column_name, feature) for feature in self._FEATURE_SUFFIXES]

    def _construct_datatime_feature(self, x: pd.Series) -> pd.DataFrame:
        x_columns = self._get_feature_names_one_column(x.name)

        return pd.DataFrame(data=pd.concat([
            x.dt.year,                      # Year
            x.dt.month,                     # Month
            x.dt.day,                       # Day
            x.dt.dayofweek,                 # DayOfWeek
            x.dt.dayofyear,                 # DayOfYear
            x.dt.quarter,                   # QuarterOfYear
            (x.dt.day - 1) // 7 + 1,        # WeekOfMonth
            x.dt.hour,                      # Hour
            x.dt.minute,                    # Minute
            x.dt.second,                    # Second
        ], axis=1).values, columns=x_columns)

    def _construct_features_from_time_columns(self, X: TimeSeriesDataFrame) -> TimeSeriesDataFrame:
        if len(self.datetime_columns) == 0:
            return X
        for col in self.datetime_columns:
            try:
                col_as_dt = pd.to_datetime(X[col])
            except KeyError:
                raise DataErrorException._with_error(
                    AzureMLError.create(
                        MissingColumnsInData, target='X',
                        reference_code=ReferenceCodes._TS_DATETIME_COLUMN_FEATURIZER_MISSING_COLUMN,
                        columns=col, data_object_name='X'
                    )
                )
            except Exception:
                raise DataErrorException._with_error(
                    AzureMLError.create(
                        PandasDatetimeConversion, target='X',
                        reference_code=ReferenceCodes._TS_DATETIME_COLUMN_FEATURIZER_PD_DATETIME_CONVERSION,
                        column=col, column_type=X[col].dtype
                    )
                )
            time_features = self._construct_datatime_feature(col_as_dt)
            for c in time_features.columns.values:
                X[c] = time_features[c].values
        X.drop(columns=self.datetime_columns, inplace=True)
        return X

    def preview_datetime_column_feature_names(self) -> Dict[str, List[str]]:
        """
        Get the time features names that would be generated for datetime columns.

        :return: dict that maps each raw datetime feature to a list of generated calendar feature names
        :rtype: dict
        """
        return {raw_name: self._get_feature_names_one_column(raw_name) for raw_name in self.datetime_columns}

    @function_debug_log_wrapped(logging.INFO)
    def fit(self, X: TimeSeriesDataFrame,
            y: Optional[DataSingleColumnInputType] = None) -> 'DatetimeColumnFeaturizer':
        """
        Fit the transform.

        Determine which features, if any, should be pruned.

        :param X: Input data
        :type X: azureml.automl.runtime.shared.time_series_data_frame.TimeSeriesDataFrame

        :param y: Passed on to sklearn transformer fit

        :return: Fitted transform
        :rtype: azureml.automl.runtime.featurizer.transformer.timeseries.time_index_featurizer.TimeIndexFeaturizer
        """
        return self

    @function_debug_log_wrapped(logging.INFO)
    def transform(self, X: TimeSeriesDataFrame) -> TimeSeriesDataFrame:
        """
        Create calendrical for an input data frame.

        :param X: Input data
        :type X: azureml.automl.runtime.shared.time_series_data_frame.TimeSeriesDataFrame

        :return: Data frame with time index features
        :rtype: azureml.automl.runtime.shared.time_series_data_frame.TimeSeriesDataFrame
        """
        return self._construct_features_from_time_columns(X)

    @function_debug_log_wrapped(logging.INFO)
    def fit_transform(self, X: TimeSeriesDataFrame,
                      y: Optional[DataSingleColumnInputType] = None) -> TimeSeriesDataFrame:
        """
        Apply `fit` and `transform` methods in sequence.

        Determine which features, if any, should be pruned.

        :param X: Input data
        :type X: azureml.automl.runtime.shared.time_series_data_frame.TimeSeriesDataFrame

        :param y: Passed on to sklearn transformer fit

        :return: Data frame with time index features
        :rtype: azureml.automl.runtime.shared.time_series_data_frame.TimeSeriesDataFrame
        """
        X_trans = self.fit(X, y).transform(X)
        return cast(TimeSeriesDataFrame, X_trans)
