# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
import numpy as np
import pandas as pd
import random

from typing import List, Optional

from azureml._common._error_definition import AzureMLError
from azureml.exceptions import AzureMLException

from azureml.responsibleai.common._errors.error_definitions import SubsamplingError
from azureml.responsibleai.tools._common.constants import SUBSAMPLE_SIZE


_logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)


class Subsample:
    """
    Helper for subsampling the various bits of data to be persisted as part of a Model Analysis. This class is
    currently unused as we are limiting test datasets to 5k rows, and UI does not need train data.
    """

    def __init__(self,
                 data: pd.DataFrame,
                 y_pred: np.ndarray,
                 y_proba: Optional[pd.DataFrame],
                 X_column_names: List[str],
                 target_column_name: str):
        self.data = data
        self.y_pred = pd.DataFrame(y_pred, columns=[target_column_name])
        self.y_proba = y_proba
        self.X_column_names = X_column_names
        self.target_column_name = target_column_name
        self._sample_indices = None      # type: Optional[List[int]]
        self._X_subsample = None         # type: Optional[pd.DataFrame]
        self._y_actual_subsample = None  # type: Optional[pd.DataFrame]
        self._y_pred_subsample = None    # type: Optional[pd.DataFrame]
        self._y_proba_subsample = None   # type: Optional[pd.DataFrame]

    def _take_subsamples(self) -> None:
        """This is a naive implementation, it should be replaced with a better implementation."""
        length = self.data.shape[0]
        self._sample_indices = list(range(length))
        if SUBSAMPLE_SIZE < length:
            _logger.info("The data contains {} samples which is more than the subsample size {}, "
                         "subsampling the data.".format(length, SUBSAMPLE_SIZE))
            self._sample_indices = random.sample(self._sample_indices, SUBSAMPLE_SIZE)
            self._sample_indices.sort()
            data_subsample = self.data.take(self._sample_indices)
            data_subsample = data_subsample.reset_index().drop(columns='index')
            self._y_pred_subsample = self.y_pred.take(self._sample_indices)
            if self.y_proba is not None:
                self._y_proba_subsample = self.y_proba.take(self._sample_indices)
                self._y_proba_subsample = self._y_proba_subsample.reset_index().drop(columns='index')
            else:
                self._y_proba_subsample = None
        else:
            _logger.info("The data contains {} samples which is less than the subsample size {}, "
                         "skipping subsampling.".format(length, SUBSAMPLE_SIZE))
            data_subsample = self.data
            self._y_pred_subsample = self.y_pred
            self._y_proba_subsample = self.y_proba

        self._X_subsample = data_subsample.drop(columns=[self.target_column_name])
        self._y_actual_subsample = data_subsample.drop(columns=self.X_column_names)

    @property
    def sample_indices(self) -> List[int]:
        if self._sample_indices is None:
            self._take_subsamples()
        if self._sample_indices is None:
            # _take_subsamples guarantees this is set, but typechecking gate doesn't understand
            raise AzureMLException._with_error(AzureMLError.create(SubsamplingError))
        return self._sample_indices

    @property
    def X_subsample(self) -> pd.DataFrame:
        if self._X_subsample is None:
            self._take_subsamples()
        return self._X_subsample

    @property
    def y_actual_subsample(self) -> pd.DataFrame:
        if self._y_actual_subsample is None:
            self._take_subsamples()
        return self._y_actual_subsample

    @property
    def y_pred_subsample(self) -> pd.DataFrame:
        if self._y_pred_subsample is None:
            self._take_subsamples()
        return self._y_pred_subsample

    @property
    def y_proba_subsample(self) -> Optional[pd.DataFrame]:
        # y_proba can be None in the case of a non-classification problem
        if self._y_proba_subsample is None and self.y_proba is not None:
            self._take_subsamples()
        return self._y_proba_subsample
