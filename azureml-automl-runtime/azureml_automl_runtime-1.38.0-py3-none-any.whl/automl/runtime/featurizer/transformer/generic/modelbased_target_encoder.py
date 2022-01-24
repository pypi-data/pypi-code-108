# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Generic target encoder."""
from typing import Any, cast, Dict, Optional, Type
import logging

import numpy as np
from azureml._common._error_definition import AzureMLError
from azureml._common._error_definition.user_error import ArgumentBlankOrEmpty
from sklearn.base import BaseEstimator
from sklearn.naive_bayes import MultinomialNB
from azureml.automl.core.shared.exceptions import ConfigException
from ..automltransformer import AutoMLTransformer
from azureml.automl.core import _codegen_utilities
from azureml.automl.core.shared.logging_utilities import function_debug_log_wrapped
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.runtime.shared.model_wrappers import _AbstractModelWrapper
from azureml.automl.runtime.shared.types import DataSingleColumnInputType


logger = logging.getLogger(__name__)


class ModelBasedTargetEncoder(AutoMLTransformer, _AbstractModelWrapper):
    """Generic target encoder."""

    def __init__(self,
                 model_class: 'Type[BaseEstimator]',
                 model_params: Optional[Dict[str, Any]] = None) -> None:
        """Construct the target encoder.

        :param model_class: The class to be instantiated for the model.
        :param model_params: Params to be passed to the model when initiating.
        """
        super().__init__()

        self._model_class = model_class
        self._model_params = model_params or {}
        self._model = None                              # type: Optional[BaseEstimator]

    def __repr__(self):
        params = {
            "model_params": self._model_params
        }
        return _codegen_utilities.generate_repr_str(self.__class__, params, model_class=self._model_class.__name__)

    def _get_imports(self):
        return [(self._model_class.__module__, self._model_class.__name__, self._model_class)]

    def _to_dict(self):
        """
        Create dict from transformer for  serialization usage.

        :return: a dictionary
        """
        dct = super(ModelBasedTargetEncoder, self)._to_dict()
        if self._model_class and self._model_class == MultinomialNB:
            dct['id'] = "naive_bayes"
        else:
            dct['id'] = "text_target_encoder"
        if self._model_class:
            dct['kwargs']['model_class'] = "{}.{}".format(str(self._model_class.__module__),
                                                          self._model_class.__name__)
        if self._model_params and len(self._model_params) > 0:
            dct['kwargs']['model_params'] = self._model_params
        dct['type'] = 'text'

        return dct

    @function_debug_log_wrapped()
    def fit(self, X: DataSingleColumnInputType, y: Optional[DataSingleColumnInputType] = None) \
            -> "ModelBasedTargetEncoder":
        """
        Instantiate and train on the input data.

        :param X: The data to transform.
        :param y: Target values.
        :return: The instance object: self.
        """
        self._model = self._model_class(**self._model_params)
        self._model.fit(X, y)
        return self

    @function_debug_log_wrapped()
    def transform(self, X: DataSingleColumnInputType) -> np.ndarray:
        """
        Transform data x.

        :param X: The data to transform.
        :return: Prediction probability values from input model.
        """
        # TODO How do we do this in case of regression.
        if X is not None and self._model is not None:
            return cast(np.ndarray, self._model.predict_proba(X))
        else:
            return np.array([])

    def get_model(self):
        """
        Return the inner model object.

        :return: An inner model object.
        """
        return self._model
