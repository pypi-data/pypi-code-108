# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Imputer for missing values in Categorical data."""
from typing import Any, Optional

import numpy as np
import pandas as pd

from azureml.automl.core.shared.logging_utilities import function_debug_log_wrapped
from azureml.automl.core.shared.transformer_runtime_exceptions import (
    CatImputerRuntimeNotCalledException)
from azureml.automl.runtime.shared.types import DataInputType, DataSingleColumnInputType

from ..automltransformer import AutoMLTransformer
from azureml.automl.core.constants import SupportedTransformersInternal as _SupportedTransformersInternal


class CatImputer(AutoMLTransformer):
    """Impute missing values for categorical data by the most frequent category."""

    def __init__(self, copy: bool = True, *args: Any, **kwargs: Any) -> None:
        """
        Construct the CatImputer.

        :param copy: Create copy of the categorical column.
        """
        super().__init__()
        ii32 = np.iinfo(np.int32)
        ii64 = np.iinfo(np.int64)
        self._missing_vals = [np.nan, ii32.min, ii64.min]
        self._copy = copy
        self._transformer_name = _SupportedTransformersInternal.CatImputer

    def get_params(self, deep=True):
        return {
            "copy": self._copy
        }

    def _get_transformer_name(self) -> str:
        return self._transformer_name

    def _get_mask(self, X: DataInputType) -> np.ndarray:
        """
        Get missing values mask.

        :param X: Input array.
        :return: Mask with missing values.
        """
        mask = np.zeros(X.shape, dtype=bool)
        x_object = None
        for val in self._missing_vals:
            if val is None or (isinstance(val, float) and np.isnan(val)):
                mask = mask | pd.isnull(X)
            else:
                x_object = X.astype(np.object) if x_object is None else x_object
                mask = mask | (x_object == val)

        return mask

    def _to_dict(self):
        """
        Create dict from transformer for  serialization usage.

        :return: a dictionary
        """
        dct = super(CatImputer, self)._to_dict()
        dct['id'] = "cat_imputer"
        dct['type'] = 'categorical'
        dct['kwargs']['copy'] = self._copy
        return dct

    @function_debug_log_wrapped()
    def fit(self, x, y=None):
        """
        Transform the data to mark the missing values and identify the most frequent category.

        :param x: The data to transform.
        :type x: numpy.ndarray or pandas.core.series.Series
        :param y: Target values.
        :type y: numpy.ndarray
        :return: The instance object: self.
        """
        non_na = x.dropna()
        if non_na.empty:
            self._fill = str(np.nan)
            return self

        series_name = x.name if getattr(x, 'name', None) is not None else 0

        mode = non_na.to_frame().groupby(series_name)[
            series_name].agg("count").idxmax()
        self._fill = mode

        return self

    @function_debug_log_wrapped()
    def transform(self, x):
        """
        Transform data x by adding the missing values with the most frequent categories.

        Must call fit() before calling transform()

        :param x: The data to transform.
        :type x: numpy.ndarray or pandas.core.series.Series
        :return: The transformed data.
        """
        if self._fill is None:
            raise CatImputerRuntimeNotCalledException("CatImputer fit not called", has_pii=False)

        mask = self._get_mask(x)
        if self._copy:
            x = x.copy()
        x[mask] = self._fill

        return x.values
