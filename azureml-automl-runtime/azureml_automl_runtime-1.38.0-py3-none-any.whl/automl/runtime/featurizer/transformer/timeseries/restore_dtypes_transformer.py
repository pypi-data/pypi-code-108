# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Fix the dtypes after the infertence."""
from typing import Optional, cast, Dict, List, Any, Union, Tuple
import logging

import numpy as np
import pandas as pd
from azureml._common._error_definition import AzureMLError
from azureml.automl.core import _codegen_utilities
from azureml.automl.core.featurization.featurizationconfig import FeaturizationConfig
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    TimeseriesDfInvalidValOfNumberTypeInTestData)
from azureml.automl.core.shared.constants import TimeSeriesInternal
from azureml.automl.core.shared.forecasting_exception import ForecastingDataException
from azureml.automl.core.shared.logging_utilities import function_debug_log_wrapped
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.runtime.shared.time_series_data_frame import TimeSeriesDataFrame

from ..automltransformer import AutoMLTransformer
from azureml.automl.core.constants import FeatureType


class RestoreDtypesTransformer(AutoMLTransformer):
    """Restore the dtypes of numerical data types."""

    def __init__(self,
                 tsdf: Optional[TimeSeriesDataFrame] = None,
                 target_column: Optional[str] = None,
                 dtypes: Optional[Union[Dict[str, Any], pd.Series]] = None,
                 featurization_config: Optional[FeaturizationConfig] = None) -> None:
        """
        Construct for RestoreDtypesTransformer.

        :param tsdf: The initial time series data frame before
                     transforms application.
        :type tsdf: azureml.automl.runtime.shared.time_series_data_frame.TimeSeriesDataFrame
        """
        super().__init__()

        if tsdf is None:
            self._target_column = target_column
            if isinstance(dtypes, dict):
                self._dtypes = pd.Series(data=dtypes)
            else:
                self._dtypes = dtypes
        else:
            self._target_column = tsdf.ts_value_colname
            # The actual fit have to happen in the constructor
            # because during fit-transform the dataframe will be modified
            # and the dtypes will be changed.
            skip_col = set()
            for col in tsdf.columns:
                if all([pd.isna(val) for val in tsdf[col]]):
                    skip_col.add(col)
            if featurization_config is not None:
                # If we have categorical column, do not try to convert it to float.
                if featurization_config.column_purposes is not None:
                    for k, v in featurization_config.column_purposes.items():
                        if v == FeatureType.Categorical:
                            skip_col.add(k)
            if len(skip_col) == tsdf.shape[1]:
                # Nothing to do, the types can not be determined.
                self._dtypes = None
                return
            # We do not want to fix the type of dummy order column.
            skip_col.add(TimeSeriesInternal.DUMMY_ORDER_COLUMN)
            x_no_na = tsdf[list(set(tsdf.columns.values).difference(skip_col))]
            self._dtypes = x_no_na.dtypes

    def _get_imports(self) -> List[Tuple[str, str, Any]]:
        return [
            _codegen_utilities.get_import(np.dtype)
        ]

    def get_params(self, deep=True):
        return {
            "target_column": self._target_column,
            "dtypes": self._dtypes.to_dict() if self._dtypes is not None else None
        }

    @function_debug_log_wrapped(logging.INFO)
    def fit(self,
            x: TimeSeriesDataFrame,
            y: Optional[np.ndarray] = None) -> 'RestoreDtypesTransformer':
        """
        Fit function for RestoreDtypesTransformer.

        :param x: Input data.
        :type x: azureml.runtime.core.shared.time_series_data_frame.TimeSeriesDataFrame
        :param y: Unused.
        :type y: numpy.ndarray
        :return: Class object itself.
        """
        return self

    @function_debug_log_wrapped(logging.INFO)
    def transform(self,
                  x: TimeSeriesDataFrame) -> TimeSeriesDataFrame:
        """
        Transform the data frame.

        :param x: Input data.
        :type x: azureml.automl.runtime.shared.time_series_data_frame.TimeSeriesDataFrame
        :return: The data frame with correct dtypes.
        """
        # Ensure the data types are the same as before featurization
        # for numeric columns.
        if self._dtypes is None:
            return x
        for col in self._dtypes.index:
            if col == self._target_column:
                # Skip the type for target column
                continue
            if not type(self._dtypes[col]).__module__.startswith('pandas') and \
                    np.issubdtype(self._dtypes[col], np.number) and col in x.columns:
                try:
                    # We should not set value to int type to be safe to NaN in the test set.
                    x[col] = x[col].astype('float')
                except ValueError:
                    raise ForecastingDataException._with_error(
                        AzureMLError.create(TimeseriesDfInvalidValOfNumberTypeInTestData, target='x',
                                            reference_code=ReferenceCodes._TSDF_INV_VAL_OF_NUMBER_TYPE_IN_TEST_DATA,
                                            column=col)
                    )
        return x

    def get_non_numeric_columns(self) -> List[Any]:
        """
        Return the list of caegorical columns.

        :return: The list of categorical columns.
        """
        if self._dtypes is None:
            return []

        def filter_fun(x):
            """The function to filter columns."""
            return type(self._dtypes[x]).__module__.startswith('pandas') or \
                not np.issubdtype(self._dtypes[x], np.number)

        return list(
            filter(
                filter_fun,
                self._dtypes.index))
