# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Drop columns from dataset."""
import logging
from warnings import warn

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    TimeseriesInputIsNotTimeseriesDf,
    TimeseriesDfColumnTypeNotSupported)
from azureml.automl.core.shared.forecasting_exception import (ForecastingDataException,
                                                              ForecastingConfigException)
from azureml.automl.core.shared.logging_utilities import function_debug_log_wrapped
from azureml.automl.core.shared.reference_codes import ReferenceCodes

from azureml.automl.runtime.shared import forecasting_verify as verify
from azureml.automl.runtime.shared.time_series_data_frame import TimeSeriesDataFrame


from .forecasting_base_estimator import AzureMLForecastTransformerBase


class DropColumns(AzureMLForecastTransformerBase):
    """A transform class for dropping columns from a TimeSeriesDataFrame.

    Metadata columns (grain, value, time_index, group) cannot be dropped.
    """

    def __init__(self, drop_columns):
        """
        Construct a column dropper.

        :param drop_columns: list of names of columns to be dropped
        :type drop_columns: list
        """
        super().__init__()
        self.drop_columns = drop_columns

    @property
    def drop_columns(self):
        """List of column names to drop."""
        return self._drop_columns

    @drop_columns.setter
    def drop_columns(self, val):
        if verify.is_iterable_but_not_string(val):
            self._drop_columns = val
        else:
            self._drop_columns = [val]

        if not all(isinstance(col, str) for col in self._drop_columns):
            raise ForecastingConfigException._with_error(
                AzureMLError.create(TimeseriesDfColumnTypeNotSupported, target='self._drop_columns',
                                    reference_code=ReferenceCodes._TSDF_COL_TYPE_NOT_SUPPORTED_DROP_COLS,
                                    col_name='drop_columns',
                                    supported_type='string')
            )

    def _check_columns_against_input(self, X):
        """
        Check the list of columns to drop.

        Exclude columns that are not in X or are properties
        of X (grain, group, time_index, value).

        :param X: is a TimeSeriesDataFrame
        :returns: a list of valid column labels to drop.
        """
        # Need to check against tsdf properties
        # Concat properties (as lists) into a list
        properties = [item if verify.is_iterable_but_not_string(item)
                      else [item]
                      for item in (X.grain_colnames, X.time_colname,
                                   X.ts_value_colname, X.group_colnames)]

        # We will not check against _metadata.
        # This transform will be willing to drop important metadata columns
        # from subclasses (ForecastDataFrame, MultiForecastDataFrame).
        # However, they are *outputs* we do not wish to lock down as tightly.

        # Flatten the list of properties to a list of column names
        properties_colnames = [item for sublist in properties
                               for item in sublist]

        # Filter out columns we can't drop
        drop_columns_safe = [col for col in self._drop_columns
                             if col in X.columns
                             and col not in properties_colnames]

        if len(self._drop_columns) != len(drop_columns_safe):
            warn('One or more requested columns will not be dropped. '
                 + 'Cannot drop nonexistent columns or TimeSeriesDataFrame '
                 + 'property columns (time_series_id_column_names, time_colname, '
                 + 'ts_value_colname, group_colnames)')

        return drop_columns_safe

    @function_debug_log_wrapped(logging.INFO)
    def fit(self, X, y=None):
        """
        Fit is empty for this transform.

        This method is just a pass-through

        :param X: Ignored.

        :param y: Ignored.

        :return: self
        :rtype: azureml.automl.runtime.featurizer.transformer.timeseries.drop_columns.DropColumns
        """
        return self

    @function_debug_log_wrapped(logging.INFO)
    def transform(self, X):
        """
        Drop the columns from dataframe.

        :param X: Input data
        :type X: azureml.automl.runtime.shared.time_series_data_frame.TimeSeriesDataFrame

        :return: Data with columns dropped.
        :rtype: azureml.automl.runtime.shared.time_series_data_frame.TimeSeriesDataFrame
        """
        if not isinstance(X, TimeSeriesDataFrame):
            raise ForecastingDataException._with_error(
                AzureMLError.create(TimeseriesInputIsNotTimeseriesDf, target='X',
                                    reference_code=ReferenceCodes._TS_INPUT_IS_NOT_TSDF)
            )
        drop_labels = self._check_columns_against_input(X)
        X_new = X.drop(drop_labels, axis=1)

        return X_new
