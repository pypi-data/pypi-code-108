# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Convenience names for long types."""
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, Union

T = TypeVar('T')

# Convenience type for function inputs to DataFrame.apply (either a function or the name of one)
DataFrameApplyFunction = Union['Callable[..., Optional[Any]]', str]

# Convenience type representing transformer params for input columns
# First param: set of column inputs transformer takes (e.g. MiniBatchKMeans takes multiple columns as input).
# Second param: dictionary of parameter options and value pairs to apply for the transformation.
ColumnTransformerParamType = Tuple[List[str], Dict[str, Any]]

# Convenience type for featurization summary
FeaturizationSummaryType = List[Dict[str, Optional[Any]]]

# Convenience type for grains
GrainType = Union[Tuple[str], str, List[str]]
