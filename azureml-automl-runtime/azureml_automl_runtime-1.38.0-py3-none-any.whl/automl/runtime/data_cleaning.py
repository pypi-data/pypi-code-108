# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Dataset row dropping pre-featurization."""
import logging
import scipy

import numpy as np
import pandas as pd

from typing import Optional, Tuple, Union

from azureml.automl.core.constants import TransformerParams, SupportedTransformers
from azureml.automl.core.featurization import FeaturizationConfig
from azureml.automl.runtime.shared import utilities as runtime_utilities
from azureml.automl.runtime.shared.types import CoreDataInputType, DataSingleColumnInputType


logger = logging.getLogger(__name__)


def _remove_nan_rows_in_X_y(
        X: CoreDataInputType,
        y: DataSingleColumnInputType,
        sample_weight: Optional[np.ndarray] = None,
        is_timeseries: bool = False,
        target_column: Optional[str] = None,
        featurization_config: Optional[Union[FeaturizationConfig, str]] = None
) -> Tuple[CoreDataInputType, DataSingleColumnInputType, Optional[DataSingleColumnInputType]]:
    """Remove the NaN columns in y and the corresponding rows in X."""
    X_new = X
    y_new = y
    sample_weight_new = sample_weight

    if X is not None and y is not None and _remove_y_nan_needed(is_timeseries, target_column, featurization_config):
        if isinstance(y, pd.DataFrame):
            y = y.values.ravel()
        nan_y_index = runtime_utilities._get_indices_missing_labels_output_column(y)

        logger.info("Inspecting target column for missing values.")

        if len(nan_y_index) > 0:
            logger.info("Dropping rows with invalid or empty values [np.nan, 'nan', '', None] in the target column.")
            y_new = np.delete(y, nan_y_index)
            if scipy.sparse.issparse(X):
                X_new = X_new.toarray()
            if isinstance(X_new, pd.DataFrame):
                X_new = X_new.iloc[list(set(range(X_new.shape[0])) - set(nan_y_index))]
            else:
                X_new = np.delete(X_new, nan_y_index, axis=0)
            if sample_weight is not None and sample_weight_new is not None:
                if scipy.sparse.issparse(sample_weight):
                    sample_weight_new = sample_weight_new.toarray()
                sample_weight_new = np.delete(sample_weight_new, nan_y_index, axis=0)
            # if input is sparse, convert back to csr
            if scipy.sparse.issparse(X):
                X_new = scipy.sparse.csr_matrix(X_new)
            if scipy.sparse.issparse(sample_weight):
                sample_weight_new = scipy.sparse.csr_matrix(sample_weight_new)
    return X_new, y_new, sample_weight_new


def _remove_y_nan_needed(is_timeseries: bool,
                         target_column: Optional[str],
                         featurization_config: Optional[Union[FeaturizationConfig, str]]) -> bool:
    if (not is_timeseries or featurization_config is None
            or not isinstance(featurization_config, FeaturizationConfig)
            or featurization_config.transformer_params is None
            or featurization_config.transformer_params.get(SupportedTransformers.Imputer) is None):
        return True
    for cols, params in featurization_config.transformer_params.get(SupportedTransformers.Imputer):
        if params.get(TransformerParams.Imputer.Strategy) != TransformerParams.Imputer.Constant \
                and target_column in cols:
            return False
    return True
