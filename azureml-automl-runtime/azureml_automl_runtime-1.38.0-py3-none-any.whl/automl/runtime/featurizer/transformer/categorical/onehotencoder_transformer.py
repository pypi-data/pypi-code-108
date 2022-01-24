# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Transforms column using a label encoder to encode categories into numbers."""
from typing import Optional, Any, List
import logging
from sklearn.preprocessing import OneHotEncoder
import numpy as np
import pandas as pd

from azureml.automl.core import _codegen_utilities
from azureml.automl.core.constants import SupportedTransformersInternal as _SupportedTransformersInternal
from azureml.automl.core.shared import constants
from azureml.automl.core.shared.logging_utilities import function_debug_log_wrapped
from azureml.automl.runtime.shared.model_wrappers import _AbstractModelWrapper
from azureml.automl.runtime.shared.types import DataSingleColumnInputType, DataInputType
from ..automltransformer import AutoMLTransformer


class OneHotEncoderTransformer(AutoMLTransformer, _AbstractModelWrapper):
    """Convert input to one hot encoded vector."""

    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize for onehotencoding transform.

        :param args: args for transform.
        :param kwargs: kwargs for transform.
        :return:
        """
        super().__init__()
        if 'dtype' not in kwargs:
            kwargs['dtype'] = np.uint8
        self._onehotencoder = OneHotEncoder(**kwargs)
        self._transformer_name = _SupportedTransformersInternal.OneHotEncoder

    def __repr__(self):
        params = self.get_params()
        dtype = params.pop("dtype", np.uint8)
        return _codegen_utilities.generate_repr_str(self.__class__, params,
                                                    dtype="{}.{}".format(dtype.__module__, dtype.__name__))

    def get_params(self, deep=True):
        return self._onehotencoder.get_params(deep)

    def _get_imports(self):
        params = self.get_params(deep=False)
        dtype = params.pop("dtype", np.uint8)
        return super()._get_imports() + [
            _codegen_utilities.get_import(dtype)
        ]

    def _get_transformer_name(self) -> str:
        return self._transformer_name

    def _to_dict(self):
        """
        Create dict from transformer for serialization usage.

        :return: a dictionary
        """
        dct = super(OneHotEncoderTransformer, self)._to_dict()
        dct['id'] = "onehotencoder"
        dct['type'] = 'categorical'

        return dct

    @function_debug_log_wrapped()
    def fit(self, x: DataInputType, y: Optional[DataSingleColumnInputType] = None) -> "OneHotEncoderTransformer":
        """
        Fit function for label encoding transform which learns the labels.

        :param x: Input array of values to be encoded.
        :type x: pandas.DataFrame or numpy.ndarray
        :param y: Target values.
        :type y: numpy.ndarray
        :return: The instance object: self.
        """
        if isinstance(x, np.ndarray) and len(x.shape) == 1:
            x = x.reshape(x.shape[0], 1)
        if isinstance(x, pd.Series):
            x = pd.DataFrame(x)
        self._onehotencoder.fit(x)
        return self

    @function_debug_log_wrapped()
    def transform(self, x: DataInputType) -> DataInputType:
        """
        Transform categorical data to onehotencoded value.

        :param x: Input array.
        :type x: pandas.DataFrame or numpy.ndarray
        :return: OneHotEncoded array.
        """
        if isinstance(x, np.ndarray) and len(x.shape) == 1:
            x = x.reshape(x.shape[0], 1)
        if isinstance(x, pd.Series):
            x = pd.DataFrame(x)
        return self._onehotencoder.transform(x)

    def get_model(self) -> OneHotEncoder:
        """
        Return OneHotEncoder model.

        :return: OneHotEncoder model.
        """
        return self._onehotencoder

    def get_feature_names(self) -> List[str]:
        """
        Return names of categories encoded.

        :return: List of encoded properties.
        """
        return list(self._onehotencoder.categories_[0])
