# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Base objects for Transformers and Estimators."""
from typing import Any, Dict
from abc import ABCMeta

from sklearn.base import BaseEstimator, TransformerMixin
from azureml.automl.core import _codegen_utilities


class AzureMLForecastEstimatorBase(BaseEstimator, metaclass=ABCMeta):
    """Base estimator for all AzureMLForecastSDK."""

    def __repr__(self):
        return _codegen_utilities.generate_repr_str(self.__class__, self.get_params(deep=False))

    """
    def fit(self, X, y):
        A reference implementation of a fitting function

        Parameters
        ----------
        X : array-like or sparse matrix of shape = [n_samples, n_features]
            The training input samples.
        y : array-like, shape = [n_samples] or [n_samples, n_outputs]
            The target values (class labels in classification, real numbers in
            regression).

        Returns
        -------
        self : object
            Returns self.

        X, y = check_X_y(X, y)
        # Return the estimator
        return self


    def predict(self, X):
        A reference implementation of a predicting function.

        Parameters
        ----------
        X : array-like of shape = [n_samples, n_features]
            The input samples.

        Returns
        -------
        y : array of shape = [n_samples]
            Returns :math:`x^2` where :math:`x` is the first column of `X`.
        X = check_array(X)
        return X[:, 0]**2
        pass
    """


class AzureMLForecastTransformerBase(AzureMLForecastEstimatorBase, TransformerMixin):
    """
    Base transformer for AzureMLForecastSDK ..

    :param demo_param: str, optional
        A parameter used for demonstration.

    :Attributes:
    input_shape: tuple
        The shape the data passed to :meth:`fit`

    def fit(self, X, y):
        A reference implementation of a fitting function for a transformer.

        :Parameters:
        X : array-like or sparse matrix of shape = [n_samples, n_features]
            The training input samples.
        y : None
            There is no need of a target in a transformer, yet the pipeline API
            requires this parameter.

        :Returns:
        self: object
            Returns self.

    def transform(self, X):
        A reference implementation of a transform function.

        :Parameters:
        X : array-like of shape = [n_samples, n_features]
            The input samples.

        :Returns:
        X_transformed : array of int of shape = [n_samples, n_features]
            The array containing the element-wise square roots of the values
            in `X`

        # Check is fit had been called
        check_is_fitted(self, ['input_shape_'])

        # Input validation
        X = check_array(X)

        # Check that the input is of the same shape as the one passed
        # during fit.
        if X.shape != self.input_shape_:
            raise ValueError('Shape of input is different from what was seen'
                             'in `fit`')
        return np.sqrt(X)
    """


class _GrainBasedStatefulTransformer(TransformerMixin):
    """Defines transformers which maintain per grain state."""
    pass
