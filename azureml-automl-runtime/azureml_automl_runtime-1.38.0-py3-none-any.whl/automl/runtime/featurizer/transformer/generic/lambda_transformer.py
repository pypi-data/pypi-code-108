# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Lambda function based transformer."""
from typing import Any, cast, Callable, Dict, Optional, Union
import dill
import logging

import numpy as np

from azureml.automl.core.shared.logging_utilities import function_debug_log_wrapped
from ..automltransformer import AutoMLTransformer
from azureml.automl.core.constants import SupportedTransformersInternal as _SupportedTransformersInternal


class LambdaTransformer(AutoMLTransformer):
    """
    Transforms column through a lambda function.

    :param func: The lambda function to use in the transformation.
    :type func: Callable
    """

    def __init__(self, func: Union[bytes, Callable[[np.ndarray], Any]] = lambda x: x):
        """
        Construct the LambdaTransformer.

        :param func: The lambda function to use in the transformation.
        :return:
        """
        super().__init__()
        if callable(func):
            self.func = func
        else:
            self.func = cast(Callable[[np.ndarray], Any], dill.loads(func))

        self._transformer_name = _SupportedTransformersInternal.LambdaTransformer

    def get_params(self, deep: bool = True) -> Dict[str, Any]:
        params = cast(Dict[str, Any], super().get_params(deep))
        params["func"] = dill.dumps(self.func)
        return params

    def _get_transformer_name(self) -> str:
        return self._transformer_name

    def __getstate__(self):
        """
        Overriden to remove func object when pickling.

        :return: this object's state as a dictionary
        """
        state = super(LambdaTransformer, self).__getstate__()
        newstate = {**state, **self.__dict__}
        newstate['func'] = None
        return newstate

    def _to_dict(self):
        """
        Create dict from transformer for  serialization usage.

        :return: a dictionary
        """
        dct = super(LambdaTransformer, self)._to_dict()
        dct['id'] = "lambda_featurizer"
        dct['type'] = "generic"

        return dct

    @function_debug_log_wrapped()
    def fit(self, x, y=None):
        """
        Fit function for lambda transform.

        :param x: Input array.
        :type x: numpy.ndarray
        :param y: Target values.
        :type y: numpy.ndarray
        :return: The instance object: self.
        """
        return self

    @function_debug_log_wrapped()
    def transform(self, x):
        """
        Lambda transform which calls the lambda function over the input.

        :param x: Input array.
        :type x: numpy.ndarray
        :return: Result of lambda transform.
        """
        return self.func(x)
