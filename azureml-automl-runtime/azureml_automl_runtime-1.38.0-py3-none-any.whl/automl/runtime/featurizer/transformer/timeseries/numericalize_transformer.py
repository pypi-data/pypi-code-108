# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Encode categorical columns with integer codes."""
import warnings
import numpy as np
import pandas as pd
from typing import Optional, cast, Set, Dict, List, Any
import logging

from azureml.automl.core.shared.logging_utilities import function_debug_log_wrapped
from ..automltransformer import AutoMLTransformer
from azureml.automl.core.shared.exceptions import ClientException, TransformException
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.runtime.shared.time_series_data_frame import TimeSeriesDataFrame

# Prevent warnings when using Jupyter
warnings.simplefilter("ignore")
pd.options.mode.chained_assignment = None


class NumericalizeTransformer(AutoMLTransformer):
    """Encode categorical columns with integer codes."""

    NA_CODE = pd.Categorical(np.nan).codes[0]

    def __init__(
            self,
            include_columns: Optional[Set[str]] = None,
            exclude_columns: Optional[Set[str]] = None,
            categories_by_col: Optional[Dict[str, List[Any]]] = None) -> None:
        """
        Construct for NumericalizeTransformer.

        :param categories_by_grain_cols: Dictionary of categorical column names to unique categories in those columns
        :type categories_by_grain_cols: Optional[Dict[str, List[Any]]]
        :return:
        """
        super().__init__()
        self._categories_by_col = categories_by_col
        self._include_columns = include_columns or set()
        self._exclude_columns = exclude_columns or set()

        if len(self._include_columns.intersection(self._exclude_columns)) > 0:
            raise TransformException(
                "The include and exclude columns contain the same columns.",
                target="customized_columns",
                has_pii=False,
                reference_code=ReferenceCodes._NUMERICALIZE_TRANSFORMER_CONLFICT_COL
            )

    def get_params(self, deep=True):
        return {
            "include_columns": self._include_columns,
            "exclude_columns": self._exclude_columns,
            "categories_by_col": self._categories_by_col
        }

    @function_debug_log_wrapped(logging.INFO)
    def fit(self, x: TimeSeriesDataFrame, y: Optional[np.ndarray] = None) -> 'NumericalizeTransformer':
        """
        Fit function for NumericalizeTransformer.

        :param x: Input data.
        :type x: azureml.automl.runtime.shared.time_series_data_frame.TimeSeriesDataFrame
        :param y: Target values.
        :type y: numpy.ndarray
        :return: Class object itself.
        """

        if not self._categories_by_col:
            # If no cols as input defined, we will detect all categorical type columns
            fit_cols = x.select_dtypes(['object', 'category', 'bool']).columns

            # Save the category levels to ensure consistent encoding
            #   between fit and transform
            self._categories_by_col = {col: pd.Categorical(x[col]).categories
                                       for col in fit_cols if col not in self._exclude_columns}
            for col in self._include_columns:
                if col not in self._categories_by_col:
                    self._categories_by_col[col] = pd.Categorical(x[col]).categories

        return self

    @function_debug_log_wrapped(logging.INFO)
    def transform(self, x: TimeSeriesDataFrame) -> TimeSeriesDataFrame:
        """
        Transform function for NumericalizeTransformer transforms categorical data to numeric.

        :param x: Input data.
        :type x: azureml.automl.runtime.shared.time_series_data_frame.TimeSeriesDataFrame
        :return: Result of NumericalizeTransformer.
        """
        if self._categories_by_col is None:
            raise ClientException("NumericalizeTransformer transform method called before fit.", has_pii=False,
                                  reference_code=ReferenceCodes._NUMERICALIZE_TRANSFORMER_NOT_FITTED)
        # Check if X categoricals have categories not present at fit
        # If so, warn that they will be coded as NAs
        for col, fit_cats in self._categories_by_col.items():
            now_cats = pd.Categorical(x[col]).categories
            new_cats = set(now_cats) - set(fit_cats)
            if len(new_cats) > 0:
                warnings.warn(type(self).__name__ + ': Column contains '
                              'categories not present at fit. '
                              'These categories will be set to NA prior to encoding.')

        # Get integer codes according to the categories found during fit
        assign_dict = {col:
                       pd.Categorical(x[col],
                                      categories=fit_cats)
                       .codes
                       for col, fit_cats in self._categories_by_col.items()}

        return cast(TimeSeriesDataFrame, x.assign(**assign_dict))
