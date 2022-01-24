# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Dataset class for Tabular Networks"""

from typing import Any, Dict, Optional

import numpy as np
import pandas as pd
import torch

from azureml.automl.runtime.shared._tabularnetworks.tabular_nn_constants import FEATURES, TARGET


class TabularDataset(torch.utils.data.Dataset):
    def __init__(self, X: np.ndarray, y: np.ndarray, label_dtype: type = np.int64, feature_dtype: type = np.float32):
        """Creates a `TabularDataset`.

        Parameters
        ----------
        X: np.ndarray
            An array like with tabular features
            Helpful for automl datasets or sparse datasets you dont want to put in pandas
        y: np.ndarray
            An array with targets
        label_dtype: type, optional
            The datatype to which the data in target column should be cast (defaults to None, no casting)
        feature_dtype: type
            The datatype to which the data in the feature columns should be cast (defaults to np.float32)

        """
        self._data = X.astype(feature_dtype)
        self._labels = y.astype(label_dtype)

    @staticmethod
    def from_pandas(df: pd.DataFrame, label_col: Optional[Any], label_dtype: Optional[type], feature_dtype=np.float32):
        """Creates a `TabularDataset` from pandas.

        Parameters
        ----------
        df: pd.DataFrame
            A DataFrame from which the tabular data may be loaded.
        label_col: Any
            The column containing the label data
        label_dtype: type, optional
            The datatype to which the data in target column should be cast (defaults to None, no casting)
        feature_dtype: type
            The datatype to which the data in the feature columns should be cast (defaults to np.float32)

        """
        X = df.loc[:, df.columns != label_col].values
        if label_col is not None:
            y = df.loc[:, label_col].values
        else:
            # may be better to not have to store y but shouldn't be a significant issue
            y = np.empty(X.shape[0])
            y.fill(np.nan)
            label_dtype = None  # don't want casting of np.nan
        return TabularDataset(X, y, label_dtype, feature_dtype=feature_dtype)

    @staticmethod
    def from_numpy(X: np.ndarray, y: Optional[np.ndarray], label_dtype: Optional[type], feature_dtype=np.float32):
        """Creates a `TabularDataset` from numpy.

        Parameters
        ----------
        X: np.ndarray
            An array like with tabular features
            Helpful for automl datasets or sparse datasets you dont want to put in pandas
        y: np.ndarray
            An array with targets
        label_dtype: type, optional
            The datatype to which the data in target column should be cast (defaults to None, no casting)
        feature_dtype: type
            The datatype to which the data in the feature columns should be cast (defaults to np.float32)

        """
        if y is None:
            # TODO may be better to not have to store y but shouldn't be a significant issue
            y = np.empty(X.shape[0])
            y.fill(np.nan)
            label_dtype = None  # don't want casting of np.nan
        elif y.ndim != 1:
            y = y.ravel()
        return TabularDataset(X, y, label_dtype, feature_dtype=feature_dtype)

    def __getitem__(self, item) -> Dict[str, Any]:
        """Returns an item from the dataset."""
        return {FEATURES: self._data[item, :], TARGET: self._labels[item]}

    def __len__(self):
        """Returns the length of the dataset."""
        return self._data.shape[0]
