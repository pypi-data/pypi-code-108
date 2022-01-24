# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Transforms the input data by adding lagging features."""
from typing import List, Optional
import logging

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared._diagnostics.automl_error_definitions import InsufficientSampleSize
from azureml.automl.core.shared._diagnostics.validation import Validation
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from scipy import sparse
import numpy as np
import pandas as pd

from azureml.automl.core.shared.logging_utilities import function_debug_log_wrapped
from ..automltransformer import AutoMLTransformer
from azureml.automl.core.shared.exceptions import DataException


class LaggingTransformer(AutoMLTransformer):
    """Transforms the input data by adding lagging features."""

    def __init__(self, lag_length: int):
        """
        Initialize for lagging transform with lagging length.

        :param lag_length: Lagging length.
        :return:
        """
        super().__init__()
        self._lag_length = lag_length
        self._missing_fill = 0
        self._engineered_feature_names = []     # type: List[str]
        self._are_engineered_feature_names_available = False

    def get_params(self, deep=True):
        return {
            "lag_length": self._lag_length
        }

    def _learn_transformations(self, x, y=None):
        """
        Learn data transformation to be done on the raw data.

        :param x: Input dataframe or sparse matrix.
        :type x: numpy.ndarray or pandas.DataFrame or scipy.sparse.spmatrix
        :param y: Target values.
        :type y: numpy.ndarray or pandas.DataFrame
        """
        pass

    @function_debug_log_wrapped(logging.INFO)
    def fit(self, x, y=None):
        """
        Fit function for lagging transform.

        :param x: Input dataframe or sparse matrix.
        :type x: numpy.ndarray or pandas.DataFrame or scipy.sparse.spmatrix
        :param y: Target values.
        :type y: numpy.ndarray or pandas.DataFrame
        :return: The instance object: self.
        """
        self._learn_transformations(x, y)
        if not self._are_engineered_feature_names_available:
            # Generate engineered feature names
            self._generate_engineered_feature_names(x)

            self._are_engineered_feature_names_available = True

        return self

    def get_engineered_feature_names(self):
        """
        Return the list of engineered feature names as string.

        Return the list of engineered feature names as string after data transformations
        on the raw data have been finished.

        :return: The list of engineered fearure names as strings
        """
        return self._engineered_feature_names

    def _generate_engineered_feature_names(self, x):
        """
        Generate engineered feature names for lagging transformer features.

        :type x: numpy.ndarray or pandas.DataFrame or scipy.sparse.spmatrix
        :param y: Target values.
        """
        raw_feature_names = None
        if isinstance(x, pd.DataFrame) or isinstance(x, pd.SparseDataFrame):
            raw_feature_names = x.columns

        # If no raw feature names are available, prefix them with 'C'
        column_name = 'C'
        temp_list = []
        if raw_feature_names is None:
            if len(x.shape) == 1:
                num_cols = 1
            else:
                num_cols = x.shape[1]
            for index in range(1, num_cols + 1):
                temp_list.append(column_name + str(index))
        elif isinstance(raw_feature_names[0], (int, np.integer)):
            for index in range(1, len(raw_feature_names) + 1):
                temp_list.append(column_name + str(index))
        else:
            for index in range(len(raw_feature_names)):
                temp_list.append(raw_feature_names[index])

        # For each lag length generate the engineered feature name of the format
        # "raw_feature_name" + "_lag_" + str(lag_length).
        for lag_length in range(0 + self._lag_length + 1):
            for index, raw_feature_name in enumerate(temp_list):
                if lag_length == 0:
                    engineered_name = temp_list[index]
                else:
                    engineered_name = temp_list[index] + '_lag_' + str(lag_length)

                # Add the engineered name to the list
                self._engineered_feature_names.insert(index + lag_length * len(temp_list), engineered_name)

    @function_debug_log_wrapped(logging.INFO)
    def transform(self, x):
        """
        Transform function for lagging transform.

        The function appends columns with previous seen rows to the input dataframe
        or sparse matrix depending on the specified lagging length.

        :param x: Input dataframe or sparse matrix.
        :type x: numpy.ndarray or pandas.DataFrame or scipy.sparse.spmatrix
        :return: Result of lagging transform.
        """
        # If we get a sparse data frame, convert to sparse matrix
        if isinstance(x, pd.SparseDataFrame):
            x = x.to_coo().tocsr()

        x_is_sparse = sparse.issparse(x)
        if not x_is_sparse:
            Validation.validate_type(x, "X", expected_types=(pd.DataFrame, np.ndarray))

        if x.shape[0] < self._lag_length:
            raise DataException._with_error(AzureMLError.create(
                InsufficientSampleSize, target="X", data_object_name="X", sample_count=x.shape[0],
                minimum_count=self._lag_length, reference_code=ReferenceCodes._LAGGING_TRANSFORMER_INSUFFICIENT_DATA)
            )

        if isinstance(x, np.ndarray):
            df = pd.DataFrame(x)
        elif x_is_sparse:
            # SparseDataFrame throws error with to_coo if dtype is int
            df = pd.SparseDataFrame(x.astype(float))
        else:
            df = x

        df_lag = df
        for i in range(1, self._lag_length + 1):
            df_lag = pd.concat([df_lag, df.shift(i)], axis=1)

        df_lag.columns = self._engineered_feature_names
        return df_lag.to_coo().tocsr() if x_is_sparse else \
            df_lag.fillna(self._missing_fill).values
