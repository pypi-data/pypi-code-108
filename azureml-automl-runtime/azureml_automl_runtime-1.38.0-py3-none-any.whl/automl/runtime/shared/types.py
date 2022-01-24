# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Convenience names for long types."""
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, Union

import numpy as np
import pandas as pd
import scipy
from sklearn.base import TransformerMixin

import azureml.dataprep as dprep
from azureml.automl.core.shared.types import (T,
                                              DataFrameApplyFunction,
                                              ColumnTransformerParamType,
                                              FeaturizationSummaryType,
                                              GrainType)


# Convenience type for general data input
CoreDataInputType = Union[np.ndarray, pd.DataFrame, scipy.sparse.spmatrix]
DataInputType = Union[CoreDataInputType, dprep.Dataflow]

# Convenience type for single column data input
CoreDataSingleColumnInputType = Union[np.ndarray, pd.Series, pd.Categorical]
DataSingleColumnInputType = Union[CoreDataSingleColumnInputType, dprep.Dataflow]

# Convenience type representing transformers
# First param: column selector, either a column name string or a list of column name strings.
# Second param: list of sklearn transformation pipeline.
# Third param: dictionary of parameter options and value pairs to apply for the transformation.
TransformerType = Tuple[Union[str, List[str]], List[TransformerMixin], Dict[str, str]]
