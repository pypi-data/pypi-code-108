# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Add boolean imputation marker for values that are imputed."""
from typing import Any

import pandas as pd

from azureml.automl.core.shared.logging_utilities import function_debug_log_wrapped
from ..automltransformer import AutoMLTransformer
from azureml.automl.core.constants import SupportedTransformersInternal as _SupportedTransformersInternal


class ImputationMarker(AutoMLTransformer):
    """Add boolean imputation marker for values that are imputed."""

    def __init__(self) -> None:
        """
        Initialize the ImputationMarker.
        """
        super().__init__()
        self._transformer_name = _SupportedTransformersInternal.ImputationMarker

    def _get_transformer_name(self) -> str:
        return self._transformer_name

    def _to_dict(self):
        """
        Create dict from transformer for  serialization usage.

        :return: a dictionary
        """
        dct = super(ImputationMarker, self)._to_dict()
        dct['id'] = "imputation_marker"
        dct['type'] = "generic"

        return dct

    @function_debug_log_wrapped()
    def fit(self, x, y=None):
        """
        Fit function for imputation marker transform.

        :param x: Input array of integers or strings.
        :type x: numpy.ndarray or pandas.core.series.Series
        :param y: Target values.
        :type y: numpy.ndarray
        :return: The instance object: self.
        """
        return self

    @function_debug_log_wrapped()
    def transform(self, x):
        """
        Transform function for imputation marker.

        :param x: Input array of integers or strings.
        :type x: numpy.ndarray or pandas.core.series.Series
        :return: Boolean array having True where the value is not present.
        """
        return pd.isnull(x).values
