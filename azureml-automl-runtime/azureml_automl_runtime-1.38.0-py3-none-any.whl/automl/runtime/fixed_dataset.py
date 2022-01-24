# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""The object to hold the output of a frequency fixer."""
from typing import Optional

import pandas as pd

from azureml.automl.runtime.shared.types import DataSingleColumnInputType


class FixedDataSet(object):
    """The object-container for the fixed data set."""

    def __init__(self, X: pd.DataFrame,
                 y: Optional[DataSingleColumnInputType],
                 is_failed: bool, is_modified: bool,
                 freq: Optional[pd.DateOffset]) -> None:
        """
        Constructor.

        :param X: The data frame with features.
        :param y: The target values.
        :param is_failed: The flag, showing that the frequency fixer has failed.
        :param is_modified: The flag showing that the data frame was modified.
        :param freq: The data set frequency.
        """
        self._X = X
        self._y = y
        self._is_failed = is_failed
        self._is_modified = is_modified
        self._freq = freq

    @property
    def data_x(self) -> pd.DataFrame:
        """Return the data frame with features."""
        return self._X

    @property
    def data_y(self) -> Optional[DataSingleColumnInputType]:
        """Return target values."""
        return self._y

    @property
    def is_failed(self) -> bool:
        """Return if data set was failed."""
        return self._is_failed

    @property
    def is_modified(self) -> bool:
        """Return if data set was modified."""
        return self._is_modified

    @property
    def freq(self) -> Optional[pd.DateOffset]:
        """Return the forecast frequency."""
        return self._freq
