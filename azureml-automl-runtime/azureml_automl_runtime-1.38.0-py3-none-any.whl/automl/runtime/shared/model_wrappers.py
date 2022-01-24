# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module to wrap models that don't accept parameters such as 'fraction of the dataset'."""
import copy
import importlib
import logging
import math
import os
import pickle
import uuid
import warnings
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union, cast
from typing import TYPE_CHECKING
import lightgbm as lgb
import nimbusml
import numpy as np
import pandas as pd
import scipy
import sklearn
import sklearn.decomposition
import sklearn.naive_bayes
import sklearn.pipeline
from azureml._common._error_definition import AzureMLError
from azureml.automl.core import _codegen_utilities
from azureml.automl.core.automl_base_settings import AutoMLBaseSettings
from azureml.automl.core.forecasting_parameters import ForecastingParameters
from azureml.automl.core.shared import constants
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    AutoMLInternal,
    DataShapeMismatch,
    ForecastingEmptyDataAfterAggregation,
    ForecastHorizonExceeded,
    ForecastFitNotSupported,
    ForecastPredictNotSupported,
    GenericTransformError,
    InsufficientMemory,
    InvalidArgumentType,
    MissingColumnsInData,
    PandasDatetimeConversion,
    PowerTransformerInverseTransform,
    QuantileRange,
    TimeseriesContextAtEndOfY,
    TimeseriesDfContainsNaN,
    TimeseriesDfInvalidArgFcPipeYOnly,
    TimeseriesDfInvalidArgOnlyOneArgRequired,
    TimeseriesGrainAbsentNoDataContext,
    TimeseriesGrainAbsentNoGrainInTrain,
    TimeseriesGrainAbsentNoLastDate,
    TimeseriesInsufficientDataForecast,
    TimeseriesMissingValuesInY,
    TimeseriesNoDataContext,
    TimeseriesNonContiguousTargetColumn,
    TimeseriesNothingToPredict,
    TimeseriesNoUsableGrains,
    TimeseriesWrongShapeDataEarlyDest,
    TimeseriesWrongShapeDataSizeMismatch,
    TransformerYMinGreater)
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.constants import TimeSeries, TimeSeriesInternal
from azureml.automl.core.shared.exceptions import (AutoMLException,
                                                   DataException,
                                                   FitException,
                                                   PredictionException,
                                                   TransformException,
                                                   UntrainedModelException,
                                                   UserException,
                                                   ValidationException,
                                                   ResourceException)
from azureml.automl.core.shared.forecasting_exception import (
    ForecastingDataException, ForecastingConfigException
)
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared.types import GrainType
from azureml.automl.core.shared.utilities import get_min_points
from azureml.automl.runtime import _freq_aggregator
from azureml.automl.runtime._time_series_data_config import TimeSeriesDataConfig
from azureml.automl.runtime.column_purpose_detection._time_series_column_helper import convert_check_grain_value_types
from azureml.automl.runtime.frequency_fixer import fix_data_set_regularity_may_be
from azureml.automl.runtime.shared import time_series_data_frame as tsdf
from azureml.automl.runtime.shared import forecasting_utils

from azureml.automl.runtime.shared.score import _scoring_utilities
from azureml.automl.runtime.shared.types import DataInputType
from azureml.automl.core.constants import PredictionTransformTypes as _PredictionTransformTypes

from packaging import version
from pandas.tseries.frequencies import to_offset
from scipy.special import inv_boxcox
from scipy.stats import norm, boxcox
from sklearn import preprocessing
from sklearn.base import (BaseEstimator, ClassifierMixin, RegressorMixin,
                          TransformerMixin, clone)
from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import TruncatedSVD
from sklearn.ensemble import VotingClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold, KFold
from sklearn.pipeline import Pipeline as SKPipeline
from sklearn.preprocessing import LabelEncoder, Normalizer
from sklearn.utils.metaestimators import _BaseComposition


try:
    import xgboost as xgb

    xgboost_present = True
except ImportError:
    xgboost_present = False

try:
    import catboost as catb

    catboost_present = True
except ImportError:
    catboost_present = False


try:
    import torch
    from azureml.automl.runtime.shared._tabularnetworks import trainer as tabnet

    tabnet_present = True
except ImportError:
    tabnet_present = False

# NOTE:
# Here we import type checking only for type checking time.
# during runtime TYPE_CHECKING is set to False.
if TYPE_CHECKING:
    from azureml._common._error_definition.error_definition import ErrorDefinition
    from azureml.automl.runtime.featurizer.transformer.timeseries.timeseries_transformer import TimeSeriesTransformer

logger = logging.getLogger(__name__)

_generic_fit_error_message = 'Failed to fit the input data using {}'
_generic_transform_error_message = 'Failed to transform the input data using {}'
_generic_prediction_error_message = 'Failed to predict the test data using {}'


class _AbstractModelWrapper(ABC):
    """Abstract base class for the model wrappers."""

    def __init__(self):
        """Initialize AbstractModelWrapper class."""
        pass

    @abstractmethod
    def get_model(self):
        """
        Abstract method for getting the inner original model object.

        :return: An inner model object.
        """
        raise NotImplementedError


class LightGBMClassifier(BaseEstimator, ClassifierMixin, _AbstractModelWrapper):
    """
    LightGBM Classifier class.

    :param random_state:
        RandomState instance or None, optional (default=None)
        If int, random_state is the seed used by the random number generator;
        If RandomState instance, random_state is the random number generator;
        If None, the random number generator is the RandomState instance used
        by `np.random`.
    :type random_state: int or np.random.RandomState
    :param n_jobs: Number of parallel threads.
    :type n_jobs: int
    :param kwargs: Other parameters
        Check http://lightgbm.readthedocs.io/en/latest/Parameters.html
        for more parameters.
    """

    DEFAULT_MIN_DATA_IN_LEAF = 20

    def __init__(self, random_state=None, n_jobs=1, problem_info=None, **kwargs):
        """
        Initialize LightGBM Classifier class.

        :param random_state:
            RandomState instance or None, optional (default=None)
            If int, random_state is the seed used by the random number
            generator.
            If RandomState instance, random_state is the random number
            generator.
            If None, the random number generator is the RandomState instance
            used by `np.random`.
        :type random_state: int or np.random.RandomState
        :param n_jobs: Number of parallel threads.
        :type n_jobs: int
        :param problem_info: Problem metadata.
        :type problem_info: ProblemInfo
        :param kwargs: Other parameters
            Check http://lightgbm.readthedocs.io/en/latest/Parameters.html
            for more parameters.
        """
        self._kwargs = kwargs.copy()
        self.params = kwargs
        self.params['random_state'] = random_state
        self.params['n_jobs'] = n_jobs
        if problem_info is not None and problem_info.gpu_training_param_dict is not None and \
                problem_info.gpu_training_param_dict.get("processing_unit_type", "cpu") == "gpu":
            self.params['device'] = 'gpu'

            # We have seen lightgbm gpu fit can fail on bin size too big, the bin size during fit may come from
            # dataset / the pipeline spec itself. With one hot encoding, the categorical features from dataset should
            # not have big cardinality that causing the bin size too big, so the only source is pipeline itself. Cap to
            # 255 max if it exceeded the size.
            if self.params.get('max_bin', 0) > 255:
                self.params['max_bin'] = 255
        self.model = None  # type: Optional[sklearn.base.BaseEstimator]
        self._min_data_str = "min_data_in_leaf"
        self._min_child_samples = "min_child_samples"
        self._problem_info = problem_info.clean_attrs(['gpu_training_param_dict',
                                                       'dataset_categoricals']) if problem_info is not None else None

        # Both 'min_data_in_leaf' and 'min_child_samples' are required
        Contract.assert_true(
            self._min_data_str in kwargs or self._min_child_samples in kwargs,
            message="Failed to initialize LightGBMClassifier. Neither min_data_in_leaf nor min_child_samples passed",
            target="LightGBMClassifier", log_safe=True
        )

    def get_model(self):
        """
        Return LightGBM Classifier model.

        :return: Returns the fitted model if fit method has been called.
        Else returns None.
        """
        return self.model

    def fit(self, X: np.ndarray, y: np.ndarray, **kwargs: Any) -> "LightGBMClassifier":
        """
        Fit function for LightGBM Classifier model.

        :param X: Input data.
        :param y: Input target values.
        :param kwargs: other parameters
            Check http://lightgbm.readthedocs.io/en/latest/Parameters.html
            for more parameters.
        :return: Self after fitting the model.
        """
        N = X.shape[0]
        args = dict(self.params)
        if (self._min_data_str in args):
            if (self.params[self._min_data_str]
                    == LightGBMClassifier.DEFAULT_MIN_DATA_IN_LEAF):
                args[self._min_child_samples] = self.params[
                    self._min_data_str]
            else:
                args[self._min_child_samples] = int(
                    self.params[self._min_data_str] * N) + 1
            del args[self._min_data_str]
        else:
            min_child_samples = self.params[self._min_child_samples]
            if min_child_samples > 0 and min_child_samples < 1:
                # we'll convert from fraction to int as that's what LightGBM expects
                args[self._min_child_samples] = int(
                    self.params[self._min_child_samples] * N) + 1
            else:
                args[self._min_child_samples] = min_child_samples

        verbose_str = "verbose"
        if verbose_str not in args:
            args[verbose_str] = -10

        if self._problem_info is not None and self._problem_info.dataset_categoricals is not None:
            n_categorical = len(np.where(self._problem_info.dataset_categoricals)[0])
            kwargs['categorical_feature'] = [i for i in range(n_categorical)]

        self.model = lgb.LGBMClassifier(**args)
        try:
            self.model.fit(X, y, **kwargs)
        except Exception as e:
            # std::bad_alloc shows up as the error message if memory allocation fails. Unfortunately there is no
            # better way to check for this due to how LightGBM raises exceptions
            if 'std::bad_alloc' in str(e):
                raise ResourceException._with_error(
                    AzureMLError.create(InsufficientMemory, target='LightGbm'), inner_exception=e) from e
            raise FitException.from_exception(e, has_pii=True, target="LightGbm"). \
                with_generic_msg(_generic_fit_error_message.format(self.__class__.__name__))

        self.classes_ = np.unique(y)

        return self

    def __setstate__(self, state):
        if "_kwargs" not in state:
            state["_kwargs"] = {}
        if "_problem_info" in state:
            state["_problem_info"] = state["_problem_info"].clean_attrs(
                ['gpu_training_param_dict',
                 'dataset_categoricals']) if state["_problem_info"] is not None else None

        super().__setstate__(state)

    def __getstate__(self):
        state = self.__dict__

        # Backwards compatibility to handle inferencing on old SDK
        # pipeline_categoricals in ProblemInfo will always be None since we cleaned it, so we can inject it as part
        # of model init instead of fit
        if self._problem_info is not None and self._problem_info.dataset_categoricals is not None:
            n_categorical = len(np.where(self._problem_info.dataset_categoricals)[0])
            state["params"]["categorical_feature"] = [i for i in range(n_categorical)]

        return state

    def get_params(self, deep: bool = True) -> Dict[str, Any]:
        """
        Return parameters for LightGBM Regressor model.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: bool
        :return: Parameters for LightGBM Regressor model.
        """
        params = self._kwargs.copy()
        params["random_state"] = self.params["random_state"]
        params["n_jobs"] = self.params["n_jobs"]
        params["problem_info"] = self._problem_info

        return params

    def __repr__(self) -> str:
        params = self.get_params(deep=False)
        return _codegen_utilities.generate_repr_str(self.__class__, params)

    def _get_imports(self) -> List[Tuple[str, str, Any]]:
        if self._problem_info:
            return [
                _codegen_utilities.get_import(self._problem_info)
            ]
        else:
            return []

    def predict(self, X):
        """
        Prediction function for LightGBM Classifier model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return: Prediction values from LightGBM Classifier model.
        """
        try:
            return self.model.predict(X)
        except Exception as e:
            raise PredictionException.from_exception(e, target='LightGbm', has_pii=True). \
                with_generic_msg(_generic_prediction_error_message.format(self.__class__.__name__))

    def predict_proba(self, X):
        """
        Prediction class probabilities for X for LightGBM Classifier model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return: Prediction probability values from LightGBM Classifier model.
        """
        try:
            predict_probas = self.model.predict_proba(X)
            if self.classes_ is not None and len(self.classes_) == 1:
                # Select only the first class since a dummy class is added when the train has only 1 class.
                return predict_probas[:, [0]]

            return predict_probas
        except Exception as e:
            raise PredictionException.from_exception(e, target='LightGbm', has_pii=True). \
                with_generic_msg(_generic_prediction_error_message.format(self.__class__.__name__))


class XGBoostClassifier(BaseEstimator, ClassifierMixin, _AbstractModelWrapper):
    """
    XGBoost Classifier class.

    :param random_state:
        RandomState instance or None, optional (default=None)
        If int, random_state is the seed used by the random number generator;
        If RandomState instance, random_state is the random number generator;
        If None, the random number generator is the RandomState instance used
        by `np.random`.
    :type random_state: int or np.random.RandomState
    :param n_jobs: Number of parallel threads.
    :type n_jobs: int
    :param kwargs: Other parameters
        Check https://xgboost.readthedocs.io/en/latest/parameter.html
        for more parameters.
    """

    def __init__(self, random_state=0, n_jobs=1, problem_info=None, **kwargs):
        """
        Initialize XGBoost Classifier class.

        :param random_state:
            RandomState instance or None, optional (default=None)
            If int, random_state is the seed used by the random number
            generator.
            If RandomState instance, random_state is the random number
            generator.
            If None, the random number generator is the RandomState instance
            used by `np.random`.
        :type random_state: int or np.random.RandomState
        :param n_jobs: Number of parallel threads.
        :type n_jobs: int
        :param kwargs: Other parameters
            Check https://xgboost.readthedocs.io/en/latest/parameter.html
            for more parameters.
        """
        self.params = kwargs.copy()
        self.params['random_state'] = random_state if random_state is not None else 0
        self.params['n_jobs'] = n_jobs
        self.params['verbosity'] = 0
        self.params = GPUHelper.xgboost_add_gpu_support(problem_info, self.params)
        self._kwargs = kwargs
        self._problem_info = problem_info.clean_attrs(['gpu_training_param_dict']) \
            if problem_info is not None else None
        self.model = None
        self.classes_ = None

        Contract.assert_true(
            xgboost_present, message="Failed to initialize XGBoostClassifier. xgboost is not installed, "
                                     "please install xgboost for including xgboost based models.",
            target='XGBoostClassifier', log_safe=True
        )

    def __setstate__(self, state):
        if "_kwargs" not in state:
            state["_kwargs"] = {}
        if "_problem_info" not in state:
            state["_problem_info"] = None
        state["_problem_info"] = state["_problem_info"].clean_attrs(
            ['gpu_training_param_dict']) if state["_problem_info"] is not None else None
        super().__setstate__(state)

    def __repr__(self) -> str:
        params = self.get_params(deep=False)
        params.update(self._kwargs)
        return _codegen_utilities.generate_repr_str(self.__class__, params)

    def _get_imports(self) -> List[Tuple[str, str, Any]]:
        if self._problem_info:
            return [
                _codegen_utilities.get_import(self._problem_info)
            ]
        else:
            return []

    def get_model(self):
        """
        Return XGBoost Classifier model.

        :return: Returns the fitted model if fit method has been called.
        Else returns None.
        """
        return self.model

    def fit(self, X, y, **kwargs):
        """
        Fit function for XGBoost Classifier model.

        :param X: Input data.
        :type X: numpy.ndarray
        :param y: Input target values.
        :type y: numpy.ndarray
        :param kwargs: other parameters
            Check https://xgboost.readthedocs.io/en/latest/parameter.html
            for more parameters.
        :return: Self after fitting the model.
        """
        args = dict(self.params)
        verbose_str = "verbose"
        if verbose_str not in args:
            args[verbose_str] = -10

        self.model = xgb.XGBClassifier(**args)
        try:
            self.model.fit(X, y, **kwargs)
        except Exception as e:
            raise FitException.from_exception(e, has_pii=True, target="Xgboost"). \
                with_generic_msg(_generic_fit_error_message.format(self.__class__.__name__))

        self.classes_ = np.unique(y)

        return self

    def get_params(self, deep=True):
        """
        Return parameters for XGBoost Classifier model.

        :param deep: If True, will return the parameters for this estimator and contained subobjects that are
            estimators.
        :type deep: bool
        :return: Parameters for the XGBoost classifier model.
        """
        if deep:
            if self.model:
                return self.model.get_params(deep)
            else:
                return self.params
        else:
            params = {
                "random_state": self.params["random_state"],
                "n_jobs": self.params["n_jobs"],
                "problem_info": self._problem_info
            }
            params.update(self._kwargs)
            return params

    def predict(self, X):
        """
        Prediction function for XGBoost Classifier model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return: Prediction values from XGBoost Classifier model.
        """
        if self.model is None:
            raise UntrainedModelException(target="Xgboost", has_pii=False)

        try:
            return self.model.predict(X)
        except Exception as e:
            raise PredictionException.from_exception(e, target="Xgboost", has_pii=True). \
                with_generic_msg(_generic_prediction_error_message.format(self.__class__.__name__))

    def predict_proba(self, X):
        """
        Prediction class probabilities for X for XGBoost Classifier model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return: Prediction probability values from XGBoost Classifier model.
        """
        if self.model is None:
            raise UntrainedModelException(target="Xgboost", has_pii=False)
        try:
            predict_probas = self.model.predict_proba(X)
            if self.classes_ is not None and len(self.classes_) == 1:
                # Select only the first class since a dummy class is added when the train has only 1 class.
                return predict_probas[:, [0]]

            return predict_probas
        except Exception as e:
            raise PredictionException.from_exception(e, target="Xgboost", has_pii=True). \
                with_generic_msg(_generic_prediction_error_message.format(self.__class__.__name__))


class CatBoostClassifier(ClassifierMixin, _AbstractModelWrapper):
    """Model wrapper for the CatBoost Classifier."""

    def __init__(self, random_state=0, thread_count=1, **kwargs):
        """
        Construct a CatBoostClassifier.

        :param random_state:
            RandomState instance or None, optional (default=None)
            If int, random_state is the seed used by the random number
            generator.
            If RandomState instance, random_state is the random number
            generator.
            If None, the random number generator is the RandomState instance
            used by `np.random`.
        :type random_state: int or np.random.RandomState
        :param n_jobs: Number of parallel threads.
        :type n_jobs: int
        :param kwargs: Other parameters
            Check https://catboost.ai/docs/concepts/python-reference_parameters-list.html
            for more parameters.
        """
        self.params = kwargs
        self.params['random_state'] = random_state if random_state is not None else 0
        self.params['thread_count'] = thread_count
        self.model = None

        Contract.assert_true(
            catboost_present, message="Failed to initialize CatBoostClassifier. CatBoost is not installed, "
                                      "please install CatBoost for including CatBoost based models.",
            target='CatBoostClassifier', log_safe=True
        )

    def __repr__(self):
        return _codegen_utilities.generate_repr_str(self.__class__, self.get_params(deep=False))

    def get_model(self):
        """
        Return CatBoostClassifier model.

        :return: Returns the fitted model if fit method has been called.
        Else returns None.
        """
        return self.model

    def fit(self, X, y, **kwargs):
        """
        Fit function for CatBoostClassifier model.

        :param X: Input data.
        :param y: Input target values.
        :param kwargs: Other parameters
            Check https://catboost.ai/docs/concepts/python-reference_parameters-list.html
            for more parameters.
        :return: Self after fitting the model.
        """
        args = dict(self.params)
        verbose_str = "verbose"
        if verbose_str not in args:
            args[verbose_str] = False

        self.model = catb.CatBoostClassifier(**args)

        try:
            self.model.fit(X, y, **kwargs)
        except Exception as e:
            raise FitException.from_exception(e, has_pii=True, target="CatBoostClassifier"). \
                with_generic_msg(_generic_fit_error_message.format(self.__class__.__name__))

        return self

    def get_params(self, deep=True):
        """
        Return parameters for the CatBoostClassifier model.

        :param deep: If True, returns the model parameters for sub-estimators as well.
        :return: Parameters for the CatBoostClassifier model.
        """
        if self.model and deep:
            return self.model.get_params(deep)
        else:
            return self.params

    def predict(self, X):
        """
        Predict the target based on the dataset features.

        :param X: Input data.
        :return: Model predictions.
        """
        if self.model is None:
            raise UntrainedModelException(target="CatBoostClassifier", has_pii=False)
        try:
            return self.model.predict(X)
        except Exception as e:
            raise PredictionException.from_exception(e, target="CatBoostClassifier", has_pii=True). \
                with_generic_msg(_generic_prediction_error_message.format(self.__class__.__name__))

    def predict_proba(self, X):
        """
        Predict the probability of each class based on the dataset features.

        :param X: Input data.
        :return: Model predicted probabilities per class.
        """
        if self.model is None:
            raise UntrainedModelException(target="CatBoostClassifier", has_pii=False)
        try:
            return self.model.predict_proba(X)
        except Exception as e:
            raise PredictionException.from_exception(e, target="CatBoostClassifier", has_pii=True). \
                with_generic_msg(_generic_prediction_error_message.format(self.__class__.__name__))


class TabnetClassifier(ClassifierMixin, _AbstractModelWrapper):
    """Model wrapper for the Tabnet Classifier."""

    def __init__(self, num_steps=3, hidden_features=16, epochs=10, learning_rate=0.03, problem_info=None, **kwargs):
        """
        Construct a TabnetClassifier.

        :param kwargs: Other parameters
        """
        self.params = kwargs
        self.params['num_steps'] = num_steps if num_steps is not None else 3
        self.params['hidden_features'] = hidden_features if hidden_features is not None else 16
        self.params['epochs'] = epochs if epochs is not None else 10
        self.params['learning_rate'] = learning_rate if learning_rate is not None else 0.03
        self.params['problem_info'] = problem_info
        self.model = None
        self.classes_ = None
        Contract.assert_true(
            tabnet_present, message="Failed to initialize TabnetClassifier. Tabnet is not installed, "
                                    "please install pytorch and Tabnet for including Tabnet based models.",
            target=self.__class__.__name__, log_safe=True
        )

    def __repr__(self):
        return _codegen_utilities.generate_repr_str(self.__class__, self.get_params(deep=False))

    def get_model(self):
        """
        Return TabnetClassifier model.

        :return: Returns the fitted model if fit method has been called.
        Else returns None.
        """
        return self.model

    def fit(self, X, y, **kwargs):
        """
        Fit function for TabnetClassifier model.

        :param X: Input data.
        :param y: Input target values.
        :param kwargs: Other parameters
        :return: Self after fitting the model.
        """
        args = dict(self.params)
        self.model = tabnet.TabnetClassifier(**args)

        try:
            self.model.fit(X, y, **kwargs)
        except Exception as e:
            raise FitException.from_exception(e, has_pii=True, target=self.__class__.__name__). \
                with_generic_msg(_generic_fit_error_message.format(self.__class__.__name__))

        self.classes_ = np.unique(y)

        return self

    def get_params(self, deep=True):
        """
        Return parameters for the TabnetClassifier model.

        :param deep: If True, returns the model parameters for sub-estimators as well.
        :return: Parameters for the TabnetClassifier model.
        """
        if self.model and deep:
            return self.model.get_params(deep)
        else:
            return self.params

    def predict(self, X):
        """
        Predict the target based on the dataset features.

        :param X: Input data.
        :return: Model predictions.
        """
        if self.model is None:
            raise UntrainedModelException(target=self.__class__.__name__, has_pii=False)
        try:
            return self.model.predict(X)
        except Exception as e:
            raise PredictionException.from_exception(e, target=self.__class__.__name__, has_pii=True). \
                with_generic_msg(_generic_prediction_error_message.format(self.__class__.__name__))

    def predict_proba(self, X):
        """
        Predict the probability of each class based on the dataset features.

        :param X: Input data.
        :return: Model predicted probabilities per class.
        """
        if self.model is None:
            raise UntrainedModelException(target=self.__class__.__name__, has_pii=False)
        try:
            return self.model.predict_proba(X)
        except Exception as e:
            raise PredictionException.from_exception(e, target=self.__class__.__name__, has_pii=True). \
                with_generic_msg(_generic_prediction_error_message.format(self.__class__.__name__))


class SparseNormalizer(TransformerMixin, _AbstractModelWrapper):
    """
    Normalizes rows of an input matrix. Supports sparse matrices.

    :param norm:
        Type of normalization to perform - l1’, ‘l2’, or ‘max’,
        optional (‘l2’ by default).
    :type norm: str
    """

    def __init__(self, norm="l2", copy=True):
        """
        Initialize function for Sparse Normalizer transformer.

        :param norm:
            Type of normalization to perform - l1’, ‘l2’, or ‘max’,
            optional (‘l2’ by default).
        :type norm: str
        """
        self.norm = norm
        self.norm_str = "norm"
        self.model = Normalizer(norm, copy=True)

    def __repr__(self):
        return repr(self.model)

    def _get_imports(self) -> List[Tuple[str, str, Any]]:
        return [_codegen_utilities.get_import(self.model)]

    def get_model(self):
        """
        Return Sparse Normalizer model.

        :return: Sparse Normalizer model.
        """
        return self.model

    def fit(self, X, y=None):
        """
        Fit function for Sparse Normalizer model.

        :param X: Input data.
        :type X: numpy.ndarray
        :param y: Input target values.
        :type y: numpy.ndarray
        :return: Returns self.
        """
        return self

    def get_params(self, deep=True):
        """
        Return parameters for Sparse Normalizer model.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :return: Parameters for Sparse Normalizer model.
        """
        params = {self.norm_str: self.norm}
        if self.model:
            params.update(self.model.get_params(deep))

        return params

    def transform(self, X):
        """
        Transform function for Sparse Normalizer model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return: Transformed output of Sparse Normalizer.
        """
        try:
            return self.model.transform(X)
        except Exception as e:
            raise TransformException.from_exception(
                e, has_pii=True, target="SparseNormalizer",
                reference_code='model_wrappers.SparseNormalizer.transform'). \
                with_generic_msg(_generic_transform_error_message.format(self.__class__.__name__))


class SparseScaleZeroOne(BaseEstimator, TransformerMixin, _AbstractModelWrapper):
    """Transforms the input data by appending previous rows."""

    def __init__(self):
        """Initialize Sparse Scale Transformer."""
        self.scaler = None
        self.model = None

    def get_model(self):
        """
        Return Sparse Scale model.

        :return: Sparse Scale model.
        """
        return self.model

    def fit(self, X, y=None):
        """
        Fit function for Sparse Scale model.

        :param X: Input data.
        :type X: scipy.sparse.spmatrix
        :param y: Input target values.
        :type y: numpy.ndarray
        :return: Returns self after fitting the model.
        """
        self.model = sklearn.preprocessing.MaxAbsScaler()
        try:
            self.model.fit(X)
            return self
        except Exception as e:
            raise FitException.from_exception(
                e, has_pii=True, target="SparseScaleZeroOne",
                reference_code='model_wrappers.SparseScaleZeroOne.fit'). \
                with_generic_msg(_generic_fit_error_message.format(self.__class__.__name__))

    def transform(self, X):
        """
        Transform function for Sparse Scale model.

        :param X: Input data.
        :type X: scipy.sparse.spmatrix
        :return: Transformed output of MaxAbsScaler.
        """
        if self.model is None:
            raise UntrainedModelException(target=SparseScaleZeroOne, has_pii=False)
        try:
            X = self.model.transform(X)
        except Exception as e:
            raise TransformException.from_exception(
                e, has_pii=True, target='SparseScaleZeroOne',
                reference_code='model_wrappers.SparseScaleZeroOne.transform'). \
                with_generic_msg(_generic_transform_error_message.format(self.__class__.__name__))
        X.data = (X.data + 1) / 2
        return X

    def get_params(self, deep=True):
        """
        Return parameters for Sparse Scale model.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: bool
        :return: Parameters for Sparse Scale model.
        """
        return {}


class PreprocWrapper(TransformerMixin, _AbstractModelWrapper):
    """Normalizes rows of an input matrix. Supports sparse matrices."""

    def __init__(self, cls, module_name=None, class_name=None, **kwargs):
        """
        Initialize PreprocWrapper class.

        :param cls:
        :param kwargs:
        """
        self.cls = cls
        if cls is not None:
            self.module_name = cls.__module__
            self.class_name = cls.__name__
        else:
            self.module_name = module_name
            self.class_name = class_name

        self.args = kwargs
        self.model = None

    def __repr__(self):
        params = self.get_params(deep=False)

        for param in ["module_name", "class_name"]:
            params.pop(param, None)

        return _codegen_utilities.generate_repr_str(self.__class__, params)

    def get_model(self):
        """
        Return wrapper model.

        :return: wrapper model
        """
        return self.model

    def fit(self, X, y=None):
        """
        Fit function for PreprocWrapper.

        :param X: Input data.
        :type X: numpy.ndarray or scipy.sparse.spmatrix
        :param y: Ignored.
        :type y: numpy.ndarray
        :return: Returns an instance of self.
        """
        args = dict(self.args)
        if self.cls is not None:
            self.model = self.cls(**args)
        else:
            assert self.module_name is not None
            assert self.class_name is not None
            mod = importlib.import_module(self.module_name)
            self.cls = getattr(mod, self.class_name)
        try:
            self.model.fit(X)
        except Exception as e:
            raise FitException.from_exception(e, has_pii=True, target="PreprocWrapper"). \
                with_generic_msg(_generic_fit_error_message.format(self.__class__.__name__))
        return self

    def get_params(self, deep=True):
        """
        Return parameters for PreprocWrapper.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: bool
        :return: Parameters for PreprocWrapper.
        """
        # using the cls field instead of class_name & class_name because these fields might not be set
        # when this instance is created through unpickling
        params = {'module_name': self.cls.__module__, 'class_name': self.cls.__name__}
        if self.model:
            params.update(self.model.get_params(deep))
        else:
            params.update(self.args)

        return params

    def transform(self, X):
        """
        Transform function for PreprocWrapper.

        :param X: Input data.
        :type X: numpy.ndarray or scipy.sparse.spmatrix
        :return: Transformed output of inner model.
        """
        try:
            return self.model.transform(X)
        except Exception as e:
            raise TransformException.from_exception(
                e, has_pii=True, target="PreprocWrapper",
                reference_code='model_wrappers.PreprocWrapper.transform'). \
                with_generic_msg(_generic_transform_error_message.format(self.__class__.__name__))

    def inverse_transform(self, X):
        """
        Inverse transform function for PreprocWrapper.

        :param X: New data.
        :type X: numpy.ndarray or scipy.sparse.spmatrix
        :return: Inverse transformed data.
        """
        try:
            return self.model.inverse_transform(X)
        except Exception as e:
            raise TransformException.from_exception(
                e, has_pii=True, target="PreprocWrapper_Inverse",
                reference_code='model_wrappers.PreprocWrapper_Inverse.inverse_transform'). \
                with_generic_msg(_generic_transform_error_message.format(self.__class__.__name__))


class StandardScalerWrapper(PreprocWrapper):
    """Standard Scaler Wrapper around StandardScaler transformation."""

    def __init__(self, **kwargs):
        """Initialize Standard Scaler Wrapper class."""
        super().__init__(sklearn.preprocessing.StandardScaler,
                         **kwargs)


class NBWrapper(BaseEstimator, ClassifierMixin, _AbstractModelWrapper):
    """Naive Bayes Wrapper for conditional probabilities using either Bernoulli or Multinomial models."""

    def __init__(self, model, **kwargs):
        """
        Initialize Naive Bayes Wrapper class with either Bernoulli or Multinomial models.

        :param model: The actual model name.
        :type model: str
        """
        assert model in ['Bernoulli', 'Multinomial']
        self.model_name = model
        self.args = kwargs
        self.model = None

    def __repr__(self) -> str:
        params = self.get_params(deep=False)
        return _codegen_utilities.generate_repr_str(self.__class__, params)

    def get_model(self):
        """
        Return Naive Bayes model.

        :return: Naive Bayes model.
        """
        return self.model

    def fit(self, X, y, **kwargs):
        """
        Fit function for Naive Bayes model.

        :param X: Input data.
        :type X: numpy.ndarray or scipy.sparse.spmatrix
        :param y: Input target values.
        :type y: numpy.ndarray
        :param kwargs: Other arguments.
        """
        if self.model_name == 'Bernoulli':
            base_clf = sklearn.naive_bayes.BernoulliNB(**self.args)
        elif self.model_name == 'Multinomial':
            base_clf = sklearn.naive_bayes.MultinomialNB(**self.args)
        model = base_clf
        is_sparse = scipy.sparse.issparse(X)
        # sparse matrix with negative cells
        if is_sparse and np.any(X < 0).max():
            clf = sklearn.pipeline.Pipeline(
                [('MinMax scaler', SparseScaleZeroOne()),
                 (self.model_name + 'NB', base_clf)])
            model = clf
        # regular matrix with negative cells
        elif not is_sparse and np.any(X < 0):
            clf = sklearn.pipeline.Pipeline(
                [('MinMax scaler',
                  sklearn.preprocessing.MinMaxScaler(
                      feature_range=(0, X.max()))),
                 (self.model_name + 'NB', base_clf)])
            model = clf

        self.model = model
        try:
            self.model.fit(X, y, **kwargs)
        except MemoryError as me:
            raise ResourceException._with_error(
                AzureMLError.create(InsufficientMemory, target='NBWrapper'), inner_exception=me) from me
        except Exception as e:
            raise FitException.from_exception(e, has_pii=True, target="NBWrapper"). \
                with_generic_msg(_generic_fit_error_message.format(self.__class__.__name__))
        if hasattr(self.model, "classes_"):
            self.classes_ = self.model.classes_
        else:
            self.classes_ = np.unique(y)

    def get_params(self, deep=True):
        """
        Return parameters for Naive Bayes model.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: bool
        :return: Parameters for Naive Bayes model.
        """
        params = {'model': self.model_name}
        if self.model:
            if isinstance(self.model, sklearn.pipeline.Pipeline):
                # we just want to get the parameters of the final estimator, excluding the preprocessors
                params.update(self.model._final_estimator.get_params(deep))
            else:
                params.update(self.model.get_params(deep))
        else:
            params.update(self.args)

        return params

    def predict(self, X):
        """
        Prediction function for Naive Bayes Wrapper Model.

        :param X: Input samples.
        :type X: numpy.ndarray or scipy.sparse.spmatrix
        :return: Prediction values from actual Naive Bayes model.
        """
        if self.model is None:
            raise UntrainedModelException(target="NBWrapper", has_pii=False)

        try:
            return self.model.predict(X)
        except Exception as e:
            raise PredictionException.from_exception(e, has_pii=True, target='NBWrapper'). \
                with_generic_msg(_generic_prediction_error_message.format(self.__class__.__name__))

    def predict_proba(self, X):
        """
        Prediction class probabilities for X for Naive Bayes Wrapper model.

        :param X: Input samples.
        :type X: numpy.ndarray or scipy.sparse.spmatrix
        :return: Prediction probability values from actual Naive Bayes model.
        """
        if self.model is None:
            raise UntrainedModelException(target="NBWrapper", has_pii=False)

        try:
            return self.model.predict_proba(X)
        except Exception as e:
            raise PredictionException.from_exception(e, has_pii=True, target='NBWrapper'). \
                with_generic_msg(_generic_prediction_error_message.format(self.__class__.__name__))


class TruncatedSVDWrapper(BaseEstimator, TransformerMixin, _AbstractModelWrapper):
    """
    Wrapper around Truncated SVD so that we only have to pass a fraction of dimensions.

    Read more at http://scikit-learn.org/stable/modules/generated/sklearn.decomposition.TruncatedSVD.html

    :param min_components: Min number of desired dimensionality of output data.
    :type min_components: int
    :param max_components: Max number of desired dimensionality of output data.
    :type max_components: int
    :param random_state: RandomState instance or None, optional, default = None
        If int, random_state is the seed used by the random number generator;
        If RandomState instance, random_state is the random number generator;
        If None, the random number generator is the RandomState instance used
        by np.random.
    :type random_state: int or np.random.RandomState
    :param kwargs: Other args taken by sklearn TruncatedSVD.
    """

    def __init__(
            self,
            min_components=2,
            max_components=200,
            random_state=None,
            **kwargs):
        """
        Initialize Truncated SVD Wrapper Model.

        :param min_components:
            Min number of desired dimensionality of output data.
        :type min_components: int
        :param max_components:
            Max number of desired dimensionality of output data.
        :type max_components: int
        :param random_state:
            RandomState instance or None, optional, default = None
            If int, random_state is the seed used by the random number
            generator;
            If RandomState instance, random_state is the random number
            generator;
            If None, the random number generator is the RandomState instance
            used by np.random.
        :type random_state: int or np.random.RandomState
        :param kwargs: Other args taken by sklearn TruncatedSVD.
        :return:
        """
        self._min_components = min_components
        self._max_components = max_components
        self.args = kwargs
        self.args['random_state'] = random_state

        self.n_components_str = "n_components"
        self.model = None

        Contract.assert_value(self.args.get(self.n_components_str), self.n_components_str,
                              reference_code=ReferenceCodes._TRUNCATED_SVD_WRAPPER_INIT)

    def get_model(self):
        """
        Return sklearn Truncated SVD Model.

        :return: Truncated SVD Model.
        """
        return self.model

    def fit(self, X, y=None):
        """
        Fit function for Truncated SVD Wrapper Model.

        :param X: Input data.
        :type X: numpy.ndarray or scipy.sparse.spmatrix
        :param y: Ignored.
        :return: Returns an instance of self.
        :rtype: azureml.automl.runtime.shared.model_wrappers.TruncatedSVDWrapper
        """
        args = dict(self.args)
        args[self.n_components_str] = min(
            self._max_components,
            max(self._min_components,
                int(self.args[self.n_components_str] * X.shape[1])))
        self.model = TruncatedSVD(**args)
        try:
            self.model.fit(X)
        except Exception as e:
            raise FitException.from_exception(e, has_pii=True, target="TruncatedSVDWrapper"). \
                with_generic_msg(_generic_fit_error_message.format(self.__class__.__name__))

        return self

    def get_params(self, deep=True):
        """
        Return parameters for Truncated SVD Wrapper Model.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: bool
        :return: Parameters for Truncated SVD Wrapper Model.
        """
        params = {}
        params['min_components'] = self._min_components
        params['max_components'] = self._max_components
        params['random_state'] = self.args['random_state']
        if self.model:
            params.update(self.model.get_params(deep=deep))
        else:
            params.update(self.args)

        return self.args

    def transform(self, X):
        """
        Transform function for Truncated SVD Wrapper Model.

        :param X: Input data.
        :type X: numpy.ndarray or scipy.sparse.spmatrix
        :return: Transformed data of reduced version of X.
        :rtype: array
        """
        try:
            return self.model.transform(X)
        except Exception as e:
            raise TransformException.from_exception(
                e, has_pii=True, target="TruncatedSVDWrapper",
                reference_code='model_wrappers.TruncatedSVDWrapper.transform'). \
                with_generic_msg(_generic_transform_error_message.format(self.__class__.__name__))

    def inverse_transform(self, X):
        """
        Inverse Transform function for Truncated SVD Wrapper Model.

        :param X: New data.
        :type X: numpy.ndarray
        :return: Inverse transformed data. Always a dense array.
        :rtype: array
        """
        try:
            return self.model.inverse_transform(X)
        except Exception as e:
            raise TransformException.from_exception(
                e, has_pii=True, target="TruncatedSVDWrapper_Inverse",
                reference_code='model_wrappers.TruncatedSVDWrapper_Inverse.inverse_transform'). \
                with_generic_msg(_generic_transform_error_message.format(self.__class__.__name__))


class SVCWrapper(BaseEstimator, ClassifierMixin, _AbstractModelWrapper):
    """
    Wrapper around svm.SVC that always sets probability to True.

    Read more at:
    http://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html.

    :param random_state: RandomState instance or None, optional, default = None
        If int, random_state is the seed used by the random number generator;
        If RandomState instance, random_state is the random number generator;
        If None, the random number generator is the RandomState instance used
        by np.random.
    :type random_state: int or np.random.RandomState
    :param: kwargs: Other args taken by sklearn SVC.
    """

    def __init__(self, random_state=None, **kwargs):
        """
        Initialize svm.SVC Wrapper Model.

        :param random_state:
            RandomState instance or None, optional, default = None
            If int, random_state is the seed used by the random number
            generator;
            If RandomState instance, random_state is the random number
            generator;
            If None, the random number generator is the RandomState instance
            used by np.random.
        :type random_state: int or np.random.RandomState
        :param: kwargs: Other args taken by sklearn SVC.
        """
        kwargs["probability"] = True
        self.args = kwargs
        self.args['random_state'] = random_state
        self.model = sklearn.svm.SVC(**self.args)

    def __repr__(self) -> str:
        params = self.get_params(deep=False)
        return _codegen_utilities.generate_repr_str(self.__class__, params)

    def get_model(self):
        """
        Return sklearn.svm.SVC Model.

        :return: The svm.SVC Model.
        """
        return self.model

    def fit(self, X, y, **kwargs):
        """
        Fit function for svm.SVC Wrapper Model.

        :param X: Input data.
        :type X: numpy.ndarray or scipy.sparse.spmatrix
        :param y: Input target values.
        :type y: numpy.ndarray
        """
        try:
            self.model.fit(X, y, **kwargs)
        except Exception as e:
            raise FitException.from_exception(e, has_pii=True, target="SVCWrapper"). \
                with_generic_msg(_generic_fit_error_message.format(self.__class__.__name__))
        if hasattr(self.model, "classes_"):
            self.classes_ = self.model.classes_
        else:
            self.classes_ = np.unique(y)

    def get_params(self, deep=True):
        """
        Return parameters for svm.SVC Wrapper Model.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: bool
        :return: parameters for svm.SVC Wrapper Model.
        """
        params = {'random_state': self.args['random_state']}
        params.update(self.model.get_params(deep=deep))

        return params

    def predict(self, X):
        """
        Prediction function for svm.SVC Wrapper Model. Perform classification on samples in X.

        :param X: Input samples.
        :type X: numpy.ndarray or scipy.sparse.spmatrix
        :return: Prediction values from svm.SVC model.
        :rtype: array
        """
        if self.model is None:
            raise UntrainedModelException(target='SVCWrapper', has_pii=False)

        try:
            return self.model.predict(X)
        except Exception as e:
            raise PredictionException.from_exception(e, has_pii=True, target='SVCWrapper'). \
                with_generic_msg(_generic_prediction_error_message.format(self.__class__.__name__))

    def predict_proba(self, X):
        """
        Prediction class probabilities for X for svm.SVC Wrapper model.

        :param X: Input samples.
        :type X: numpy.ndarray
        :return: Prediction probabilities values from svm.SVC model.
        :rtype: array
        """
        if self.model is None:
            raise UntrainedModelException(target='SVCWrapper', has_pii=False)

        try:
            return self.model.predict_proba(X)
        except Exception as e:
            raise PredictionException.from_exception(e, has_pii=True, target='SVCWrapper'). \
                with_generic_msg(_generic_prediction_error_message.format(self.__class__.__name__))


class NuSVCWrapper(BaseEstimator, ClassifierMixin, _AbstractModelWrapper):
    """
    Wrapper around svm.NuSVC that always sets probability to True.

    Read more at:
    http://scikit-learn.org/stable/modules/generated/sklearn.svm.NuSVC.html.

    :param random_state: RandomState instance or None, optional, default = None
        If int, random_state is the seed used by the random number generator;
        If RandomState instance, random_state is the random number generator;
        If None, the random number generator is the RandomState instance used
        by np.random.
    :type random_state: int or np.random.RandomState
    :param: kwargs: Other args taken by sklearn NuSVC.
    """

    def __init__(self, random_state=None, **kwargs):
        """
        Initialize svm.NuSVC Wrapper Model.

        :param random_state: RandomState instance or None, optional,
        default = None
            If int, random_state is the seed used by the random number
            generator;
            If RandomState instance, random_state is the random number
            generator;
            If None, the random number generator is the RandomState instance
            used by np.random.
        :type random_state: int or np.random.RandomState
        :param: kwargs: Other args taken by sklearn NuSVC.
        """
        kwargs["probability"] = True
        self.args = kwargs
        self.args['random_state'] = random_state
        self.model = sklearn.svm.NuSVC(**self.args)

    def __repr__(self) -> str:
        params = self.get_params(deep=False)
        return _codegen_utilities.generate_repr_str(self.__class__, params)

    def get_model(self):
        """
        Return sklearn svm.NuSVC Model.

        :return: The svm.NuSVC Model.
        """
        return self.model

    def fit(self, X, y, **kwargs):
        """
        Fit function for svm.NuSVC Wrapper Model.

        :param X: Input data.
        :type X: numpy.ndarray or scipy.sparse.spmatrix
        :param y: Input target values.
        :type y: numpy.ndarray
        """
        try:
            self.model.fit(X, y, **kwargs)
        except Exception as e:
            raise FitException.from_exception(e, has_pii=True, target="NuSVCWrapper"). \
                with_generic_msg(_generic_fit_error_message.format(self.__class__.__name__))
        if hasattr(self.model, "classes_"):
            self.classes_ = self.model.classes_
        else:
            self.classes_ = np.unique(y)

    def get_params(self, deep=True):
        """
        Return parameters for svm.NuSVC Wrapper Model.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: bool
        :return: Parameters for svm.NuSVC Wrapper Model.
        """
        params = {'random_state': self.args['random_state']}
        params.update(self.model.get_params(deep=deep))
        return params

    def predict(self, X):
        """
        Prediction function for svm.NuSVC Wrapper Model. Perform classification on samples in X.

        :param X: Input samples.
        :type X: numpy.ndarray or scipy.sparse.spmatrix
        :return: Prediction values from svm.NuSVC model.
        :rtype: array
        """
        if self.model is None:
            raise UntrainedModelException(target='NuSVCWrapper', has_pii=False)

        try:
            return self.model.predict(X)
        except Exception as e:
            raise PredictionException.from_exception(e, has_pii=True, target='NuSVCWrapper'). \
                with_generic_msg(_generic_prediction_error_message.format(self.__class__.__name__))

    def predict_proba(self, X):
        """
        Prediction class probabilities for X for svm.NuSVC Wrapper model.

        :param X: Input samples.
        :type X: numpy.ndarray
        :return: Prediction probabilities values from svm.NuSVC model.
        :rtype: array
        """
        if self.model is None:
            raise UntrainedModelException(target='NuSVCWrapper', has_pii=False)

        try:
            return self.model.predict_proba(X)
        except Exception as e:
            raise PredictionException.from_exception(e, has_pii=True, target='NuSVCWrapper'). \
                with_generic_msg(_generic_prediction_error_message.format(self.__class__.__name__))


class SGDClassifierWrapper(BaseEstimator, ClassifierMixin, _AbstractModelWrapper):
    """
    SGD Classifier Wrapper Class.

    Wrapper around SGD Classifier to support predict probabilities on loss
    functions other than log loss and modified huber loss. This breaks
    partial_fit on loss functions other than log and modified_huber since the
    calibrated model does not support partial_fit.

    Read more at:
    http://scikit-learn.org/stable/modules/generated/sklearn.linear_model.SGDClassifier.html.
    """

    def __init__(self, random_state=None, n_jobs=1, **kwargs):
        """
        Initialize SGD Classifier Wrapper Model.

        :param random_state:
            RandomState instance or None, optional (default=None)
            If int, random_state is the seed used by the random number
            generator;
            If RandomState instance, random_state is the random number
            generator;
            If None, the random number generator is the RandomState
            instance used
            by `np.random`.
        :type random_state: int or np.random.RandomState
        :param n_jobs: Number of parallel threads.
        :type n_jobs: int
        :param kwargs: Other parameters.
        """
        self.loss = "loss"
        self.model = None
        self._calibrated = False

        self.args = kwargs
        self.args['random_state'] = random_state
        self.args['n_jobs'] = n_jobs
        loss_arg = kwargs.get(self.loss, None)
        if loss_arg in ["log", "modified_huber"]:
            self.model = sklearn.linear_model.SGDClassifier(**self.args)
        else:
            self.model = CalibratedModel(
                sklearn.linear_model.SGDClassifier(**self.args), random_state)
            self._calibrated = True

    def __repr__(self) -> str:
        params = self.get_params(deep=False)
        return _codegen_utilities.generate_repr_str(self.__class__, params)

    def get_model(self):
        """
        Return SGD Classifier Wrapper Model.

        :return: Returns the fitted model if fit method has been called.
        Else returns None
        """
        return self.model

    def fit(self, X, y, **kwargs):
        """
        Fit function for SGD Classifier Wrapper Model.

        :param X: Input data.
        :type X: numpy.ndarray
        :param y: Input target values.
        :type y: numpy.ndarray
        :param kwargs: Other parameters.
        :return: Returns an instance of inner SGDClassifier model.
        """
        try:
            model = self.model.fit(X, y, **kwargs)
        except Exception as e:
            raise FitException.from_exception(e, has_pii=True, target="SGDClassifierWrapper"). \
                with_generic_msg(_generic_fit_error_message.format(self.__class__.__name__))
        if hasattr(model, "classes_"):
            self.classes_ = model.classes_
        else:
            self.classes_ = np.unique(y)

        return model

    def get_params(self, deep=True):
        """
        Return parameters for SGD Classifier Wrapper Model.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: bool
        :return: parameters for SGD Classifier Wrapper Model.
        """
        params = {}
        params['random_state'] = self.args['random_state']
        params['n_jobs'] = self.args['n_jobs']
        params.update(self.model.get_params(deep=deep))
        return self.args

    def predict(self, X):
        """
        Prediction function for SGD Classifier Wrapper Model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return: Prediction values from SGD Classifier Wrapper model.
        """
        if self.model is None:
            raise UntrainedModelException(target='SGDClassifierWrapper', has_pii=False)

        try:
            return self.model.predict(X)
        except Exception as e:
            raise PredictionException.from_exception(e, has_pii=True, target='SGDClassifierWrapper'). \
                with_generic_msg(_generic_prediction_error_message.format(self.__class__.__name__))

    def predict_proba(self, X):
        """
        Prediction class probabilities for X for SGD Classifier Wrapper model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return:
            Prediction probability values from SGD Classifier Wrapper model.
        """
        if self.model is None:
            raise UntrainedModelException(target='SGDClassifierWrapper', has_pii=False)

        try:
            return self.model.predict_proba(X)
        except Exception as e:
            raise PredictionException.from_exception(e, has_pii=True, target='SGDClassifierWrapper'). \
                with_generic_msg(_generic_prediction_error_message.format(self.__class__.__name__))

    def partial_fit(self, X, y, **kwargs):
        """
        Return partial fit result.

        :param X: Input data.
        :type X: numpy.ndarray
        :param y: Input target values.
        :type y: numpy.ndarray
        :param kwargs: Other parameters.
        :return: Returns an instance of inner SGDClassifier model.
        """
        Contract.assert_true(
            not self._calibrated, message="Failed to partially fit SGDClassifier. Calibrated model used.",
            target='SGDClassifierWrapper', log_safe=True
        )

        try:
            return self.model.partial_fit(X, y, **kwargs)
        except Exception as e:
            raise FitException.from_exception(e, has_pii=True, target="SGDClassifierWrapper"). \
                with_generic_msg(_generic_fit_error_message.format(self.__class__.__name__))


class EnsembleWrapper(BaseEstimator, ClassifierMixin):
    """Wrapper around multiple pipelines that combine predictions."""

    def __init__(self, models=None, clf=None, weights=None, task=constants.Tasks.CLASSIFICATION,
                 **kwargs):
        """
        Initialize EnsembleWrapper model.

        :param models: List of models to use in ensembling.
        :type models: list
        :param clf:
        """
        self.models = models
        self.clf = clf
        self.classes_ = None
        if self.clf:
            if hasattr(self.clf, 'classes_'):
                self.classes_ = self.clf.classes_
        self.weights = weights
        self.task = task

    def _get_imports(self) -> List[Tuple[str, str, Any]]:
        imports = []
        if self.models:
            imports.extend([
                _codegen_utilities.get_import(model[1]) for model in self.models
            ])
        if self.clf:
            imports.append(_codegen_utilities.get_import(self.clf))
        return imports

    def fit(self, X, y):
        """
        Fit function for EnsembleWrapper.

        :param X: Input data.
        :type X: numpy.ndarray
        :param y: Input target values.
        :type y: numpy.ndarray
        :return:
        """
        try:
            for m in self.models:
                m.fit(X, y)
        except Exception as e:
            # models in an ensemble could be from multiple frameworks
            raise FitException.from_exception(e, has_pii=True, target='EnsembleWrapper'). \
                with_generic_msg(_generic_fit_error_message.format(self.__class__.__name__))
        return self

    def get_params(self, deep=True):
        """
        Return parameters for Ensemble Wrapper Model.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: bool
        :return: parameters for Ensemble Wrapper Model.
        """
        params = {
            "models": self.models,
            "clf": self.clf,
            "weights": self.weights,
            "task": self.task
        }

        return params

    def __repr__(self) -> str:
        params = self.get_params(deep=False)
        return _codegen_utilities.generate_repr_str(self.__class__, params)

    @staticmethod
    def get_ensemble_predictions(preds, weights=None,
                                 task=constants.Tasks.CLASSIFICATION):
        """
        Combine an array of probilities from compute_valid_predictions.

        Probabilities are combined into a single array of shape [num_samples, num_classes].
        """
        preds = np.average(preds, axis=2, weights=weights)
        if task == constants.Tasks.CLASSIFICATION:
            preds /= preds.sum(1)[:, None]
            assert np.all(preds >= 0) and np.all(preds <= 1)

        return preds

    @staticmethod
    def compute_valid_predictions(models, X, model_file_name_format=None, num_scores=None, splits=None):
        """Return an array of probabilities of shape [num_samples, num_classes, num_models]."""
        found_model = False
        if model_file_name_format:
            for i in range(num_scores):
                model_file_name = model_file_name_format.format(i)
                if os.path.exists(model_file_name):
                    with open(model_file_name, 'rb') as f:
                        m = pickle.load(f)
                    found_model = True
                    break
        else:
            for m in models:
                if m is not None:
                    found_model = True
                    break
        if not found_model:
            raise PredictionException.create_without_pii('Failed to generate predictions, no models found.',
                                                         target='EnsembleWrapper')
        if isinstance(m, list):
            m = m[0]
        preds0 = EnsembleWrapper._predict_proba_if_possible(m, X)
        num_classes = preds0.shape[1]

        preds = np.zeros((X.shape[0], num_classes, num_scores if num_scores else len(models)))
        if model_file_name_format:
            for i in range(num_scores):
                model_file_name = model_file_name_format.format(i)
                if os.path.exists(model_file_name):
                    with open(model_file_name, 'rb') as f:
                        m = pickle.load(f)
                    if isinstance(m, list):
                        for cv_fold, split in enumerate(splits):
                            preds[split, :, i] = EnsembleWrapper._predict_proba_if_possible(m[cv_fold], X[split])
                    else:
                        preds[:, :, i] = EnsembleWrapper._predict_proba_if_possible(m, X)
        else:
            for i, m in enumerate(models):
                if m is None:
                    continue
                if isinstance(m, list):
                    for cv_fold, split in enumerate(splits):
                        preds[split, :, i] = EnsembleWrapper._predict_proba_if_possible(m[cv_fold], X[split])
                else:
                    preds[:, :, i] = EnsembleWrapper._predict_proba_if_possible(m, X)
        return preds

    @staticmethod
    def _predict_proba_if_possible(model, X):
        try:
            if hasattr(model, 'predict_proba'):
                preds = model.predict_proba(X)
            else:
                preds = model.predict(X)
                preds = preds.reshape(-1, 1)
            return preds
        except Exception as e:
            raise PredictionException.from_exception(e, has_pii=True, target='EnsembleWrapper'). \
                with_generic_msg(_generic_prediction_error_message.format('EnsembleWrapper'))

    def predict(self, X):
        """
        Prediction function for EnsembleWrapper model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return: Prediction values from EnsembleWrapper model.
        """
        try:
            if self.task == constants.Tasks.CLASSIFICATION:
                probs = self.predict_proba(X)
                return np.argmax(probs, axis=1)
            else:
                return self.predict_regression(X)
        except Exception as e:
            raise PredictionException.from_exception(e, has_pii=True, target='EnsembleWrapper'). \
                with_generic_msg(_generic_prediction_error_message.format(self.__class__.__name__))

    def predict_regression(self, X):
        """
        Predict regression results for X for EnsembleWrapper model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return:
            Prediction probability values from EnsembleWrapper model.
        """
        valid_predictions = EnsembleWrapper.compute_valid_predictions(
            self.models, X)
        if self.clf is None:
            return EnsembleWrapper.get_ensemble_predictions(
                valid_predictions, self.weights, task=self.task)
        else:
            try:
                return self.clf.predict(valid_predictions.reshape(
                    valid_predictions.shape[0],
                    valid_predictions.shape[1] * valid_predictions.shape[2]))
            except Exception as e:
                raise PredictionException.from_exception(e, has_pii=True, target='EnsembleWrapper'). \
                    with_generic_msg(_generic_prediction_error_message.format(self.__class__.__name__))

    def predict_proba(self, X):
        """
        Prediction class probabilities for X for EnsembleWrapper model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return:
            Prediction probability values from EnsembleWrapper model.
        """
        valid_predictions = EnsembleWrapper.compute_valid_predictions(
            self.models, X)
        if self.clf is None:
            return EnsembleWrapper.get_ensemble_predictions(
                valid_predictions, self.weights)
        else:
            try:
                # TODO make sure the order is same as during training\
                # ignore the first column due to collinearity
                valid_predictions = valid_predictions[:, 1:, :]
                return self.clf.predict_proba(valid_predictions.reshape(
                    valid_predictions.shape[0],
                    valid_predictions.shape[1] * valid_predictions.shape[2]))
            except Exception as e:
                raise PredictionException.from_exception(e, has_pii=True, target='EnsembleWrapper'). \
                    with_generic_msg(_generic_prediction_error_message.format(self.__class__.__name__))


class LinearSVMWrapper(BaseEstimator, ClassifierMixin, _AbstractModelWrapper):
    """
    Wrapper around linear svm to support predict_proba on sklearn's liblinear wrapper.

    :param random_state:
        RandomState instance or None, optional (default=None)
        If int, random_state is the seed used by the random number generator;
        If RandomState instance, random_state is the random number generator;
        If None, the random number generator is the RandomState instance used
        by `np.random`.
    :type random_state: int or np.random.RandomState
    :param kwargs: Other parameters.
    """

    def __init__(self, random_state=None, **kwargs):
        """
        Initialize Linear SVM Wrapper Model.

        :param random_state:
            RandomState instance or None, optional (default=None)
            If int, random_state is the seed used by the random number
            generator;
            If RandomState instance, random_state is the random number
            generator;
            If None, the random number generator is the RandomState
            instance used by `np.random`.
        :type random_state: int or np.random.RandomState
        :param kwargs: Other parameters.
        """
        self.args = kwargs
        self.args['random_state'] = random_state
        self.model = CalibratedModel(sklearn.svm.LinearSVC(**self.args))

    def __repr__(self) -> str:
        params = self.get_params(deep=False)
        return _codegen_utilities.generate_repr_str(self.__class__, params)

    def get_model(self):
        """
        Return Linear SVM Wrapper Model.

        :return: Linear SVM Wrapper Model.
        """
        return self.model

    def fit(self, X, y, **kwargs):
        """
        Fit function for Linear SVM Wrapper Model.

        :param X: Input data.
        :type X: numpy.ndarray
        :param y: Input target values.
        :type y: numpy.ndarray
        :param kwargs: Other parameters.
        """
        try:
            self.model.fit(X, y, **kwargs)
        except Exception as e:
            raise FitException.from_exception(e, has_pii=True, target="LinearSVMWrapper"). \
                with_generic_msg(_generic_fit_error_message.format(self.__class__.__name__))
        if hasattr(self.model, "classes_"):
            self.classes_ = self.model.classes_
        else:
            self.classes_ = np.unique(y)

    def get_params(self, deep=True):
        """
        Return parameters for Linear SVM Wrapper Model.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: bool
        :return: parameters for Linear SVM Wrapper Model
        """
        params = {'random_state': self.args['random_state']}

        assert (isinstance(self.model, CalibratedModel))
        if isinstance(self.model.model, CalibratedClassifierCV):
            params.update(self.model.model.base_estimator.get_params(deep=deep))
        return params

    def predict_proba(self, X):
        """
        Prediction class probabilities for X for Linear SVM Wrapper model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return: Prediction probability values from Linear SVM Wrapper model.
        """
        try:
            return self.model.predict_proba(X)
        except Exception as e:
            raise PredictionException.from_exception(e, has_pii=True, target='LinearSVMWrapper'). \
                with_generic_msg(_generic_prediction_error_message.format(self.__class__.__name__))

    def predict(self, X):
        """
        Prediction function for Linear SVM Wrapper Model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return: Prediction values from Linear SVM Wrapper model.
        """
        try:
            return self.model.predict(X)
        except Exception as e:
            raise PredictionException.from_exception(e, has_pii=True, target='LinearSVMWrapper'). \
                with_generic_msg(_generic_prediction_error_message.format(self.__class__.__name__))


class CalibratedModel(BaseEstimator, ClassifierMixin, _AbstractModelWrapper):
    """
    Trains a calibrated model.

    Takes a base estimator as input and trains a calibrated model.
    :param base_estimator: Base Model on which calibration has to be performed.
    :param random_state:
        RandomState instance or None, optional (default=None)
        If int, random_state is the seed used by the random number generator;
        If RandomState instance, random_state is the random number generator;
        If None, the random number generator is the RandomState instance used
        by `np.random`.
    :type random_state: int or np.random.RandomState

    Read more at:
    http://scikit-learn.org/stable/modules/generated/sklearn.calibration.CalibratedClassifierCV.html.
    """

    def __init__(self, base_estimator, random_state=None):
        """
        Initialize Calibrated Model.

        :param base_estimator: Base Model on which calibration has to be
            performed.
        :param random_state:
            RandomState instance or None, optional (default=None)
            If int, random_state is the seed used by the random number
            generator.
            If RandomState instance, random_state is the random number
            generator.
            If None, the random number generator is the RandomState instance
            used by `np.random`.
        :type random_state: int or np.random.RandomState
        """
        self._train_ratio = 0.8
        self.random_state = random_state
        self.model = CalibratedClassifierCV(
            base_estimator=base_estimator, cv="prefit")

    def __repr__(self) -> str:
        params = self.get_params(deep=False)
        return _codegen_utilities.generate_repr_str(self.__class__, params)

    def _get_imports(self) -> List[Tuple[str, str, Any]]:
        return [
            _codegen_utilities.get_import(self.model.base_estimator)
        ]

    def get_model(self):
        """
        Return the sklearn Calibrated Model.

        :return: The Calibrated Model.
        :rtype: sklearn.calibration.CalibratedClassifierCV
        """
        return self.model

    def fit(self, X, y, **kwargs):
        """
        Fit function for Calibrated Model.

        :param X: Input training data.
        :type X: numpy.ndarray
        :param y: Input target values.
        :type y: numpy.ndarray
        :return: self: Returns an instance of self.
        :rtype: azureml.automl.runtime.shared.model_wrappers.CalibratedModel
        """
        arrays = [X, y]
        if "sample_weight" in kwargs:
            arrays.append(kwargs["sample_weight"])
        self.args = kwargs
        out_arrays = train_test_split(
            *arrays,
            train_size=self._train_ratio,
            random_state=self.random_state,
            stratify=y)
        X_train, X_valid, y_train, y_valid = out_arrays[:4]

        if "sample_weight" in kwargs:
            sample_weight_train, sample_weight_valid = out_arrays[4:]
        else:
            sample_weight_train = None
            sample_weight_valid = None

        try:
            # train model
            self.model.base_estimator.fit(
                X_train, y_train, sample_weight=sample_weight_train)
        except Exception as e:
            raise FitException.from_exception(e, has_pii=True, target="CalibratedModel_train_model"). \
                with_generic_msg(_generic_fit_error_message.format(self.__class__.__name__))

        # fit calibration model
        try:
            self.model.fit(X_valid, y_valid, sample_weight=sample_weight_valid)
        except ValueError as e:
            y_labels = np.unique(y)
            y_train_labels = np.unique(y_train)
            y_valid_labels = np.unique(y_valid)
            y_train_missing_labels = np.setdiff1d(y_labels, y_train_labels, assume_unique=True)
            y_valid_missing_labels = np.setdiff1d(y_labels, y_valid_labels, assume_unique=True)
            if y_train_missing_labels.shape[0] > 0 or y_valid_missing_labels.shape[0] > 0:
                error_msg = "Could not fit the calibrated model. Internal train/validation sets could not be split, " \
                            "even with stratification. Missing train: {} Missing valid: {}"
                raise FitException.from_exception(
                    e, msg=error_msg.format(y_train_missing_labels, y_valid_missing_labels), has_pii=True,
                    target="CalibratedModel_imbalanced").with_generic_msg(error_msg)
            else:
                # We don't know what happened in this case, so just re-raise with the same inner exception
                raise FitException.from_exception(e, has_pii=True, target="CalibratedModel")
        except Exception as e:
            raise FitException.from_exception(e, has_pii=True, target="CalibratedModel"). \
                with_generic_msg(_generic_fit_error_message.format(self.__class__.__name__))

        try:
            # retrain base estimator on full dataset
            self.model.base_estimator.fit(X, y, **kwargs)
        except Exception as e:
            raise FitException.from_exception(e, has_pii=True, target="CalibratedModel_retrain_full"). \
                with_generic_msg(_generic_fit_error_message.format(self.__class__.__name__))

        if hasattr(self.model, "classes_"):
            self.classes_ = self.model.classes_
        else:
            self.classes_ = np.unique(y)
        return self

    def get_params(self, deep=True):
        """
        Return parameters for Calibrated Model.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: bool
        :return: Parameters for Calibrated Model.
        """
        params = {'random_state': self.random_state}
        assert (isinstance(self.model, CalibratedClassifierCV))
        params['base_estimator'] = self.model.base_estimator
        return params

    def predict(self, X):
        """
        Prediction function for Calibrated Model.

        :param X: Input samples.
        :type X: numpy.ndarray
        :return: Prediction values from Calibrated model.
        :rtype: array
        """
        try:
            return self.model.predict(X)
        except Exception as e:
            raise PredictionException.from_exception(e, has_pii=True, target='CalibratedModel'). \
                with_generic_msg(_generic_prediction_error_message.format(self.__class__.__name__))

    def predict_proba(self, X):
        """
        Prediction class probabilities for X for Calibrated model.

        :param X: Input samples.
        :type X: numpy.ndarray
        :return: Prediction proba values from Calibrated model.
        :rtype: array
        """
        try:
            return self.model.predict_proba(X)
        except Exception as e:
            raise PredictionException.from_exception(e, has_pii=True, target='CalibratedModel'). \
                with_generic_msg(_generic_prediction_error_message.format(self.__class__.__name__))


class LightGBMRegressor(BaseEstimator, RegressorMixin, _AbstractModelWrapper):
    """
    LightGBM Regressor class.

    :param random_state:
        RandomState instance or None, optional (default=None)
        If int, random_state is the seed used by the random number generator;
        If RandomState instance, random_state is the random number generator;
        If None, the random number generator is the RandomState instance used
        by `np.random`.
    :type random_state: int or np.random.RandomState
    :param kwargs: Other parameters.
    """

    DEFAULT_MIN_DATA_IN_LEAF = 20

    def __init__(self, random_state=None, n_jobs=1, problem_info=None, **kwargs):
        """
        Initialize LightGBM Regressor class.

        :param random_state:
            RandomState instance or None, optional (default=None)
            If int, random_state is the seed used by the random number
            generator;
            If RandomState instance, random_state is the random number
            generator;
            If None, the random number generator is the RandomState
            instance used by `np.random`.
        :type random_state: int or np.random.RandomState
        :param problem_info: Problem metadata.
        :type problem_info: ProblemInfo
        :param kwargs: Other parameters.
        """
        self._kwargs = kwargs.copy()
        self.params = kwargs
        self.params['random_state'] = random_state
        self.params['n_jobs'] = n_jobs
        if problem_info is not None and problem_info.gpu_training_param_dict is not None and \
                problem_info.gpu_training_param_dict.get("processing_unit_type", "cpu") == "gpu":
            self.params['device'] = 'gpu'

            # We have seen lightgbm gpu fit can fail on bin size too big, the bin size during fit may come from
            # dataset / the pipeline spec itself. With one hot encoding, the categorical features from dataset should
            # not have big cardinality that causing the bin size too big, so the only source is pipeline itself. Cap to
            # 255 max if it exceeded the size.
            if self.params.get('max_bin', 0) > 255:
                self.params['max_bin'] = 255
        self.model = None
        self._min_data_in_leaf = "min_data_in_leaf"
        self._min_child_samples = "min_child_samples"

        self._problem_info = problem_info.clean_attrs(
            ['gpu_training_param_dict',
             'dataset_categoricals']) if problem_info is not None else None

        # Both 'min_data_in_leaf' and 'min_child_samples' are required
        Contract.assert_true(
            self._min_data_in_leaf in kwargs or self._min_child_samples in kwargs,
            message="Failed to initialize LightGBMRegressor. Neither min_data_in_leaf nor min_child_samples passed",
            target="LightGBMRegressor", log_safe=True
        )

    def get_model(self):
        """
        Return LightGBM Regressor model.

        :return:
            Returns the fitted model if fit method has been called.
            Else returns None
        """
        return self.model

    def fit(self, X, y, **kwargs):
        """
        Fit function for LightGBM Regressor model.

        :param X: Input data.
        :type X: numpy.ndarray
        :param y: Labels for the data.
        :type y: numpy.ndarray
        :param kwargs: Other parameters.
        :return: Returns self after fitting the model.
        """
        verbose_str = "verbose"
        n = X.shape[0]
        params = dict(self.params)
        if (self._min_data_in_leaf in params):
            if (self.params[self._min_data_in_leaf]
                    == LightGBMRegressor.DEFAULT_MIN_DATA_IN_LEAF):
                params[self._min_child_samples] = self.params[
                    self._min_data_in_leaf]
            else:
                params[self._min_child_samples] = int(
                    self.params[self._min_data_in_leaf] * n) + 1
            del params[self._min_data_in_leaf]
        else:
            min_child_samples = self.params[self._min_child_samples]
            if min_child_samples > 0 and min_child_samples < 1:
                # we'll convert from fraction to int as that's what LightGBM expects
                params[self._min_child_samples] = int(
                    self.params[self._min_child_samples] * n) + 1
            else:
                params[self._min_child_samples] = min_child_samples

        if verbose_str not in params:
            params[verbose_str] = -1

        if self._problem_info is not None and self._problem_info.dataset_categoricals is not None:
            n_categorical = len(np.where(self._problem_info.dataset_categoricals)[0])
            kwargs['categorical_feature'] = [i for i in range(n_categorical)]

        self.model = lgb.LGBMRegressor(**params)
        try:
            self.model.fit(X, y, **kwargs)
        except Exception as e:
            raise FitException.from_exception(e, has_pii=True, target="LightGbm"). \
                with_generic_msg(_generic_fit_error_message.format(self.__class__.__name__))

        return self

    def __setstate__(self, state):
        if "_kwargs" not in state:
            state["_kwargs"] = {}
        if "_problem_info" in state:
            state["_problem_info"] = state["_problem_info"].clean_attrs(
                ['gpu_training_param_dict',
                 'dataset_categoricals']) if state["_problem_info"] is not None else None

        super().__setstate__(state)

    def __getstate__(self):
        state = self.__dict__

        # Backwards compatibility to handle inferencing on old SDK
        # pipeline_categoricals in ProblemInfo will always be None since we cleaned it, so we can inject it as part
        # of model init instead of fit
        if self._problem_info is not None and self._problem_info.dataset_categoricals is not None:
            n_categorical = len(np.where(self._problem_info.dataset_categoricals)[0])
            state["params"]["categorical_feature"] = [i for i in range(n_categorical)]

        return state

    def get_params(self, deep: bool = True) -> Dict[str, Any]:
        """
        Return parameters for LightGBM Regressor model.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: bool
        :return: Parameters for LightGBM Regressor model.
        """
        params = self._kwargs.copy()
        params["random_state"] = self.params["random_state"]
        params["n_jobs"] = self.params["n_jobs"]
        params["problem_info"] = self._problem_info

        return params

    def __repr__(self) -> str:
        params = self.get_params(deep=False)
        return _codegen_utilities.generate_repr_str(self.__class__, params)

    def _get_imports(self) -> List[Tuple[str, str, Any]]:
        if self._problem_info:
            return [
                _codegen_utilities.get_import(self._problem_info)
            ]
        else:
            return []

    def predict(self, X):
        """
        Prediction function for LightGBM Regressor model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return: Prediction values from LightGBM Regressor model.
        """
        try:
            return self.model.predict(X)
        except Exception as e:
            raise PredictionException.from_exception(e, has_pii=True, target='LightGBMRegressor'). \
                with_generic_msg(_generic_prediction_error_message.format(self.__class__.__name__))


class XGBoostRegressor(BaseEstimator, RegressorMixin, _AbstractModelWrapper):
    """
    XGBoost Regressor class.

    :param random_state:
        RandomState instance or None, optional (default=None)
        If int, random_state is the seed used by the random number generator;
        If RandomState instance, random_state is the random number generator;
        If None, the random number generator is the RandomState instance used
        by `np.random`.
    :type random_state: int or np.random.RandomState
    :param n_jobs: Number of parallel threads.
    :type n_jobs: int
    :param kwargs: Other parameters
        Check https://xgboost.readthedocs.io/en/latest/parameter.html
        for more parameters.
    """
    # The version after which the XGBOOST started to create a warning as:
    #  src/objective/regression_obj.cu:152: reg:linear is now deprecated in favor of reg:squarederror.
    _RENAME_VERSION = version.parse('0.83')
    _OBJECTIVE = 'objective'
    _REG_LINEAR = 'reg:linear'
    _REG_SQUAREDERROR = 'reg:squarederror'
    _ALL_OBJECTIVES = {_REG_LINEAR, _REG_SQUAREDERROR}

    def __init__(self, random_state=0, n_jobs=1, problem_info=None, **kwargs):
        """
        Initialize XGBoost Regressor class.

        :param random_state:
            RandomState instance or None, optional (default=None)
            If int, random_state is the seed used by the random number
            generator.
            If RandomState instance, random_state is the random number
            generator.
            If None, the random number generator is the RandomState instance
            used by `np.random`.
        :type random_state: int or np.random.RandomState
        :param n_jobs: Number of parallel threads.
        :type n_jobs: int
        :param kwargs: Other parameters
            Check https://xgboost.readthedocs.io/en/latest/parameter.html
            for more parameters.
        """
        self.params = kwargs.copy()
        self.params['random_state'] = random_state if random_state is not None else 0
        self.params['n_jobs'] = n_jobs
        self.params['verbosity'] = 0
        self.params = GPUHelper.xgboost_add_gpu_support(problem_info, self.params)
        self.model = None
        self._problem_info = problem_info.clean_attrs(['gpu_training_param_dict']) \
            if problem_info is not None else None
        self._kwargs = kwargs

        Contract.assert_true(
            xgboost_present, message="Failed to initialize XGBoostRegressor. xgboost is not installed, "
                                     "please install xgboost for including xgboost based models.",
            target='XGBoostRegressor', log_safe=True
        )

    def __setstate__(self, state):
        if "_kwargs" not in state:
            state["_kwargs"] = {}
        if "_problem_info" not in state:
            state["_problem_info"] = None
        state["_problem_info"] = state["_problem_info"].clean_attrs(['gpu_training_param_dict']) \
            if state["_problem_info"] is not None else None
        super().__setstate__(state)

    def __repr__(self) -> str:
        params = self.get_params(deep=False)
        params.update(self._kwargs)
        return _codegen_utilities.generate_repr_str(self.__class__, params)

    def _get_imports(self) -> List[Tuple[str, str, Any]]:
        if self._problem_info:
            return [
                _codegen_utilities.get_import(self._problem_info)
            ]
        else:
            return []

    def get_model(self):
        """
        Return XGBoost Regressor model.

        :return: Returns the fitted model if fit method has been called.
        Else returns None.
        """
        return self.model

    def _get_objective_safe(self) -> str:
        """
        Get the objective, which will not throw neither error nor warning.

        :return: The objective, which is safe to use: reg:linear or reg:squarederror.
        """
        if version.parse(xgb.__version__) < XGBoostRegressor._RENAME_VERSION:
            # This objective is deprecated in versions later then _RENAME_VERSION.
            return XGBoostRegressor._REG_LINEAR
        return XGBoostRegressor._REG_SQUAREDERROR

    def _replace_objective_maybe(self, params_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check the self.params for unsafe objective and replace it by the safe one.

        Replae the objective, so that we will not get neither error nor warning during
        XGBoostRegressor fitting.
        """
        params_dict = copy.deepcopy(params_dict)
        if XGBoostRegressor._OBJECTIVE in self.params.keys():
            objective = params_dict.get(XGBoostRegressor._OBJECTIVE)
            if objective in XGBoostRegressor._ALL_OBJECTIVES:
                params_dict[XGBoostRegressor._OBJECTIVE] = self._get_objective_safe()
        else:
            params_dict[XGBoostRegressor._OBJECTIVE] = self._get_objective_safe()
        return params_dict

    def fit(self, X, y, **kwargs):
        """
        Fit function for XGBoost Regressor model.

        :param X: Input data.
        :type X: numpy.ndarray
        :param y: Input target values.
        :type y: numpy.ndarray
        :param kwargs: other parameters
            Check https://xgboost.readthedocs.io/en/latest/parameter.html
            for more parameters.
        :return: Self after fitting the model.
        """
        args = dict(self.params)
        args = self._replace_objective_maybe(args)
        verbose_str = "verbose"
        if verbose_str not in args:
            args[verbose_str] = -10

        self.model = xgb.XGBRegressor(**args)
        try:
            self.model.fit(X, y, **kwargs)
        except Exception as e:
            raise FitException.from_exception(e, has_pii=True, target="Xgboost"). \
                with_generic_msg(_generic_fit_error_message.format(self.__class__.__name__))

        return self

    def get_params(self, deep=True):
        """
        Return parameters for XGBoost Regressor model.

        :param deep:
            If True, will return the parameters for this estimator and contained subobjects that are estimators.
        :type deep: bool
        :return: Parameters for the XGBoost classifier model.
        """
        if deep:
            if self.model:
                return self.model.get_params(deep)
            else:
                return self.params
        else:
            params = {
                "random_state": self.params["random_state"],
                "n_jobs": self.params["n_jobs"],
                "problem_info": self._problem_info,
            }
            params.update(self._kwargs)
            return params

    def predict(self, X):
        """
        Prediction function for XGBoost Regressor model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return: Prediction values from XGBoost Regressor model.
        """
        if self.model is None:
            raise UntrainedModelException.create_without_pii(target="Xgboost")
        return self.model.predict(X)


class CatBoostRegressor(RegressorMixin, _AbstractModelWrapper):
    """Model wrapper for the CatBoost Regressor."""

    def __init__(self, random_state=0, thread_count=1, **kwargs):
        """
        Construct a CatBoostRegressor.

        :param random_state:
            RandomState instance or None, optional (default=None)
            If int, random_state is the seed used by the random number
            generator.
            If RandomState instance, random_state is the random number
            generator.
            If None, the random number generator is the RandomState instance
            used by `np.random`.
        :type random_state: int or np.random.RandomState
        :param n_jobs: Number of parallel threads.
        :type n_jobs: int
        :param kwargs: Other parameters
            Check https://catboost.ai/docs/concepts/python-reference_parameters-list.html
            for more parameters.
        """
        self.params = kwargs
        self.params['random_state'] = random_state
        self.params['thread_count'] = thread_count
        self.model = None

        Contract.assert_true(
            catboost_present, message="Failed to initialize CatBoostRegressor. CatBoost is not installed, "
                                      "please install CatBoost for including CatBoost based models.",
            target='CatBoostRegressor', log_safe=True
        )

    def __repr__(self):
        return _codegen_utilities.generate_repr_str(self.__class__, self.get_params(deep=False))

    def get_model(self):
        """
        Return CatBoostRegressor model.

        :return: Returns the fitted model if fit method has been called.
        Else returns None.
        """
        return self.model

    def fit(self, X, y, **kwargs):
        """
        Fit function for CatBoostRegressor model.

        :param X: Input data.
        :param y: Input target values.
        :param kwargs: Other parameters
            Check https://catboost.ai/docs/concepts/python-reference_parameters-list.html
            for more parameters.
        :return: Self after fitting the model.
        """
        args = dict(self.params)
        verbose_str = "verbose"
        if verbose_str not in args:
            args[verbose_str] = False

        self.model = catb.CatBoostRegressor(**args)
        self.model.fit(X, y, **kwargs)

        return self

    def get_params(self, deep=True):
        """
        Return parameters for the CatBoostRegressor model.

        :param deep: If True, returns the model parameters for sub-estimators as well.
        :return: Parameters for the CatBoostRegressor model.
        """
        if self.model and deep:
            return self.model.get_params(deep)
        else:
            return self.params

    def predict(self, X):
        """
        Predict the target based on the dataset features.

        :param X: Input data.
        :return: Model predictions.
        """
        if self.model is None:
            raise UntrainedModelException.create_without_pii(target='CatBoostRegressor')
        return self.model.predict(X)


class TabnetRegressor(RegressorMixin, _AbstractModelWrapper):
    """Model wrapper for the Tabnet Regressor."""

    def __init__(self, num_steps=3, hidden_features=16, epochs=10, learning_rate=0.03, problem_info=None, **kwargs):
        """
        Construct a TabnetRegressor.

        :param kwargs: Other parameters
        """
        self.params = kwargs
        self.params['num_steps'] = num_steps if num_steps is not None else 3
        self.params['hidden_features'] = hidden_features if hidden_features is not None else 16
        self.params['epochs'] = epochs if epochs is not None else 10
        self.params['learning_rate'] = learning_rate if learning_rate is not None else 0.03
        self.params['problem_info'] = problem_info
        self.model = None

        Contract.assert_true(
            tabnet_present, message="Failed to initialize TabnetRegressor. Tabnet is not installed, "
                                    "please install pytorch and Tabnet for including Tabnet based models.",
            target=self.__class__.__name__, log_safe=True
        )

    def __repr__(self):
        return _codegen_utilities.generate_repr_str(self.__class__, self.get_params(deep=False))

    def get_model(self):
        """
        Return TabnetRegressor model.

        :return: Returns the fitted model if fit method has been called.
        Else returns None.
        """
        return self.model

    def fit(self, X, y, **kwargs):
        """
        Fit function for TabnetRegressor model.

        :param X: Input data.
        :param y: Input target values.
        :param kwargs: Other parameters
        :return: Self after fitting the model.
        """
        args = dict(self.params)

        self.model = tabnet.TabnetRegressor(**args)
        self.model.fit(X, y, **kwargs)

        return self

    def get_params(self, deep=True):
        """
        Return parameters for the TabnetRegressor model.

        :param deep: If True, returns the model parameters for sub-estimators as well.
        :return: Parameters for the TabnetRegressor model.
        """
        if self.model and deep:
            return self.model.get_params(deep)
        else:
            return self.params

    def predict(self, X):
        """
        Predict the target based on the dataset features.

        :param X: Input data.
        :return: Model predictions.
        """
        if self.model is None:
            raise UntrainedModelException.create_without_pii(target=self.__class__.__name__)
        return self.model.predict(X)


class RegressionPipeline(sklearn.pipeline.Pipeline):
    """
    A pipeline with quantile predictions.

    This pipeline is a wrapper on the sklearn.pipeline.Pipeline to
    provide methods related to quantile estimation on predictions.
    """

    def __init__(self,
                 pipeline: Union[SKPipeline, nimbusml.Pipeline],
                 stddev: Union[float, List[float]]) -> None:
        """
        Create a pipeline.

        :param pipeline: The pipeline to wrap.
        :param stddev:
            The standard deviation of the residuals from validation fold(s).
        """
        # We have to initiate the parameters from the constructor to avoid warnings.
        self.pipeline = pipeline
        if not isinstance(stddev, list):
            stddev = [stddev]
        self._stddev = stddev  # type: List[float]
        if isinstance(pipeline, nimbusml.Pipeline):
            super().__init__([('nimbusml_pipeline', pipeline)])
        else:
            super().__init__(pipeline.steps, memory=pipeline.memory)
        self._quantiles = [.5]

    @property
    def stddev(self) -> List[float]:
        """The standard deviation of the residuals from validation fold(s)."""
        return self._stddev

    @property
    def quantiles(self) -> List[float]:
        """Quantiles for the pipeline to predict."""
        return self._quantiles

    @quantiles.setter
    def quantiles(self, quantiles: Union[float, List[float]]) -> None:
        if not isinstance(quantiles, list):
            quantiles = [quantiles]

        for quant in quantiles:
            if quant <= 0 or quant >= 1:
                raise ValidationException._with_error(
                    AzureMLError.create(QuantileRange, target="quantiles", quantile=str(quant))
                )

        self._quantiles = quantiles

    def predict_quantiles(self, X: Any,
                          **predict_params: Any) -> pd.DataFrame:
        """
        Get the prediction and quantiles from the fitted pipeline.

        :param X: The data to predict on.
        :return: The requested quantiles from prediction.
        :rtype: pandas.DataFrame
        """
        try:
            pred = self.predict(X, **predict_params)
        except Exception as e:
            raise PredictionException.from_exception(e, has_pii=True, target='RegressionPipeline'). \
                with_generic_msg(_generic_prediction_error_message.format(self.__class__.__name__))
        return self._get_ci(pred, np.full(len(pred), self._stddev[0]), self._quantiles)

    def _get_ci(self, y_pred: np.ndarray, stddev: np.ndarray, quantiles: List[float]) -> pd.DataFrame:
        """
        Get Confidence intervales for predictions.

        :param y_pred: The predicted values.
        :param stddev: The standard deviations.
        :param quantiles: The desired quantiles.
        """
        res = pd.DataFrame()
        for quantile in quantiles:
            ci_bound = 0.0
            if quantile != .5:
                z_score = norm.ppf(quantile)
                ci_bound = z_score * stddev
            res[quantile] = pd.Series(y_pred + ci_bound)
        return res


class ForecastingPipelineWrapper(RegressionPipeline):
    """A pipeline for forecasting."""

    # Constants for errors and warnings
    # Non recoverable errors.
    FATAL_WRONG_DESTINATION_TYPE = ("The forecast_destination argument has wrong type, "
                                    "it is a {}. We expected a datetime.")
    FATAL_DATA_SIZE_MISMATCH = "The length of y_pred is different from the X_pred"
    FATAL_WRONG_X_TYPE = ("X_pred has unsupported type, x should be pandas.DataFrame, "
                          "but it is a {}.")
    FATAL_WRONG_Y_TYPE = ("y_pred has unsupported type, y should be numpy.array or pandas.DataFrame, "
                          "but it is a {}.")
    FATAL_NO_DATA_CONTEXT = ("No y values were provided for one of time series. "
                             "We expected non-null target values as prediction context because there "
                             "is a gap between train and test and the forecaster "
                             "depends on previous values of target. ")
    FATAL_NO_DESTINATION_OR_X_PRED = ("Input prediction data X_pred and forecast_destination are both None. "
                                      + "Please provide either X_pred or a forecast_destination date, but not both.")
    FATAL_DESTINATION_AND_X_PRED = ("Input prediction data X_pred and forecast_destination are both set. "
                                    + "Please provide either X_pred or a forecast_destination date, but not both.")
    FATAL_DESTINATION_AND_Y_PRED = ("Input prediction data y_pred and forecast_destination are both set. "
                                    + "Please provide either y_pred or a forecast_destination date, but not both.")
    FATAL_Y_ONLY = "If y_pred is provided X_pred should not be None."
    FATAL_NO_LAST_DATE = ("The last training date was not provided."
                          "One of time series in scoring set was not present in training set.")
    FATAL_EARLY_DESTINATION = ("Input prediction data X_pred or input forecast_destination contains dates "
                               + "prior to the latest date in the training data. "
                               + "Please remove prediction rows with datetimes in the training date range "
                               + "or adjust the forecast_destination date.")
    FATAL_NO_TARGET_IN_Y_DF = ("The y_pred is a data frame, "
                               "but it does not contain the target value column")
    FATAL_WRONG_QUANTILE = "Quantile should be a number between 0 and 1 (not inclusive)."
    FATAL_NO_TS_TRANSFORM = ("The time series transform is absent. "
                             "Please try training model again.")

    FATAL_NO_GRAIN_IN_TRAIN = ("One of time series was not present in the training data set. "
                               "Please remove it from the prediction data set to proceed.")
    FATAL_NO_TARGET_IMPUTER = 'No target imputers were found in TimeSeriesTransformer.'
    FATAL_NONPOSITIVE_HORIZON = "Forecast horizon must be a positive integer."

    # Constants
    TEMP_PRED_COLNAME = '__predicted'

    def __init__(self,
                 pipeline: SKPipeline,
                 stddev: List[float]) -> None:
        """
        Create a pipeline.

        :param pipeline: The pipeline to wrap.
        :type pipeline: sklearn.pipeline.Pipeline
        :param stddev:
            The standard deviation of the residuals from validation fold(s).
        """
        super().__init__(pipeline, stddev)
        for _, transformer in pipeline.steps:
            # FIXME: Work item #400231
            if type(transformer).__name__ == 'TimeSeriesTransformer':
                ts_transformer = transformer

        if "ts_transformer" not in vars() or ts_transformer is None:
            raise ValidationException._with_error(AzureMLError.create(
                AutoMLInternal, target="ForecastingPipelineWrapper",
                error_details='Failed to initialize ForecastingPipelineWrapper: {}'.format(
                    ForecastingPipelineWrapper.FATAL_NO_TS_TRANSFORM))
            )
        y_transformer = None
        if hasattr(self.pipeline, 'y_transformer'):
            y_transformer = self.pipeline.y_transformer

        self._ts_transformer = ts_transformer
        self._y_transformer = y_transformer
        self._origin_col_name = ts_transformer.origin_column_name
        self._time_col_name = ts_transformer.time_column_name
        self._quantiles = [.5]
        self._horizon_idx = None  # type: Optional[int]
        self.grain_column_names = ts_transformer.grain_column_names
        self.target_column_name = ts_transformer.target_column_name
        self.data_frequency = ts_transformer.freq_offset
        self.forecast_origin = {}  # type: Dict[GrainType, pd.Timestamp]

    def __setstate__(self, state):
        if "_y_transformer" not in state:
            state["_y_transformer"] = None
        self.__dict__.update(state)

    @property
    def time_column_name(self) -> str:
        """Return the name of the time column."""
        return cast(str, self._time_col_name)

    @property
    def origin_col_name(self) -> str:
        """Return the origin column name."""
        # Note this method will return origin column name,
        # which is only used for reconstruction of a TimeSeriesDataFrame.
        # If origin column was introduced during transformation it is still None
        # on ts_transformer.
        if self._origin_col_name is None:
            self._origin_col_name = self._ts_transformer.origin_column_name
        # TODO: Double check type: Union[str, List[str]]
        ret = self._origin_col_name if self._origin_col_name \
            else constants.TimeSeriesInternal.ORIGIN_TIME_COLNAME_DEFAULT
        return cast(str, ret)

    def _check_data(self, X_pred: pd.DataFrame,
                    y_pred: Union[pd.DataFrame, np.ndarray],
                    forecast_destination: pd.Timestamp) -> None:
        """
        Check the user input.

        :param X_pred: the prediction dataframe combining X_past and X_future in a time-contiguous manner.
                       Empty values in X_pred will be imputed.
        :param y_pred: the target value combining definite values for y_past and missing values for Y_future.
        :param forecast_destination: Forecast_destination: a time-stamp value.
                                     Forecasts will be made all the way to the forecast_destination time,
                                     for all grains. Dictionary input { grain -> timestamp } will not be accepted.
                                     If forecast_destination is not given, it will be imputed as the last time
                                     occurring in X_pred for every grain.
        :raises: DataException

        """
        # Check types
        # types are not PII
        if X_pred is not None and not isinstance(X_pred, pd.DataFrame):
            raise ForecastingConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentType,
                    target='X_pred',
                    reference_code=ReferenceCodes._TSDF_INVALID_ARG_FC_PIPELINE_X_PRED,
                    argument='X_pred',
                    expected_types='pandas.DataFrame',
                    actual_type=str(type(X_pred))
                )
            )
        if y_pred is not None and not isinstance(y_pred, pd.DataFrame) and not isinstance(y_pred, np.ndarray):
            raise ForecastingConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentType,
                    target='y_pred',
                    reference_code=ReferenceCodes._TSDF_INVALID_ARG_FC_PIPELINE_Y_PRED,
                    argument='y_pred',
                    expected_types='numpy.array or pandas.DataFrame',
                    actual_type=str(type(y_pred))
                )
            )
        if forecast_destination is not None and not isinstance(forecast_destination, pd.Timestamp) and not isinstance(
                forecast_destination, np.datetime64):
            raise ForecastingConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentType,
                    target='forecast_destination',
                    reference_code=ReferenceCodes._TSDF_INVALID_ARG_FC_PIPELINE_FC_DES,
                    argument='forecast_destination',
                    expected_types='pandas.Timestamp, numpy.datetime64',
                    actual_type=str(type(forecast_destination))
                )
            )
        # Check wrong parameter combinations.
        if (forecast_destination is None) and (X_pred is None):
            raise ForecastingConfigException._with_error(
                AzureMLError.create(
                    TimeseriesDfInvalidArgOnlyOneArgRequired,
                    target='forecast_destination, X_pred',
                    reference_code=ReferenceCodes._TSDF_INVALID_ARG_FC_PIPELINE_NO_DESTINATION_OR_X_PRED,
                    arg1='X_pred',
                    arg2='forecast_destination'
                )
            )
        if (forecast_destination is not None) and (X_pred is not None):
            raise ForecastingConfigException._with_error(
                AzureMLError.create(
                    TimeseriesDfInvalidArgOnlyOneArgRequired,
                    target='forecast_destination, X_pred',
                    reference_code=ReferenceCodes._TSDF_INVALID_ARG_FC_PIPELINE_DESTINATION_AND_X_PRED,
                    arg1='X_pred',
                    arg2='forecast_destination'
                )
            )
        if (forecast_destination is not None) and (y_pred is not None):
            raise ForecastingConfigException._with_error(
                AzureMLError.create(
                    TimeseriesDfInvalidArgOnlyOneArgRequired,
                    target='forecast_destination, y_pred',
                    reference_code=ReferenceCodes._TSDF_INVALID_ARG_FC_PIPELINE_DESTINATION_AND_Y_PRED,
                    arg1='y_pred',
                    arg2='forecast_destination'
                )
            )
        if X_pred is None and y_pred is not None:
            # If user provided only y_pred raise the error.
            raise ForecastingConfigException._with_error(
                AzureMLError.create(
                    TimeseriesDfInvalidArgFcPipeYOnly,
                    target='X_pred, y_pred',
                    reference_code=ReferenceCodes._TSDF_INVALID_ARG_FC_PIPELINE_Y_ONLY
                )
            )

    def _check_convert_grain_types(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Check that the grains have the correct type.

        :param X: The test data frame.
        :return: The same data frame with grain columns converted.
        """
        effective_grain = self.grain_column_names  # type: Optional[List[str]]
        if self.grain_column_names == [constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN] and \
                self.grain_column_names[0] not in X.columns:
            effective_grain = None
        # Try to convert the grain type if TS transformer has learned it first.
        X = self._ts_transformer._convert_grain_type_safe(X)
        X, _ = convert_check_grain_value_types(
            X, None, effective_grain, self._ts_transformer._featurization_config.__dict__,
            ReferenceCodes._TS_VALIDATION_GRAIN_TYPE_INFERENCE)
        return X

    def short_grain_handling(self) -> bool:
        """Return true if short or absent grains handling is enabled for the model."""
        return forecasting_utils.get_pipeline_step(
            self._ts_transformer.pipeline, constants.TimeSeriesInternal.SHORT_SERIES_DROPPEER) is not None

    def is_grain_dropped(self, grain: GrainType) -> bool:
        """
        Return true if the grain is going to be dropped.

        :param grain: The grain to test if it will be dropped.
        :return: True if the grain will be dropped.
        """
        dropper = forecasting_utils.get_pipeline_step(
            self._ts_transformer.pipeline, constants.TimeSeriesInternal.SHORT_SERIES_DROPPEER)
        return dropper is not None and grain not in dropper.grains_to_keep

    def _check_max_horizon_and_grain(self, grain: GrainType,
                                     df_one: pd.DataFrame,
                                     ignore_data_errors: bool) -> None:
        """
        Raise error if the prediction data frame dates exceeds the max_horizon.

        :param grain: The tuple, designating grain.
        :param df_one: The data frame corresponding to a single grain.

        """
        last_train = self._ts_transformer.dict_latest_date.get(grain)
        # The grain was not met in the train data set. Throw the error.
        if last_train is None:
            if self.short_grain_handling():
                # We return here from this function, because this grain has to be dropped
                # during transform.
                return
            else:
                raise ForecastingDataException._with_error(
                    AzureMLError.create(TimeseriesGrainAbsentNoGrainInTrain, target='grain',
                                        reference_code=ReferenceCodes._TS_GRAIN_ABSENT_MDL_WRP_CHK_GRAIN,
                                        grain=grain)
                )
        if self._lag_or_rw_enabled():
            last_known = self._get_last_y_one_grain(df_one, grain, ignore_data_errors)
            if last_known is not None:
                last_known = max(self._ts_transformer.dict_latest_date[grain], last_known)
            else:
                last_known = last_train
                # If there is a gap between train and test, then the last known date will be one
                # period before the test set.
                if ignore_data_errors:
                    last_known = max(last_known, df_one[self.time_column_name].min() - self.data_frequency)
            horizon = len(pd.date_range(start=last_known,
                                        end=df_one[self.time_column_name].max(),
                                        freq=self.data_frequency)) - 1
            if horizon > self._ts_transformer.max_horizon:
                raise DataException._with_error(AzureMLError.create(ForecastHorizonExceeded, target="horizon"))

    def _do_check_max_horizon(self,
                              grain: GrainType,
                              df_one: pd.DataFrame,
                              ignore_data_errors: bool) -> bool:
        """
        Check whether the prediction data frame dates exceeds the max_horizon.

        :param grain: The tuple, designating grain.
        :param df_one: The data frame corresponding to a single grain.
        :param ignore_data_errors: Ignore errors in user data.
        :returns: True/False whether max_horizon is exceeded.

        """
        try:
            self._check_max_horizon_and_grain(grain, df_one, ignore_data_errors)
        # Exceeding maximum horizon is no longer an error.
        except DataException as de:
            if de.error_code == ForecastHorizonExceeded().code:
                return True
            raise
        return False

    def _create_prediction_data_frame(self,
                                      X_pred: pd.DataFrame,
                                      y_pred: Union[pd.DataFrame, np.ndarray],
                                      forecast_destination: pd.Timestamp,
                                      ignore_data_errors: bool) -> pd.DataFrame:
        """
        Create the data frame which will be used for prediction purposes.

        :param X_pred: the prediction dataframe combining X_past and X_future in a time-contiguous manner.
                       Empty values in X_pred will be imputed.
        :param y_pred: the target value combining definite values for y_past and missing values for Y_future.
        :param forecast_destination: Forecast_destination: a time-stamp value.
                                     Forecasts will be made all the way to the forecast_destination time,
                                     for all grains. Dictionary input { grain -> timestamp } will not be accepted.
                                     If forecast_destination is not given, it will be imputed as the last time
                                     occurring in X_pred for every grain.
        :param ignore_data_errors: Ignore errors in user data.
        :returns: The clean data frame.
        :raises: DataException

        """
        if X_pred is not None:
            X_copy = X_pred.copy()
            X_copy.reset_index(inplace=True, drop=True)
            if self.grain_column_names[0] == constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN and \
                    self.grain_column_names[0] not in X_copy.columns:
                X_copy[constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN] = \
                    constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN
            # Remember the forecast origins for each grain.
            # We will trim the data frame by these values at the end.
            # Also do the sanity check if there is at least one known grain.
            has_known_grain = False
            for grain, df_one in X_copy.groupby(self.grain_column_names):
                self.forecast_origin[grain] = df_one[self._time_col_name].min()
                has_known_grain = has_known_grain or grain in self._ts_transformer.dict_latest_date
            if not has_known_grain:
                raise ForecastingDataException._with_error(
                    AzureMLError.create(TimeseriesNoUsableGrains,
                                        target='X_test',
                                        reference_code=ReferenceCodes._TS_NO_USABLE_GRAINS))
            special_columns = self.grain_column_names.copy()
            special_columns.append(self._ts_transformer.time_column_name)
            if self.origin_col_name in X_copy.columns:
                special_columns.append(self.origin_col_name)
            if self._ts_transformer.group_column in X_copy.columns:
                special_columns.append(self._ts_transformer.group_column)
            if self._ts_transformer.drop_column_names:
                dropping_columns = self._ts_transformer.drop_column_names
            else:
                dropping_columns = []
            categorical_columns = []
            dtypes_transformer = forecasting_utils.get_pipeline_step(
                self._ts_transformer.pipeline, constants.TimeSeriesInternal.RESTORE_DTYPES)
            if dtypes_transformer is not None:
                categorical_columns = dtypes_transformer.get_non_numeric_columns()
            for column in X_copy.columns:
                if column not in special_columns and \
                        column not in dropping_columns and \
                        column not in categorical_columns and \
                        column in X_copy.select_dtypes(include=[np.number]).columns and \
                        all(np.isnan(float(var)) for var in X_copy[column].values):
                    self._warn_or_raise(TimeseriesDfContainsNaN,
                                        ReferenceCodes._FORECASTING_COLUMN_IS_NAN,
                                        ignore_data_errors)
                    break

            if y_pred is None:
                y_pred = np.repeat(np.NaN, len(X_pred))
            if y_pred.shape[0] != X_pred.shape[0]:
                # May be we need to revisit this assertion.
                raise ForecastingDataException._with_error(
                    AzureMLError.create(
                        TimeseriesWrongShapeDataSizeMismatch,
                        target='y_pred.shape[0] != X_pred.shape[0]',
                        reference_code=ReferenceCodes._TS_WRONG_SHAPE_CREATE_PRED_DF,
                        var1_name='X_pred',
                        var1_len=X_pred.shape[0],
                        var2_name='y_pred',
                        var2_len=y_pred.shape[0]
                    )
                )
            if isinstance(y_pred, pd.DataFrame):
                if self._ts_transformer.target_column_name not in y_pred.columns:
                    raise ForecastingConfigException._with_error(
                        AzureMLError.create(
                            MissingColumnsInData,
                            target='y_pred',
                            reference_code=ReferenceCodes._TSDF_INVALID_ARG_FC_PIPELINE_NO_TARGET_IN_Y_DF,
                            columns='target value column',
                            data_object_name='y_pred'
                        )
                    )
                X_copy = pd.merge(
                    left=X_copy,
                    right=y_pred,
                    how='left',
                    left_index=True,
                    right_index=True)
                if X_copy.shape[0] != X_pred.shape[0]:
                    raise ForecastingDataException._with_error(
                        AzureMLError.create(
                            TimeseriesWrongShapeDataSizeMismatch,
                            target='X_copy.shape[0] != X_pred.shape[0]',
                            reference_code=ReferenceCodes._TS_WRONG_SHAPE_CREATE_PRED_DF_XCPY_XPRED,
                            var1_name='X_copy',
                            var1_len=X_copy.shape[0],
                            var2_name='X_pred',
                            var2_len=X_pred.shape[0]
                        )
                    )
            elif isinstance(y_pred, np.ndarray) and X_copy.shape[0] == y_pred.shape[0]:
                X_copy[self._ts_transformer.target_column_name] = y_pred
            # y_pred may be pd.DataFrame or np.ndarray only, we are checking it in _check_data.
            # At that point we have generated the data frame which contains Target value column
            # filled with y_pred. The part which will need to be should be
            # filled with np.NaNs.
        else:
            # Create the empty data frame from the last date in the training set for each grain
            # and fill it with NaNs. Impute these data.
            if self._ts_transformer.dict_latest_date == {}:
                raise ForecastingDataException._with_error(
                    AzureMLError.create(TimeseriesGrainAbsentNoLastDate,
                                        target='self._ts_transformer.dict_latest_date',
                                        reference_code=ReferenceCodes._TS_GRAIN_ABSENT_MDL_WRP_NO_LAST_DATE)
                )
            dfs = []
            for grain_tuple in self._ts_transformer.dict_latest_date.keys():
                if pd.Timestamp(forecast_destination) <= self._ts_transformer.dict_latest_date[grain_tuple]:
                    raise ForecastingDataException._with_error(
                        AzureMLError.create(
                            TimeseriesWrongShapeDataEarlyDest,
                            target='forecast_destination',
                            reference_code=ReferenceCodes._TS_WRONG_SHAPE_FATAL_EARLY_DESTINATION
                        )
                    )
                # Start with the next date after the last seen date.
                start_date = \
                    self._ts_transformer.dict_latest_date[grain_tuple] + to_offset(self._ts_transformer.freq)
                df_dict = {
                    self._time_col_name: pd.date_range(
                        start=start_date,
                        end=forecast_destination,
                        freq=self._ts_transformer.freq)}
                if not isinstance(grain_tuple, tuple):
                    df_dict[self.grain_column_names[0]] = grain_tuple
                else:
                    for i in range(len(self.grain_column_names)):
                        df_dict[self.grain_column_names[i]] = grain_tuple[i]
                for col in cast(List[Any], self._ts_transformer.columns):
                    if col not in df_dict.keys():
                        df_dict[col] = np.NaN
                # target_column_name is not in the data frame columns by
                # default.
                df_dict[self._ts_transformer.target_column_name] = np.NaN
                dfs.append(pd.DataFrame(df_dict))
            X_copy = pd.concat(dfs)
            # At that point we have generated the data frame which contains target value column.
            # The data frame is filled with imputed data. Only target column is filled with np.NaNs,
            # because all gap between training data and forecast_destination
            # should be predicted.
        return X_copy

    def _infer_missing_data(
            self,
            X: pd.DataFrame,
            ignore_data_errors: bool,
            ignore_errors_and_warnings: bool) -> pd.DataFrame:
        """
        Infer missing data in the data frame X.

        :param X: The data frame used for the inference.
        :param ignore_data_errors: Ignore errors in user data.
        :param ignore_errors_and_warnings : Ignore the y-related errors and warnings.
        :returns: the data frame with no NaNs
        :raises: DataException
        """
        df_inferred = []
        is_reported = False
        for grain, df_one in X.groupby(self.grain_column_names):
            # If the grain is categorical, groupby may result in the empty
            # data frame. If it is the case, skip it.
            if df_one.shape[0] == 0:
                continue
            last_known_y_date = self._get_last_y_one_grain(df_one, grain,
                                                           ignore_data_errors,
                                                           ignore_errors_and_warnings)
            if last_known_y_date is None:
                first_unknown_y_date = min(df_one[self._time_col_name])
            else:
                first_unknown_y_date = last_known_y_date + self.data_frequency
            # If the look back features are enabled, we have to check if window size or lag size are
            # larger then max_horizon.
            lookback_horizon = max([self.max_horizon, max(self.target_lags), self.target_rolling_window_size])
            if self._ts_transformer.dict_latest_date.get(grain) is None:
                # If the grain is not present in the training set and short grains should be dropped
                # we do not want to infer missing data, because this grain will be dropped during
                # transformation.
                expected_start = min(df_one[self._time_col_name])
            else:
                expected_start = max(self._ts_transformer.dict_latest_date.get(grain) + self.data_frequency,
                                     first_unknown_y_date - self.data_frequency * lookback_horizon)
            hasgap = min(df_one[self._time_col_name]) > expected_start
            if all(pd.isnull(y) for y in df_one[constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN]) and \
                    not is_reported and hasgap and self._lag_or_rw_enabled() and not self.is_grain_dropped(grain):
                # Do not warn user multiple times.
                self._warn_or_raise(TimeseriesNoDataContext,
                                    ReferenceCodes._FORECASTING_NO_DATA_CONTEXT,
                                    ignore_data_errors)
                is_reported = True
            if self._ts_transformer.dict_latest_date.get(grain) is None:
                if not self.short_grain_handling():
                    # Throw absent grain error only if short grains are not handled.
                    raise ForecastingDataException._with_error(
                        AzureMLError.create(TimeseriesGrainAbsentNoDataContext, target='grain',
                                            grain=grain,
                                            reference_code=ReferenceCodes._TS_GRAIN_ABSENT_MDL_WRP_NO_DATA_CONTEXT)
                    )
            else:
                if min(df_one[self._time_col_name]) <= self._ts_transformer.dict_latest_date[grain]:
                    raise ForecastingDataException._with_error(
                        AzureMLError.create(
                            TimeseriesWrongShapeDataEarlyDest,
                            target='self._ts_transformer',
                            reference_code=ReferenceCodes._TS_WRONG_SHAPE_FATAL_EARLY_DESTINATION2
                        )
                    )
            # If we are given a data context, we need to mark missing values in the context
            # so that it will be featurized correctly e.g. with lag-by-occurrence
            if self._ts_transformer._keep_missing_dummies_on_target_safe():
                missing_target_dummy_transform = self._ts_transformer._init_missing_y()
                df_one = missing_target_dummy_transform.fit_transform(df_one)
                not_imputed_val = missing_target_dummy_transform.MARKER_VALUE_NOT_MISSING
                if last_known_y_date is None:
                    # There's no data context, mark all rows as not-missing
                    df_one[self._ts_transformer.target_imputation_marker_column_name] = not_imputed_val
                else:
                    # Mark targets with dates in the prediction range as not-missing
                    sel_prediction_dates = df_one[self._time_col_name] > last_known_y_date
                    df_one.loc[sel_prediction_dates, self._ts_transformer.target_imputation_marker_column_name] = \
                        not_imputed_val

            # If we have a gap between train and predict data set, we need to extend the test set.
            # If there is no last known date, nothing can be done.
            if self._ts_transformer.dict_latest_date.get(grain) is not None:
                # If we know the last date, we can evaluate and fill the gap.
                if hasgap and self._lag_or_rw_enabled():
                    # If there is a gap between train and test data for the
                    # given grain, extend the test data frame.
                    ext_dates = pd.date_range(
                        start=expected_start,
                        end=df_one[self._time_col_name].min() - self.data_frequency,
                        freq=self.data_frequency)
                    if len(ext_dates) == 0:  # end - start < self.data_frequency
                        # In this case we will just create one row.
                        ext_dates = pd.date_range(
                            start=expected_start,
                            periods=1,
                            freq=self.data_frequency)
                    extension = pd.DataFrame(np.nan, index=np.arange(
                        len(ext_dates)), columns=df_one.columns.values)
                    extension[self._time_col_name] = ext_dates
                    if not isinstance(grain, tuple):
                        extension[self.grain_column_names[0]] = grain
                    else:
                        for i in range(len(self.grain_column_names)):
                            extension[self.grain_column_names[i]] = grain[i]
                    # Make a temporary time series data frame to apply
                    # imputers.
                    tsdf_ext = tsdf.TimeSeriesDataFrame(
                        extension,
                        time_colname=self._ts_transformer.time_column_name,
                        grain_colnames=self._ts_transformer.grain_column_names,
                        ts_value_colname=self._ts_transformer.target_column_name)
                    # Mark the gap with missing target dummy indicators
                    if self._ts_transformer._keep_missing_dummies_on_target_safe():
                        tsdf_ext = self._ts_transformer._init_missing_y().fit_transform(tsdf_ext)
                    # Replace np.NaNs by imputed values.
                    tsdf_ext = forecasting_utils.get_pipeline_step(
                        self._ts_transformer.pipeline,
                        constants.TimeSeriesInternal.IMPUTE_NA_NUMERIC_DATETIME
                    ).transform(tsdf_ext)
                    # Replace np.NaNs in y column.
                    imputer = self._ts_transformer.y_imputers.get(grain)
                    if imputer is None:
                        # Should not happen on fitted time series transformer.
                        raise UntrainedModelException(
                            ForecastingPipelineWrapper.FATAL_NO_TARGET_IMPUTER,
                            target='ForecastingPipelineWrapper', has_pii=False)
                    tsdf_ext = imputer.transform(tsdf_ext)
                    # Return the regular data frame.
                    extension = pd.DataFrame(tsdf_ext)
                    extension.reset_index(drop=False, inplace=True)
                    df_one = pd.concat([extension, df_one], sort=True)
            # Make sure we do not have a gaps in the y.
            # We are actually doing it only if ignore_data_errors is set to True,
            # or we do not have non contiguous NaNs and code have no effect.
            df_one = self._impute_missing_y_one_grain(df_one)
            df_inferred.append(df_one)
        X = pd.concat(df_inferred, sort=True)
        return X

    def _impute_missing_y_one_grain(self,
                                    df_one: pd.DataFrame,
                                    is_sorted: bool = True) -> pd.DataFrame:
        """
        Do the imputation to remove the potential gap inside y values.

        :param df_one: The data frame with potential gaps in target values.
        :param is_sorted:
        :return: The same data frame with the gaps filled in.
        """
        # TODO: Unify this imputation method with self._ts_transformer.y_imputers
        if not is_sorted:
            # Because we have already ran _get_last_y_one_grain before, we know
            # that df_one is sorted by time column.
            # This sorting is needed only for bfill method.
            df_one.sort_values(by=self.time_column_name)
        df_one[self._ts_transformer.target_column_name].fillna(
            None, 'bfill', axis=0, inplace=True)
        return df_one

    def _regular_forecast(self,
                          X_copy: pd.DataFrame,
                          ignore_data_errors: bool,
                          is_rolling_forecast: bool = False) -> pd.DataFrame:
        """
        Do the forecast on the data frame X_pred.

        DataError is thrown if neither X_pred and y_pred nor
        :param X_copy: the prediction dataframe.
        :param ignore_data_errors: Ignore errors in user data.
        :param is_rolling_forecast: Flag to indicate rolling forecast which may need special handling.
        :returns: the subframe corresponding to Y_future filled in with the respective forecasts.
                  Any missing values in Y_past will be filled by imputer.
        :rtype: pandas.DataFrame
        """
        # Set/Reset forecast origin state
        self.forecast_origin = {}
        # We need to make sure that we have a context. If train set is followed by a test/predict set,
        # there should be no error. otherwise we will need to infer missing data.
        # The part of the data frame, for which y_pred is known will be
        # removed.
        X_copy = self._infer_missing_data(X_copy, ignore_data_errors, is_rolling_forecast)
        last_step = self.pipeline.steps[len(self.pipeline.steps) - 1][1]
        # Pre processing.
        test_feats = None  # type: Optional[pd.DataFrame]
        y_known_series = None  # type: Optional[pd.Series]
        for i in range(len(self.pipeline.steps) - 1):
            # FIXME: Work item #400231
            if type(self.pipeline.steps[i][1]).__name__ == 'TimeSeriesTransformer':
                test_feats = self.pipeline.steps[i][1].transform(X_copy)
                # We do not need the target column now.
                # The target column is deleted by the rolling window during transform.
                # If there is no rolling window we need to make sure the column was dropped.
                if self._ts_transformer.target_column_name in test_feats.columns:
                    # We want to store the y_known_series for future use.
                    y_known_series = test_feats[self._ts_transformer.target_column_name]
                    test_feats.drop(self._ts_transformer.target_column_name, inplace=True, axis=1)
                # If origin times are present, remove nans from look-back features and select the latest origins
                if self.origin_col_name in test_feats.index.names:
                    y = np.zeros(test_feats.shape[0])
                    test_feats, _ = self._ts_transformer._remove_nans_from_look_back_features(test_feats, y)
                    test_feats = self._ts_transformer._select_latest_origin_dates(test_feats)
                X_copy = test_feats.copy()
            else:
                X_copy = self.pipeline.steps[i][1].transform(X_copy)

        try:
            y_preds = last_step.predict(X_copy)
        except Exception as e:
            raise PredictionException.from_exception(e, has_pii=True, target='ForecastingPipelineWrapper'). \
                with_generic_msg(_generic_prediction_error_message.format(self.__class__.__name__))
        # We know that test_feats is not None, but we have to put this assertion here
        # to ensure mypy test is passing.
        # We are raising the exception if we have no time series transformer on the stage
        # of tst creation.
        assert (test_feats is not None)
        test_feats[constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN] = y_preds

        test_feats = self._postprocess_output(test_feats, y_known_series)
        return test_feats

    def _recursive_forecast(self,
                            X_copy: pd.DataFrame,
                            ignore_data_errors: bool) -> pd.DataFrame:
        """
        Produce forecasts recursively on a rolling origin.

        Each iteration makes a forecast for the next 'max_horizon' periods
        with respect to the current origin, then advances the origin by the
        horizon time duration. The prediction context for each forecast is set so
        that the forecaster uses forecasted target values for times prior to the current
        origin time for constructing lag features.

        This function returns a vector of forecasted target values and a concatenated DataFrame
        of rolling forecasts.

        :param X_copy: the prediction dataframe generated from _create_prediction_data_frame.
        :param ignore_data_errors: Ignore errors in user data.
        :returns: the subframe corresponding to Y_future filled in with the respective forecasts.
                  Any missing values in Y_past will be filled by imputer.
        :rtype: pandas.DataFrame
        """
        X_rlt = []
        dfs = []
        start_dates = {}
        # In this code we need to split data into batches,
        # so that each of batches is less then max horizon.
        # First we will determine the forecasting origin for each of grain.
        # We will keep these data in start_dates dictionary.
        # We will impute missing target here.
        for grp, df_one in X_copy.groupby(self.grain_column_names):
            if self.is_grain_dropped(grp):
                continue
            # Do not use the output but run the validation for df_one.
            self._get_last_y_one_grain(df_one, grp, ignore_data_errors)
            # Populate the start dates dictionary.
            start_dates[grp] = df_one[self.time_column_name].min()
            # After the validation is done, fill the gaps in y.
            df_one = self._impute_missing_y_one_grain(df_one)
            dfs.append(df_one)
        X_copy = pd.concat(dfs)
        groupby_ob = X_copy.groupby(self.grain_column_names)
        previous_batch = None  # type: Optional[pd.DataFrame]
        merge_index = [self._time_col_name]
        if self.grain_column_names:
            merge_index.extend(self.grain_column_names)
        # After knowing the start dates, we can start forecasting.
        while start_dates:
            batch, new_start_dates = self._get_next_batch(groupby_ob, previous_batch, start_dates.copy())
            fcst = self._regular_forecast(batch, ignore_data_errors, is_rolling_forecast=True)
            batch.drop(TimeSeriesInternal.DUMMY_TARGET_COLUMN, axis=1, inplace=True)
            batch = batch.merge(fcst[TimeSeriesInternal.DUMMY_TARGET_COLUMN], how='left', on=merge_index, sort=False)
            # If we have added the old values to the data set, we need to cut it.
            if previous_batch is not None:
                # The data missing from start_dates were not used for this iteration of
                # forecasting and need to be cut.
                batch = (batch.groupby(self.grain_column_names, group_keys=False)
                         .apply(lambda df:
                                df[df[self._time_col_name] >= start_dates[df.name]]
                                if df.name in start_dates else pd.DataFrame()))
                fcst = (fcst.groupby(self.grain_column_names, group_keys=False)
                        .apply(lambda df:
                               df[df.index.get_level_values(self._time_col_name) >= start_dates[df.name]]
                               if df.name in start_dates else pd.DataFrame()))
            X_rlt.append(fcst)
            previous_batch = batch
            start_dates = new_start_dates
        return pd.concat(X_rlt, sort=False, ignore_index=False)

    def _get_next_batch(self, groupby_ob: Any, previous_df: Optional[pd.DataFrame],
                        start_dates: Dict[GrainType, pd.Timestamp]
                        ) -> Tuple[pd.DataFrame, Dict[GrainType, pd.Timestamp]]:
        """
        Get the next batch of the data frame.

        :param groupby_ob: The groupby object to get the batches from.
        :param start_dates: the start_dates.
        :return: The tuple of new data frame and next start times.
        """
        new_batch_list = []
        for grain_one, df_one in groupby_ob:
            # If grain is not in start dates, we do not need to do
            # the forecast.
            if grain_one not in start_dates:
                continue
            origin_time = start_dates[grain_one]
            # Set the horizon time - end date of the forecast
            horizon_time = origin_time + self.max_horizon * self.data_frequency
            # Extract test data from an expanding window up-to the horizon
            expand_wind = (df_one[self.time_column_name] >= origin_time) & (
                df_one[self.time_column_name] < horizon_time)
            df_pred_expand = df_one[expand_wind]

            # If the max time of given grain is less then horizon, we remove it from start times.
            if df_one[self.time_column_name].max() < horizon_time:
                del start_dates[grain_one]
            else:
                start_dates[grain_one] = horizon_time
            new_batch_list.append(df_pred_expand)
        X_new = pd.concat(new_batch_list, sort=False, ignore_index=True)
        if previous_df is not None:
            X_new = X_new.append(previous_df, sort=False, ignore_index=True)
        return X_new, start_dates

    def _use_recursive_forecast(self,
                                X_copy: pd.DataFrame,
                                ignore_data_errors: bool = False) -> bool:
        """
        Describe conditions for using recursive forecast method.
        Recursive forecast is invoked when the prediction length is greater than the max_horizon
        and lookback features are enables. This function returns a True/False for
        whether recursive forecast method should be invoked.

        :param X_copy: the prediction dataframe generated from _create_prediction_data_frame.
        :param X_pred: the prediction dataframe combining X_past and X_future in a time-contiguous manner.
                       Empty values in X_pred will be imputed.
        :param y_pred: the target value combining definite values for y_past and missing values for Y_future.
                       If None the predictions will be made for every X_pred.
        :param forecast_destination: Forecast_destination: a time-stamp value.
                                     Forecasts will be made all the way to the forecast_destination time,
                                     for all grains. Dictionary input { grain -> timestamp } will not be accepted.
                                     If forecast_destination is not given, it will be imputed as the last time
                                     occurring in X_pred for every grain.
        :type forecast_destination: pandas.Timestamp
        :param ignore_data_errors: Ignore errors in user data.
        :type ignore_data_errors: bool
        :returns: True/False for whether recursive forecast method should be invoked.
        :rtype: bool
        """
        if not self._lag_or_rw_enabled():
            return False
        else:
            for grain, df_one in X_copy.groupby(self.grain_column_names):
                if not self.is_grain_dropped(grain):
                    if self._do_check_max_horizon(grain, df_one, ignore_data_errors):
                        return True
            return False

    def _convert_time_column_name_safe(self, X: pd.DataFrame, reference_code: str) -> pd.DataFrame:
        """
        Convert the time column name to date time.

        :param X: The prediction data frame.
        :param reference_code: The reference code to be given to error.
        :return: The modified data frame.
        :raises: DataException
        """
        try:
            X[self.time_column_name] = pd.to_datetime(X[self.time_column_name])
        except Exception as e:
            raise DataException._with_error(
                AzureMLError.create(PandasDatetimeConversion, column=self.time_column_name,
                                    column_type=X[self.time_column_name].dtype,
                                    target=constants.TimeSeries.TIME_COLUMN_NAME,
                                    reference_code=reference_code),
                inner_exception=e
            ) from e
        return X

    def forecast(self,
                 X_pred: Optional[pd.DataFrame] = None,
                 y_pred: Optional[Union[pd.DataFrame,
                                        np.ndarray]] = None,
                 forecast_destination: Optional[pd.Timestamp] = None,
                 ignore_data_errors: bool = False) -> Tuple[np.ndarray,
                                                            pd.DataFrame]:
        """
        Do the forecast on the data frame X_pred.

        :param X_pred: the prediction dataframe combining X_past and X_future in a time-contiguous manner.
                       Empty values in X_pred will be imputed.
        :param y_pred: the target value combining definite values for y_past and missing values for Y_future.
                       If None the predictions will be made for every X_pred.
        :param forecast_destination: Forecast_destination: a time-stamp value.
                                     Forecasts will be made all the way to the forecast_destination time,
                                     for all grains. Dictionary input { grain -> timestamp } will not be accepted.
                                     If forecast_destination is not given, it will be imputed as the last time
                                     occurring in X_pred for every grain.
        :type forecast_destination: pandas.Timestamp
        :param ignore_data_errors: Ignore errors in user data.
        :type ignore_data_errors: bool
        :returns: Y_pred, with the subframe corresponding to Y_future filled in with the respective forecasts.
                  Any missing values in Y_past will be filled by imputer.
        :rtype: tuple
        """
        # check the format of input
        self._check_data(X_pred, y_pred, forecast_destination)

        # Check that the grains have correct types.
        if X_pred is not None:
            X_pred = self._check_convert_grain_types(X_pred)
        # Handle the case where both an index and column have the same name. Merge/groupby both
        # cannot handle cases where column name is also in index above version 0.23. In addition,
        # index is only accepted as a kwarg in versions >= 0.24
        dict_rename = {}
        dict_rename_back = {}
        pd_compatible = pd.__version__ >= '0.24.0'
        if pd_compatible and X_pred is not None:
            for ix_name in X_pred.index.names:
                if ix_name in X_pred.columns:
                    temp_name = 'temp_{}'.format(uuid.uuid4())
                    dict_rename[ix_name] = temp_name
                    dict_rename_back[temp_name] = ix_name
            if len(dict_rename) > 0:
                X_pred.rename_axis(index=dict_rename, inplace=True)
        # If the data had to be aggregated, we have to do it here.

        if X_pred is not None:
            X_pred = self._convert_time_column_name_safe(X_pred, ReferenceCodes._FORECASTING_CONVERT_INVALID_VALUE)
            X_pred, y_pred = self.preaggregate_data_set(X_pred, y_pred)
        # create the prediction data frame
        X_copy = self._create_prediction_data_frame(
            X_pred, y_pred, forecast_destination, ignore_data_errors)
        if self._use_recursive_forecast(X_copy=X_copy, ignore_data_errors=ignore_data_errors):
            test_feats = self._recursive_forecast(X_copy, ignore_data_errors)
        else:
            test_feats = self._regular_forecast(X_copy, ignore_data_errors)
        # Order the time series data frame as it was encountered as in initial input.
        if X_pred is not None:
            test_feats = self.align_output_to_input(X_pred, test_feats)
        else:
            test_feats.sort_index(inplace=True)
        y_pred = test_feats[constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN].values

        if self._y_transformer is not None:
            y_pred = self._y_transformer.inverse_transform(y_pred)

        # name index columns back as needed.
        if len(dict_rename_back) > 0:
            test_feats.rename_axis(index=dict_rename_back, inplace=True)
            X_pred.rename_axis(index=dict_rename_back, inplace=True)
        return y_pred, test_feats

    def _check_data_rolling_evaluation(self,
                                       X_pred: pd.DataFrame,
                                       y_pred: Union[pd.DataFrame,
                                                     np.ndarray],
                                       ignore_data_errors: bool) -> None:
        """
        Check the inputs for rolling evaluation function.
        Rolling evaluation is invoked when all the entries of y_pred are definite, look_back features are enabled
        and the test length is greater than the max horizon.

        :param X_pred: the prediction dataframe combining X_past and X_future in a time-contiguous manner.
                       Empty values in X_pred will be imputed.
        :param y_pred: the target value corresponding to X_pred.
        :param ignore_data_errors: Ignore errors in user data.

        :raises: DataException
        """
        # if none of y value is definite, raise errors.
        if y_pred is None:
            y_pred_unknown = True
        elif isinstance(y_pred, np.ndarray):
            y_pred_unknown = pd.isna(y_pred).all()
        else:
            y_pred_unknown = y_pred.isnull().values.all()
        if y_pred_unknown:
            # this is a fatal error, hence not ignoring data errors
            self._warn_or_raise(TimeseriesMissingValuesInY,
                                ReferenceCodes._ROLLING_EVALUATION_NO_Y,
                                ignore_data_errors=False)

    def _infer_y(self,
                 X: pd.DataFrame,
                 grain: GrainType) -> pd.DataFrame:
        y_imputer = self._ts_transformer.y_imputers.get(grain)
        tsdf_X = tsdf.TimeSeriesDataFrame(
            X,
            time_colname=self._ts_transformer.time_column_name,
            grain_colnames=self._ts_transformer.grain_column_names,
            ts_value_colname=self._ts_transformer.target_column_name)
        X = y_imputer.transform(tsdf_X)
        X = pd.DataFrame(X)
        X.reset_index(inplace=True, drop=False)
        return X

    def rolling_evaluation(self,
                           X_pred: pd.DataFrame,
                           y_pred: Union[pd.DataFrame,
                                         np.ndarray],
                           ignore_data_errors: bool = False) -> Tuple[np.ndarray, pd.DataFrame]:
        """"
        Produce forecasts on a rolling origin over the given test set.

        Each iteration makes a forecast for the next 'max_horizon' periods
        with respect to the current origin, then advances the origin by the
        horizon time duration. The prediction context for each forecast is set so
        that the forecaster uses the actual target values prior to the current
        origin time for constructing lag features.

        This function returns a concatenated DataFrame of rolling forecasts joined
        with the actuals from the test set.

        :param X_pred: the prediction dataframe combining X_past and X_future in a time-contiguous manner.
                       Empty values in X_pred will be imputed.
        :param y_pred: the target value corresponding to X_pred.
        :param ignore_data_errors: Ignore errors in user data.

        :returns: Y_pred, with the subframe corresponding to Y_future filled in with the respective forecasts.
                  Any missing values in Y_past will be filled by imputer.
        :rtype: tuple
        """
        # check data satisfying the requiring information. If not, raise relevant error messages.
        self._check_data(X_pred, y_pred, None)
        self._check_data_rolling_evaluation(X_pred, y_pred, ignore_data_errors)
        # create the prediction dataframe

        X_pred = self._convert_time_column_name_safe(X_pred, ReferenceCodes._FORECASTING_CONVERT_INVALID_VALUE_EV)
        X_pred, y_pred = self.preaggregate_data_set(X_pred, y_pred)
        X_copy = self._create_prediction_data_frame(X_pred, y_pred, None, ignore_data_errors)
        X_rlt = []
        for grain_one, df_one in X_copy.groupby(self.grain_column_names):
            if self.is_grain_dropped(grain_one):
                continue
            if pd.isna(df_one[self.target_column_name]).any():
                df_one = self._infer_y(df_one, grain_one)
            y_pred_one = df_one[self.target_column_name].copy()
            df_one[self.target_column_name] = np.nan
            X_tmp = self._rolling_evaluation_one_grain(df_one, y_pred_one, ignore_data_errors)
            X_rlt.append(X_tmp)
        test_feats = pd.concat(X_rlt)
        test_feats = self.align_output_to_input(X_pred, test_feats)
        y_pred = test_feats[constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN].values

        if self._y_transformer is not None:
            y_pred = self._y_transformer.inverse_transform(y_pred)

        return y_pred, test_feats

    def _rolling_evaluation_one_grain(self,
                                      df_pred: pd.DataFrame,
                                      y_pred: pd.Series,
                                      ignore_data_errors: bool) -> pd.DataFrame:
        """"
        Implement rolling_evaluation for each grain.

        :param df_pred: the prediction dataframe generated from _create_prediction_data_frame.
        :param y_pred: the target value corresponding to X_pred.
        :param ignore_data_errors: Ignore errors in user data.
        :returns: Y_pred, with the subframe corresponding to Y_future filled in with the respective forecasts.
                  Any missing values in Y_past will be filled by imputer.
        :rtype: pandas.DataFrame
        """
        df_list = []
        X_trans = pd.DataFrame()
        start_time = df_pred[self.time_column_name].min()
        origin_time = start_time
        while origin_time <= df_pred[self.time_column_name].max():
            # Set the horizon time - end date of the forecast
            horizon_time = origin_time + self.max_horizon * self.data_frequency
            # Extract test data from an expanding window up-to the horizon
            expand_wind = (df_pred[self.time_column_name] < horizon_time)
            df_pred_expand = df_pred[expand_wind]
            if origin_time != start_time:
                # Set the context by including actuals up-to the origin time
                test_context_expand_wind = (df_pred[self.time_column_name] < origin_time)
                context_expand_wind = (df_pred_expand[self.time_column_name] < origin_time)
                # add the y_pred information into the df_pred_expand dataframe.
                y_tmp = X_trans.reset_index()[TimeSeriesInternal.DUMMY_TARGET_COLUMN]
                df_pred_expand[self.target_column_name][context_expand_wind] = y_pred[
                    test_context_expand_wind].combine_first(y_tmp)
            # Make a forecast out to the maximum horizon
            X_trans = self._regular_forecast(df_pred_expand, ignore_data_errors)
            trans_tindex = X_trans.index.get_level_values(self.time_column_name)
            trans_roll_wind = (trans_tindex >= origin_time) & (trans_tindex < horizon_time)
            df_list.append(X_trans[trans_roll_wind])
            # Advance the origin time
            origin_time = horizon_time
        X_fcst_all = pd.concat(df_list)
        return X_fcst_all

    def align_output_to_input(self, X_input: pd.DataFrame, transformed: pd.DataFrame) -> pd.DataFrame:
        """
        Align the transformed output data frame to the input data frame.

        *Note:* transformed will be modified by reference, no copy is being created.
        :param X_input: The input data frame.
        :param transformed: The data frame after transformation.
        :returns: The transfotmed data frame with its original index, but sorted as in X_input.
        """
        index = transformed.index.names
        # Before dropping index, we need to make sure that
        # we do not have features named as index columns.
        # we will temporary rename them.
        dict_rename = {}
        dict_rename_back = {}
        for ix_name in transformed.index.names:
            if ix_name in transformed.columns:
                temp_name = 'temp_{}'.format(uuid.uuid4())
                dict_rename[ix_name] = temp_name
                dict_rename_back[temp_name] = ix_name
        if len(dict_rename) > 0:
            transformed.rename(dict_rename, axis=1, inplace=True)
        transformed.reset_index(drop=False, inplace=True)
        merge_ix = [self.time_column_name]
        # We add grain column to index only if it is non dummy.
        if self.grain_column_names != [constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN]:
            merge_ix += self.grain_column_names
        X_merge = X_input[merge_ix]
        # Make sure, we have a correct dtype.
        for col in X_merge.columns:
            X_merge[col] = X_merge[col].astype(transformed[col].dtype)
        transformed = X_merge.merge(transformed, how='left', on=merge_ix)
        # return old index back
        transformed.set_index(index, inplace=True, drop=True)
        # If we have renamed any columns, we need to set it back.
        if len(dict_rename_back) > 0:
            transformed.rename(dict_rename_back, axis=1, inplace=True)
        return transformed

    def apply_time_series_transform(self,
                                    X: pd.DataFrame,
                                    y: np.ndarray = None) -> pd.DataFrame:
        """
        Apply all time series transforms to the data frame X.

        :param X: The data frame to be transformed.
        :type X: pandas.DataFrame
        :returns: The transformed data frame, having date, grain and origin
                  columns as indexes.
        :rtype: pandas.DataFrame

        """
        X_copy = X.copy()
        if y is not None:
            X_copy[self.target_column_name] = y
        for i in range(len(self.pipeline.steps) - 1):
            # FIXME: Work item #400231
            if type(self.pipeline.steps[i][1]).__name__ == 'TimeSeriesTransformer':
                X_copy = self.pipeline.steps[i][1].transform(X_copy)
                # When we made a time series transformation we need to break and return X.
                if self.origin_col_name in X_copy.index.names:
                    X_copy = self._ts_transformer._select_latest_origin_dates(X_copy)
                X_copy.sort_index(inplace=True)
                # If the target column was created by featurizers, drop it.
                if self.target_column_name in X_copy:
                    X_copy.drop(self.target_column_name, axis=1, inplace=True)
                return X_copy
            else:
                X_copy = self.pipeline.steps[i][1].transform(X_copy)

    def _lag_or_rw_enabled(self) -> bool:
        if forecasting_utils.get_pipeline_step(
                self._ts_transformer.pipeline, constants.TimeSeriesInternal.LAG_LEAD_OPERATOR):
            return True
        elif forecasting_utils.get_pipeline_step(
                self._ts_transformer.pipeline, constants.TimeSeriesInternal.ROLLING_WINDOW_OPERATOR):
            return True
        else:
            return False

    def _get_last_known_y(self,
                          X: pd.DataFrame,
                          ignore_data_errors: bool) -> Dict[str, pd.Timestamp]:
        """
        Return the value of date for the last known y.

        If no y is known for given grain, corresponding date is not returned.
        If y contains non contiguous numbers or NaNs the DataException is raised.
        :param X: The data frame. We need to make sure that y values
                  does not contain gaps.
        :param ignore_data_errors: Ignore errors in user data.
        :returns: dict containing grain->latest date for which y is known.
        :raises: DataException

        """
        dict_data = {}  # type: Dict[str, pd.Timestamp]
        if self.grain_column_names[0] == constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN:
            self._add_to_dict_maybe(
                dict_data,
                self._get_last_y_one_grain(
                    X,
                    constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN,
                    ignore_data_errors),
                self.grain_column_names[0])
        else:
            for grain, df_one in X.groupby(
                    self.grain_column_names, as_index=False):
                self._add_to_dict_maybe(
                    dict_data, self._get_last_y_one_grain(
                        df_one, grain, ignore_data_errors), grain)
        for grain in self._ts_transformer.dict_latest_date.keys():
            data = dict_data.get(grain)
            if data is not None and data < self._ts_transformer.dict_latest_date.get(
                    grain):
                dict_data[grain] = self._ts_transformer.dict_latest_date.get(grain)
        return dict_data

    def _add_to_dict_maybe(self,
                           dt,
                           date,
                           grain):
        """Add date to dict if it is not None."""
        if date is not None:
            dt[grain] = date

    def _get_last_y_one_grain(
            self,
            df_grain: pd.DataFrame,
            grain: GrainType,
            ignore_data_errors: bool,
            ignore_errors_and_warnings: bool = False) -> Optional[pd.Timestamp]:
        """
        Get the date for the last known y.

        This y will be used in transformation, but will not be used
        in prediction (the data frame will be trimmed).
        :param df_grain: The data frame corresponding to single grain.
        :param ignore_data_errors: Ignore errors in user data.
        :param ignore_errors_and_warnings : Ignore the y-related errors and warnings.
        :returns: The date corresponding to the last known y or None.
        """
        # We do not want to show errors for the grains which will be dropped.
        is_absent_grain = self.short_grain_handling() and grain not in self._ts_transformer.dict_latest_date.keys()
        # Make sure that frame is sorted by the time index.
        df_grain.sort_values(by=[self._time_col_name], inplace=True)
        y = df_grain[constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN].values
        sel_null_y = pd.isnull(y)
        num_null_y = sel_null_y.sum()
        if num_null_y == 0:
            # All y are known - nothing to forecast
            if not is_absent_grain and not ignore_errors_and_warnings:
                self._warn_or_raise(TimeseriesNothingToPredict,
                                    ReferenceCodes._FORECASTING_NOTHING_TO_PREDICT,
                                    ignore_data_errors)
            return df_grain[self._time_col_name].max()
        elif num_null_y == y.shape[0]:
            # We do not have any known y
            return None
        elif not sel_null_y[-1]:
            # There is context at the end of the y vector.
            # This could lead to unexpected behavior, so consider that this case means there is nothing to forecast
            if not is_absent_grain and not ignore_errors_and_warnings:
                self._warn_or_raise(TimeseriesContextAtEndOfY,
                                    ReferenceCodes._FORECASTING_CONTEXT_AT_END_OF_Y,
                                    ignore_data_errors)

        # Some y are known, some are not.
        # Are the data continguous - i.e. are there gaps in the context?
        non_nan_indices = np.flatnonzero(~sel_null_y)
        if not is_absent_grain and not ignore_errors_and_warnings \
           and not np.array_equiv(np.diff(non_nan_indices), 1):
            self._warn_or_raise(TimeseriesNonContiguousTargetColumn,
                                ReferenceCodes._FORECASTING_DATA_NOT_CONTIGUOUS,
                                ignore_data_errors)
        last_date = df_grain[self._time_col_name].iloc[non_nan_indices.max()]

        return pd.Timestamp(last_date)

    def _warn_or_raise(
            self,
            error_definition_class: 'ErrorDefinition',
            ref_code: str,
            ignore_data_errors: bool) -> None:
        """
        Raise DataException if the ignore_data_errors is False.

        :param warning_text: The text of error or warning.
        :param ignore_data_errors: if True raise the error, warn otherwise.
        """
        # All error definitions currently being passed to this function don't need any message_params.
        # Pass in error message_parameters via kwargs on `_warn_or_raise` and plumb them below, should we need to
        # create errors below with message_parameters
        error = AzureMLError.create(error_definition_class,
                                    reference_code=ref_code)
        if ignore_data_errors:
            warnings.warn(error.error_message)
        else:
            raise DataException._with_error(error)

    def forecast_quantiles(self,
                           X_pred: Optional[pd.DataFrame] = None,
                           y_pred: Optional[Union[pd.DataFrame, np.ndarray]] = None,
                           forecast_destination: Optional[pd.Timestamp] = None,
                           ignore_data_errors: bool = False) -> pd.DataFrame:
        """
        Get the prediction and quantiles from the fitted pipeline.

        :param X_pred: the prediction dataframe combining X_past and X_future in a time-contiguous manner.
                       Empty values in X_pred will be imputed.
        :param y_pred: the target value combining definite values for y_past and missing values for Y_future.
                       If None the predictions will be made for every X_pred.
        :param forecast_destination: Forecast_destination: a time-stamp value.
                                     Forecasts will be made all the way to the forecast_destination time,
                                     for all grains. Dictionary input { grain -> timestamp } will not be accepted.
                                     If forecast_destination is not given, it will be imputed as the last time
                                     occurring in X_pred for every grain.
        :type forecast_destination: pandas.Timestamp
        :param ignore_data_errors: Ignore errors in user data.
        :type ignore_data_errors: bool
        :return: A dataframe containing time, grain, and corresponding quantiles for requested prediction.
        """
        # If the data were aggregated, we have to also aggregate the input.
        if X_pred is not None:
            X_pred = self._convert_time_column_name_safe(
                X_pred, ReferenceCodes._FORECASTING_QUANTILES_CONVERT_INVALID_VALUE)
            X_pred, y_pred = self.preaggregate_data_set(X_pred, y_pred)
        pred, transformed_data = self.forecast(X_pred, y_pred, forecast_destination, ignore_data_errors)
        NOT_KNOWN_Y = 'y_not_known'

        max_horizon_featurizer = forecasting_utils.get_pipeline_step(
            self._ts_transformer.pipeline, constants.TimeSeriesInternal.MAX_HORIZON_FEATURIZER)
        horizon_column = None if max_horizon_featurizer is None else max_horizon_featurizer.horizon_colname

        dict_latest_date = self._ts_transformer.dict_latest_date
        freq = self._ts_transformer.freq

        if X_pred is not None:
            # Figure out last known y for each grain.
            X_copy = X_pred.copy()
            if y_pred is not None:
                X_copy[self.target_column_name] = y_pred
            else:
                X_copy[self.target_column_name] = np.NaN

            # add dummy grain if needed to df
            if self.grain_column_names[0] == constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN and \
                    self.grain_column_names[0] not in X_copy.columns:
                X_copy[constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN] = \
                    constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN
            # We already have shown user warnings or have thrown errors during forecast() call.
            # At this stage we can
            X_copy = self._infer_missing_data(X_copy, ignore_data_errors,
                                              ignore_errors_and_warnings=True)
            # We ignore user errors, because if desired it was already rose.
            dict_known = self._get_last_known_y(X_copy, True)
            dfs = []
            for grain, df_one in transformed_data.groupby(self.grain_column_names):
                if grain in dict_known.keys():
                    # Index levels are always sorted, but it is not guaranteed for data frame.
                    df_one.sort_index(inplace=True)
                    # Some y values are known for the given grain.
                    df_one[NOT_KNOWN_Y] = df_one.index.get_level_values(self.time_column_name) > dict_known[grain]
                else:
                    # Nothing is known. All data represent forecast.
                    df_one[NOT_KNOWN_Y] = True
                dfs.append(df_one)
            transformed_data = pd.concat(dfs)
            # Make sure data sorted in the same order as input.
            transformed_data = self.align_output_to_input(X_pred, transformed_data)
            # Some of our values in NOT_KNOWN_Y will be NaN, we need to say, that we "know" this y
            # and replace it with NaN.
            transformed_data[NOT_KNOWN_Y] = transformed_data.apply(
                lambda x: x[NOT_KNOWN_Y] if not pd.isnull(x[NOT_KNOWN_Y]) else False, axis=1)
            if horizon_column is not None and horizon_column in transformed_data.columns:
                # We also need to set horizons to make sure that horizons column
                # can be converted to integer.
                transformed_data[horizon_column] = transformed_data.apply(
                    lambda x: x[horizon_column] if not pd.isnull(x[horizon_column]) else 1, axis=1)
            # Make sure y is aligned to data frame.
            pred = transformed_data[TimeSeriesInternal.DUMMY_TARGET_COLUMN].values
        else:
            # If we have only destination date no y is known.
            transformed_data[NOT_KNOWN_Y] = True
        horizon_stddevs = np.zeros(len(pred))
        horizon_stddevs.fill(np.NaN)
        try:
            if self._horizon_idx is None and horizon_column is not None:
                self._horizon_idx = cast(int,
                                         self._ts_transformer.get_engineered_feature_names().index(horizon_column))
        except ValueError:
            self._horizon_idx = None

        is_not_known = transformed_data[NOT_KNOWN_Y].values.astype(int)
        MOD_TIME_COLUMN_CONSTANT = 'mod_time'
        # Retrieve horizon, if available, otherwise calculate it.
        # We also need to find the time difference from the origin to include it as a factor in our uncertainty
        # calculation. This is represented by mod_time and for horizon aware models will reprsent number of
        # max horizons from the original origin, otherwise number steps from origin.
        if self._horizon_idx is not None:
            X_copy_tmp = self._create_prediction_data_frame(X_pred, y_pred, forecast_destination, ignore_data_errors)
            horizons = transformed_data.values[:, self._horizon_idx].astype(int)

            if self._use_recursive_forecast(X_copy_tmp, ignore_data_errors):
                def add_horizon_counter(grp):
                    """
                    Get the modulo time column.

                    This method is used to calculate the number of times the horizon has "rolled". In the case of the
                    rolling/recursive forecast, each time delta that is beyond our max horizon is a forecast from the
                    previous time delta's forecast used as input to the lookback features. Since the estimation is
                    growing each time we recurse, we want to calculate the quantile with some added
                    uncertainty (growing with time). We use the modulo column from this method to do so. We also apply
                    this strategy on a per-grain basis.
                    """
                    grains = grp.name
                    if grains in dict_latest_date:
                        last_known_single_grain = dict_latest_date[grains]
                        forecast_times = grp.index.get_level_values(self.time_column_name)
                        date_grid = pd.date_range(
                            last_known_single_grain, forecast_times.max(), freq=freq
                        )
                        # anything forecast beyond the max horizon will need a time delta to increase uncertainty
                        grp[MOD_TIME_COLUMN_CONSTANT] = [
                            math.ceil(date_grid.get_loc(forecast_times[i]) / self.max_horizon)
                            for i in range(len(grp))
                        ]
                    else:
                        # If we have encountered grain not present in the training set, we will set mod_time to 1
                        # as finally we will get NaN as a prediction.
                        grp[MOD_TIME_COLUMN_CONSTANT] = 1

                    return grp

                mod_time = transformed_data \
                    .groupby(self.grain_column_names).apply(add_horizon_counter)[MOD_TIME_COLUMN_CONSTANT].values
            else:
                mod_time = [1] * len(horizons)
        else:
            # If no horizon is present we are doing a forecast with no lookback features.
            # The last known timestamp can be used to calculate the horizon. We can then apply
            # an increase in uncertainty as horizon increases.
            def add_horizon(grp):
                grains = grp.name
                last_known_single_grain = dict_latest_date[grains]
                forecast_times = grp.index.get_level_values(self.time_column_name)
                date_grid = pd.date_range(
                    last_known_single_grain, forecast_times.max(), freq=freq
                )

                grp[MOD_TIME_COLUMN_CONSTANT] = [
                    date_grid.get_loc(forecast_times[i])
                    for i in range(len(grp))
                ]
                return grp

            # We can groupby grain and then apply the horizon based on the time index within the grain
            # and the last known timestamps. We still need to know the horizons, but in this case the model
            # is not horizon aware, so there should only be one stddev and any forecast will use that value
            # with horizon (mod_time) used to increase uncertainty.
            mod_time = transformed_data.groupby(self.grain_column_names) \
                .apply(add_horizon)[MOD_TIME_COLUMN_CONSTANT].values
            horizons = [1] * len(mod_time)

        for idx, horizon in enumerate(horizons):
            horizon = horizon - 1  # horizon needs to be 1 indexed
            try:
                horizon_stddevs[idx] = self._stddev[horizon] * is_not_known[idx] * math.sqrt(mod_time[idx])
            except IndexError:
                # In case of short training set cv may have nor estimated
                # stdev for highest horizon(s). Fix it by returning np.NaN
                horizon_stddevs[idx] = np.NaN

        # Get the prediction quantiles
        pred_quantiles = self._get_ci(pred, horizon_stddevs, self._quantiles)

        # Get time and grain columns from transformed data
        transformed_data = transformed_data.reset_index()
        time_column = transformed_data[self.time_column_name]
        grain_df = None
        if (self.grain_column_names is not None) and \
                (self.grain_column_names[0] != constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN):
            grain_df = transformed_data[self.grain_column_names]

        return pd.concat((time_column, grain_df, pred_quantiles), axis=1)

    def _postprocess_output(self,
                            X: pd.DataFrame,
                            known_y: Optional[pd.Series]) -> pd.DataFrame:
        """
        Postprocess the data before returning it to user.

        Trim the data frame to the size of input.
        :param X: The data frame to be trimmed.
        :param known_y: The known or inferred y values.
                        We need to replace the existing values by them
        :returns: The data frame with the gap removed.

        """
        # If user have provided known y values, replace forecast by them even
        # if these values were imputed.
        if known_y is not None and any(not pd.isnull(val) for val in known_y):
            PRED_TARGET = 'forecast'
            known_df = known_y.rename(TimeSeriesInternal.DUMMY_TARGET_COLUMN).to_frame()
            X.rename({TimeSeriesInternal.DUMMY_TARGET_COLUMN: PRED_TARGET}, axis=1, inplace=True)
            # Align known y and X with merge on indices
            X_merged = X.merge(known_df, left_index=True, right_index=True, how='inner')
            assert (X_merged.shape[0] == X.shape[0])

            # Replace all NaNs in the known y column by forecast.

            def swap(x):
                return x[PRED_TARGET] if pd.isnull(
                    x[TimeSeriesInternal.DUMMY_TARGET_COLUMN]) else x[TimeSeriesInternal.DUMMY_TARGET_COLUMN]

            X_merged[TimeSeriesInternal.DUMMY_TARGET_COLUMN] = X_merged.apply(lambda x: swap(x), axis=1)
            X = X_merged.drop(PRED_TARGET, axis=1)
        # If user provided X_pred, make sure returned data frame does not contain the inferred
        # gap between train and test.
        if self.forecast_origin:  # Filter only if we were provided by data frame.
            X = (X.groupby(self.grain_column_names, group_keys=False)
                 .apply(lambda df:
                        df[df.index.get_level_values(self._time_col_name) >= self.forecast_origin.get(df.name)]
                        if df.name in self.forecast_origin.keys() else df))
        # self.forecast_origin dictionary is empty, no trimming required.
        return X

    def predict(self, X: pd.DataFrame) -> None:
        logger.error("The API predict is not supported for a forecast model.")
        raise UserException._with_error(
            AzureMLError.create(
                ForecastPredictNotSupported, target="predict",
                reference_code=ReferenceCodes._FORECASTING_PREDICT_NOT_SUPPORT
            )
        )

    def preaggregate_data_set(
            self,
            df: pd.DataFrame,
            y: Optional[np.ndarray] = None,
            is_training_set: bool = False) -> Tuple[pd.DataFrame, Optional[np.ndarray]]:
        """
        Aggregate the prediction data set.

        **Note:** This method does not guarantee that the data set will be aggregated.
        This will happen only if the data set contains the duplicated time stamps or out of grid dates.
        :param df: The data set to be aggregated.
        :patam y: The target values.
        :param is_training_set: If true, the data represent training set.
        :return: The aggregated or intact data set if no aggregation is required.
        """
        return ForecastingPipelineWrapper.static_preaggregate_data_set(self._ts_transformer,
                                                                       self.time_column_name,
                                                                       self.grain_column_names,
                                                                       df, y, is_training_set)

    def _raise_insufficient_data_maybe(
            self, X: pd.DataFrame, grain: Optional[str],
            min_points: int, operation: str) -> None:
        """
        Raise the exception about insufficient grain size.

        :param X: The grain to be checked.
        :param grain: The grain name.
        :param min_points: The minimal number of points needed.
        :param operation: The name of an operation for which the validation
                          is being performed.
        :raises: DataException
        """
        if X.shape[0] < min_points:
            raise DataException._with_error(AzureMLError.create(
                TimeseriesInsufficientDataForecast, target="X", grains=grain,
                operation=operation,
                max_horizon=self._ts_transformer.max_horizon,
                lags=str(self._ts_transformer.get_target_lags()),
                window_size=self._ts_transformer.get_target_rolling_window_size(),
                reference_code=ReferenceCodes._FORECASTING_INSUFFICIENT_DATA
            ))

    def _get_automl_base_settings(self) -> AutoMLBaseSettings:
        """Generate the AutoMLBaseSettings safely."""
        if self._ts_transformer.pipeline is not None:
            window_size = self._ts_transformer.get_target_rolling_window_size()  # type: Optional[int]
            if window_size == 0:
                window_size = TimeSeriesInternal.WINDOW_SIZE_DEFAULT
            target_lags = self._ts_transformer.get_target_lags()  # type: Optional[List[int]]
            if target_lags == [0]:
                target_lags = TimeSeriesInternal.TARGET_LAGS_DEFAULT
        else:
            window_size = self._ts_transformer.parameters.get(TimeSeriesInternal.WINDOW_SIZE, 0)
            lags = self._ts_transformer.parameters.get(TimeSeriesInternal.LAGS_TO_CONSTRUCT)
            if lags is None:
                target_lags = [0]
            target_lags = lags.get(self.target_column_name, [0])
        grains = self._ts_transformer.grain_column_names
        if grains == [TimeSeriesInternal.DUMMY_GRAIN_COLUMN]:
            grains = []
        freq_str = self._ts_transformer.freq
        # If the frequency can not be converted to a pd.DateOffset,
        # then we need to set it to None.
        try:
            to_offset(freq_str)
        except BaseException:
            freq_str = None
        fc = ForecastingParameters(
            time_column_name=self._ts_transformer.time_column_name,
            time_series_id_column_names=grains,
            forecast_horizon=self._ts_transformer.max_horizon,
            group_column_names=None,
            target_lags=target_lags,
            feature_lags=self._ts_transformer.parameters.get(
                TimeSeries.FEATURE_LAGS, TimeSeriesInternal.FEATURE_LAGS_DEFAULT),
            target_rolling_window_size=window_size,
            seasonality=self._ts_transformer.parameters.get(
                TimeSeries.SEASONALITY, TimeSeriesInternal.SEASONALITY_VALUE_DEFAULT),
            country_or_region_for_holidays=self._ts_transformer.parameters.get(TimeSeries.COUNTRY_OR_REGION),
            use_stl=self._ts_transformer.parameters.get(
                TimeSeries.USE_STL, TimeSeriesInternal.USE_STL_DEFAULT),
            short_series_handling_configuration=self._ts_transformer.parameters.get(
                TimeSeries.SHORT_SERIES_HANDLING_CONFIG,
                TimeSeriesInternal.SHORT_SERIES_HANDLING_CONFIG_DEFAULT),
            freq=freq_str,
            target_aggregation_function=self._ts_transformer.parameters.get(
                TimeSeries.TARGET_AGG_FUN, TimeSeriesInternal.TARGET_AGG_FUN_DEFAULT)
        )
        if self._ts_transformer.parameters.get(TimeSeries.DROP_COLUMN_NAMES):
            fc.drop_column_names = self._ts_transformer.parameters.get(TimeSeries.DROP_COLUMN_NAMES)
        return AutoMLBaseSettings(
            primary_metric='r2_score',
            is_timeseries=True,
            featurization=self._ts_transformer._featurization_config,
            forecasting_parameters=fc)

    def _preprocess_check(self, X: pd.DataFrame, y: np.ndarray, operation: str,
                          pad_short_grains: bool) -> Tuple[pd.DataFrame, np.ndarray]:
        """
        Do the simple preprocessing and check for model retraining and in sample forecasting.

        :param X: The prediction data frame.
        :param y: The array of target values.
        :param operation: The name of an operation for which the preprocessing
                          is being performed.
        :param pad_short_grains: If true the short grains will be padded.
        :return: The tuple of sanitized data.
        """
        # Data checks.
        self._check_data(X, y, None)
        if X.shape[0] != y.shape[0]:
            raise DataException._with_error(
                AzureMLError.create(
                    DataShapeMismatch, target='X_and_y',
                    reference_code=ReferenceCodes._FORECASTING_DATA_SHAPE_MISMATCH
                )
            )

        # Ensure the type of a time and grain columns.
        X = self._check_convert_grain_types(X)
        X = self._convert_time_column_name_safe(X, ReferenceCodes._FORECASTING_PREPROCESS_INVALID_VALUE)

        # Fix the data set frequency and aggregate data.
        automl_settings = self._get_automl_base_settings()
        fixed_ds = fix_data_set_regularity_may_be(
            X, y,
            automl_settings=automl_settings,
            # We do not set the reference code here, because we check that freq can be
            # convertible to string or None in AutoMLTimeSeriesSettings.
            freq_ref_code=""
        )
        # If short grain padding is disabled, we need to check if the short grain
        # are present.
        short_series_handling_configuration = self._ts_transformer.parameters.get(
            constants.TimeSeries.SHORT_SERIES_HANDLING_CONFIG,
            TimeSeriesInternal.SHORT_SERIES_HANDLING_CONFIG_DEFAULT)
        if short_series_handling_configuration is None:
            min_points = get_min_points(
                window_size=self._ts_transformer.get_target_rolling_window_size(),
                lags=self._ts_transformer.get_target_lags(),
                max_horizon=self._ts_transformer.max_horizon,
                cv=None,
                n_step=None)
            if self._ts_transformer.grain_column_names == [TimeSeriesInternal.DUMMY_GRAIN_COLUMN]:
                self._raise_insufficient_data_maybe(fixed_ds.data_x, None, min_points, operation)
            else:
                for grain, df in fixed_ds.data_x.groupby(self._ts_transformer.grain_column_names):
                    self._raise_insufficient_data_maybe(df, grain, min_points, operation)
        # Pad the short series if needed
        # We have to import short_grain_padding here because importing it at the top causes the cyclic
        # import while importing ml_engine.
        from azureml.automl.runtime import short_grain_padding

        if pad_short_grains:
            X, y = short_grain_padding.pad_short_grains_or_raise(
                fixed_ds.data_x, fixed_ds.data_y,
                freq=self._ts_transformer.freq_offset,
                automl_settings=automl_settings, ref_code="")
            return X, y
        return fixed_ds.data_x, fixed_ds.data_y

    def _in_sample_fit(self, X: pd.DataFrame, y: np.ndarray) -> Tuple[np.ndarray, pd.DataFrame]:
        """
        Predict the data from the training set.

        :param X: The prediction data frame.
        :param y: The array of target values.
        :return: The array and the data frame with predictions.
        """
        X_copy = X.copy()
        X_agg, _ = self.preaggregate_data_set(X, y, is_training_set=False)
        was_aggregated = False
        if X_agg.shape != X.shape:
            was_aggregated = True
        X_copy, y = self._preprocess_check(X_copy, y, 'in-sample forecasting', False)
        X_copy = self._create_prediction_data_frame(X_copy, y,
                                                    forecast_destination=None,
                                                    ignore_data_errors=True)
        y = X_copy.pop(TimeSeriesInternal.DUMMY_TARGET_COLUMN).values
        test_feats = None  # type: Optional[pd.DataFrame]
        for i in range(len(self.pipeline.steps) - 1):
            # FIXME: Work item #400231
            if type(self.pipeline.steps[i][1]).__name__ == 'TimeSeriesTransformer':
                test_feats = self.pipeline.steps[i][1].transform(X_copy, y)
                # We do not need the target column now.
                # The target column is deleted by the rolling window during transform.
                # If there is no rolling window we need to make sure the column was dropped.
                if self._ts_transformer.target_column_name in test_feats.columns:
                    # We want to store the y_known_series for future use.
                    test_feats.drop(self._ts_transformer.target_column_name, inplace=True, axis=1)
                # If origin times are present, remove nans from look-back features and select the latest origins
                if self.origin_col_name in test_feats.index.names:
                    y = np.zeros(test_feats.shape[0])
                    test_feats, _ = self._ts_transformer._remove_nans_from_look_back_features(test_feats, y)
                    test_feats = self._ts_transformer._select_latest_origin_dates(test_feats)
                X_copy = test_feats.copy()
            else:
                X_copy = self.pipeline.steps[i][1].transform(X_copy)
        # TODO: refactor prediction in the separate method and make AML style error.
        try:
            y_preds = self.pipeline.steps[-1][1].predict(X_copy)
        except Exception as e:
            raise PredictionException.from_exception(e, has_pii=True, target='ForecastingPipelineWrapper'). \
                with_generic_msg(_generic_prediction_error_message.format(self.__class__.__name__))

        test_feats[constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN] = y_preds
        test_feats = self._postprocess_output(test_feats, known_y=None)
        # Order the time series data frame as it was encountered as in initial input.
        if not was_aggregated:
            test_feats = self.align_output_to_input(X, test_feats)
        y_pred = test_feats[constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN].values
        return y_pred, test_feats

    def fit(self, X: pd.DataFrame, y: np.ndarray) -> 'ForecastingPipelineWrapper':
        """
        Train the model on different data.

        :param X: The prediction data frame.
        :param y: The array of target values.
        :return: The instance of ForecastingPipelineWrapper trained on X and y.
        """
        X.reset_index(drop=True, inplace=True)
        # Drop rows, containing NaN in timestamps or in y.

        if any(np.isnan(y_one) for y_one in y) or X[self.time_column_name].isnull().any():
            X[TimeSeriesInternal.DUMMY_TARGET_COLUMN] = y
            X = X.dropna(subset=[self.time_column_name, TimeSeriesInternal.DUMMY_TARGET_COLUMN], inplace=False, axis=0)
            y = X.pop(TimeSeriesInternal.DUMMY_TARGET_COLUMN).values
        X, y = self._preprocess_check(X, y, 'fitting', True)
        for i in range(len(self.pipeline.steps) - 1):
            # FIXME: Work item #400231
            if type(self.pipeline.steps[i][1]).__name__ == 'TimeSeriesTransformer':
                X = self.pipeline.steps[i][1].fit_transform(X, y)
                y = X.pop(TimeSeriesInternal.DUMMY_TARGET_COLUMN).values
                # If origin times are present, remove nans from look-back features and select the latest origins
                if self.origin_col_name in X.index.names:
                    X, y = self._ts_transformer._remove_nans_from_look_back_features(X, y)
            else:
                if hasattr(self.pipeline.steps[i][1], 'fit_transform'):
                    X = self.pipeline.steps[i][1].fit_transform(X, y)
                else:
                    X = self.pipeline.steps[i][1].fit(X, y).transform(X)
        # TODO: refactor prediction in the separate method and make AML style error.
        try:
            self.pipeline.steps[-1][1].fit(X, y)
        except Exception as e:
            raise FitException.from_exception(e, has_pii=True, target='ForecastingPipelineWrapper'). \
                with_generic_msg(_generic_fit_error_message.format(self.__class__.__name__))
        return self

    @property
    def max_horizon(self) -> int:
        """Return max hiorizon used in the model."""
        return cast(int, self._ts_transformer.max_horizon)

    @property
    def target_lags(self) -> List[int]:
        """Return target lags if any."""
        return cast(List[int], self._ts_transformer.get_target_lags())

    @property
    def target_rolling_window_size(self) -> int:
        """Return the size of rolling window."""
        return cast(int, self._ts_transformer.get_target_rolling_window_size())

    @staticmethod
    def static_preaggregate_data_set(
            ts_transformer: 'TimeSeriesTransformer',
            time_column_name: str,
            grain_column_names: List[str],
            df: pd.DataFrame,
            y: Optional[np.ndarray] = None,
            is_training_set: bool = False) -> Tuple[pd.DataFrame, Optional[np.ndarray]]:
        """
        Aggregate the prediction data set.

        **Note:** This method does not guarantee that the data set will be aggregated.
        This will happen only if the data set contains the duplicated time stamps or out of grid dates.
        :param ts_transformer: The timeseries tranformer used for training.
        :param time_column_name: name of the time column.
        :param grain_column_names: List of grain column names.
        :param df: The data set to be aggregated.
        :patam y: The target values.
        :param is_training_set: If true, the data represent training set.
        :return: The aggregated or intact data set if no aggregation is required.
        """
        agg_fun = ts_transformer.parameters.get(constants.TimeSeries.TARGET_AGG_FUN)
        set_columns = set(ts_transformer.columns) if ts_transformer.columns is not None else set()
        ext_resgressors = set(df.columns)
        ext_resgressors.discard(time_column_name)
        for grain in grain_column_names:
            ext_resgressors.discard(grain)
        diff_col = set_columns.symmetric_difference(set(df.columns))
        # We  do not have the TimeSeriesInternal.DUMMY_ORDER_COLUMN during inference time.
        diff_col.discard(constants.TimeSeriesInternal.DUMMY_ORDER_COLUMN)
        diff_col.discard(constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN)
        detected_types = None
        if agg_fun and ts_transformer.parameters.get(
            constants.TimeSeries.FREQUENCY) is not None and (
            diff_col or (
                not diff_col and not ext_resgressors)):
            # If we have all the data for aggregation and input data set contains columns different
            # from the transformer was fit on, we need to check if the input data set needs to be aggregated.
            detected_types = _freq_aggregator.get_column_types(
                columns_train=list(ts_transformer.columns) if ts_transformer.columns is not None else [],
                columns_test=list(df.columns),
                time_column_name=time_column_name,
                grain_column_names=grain_column_names)

        if detected_types is None or detected_types.detection_failed:
            return df, y

        ts_data = TimeSeriesDataConfig(
            df, y, time_column_name=time_column_name,
            time_series_id_column_names=grain_column_names,
            freq=ts_transformer.freq_offset, target_aggregation_function=agg_fun,
            featurization_config=ts_transformer._featurization_config)
        # At this point we do not detect the data set frequency
        # and set it to None to perform the aggregation anyways.
        # If numeric columns are not empty we have to aggregate as
        # the training data have different columns then testing data.
        # If there is no numeric columns, we will aggregate only if
        # the data do not fit into the grid.
        # In the forecast time we also have to assume that the data frequency is the same
        # as forecast frequency.
        df_fixed, y_pred = _freq_aggregator.aggregate_dataset(
            ts_data, dataset_freq=ts_transformer.freq_offset,
            force_aggregation=ext_resgressors != set(),
            start_times=None if is_training_set else ts_transformer.dict_latest_date,
            column_types=detected_types)
        if df_fixed.shape[0] == 0:
            raise DataException._with_error(
                AzureMLError.create(
                    ForecastingEmptyDataAfterAggregation, target="X_pred",
                    reference_code=ReferenceCodes._FORECASTING_EMPTY_AGGREGATION
                )
            )
        return df_fixed, y_pred


class PipelineWithYTransformations(sklearn.pipeline.Pipeline):
    """
    Pipeline transformer class.

    Pipeline and y_transformer are assumed to be already initialized.

    But fit could change this to allow for passing the parameters of the
    pipeline and y_transformer.

    :param pipeline: sklearn.pipeline.Pipeline object.
    :type pipeline: sklearn.pipeline.Pipeline
    :param y_trans_name: Name of y transformer.
    :type y_trans_name: string
    :param y_trans_obj: Object that computes a transformation on y values.
    :return: Object of class PipelineWithYTransformations.
    """

    def __init__(self, pipeline, y_trans_name, y_trans_obj):
        """
        Pipeline and y_transformer are assumed to be already initialized.

        But fit could change this to allow for passing the parameters of the
        pipeline and y_transformer.

        :param pipeline: sklearn.pipeline.Pipeline object.
        :type pipeline: sklearn.pipeline.Pipeline
        :param y_trans_name: Name of y transformer.
        :type y_trans_name: string
        :param y_trans_obj: Object that computes a transformation on y values.
        :return: Object of class PipelineWithYTransformations.
        """
        self.pipeline = pipeline
        self.y_transformer_name = y_trans_name
        self.y_transformer = y_trans_obj
        super().__init__(self.pipeline.steps, memory=self.pipeline.memory)
        self.steps = pipeline.__dict__.get("steps")

    def __str__(self):
        """
        Return transformer details into string.

        return: string representation of pipeline transform.
        """
        return "%s\nY_transformer(['%s', %s])" % (self.pipeline.__str__(),
                                                  self.y_transformer_name,
                                                  self.y_transformer.__str__())

    def fit(self, X, y, y_min=None, **kwargs):
        """
        Fit function for pipeline transform.

        Perform the fit_transform of y_transformer, then fit into the sklearn.pipeline.Pipeline.

        :param X: Input training data.
        :type X: numpy.ndarray or scipy.sparse.spmatrix
        :param y: Input target values.
        :type y: numpy.ndarray
        :param y_min: Minimum value of y, will be inferred if not set.
        :type y_min: numpy.ndarray
        :param kwargs: Other parameters
        :type kwargs: dict
        :return: self: Returns an instance of PipelineWithYTransformations.
        """
        try:
            if y_min is not None:
                # Regression task related Y transformers use y_min
                self.pipeline.fit(X, self.y_transformer.fit_transform(y, y_min=y_min), **kwargs)
            else:
                # Classification task transformers (e.g. LabelEncoder) do not need y_min
                self.pipeline.fit(X, self.y_transformer.fit_transform(y), **kwargs)
        except AutoMLException:
            raise
        except Exception as e:
            raise FitException.from_exception(
                e, has_pii=True, target="PipelineWithYTransformations",
                reference_code=ReferenceCodes._PIPELINE_WITH_Y_TRANSFORMATIONS_FIT
            ).with_generic_msg(_generic_fit_error_message.format(self.__class__.__name__))
        return self

    def fit_predict(self, X, y, y_min=None):
        """
        Fit predict function for pipeline transform.

        :param X: Input data.
        :type X: numpy.ndarray or scipy.sparse.spmatrix
        :param y: Input target values.
        :type y: numpy.ndarray
        :param y_min: Minimum value of y, will be inferred if not set.
        :type y_min: numpy.ndarray
        :return: Prediction values after performing fit.
        """
        try:
            return self.fit(X, y, y_min).predict(X)
        except AutoMLException:
            raise
        except Exception as e:
            raise FitException.from_exception(
                e, has_pii=True, target="PipelineWithYTransformations",
                reference_code=ReferenceCodes._PIPELINE_WITH_Y_TRANSFORMATIONS_FIT_PREDICT
            ).with_generic_msg(_generic_fit_error_message.format(self.__class__.__name__))

    def get_params(self, deep=True):
        """
        Return parameters for Pipeline Transformer.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: bool
        :return: Parameters for Pipeline Transformer.
        """
        return {
            "Pipeline": self.pipeline.get_params(deep),
            "y_transformer": self.y_transformer.get_params(deep),
            "y_transformer_name": self.y_transformer_name
        }

    def predict(self, X):
        """
        Prediction function for Pipeline Transformer.

        Perform the prediction of sklearn.pipeline.Pipeline, then do the inverse transform from y_transformer.

        :param X: Input samples.
        :type X: numpy.ndarray or scipy.sparse.spmatrix
        :return: Prediction values from Pipeline Transformer.
        :rtype: array
        """
        try:
            return self.y_transformer.inverse_transform(self.pipeline.predict(X))
        except AutoMLException:
            raise
        except Exception as e:
            raise TransformException.from_exception(
                e, has_pii=True, target="PipelineWithYTransformations",
                reference_code=ReferenceCodes._PIPELINE_WITH_Y_TRANSFORMATIONS_PREDICT
            ).with_generic_msg(_generic_transform_error_message.format(self.__class__.__name__))

    def predict_proba(self, X):
        """
        Prediction probability function for Pipeline Transformer with classes.

        Perform prediction and obtain probability using the sklearn.pipeline.Pipeline, then do the inverse transform
        from y_transformer.

        :param X: Input samples.
        :type X: numpy.ndarray or scipy.sparse.spmatrix
        :return: Prediction probability values from Pipeline Transformer for each class (column name). The shape of
        the returned data frame is (n_samples, n_classes). Each row corresponds to the row from the input X.
        Column name is the class name and column entry is the probability.
        :rtype: pandas.DataFrame
        """
        try:
            return pd.DataFrame(self.pipeline.predict_proba(X), columns=self.classes_)
        except AutoMLException:
            raise
        except Exception as e:
            raise TransformException._with_error(
                AzureMLError.create(
                    GenericTransformError,
                    has_pii=True,
                    target="PipelineWithYTransformations.predict_proba",
                    transformer_name="PipelineWithYTransformations",
                    reference_code=ReferenceCodes._PIPELINE_WITH_Y_TRANSFORMATIONS_PREDICT_PROBA
                ), inner_exception=e) from e

    @property
    def classes_(self) -> np.ndarray:
        """
        LabelEncoder could have potentially seen more classes than the underlying pipeline as we `fit` the
        LabelEncoder on full data whereas, the underlying pipeline is `fit` only on train data.

        Override the classes_ attribute of the model so that we can return only those classes that are seen by
        the fitted_pipeline.
        :return: Set of classes the pipeline has seen.
        """
        return cast(np.ndarray, self.y_transformer.inverse_transform(self.pipeline.classes_))


class QuantileTransformerWrapper(BaseEstimator, TransformerMixin):
    """
    Quantile transformer wrapper class.

    Transform features using quantiles information.

    :param n_quantiles:
        Number of quantiles to be computed. It corresponds to the number
        of landmarks used to discretize the cumulative density function.
    :type n_quantiles: int
    :param output_distribution:
        Marginal distribution for the transformed data.
        The choices are 'uniform' (default) or 'normal'.
    :type output_distribution: string

    Read more at:
    http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.QuantileTransformer.html.
    """

    def __init__(self, n_quantiles=1000, output_distribution="uniform"):
        """
        Initialize function for Quantile transformer.

        :param n_quantiles:
            Number of quantiles to be computed. It corresponds to the number
            of landmarks used to discretize the cumulative density function.
        :type n_quantiles: int
        :param output_distribution:
            Marginal distribution for the transformed data.
            The choices are 'uniform' (default) or 'normal'.
        :type output_distribution: string
        """
        self.transformer = preprocessing.QuantileTransformer(
            n_quantiles=n_quantiles,
            output_distribution=output_distribution)

    def __repr__(self):
        return repr(self.transformer)

    def _get_imports(self) -> List[Tuple[str, str, Any]]:
        return [
            _codegen_utilities.get_import(self.transformer)
        ]

    def __str__(self):
        """
        Return transformer details into string.

        return: String representation of Quantile transform.
        """
        return self.transformer.__str__()

    def fit(self, y):
        """
        Fit function for Quantile transform.

        :param y: The data used to scale along the features axis.
        :type y: numpy.ndarray or scipy.sparse.spmatrix
        :return: Object of QuantileTransformerWrapper.
        :rtype: azureml.automl.runtime.shared.model_wrappers.QuantileTransformerWrapper
        """
        try:
            self.transformer.fit(y.reshape(-1, 1))
        except Exception as e:
            raise FitException.from_exception(e, has_pii=True, target="QuantileTransformerWrapper"). \
                with_generic_msg(_generic_fit_error_message.format(self.__class__.__name__))
        return self

    def get_params(self, deep=True):
        """
        Return parameters of Quantile transform as dictionary.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: bool
        :return: Dictionary of Quantile transform parameters.
        """
        return self.transformer.get_params(deep)

    def transform(self, y):
        """
        Transform function for Quantile transform.

        :param y: The data used to scale along the features axis.
        :type y: typing.Union[numpy.ndarray, scipy.sparse.spmatrix]
        :return: The projected data of Quantile transform.
        :rtype: typing.Union[numpy.ndarray, scipy.sparse.spmatrix]
        """
        try:
            return self.transformer.transform(y.reshape(-1, 1)).reshape(-1)
        except Exception as e:
            raise TransformException.from_exception(
                e, has_pii=True, target="QuantileTransformerWrapper",
                reference_code='model_wrappers.QuantileTransformerWrapper.transform'). \
                with_generic_msg(_generic_transform_error_message.format(self.__class__.__name__))

    def inverse_transform(self, y):
        """
        Inverse transform function for Quantile transform. Back-projection to the original space.

        :param y: The data used to scale along the features axis.
        :type y: numpy.ndarray or scipy.sparse.spmatrix
        :return: The projected data of Quantile inverse transform.
        :rtype: typing.Union[numpy.ndarray, scipy.sparse.spmatrix]
        """
        try:
            return self.transformer.inverse_transform(y.reshape(-1, 1)).reshape(-1)
        except Exception as e:
            raise TransformException.from_exception(
                e, has_pii=True, target="QuantileTransformerWrapper_Inverse",
                reference_code='model_wrappers.QuantileTransformerWrapper_Inverse.inverse_transform'). \
                with_generic_msg(_generic_transform_error_message.format(self.__class__.__name__))


class DropColumnsTransformer(BaseEstimator, TransformerMixin):

    def __init__(self, columns_to_keep: Union[int, List[int]]):
        if not isinstance(columns_to_keep, list):
            self.columns_to_keep = [columns_to_keep]
        else:
            self.columns_to_keep = columns_to_keep
        arr = np.array(self.columns_to_keep, dtype=int)
        self.model = ColumnTransformer([("selectcolumn", "passthrough", arr)], remainder="drop")

    def fit(self, X: DataInputType, y: pd.Series) -> 'DropColumnsTransformer':
        # there is nothing to fit
        return self

    def transform(self, X: DataInputType) -> DataInputType:
        if self.columns_to_keep:
            return self.model.fit_transform(X)
        else:
            return X

    def get_params(self, deep=True):
        """
        Return parameters of DropColumnsTransformer as dictionary.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: bool
        :return: Dictionary of drop columns transform parameters.
        """

        if deep:
            return self.model.get_params(deep)
        else:
            params = {}
            params["columns_to_keep"] = self.columns_to_keep
            return params


class IdentityTransformer(BaseEstimator, TransformerMixin):
    """
    Identity transformer class.

    Returns the same X it accepts.
    """

    def fit(self,
            X: np.ndarray,
            y: Optional[np.ndarray] = None) -> Any:
        """
        Take X and does nothing with it.

        :param X: Features to transform.
        :param y: Target values.
        :return: This transformer.
        """
        return self

    def transform(self,
                  X: np.ndarray,
                  y: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Perform the identity transform.

        :param X: Features to tranform.
        :param y: Target values.
        :return: The same X that was passed
        """
        return X


class LogTransformer(BaseEstimator, TransformerMixin):
    """
    Log transformer class.

    :param safe:
        If true, truncate values outside the transformer's
        domain to the nearest point in the domain.
    :type safe: bool
    :return: Object of class LogTransformer.

    """

    def __init__(self, safe=True):
        """
        Initialize function for Log transformer.

        :param safe:
            If true, truncate values outside the transformer's
            domain to the nearest point in the domain.
        :type safe: bool
        :return: Object of class LogTransformer.
        """
        self.base = np.e
        self.y_min = None
        self.scaler = None
        self.lower_range = 1e-5
        self.safe = safe

    def __repr__(self):
        return "{}(safe={})".format(self.__class__.__name__, self.safe)

    def __str__(self):
        """
        Return transformer details into string.

        return: string representation of Log transform.
        """
        return "LogTransformer(base=e, y_min=%.5f, scaler=%s, safe=%s)" % \
               (self.y_min if self.y_min is not None else 0,
                self.scaler,
                self.safe)

    def fit(self, y, y_min=None):
        """
        Fit function for Log transform.

        :param y: Input training data.
        :type y: numpy.ndarray
        :param y_min: Minimum value of y, will be inferred if not set
        :type y_min: float
        :return: Returns an instance of the LogTransformer model.
        """
        if y_min is None:
            self.y_min = np.min(y)
        else:
            if (y_min is not None) and y_min <= np.min(y):
                self.y_min = y_min
            else:
                self.y_min = np.min(y)
                warnings.warn(
                    'Caution: y_min greater than observed minimum in y')

        if self.y_min > self.lower_range:
            self.y_min = self.lower_range
            try:
                self.scaler = preprocessing.StandardScaler(
                    copy=False, with_mean=False,
                    with_std=False).fit(y.reshape(-1, 1))
            except Exception as e:
                raise FitException.from_exception(e, has_pii=True, target="LogTransformer"). \
                    with_generic_msg(_generic_fit_error_message.format(self.__class__.__name__))
        else:
            y_max = np.max(y)
            try:
                self.scaler = preprocessing.MinMaxScaler(
                    feature_range=(self.lower_range, 1)).fit(
                    np.array([y_max, self.y_min]).reshape(-1, 1))
            except Exception as e:
                raise FitException.from_exception(e, has_pii=True, target="LogTransformer"). \
                    with_generic_msg(_generic_fit_error_message.format(self.__class__.__name__))

        return self

    def get_params(self, deep=True):
        """
        Return parameters of Log transform as dictionary.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: bool
        :return: Dictionary of Log transform parameters.
        """
        return {"base": self.base,
                "y_min": self.y_min,
                "scaler": self.scaler,
                "safe": self.safe
                }

    def return_y(self, y):
        """
        Return log value of y.

        :param y: Input data.
        :type y: numpy.ndarray
        :return: The log transform array.
        """
        return np.log(y)

    def transform(self, y):
        """
        Transform function for Log transform to return the log value.

        :param y: Input data.
        :type y: numpy.ndarray
        :return: The log transform array.
        """
        if self.y_min is None:
            raise UntrainedModelException.create_without_pii(target='LogTransformer')
        elif np.min(y) < self.y_min and \
                np.min(self.scaler.transform(
                    y.reshape(-1, 1)).reshape(-1, )) <= 0:
            if self.safe:
                warnings.warn("y_min greater than observed minimum in y, "
                              "clipping y to domain")
                y_copy = y.copy()
                y_copy[y < self.y_min] = self.y_min
                try:
                    return self.return_y(
                        self.scaler.transform(y_copy.reshape(-1, 1)).reshape(-1, ))
                except Exception as e:
                    raise TransformException.from_exception(
                        e, has_pii=True, target="LogTransformer",
                        reference_code='model_wrappers.LogTransformer.transform.y_min_greater'). \
                        with_generic_msg(_generic_transform_error_message.format(self.__class__.__name__))
            else:
                raise DataException._with_error(
                    AzureMLError.create(
                        TransformerYMinGreater, target="LogTransformer", transformer_name="LogTransformer"
                    )
                )
        else:
            try:
                return self.return_y(
                    self.scaler.transform(y.reshape(-1, 1)).reshape(-1, ))
            except Exception as e:
                raise TransformException.from_exception(
                    e, has_pii=True, target="LogTransformer",
                    reference_code='model_wrappers.LogTransformer.transform'). \
                    with_generic_msg(_generic_transform_error_message.format(self.__class__.__name__))

    def inverse_transform(self, y):
        """
        Inverse transform function for Log transform.

        :param y: Input data.
        :type y: numpy.ndarray
        :return: Inverse Log transform.
        """
        # this inverse transform has no restrictions, can exponetiate anything
        if self.y_min is None:
            raise UntrainedModelException.create_without_pii(target='LogTransformer')
        try:
            return self.scaler.inverse_transform(
                np.exp(y).reshape(-1, 1)).reshape(-1, )
        except Exception as e:
            raise TransformException.from_exception(
                e, has_pii=True, target='LogTransformer',
                reference_code='model_wrappers.LogTransformer.inverse_transform'). \
                with_generic_msg(_generic_transform_error_message.format(self.__class__.__name__))


class PowerTransformer(BaseEstimator, TransformerMixin):
    """
    Power transformer class.

    :param power: Power to raise y values to.
    :type power: float
    :param safe:
        If true, truncate values outside the transformer's domain to
        the nearest point in the domain.
    :type safe: bool
    """

    def __init__(self, power=1, safe=True):
        """
        Initialize function for Power transformer.

        :param power: Power to raise y values to.
        :type power: float
        :param safe:
            If true, truncate values outside the transformer's domain
            to the nearest point in the domain.
        :type safe: bool
        """
        # power = 1 is the identity transformation
        self.power = power
        self.y_min = None
        self.accept_negatives = False
        self.lower_range = 1e-5
        self.scaler = None
        self.safe = safe

        # check if the exponent is everywhere defined
        if self.power > 0 and \
                (((self.power % 2 == 1) or (1 / self.power % 2 == 1))
                 or (self.power % 2 == 0 and self.power > 1)):
            self.accept_negatives = True
            self.y_min = -np.inf
            self.offset = 0
            self.scaler = preprocessing.StandardScaler(
                copy=False, with_mean=False, with_std=False).fit(
                np.array([1], dtype=float).reshape(-1, 1))

    def __repr__(self):
        params = {
            "power": self.power,
            "safe": self.safe
        }

        return "{}({})".format(
            self.__class__.__name__,
            ", ".join(["{}={}".format(k, repr(params[k])) for k in params])
        )

    def __str__(self):
        """
        Return transformer details into string.

        return: String representation of Power transform.
        """
        return \
            "PowerTransformer(power=%.1f, y_min=%.5f, scaler=%s, safe=%s)" % (
                self.power,
                self.y_min if self.y_min is not None else 0,
                self.scaler,
                self.safe)

    def return_y(self, y, power, invert=False):
        """
        Return some 'power' of 'y'.

        :param y: Input data.
        :type y: numpy.ndarray
        :param power: Power value.
        :type power: float
        :param invert:
            A boolean whether or not to perform the inverse transform.
        :type invert: bool
        :return: The transformed targets.
        """
        # ignore invert, the power has already been inverted
        # can ignore invert because no offsetting has been done
        if self.accept_negatives:
            if np.any(y < 0):
                mult = np.sign(y)
                y_inter = np.multiply(np.power(np.absolute(y), power), mult)
            else:
                y_inter = np.power(y, power)
        else:
            # these are ensured to only have positives numbers as inputs
            y_inter = np.power(y, power)

        if invert:
            try:
                return self.scaler.inverse_transform(
                    y_inter.reshape(-1, 1)).reshape(-1, )
            except Exception as e:
                raise TransformException.from_exception(
                    e, has_pii=True, target="PowerTransformer",
                    reference_code='model_wrappers.PowerTransformer.return_y'). \
                    with_generic_msg(_generic_transform_error_message.format(self.__class__.__name__))
        else:
            return y_inter

    def get_params(self, deep=True):
        """
        Return parameters of Power transform as dictionary.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: bool
        :return: Dictionary of Power transform parameters.
        """
        return {
            "power": self.power,
            "scaler": self.scaler,
            "y_min": self.y_min,
            "accept_negatives": self.accept_negatives,
            "safe": self.safe
        }

    def fit(self, y, y_min=None):
        """
        Fit function for Power transform.

        :param y: Input training data.
        :type y: numpy.ndarray
        :param y_min: Minimum value of y, will be inferred if not set.
        :type y_min: float
        :return: Returns an instance of the PowerTransformer model.
        """
        if y_min is None:
            self.y_min = np.min(y)
        else:
            if (y_min is not None) and y_min <= np.min(y):
                self.y_min = y_min
            else:
                self.y_min = np.min(y)
                warnings.warn(
                    'Caution: y_min greater than observed minimum in y')

        if self.y_min > self.lower_range:
            self.y_min = self.lower_range
            try:
                self.scaler = preprocessing.StandardScaler(
                    copy=False, with_mean=False,
                    with_std=False).fit(y.reshape(-1, 1))
            except Exception as e:
                raise FitException.from_exception(e, has_pii=True, target="PowerTransformer"). \
                    with_generic_msg(_generic_fit_error_message.format(self.__class__.__name__))
        else:
            y_max = np.max(y)
            try:
                self.scaler = preprocessing.MinMaxScaler(
                    feature_range=(self.lower_range, 1)).fit(
                    np.array([y_max, self.y_min]).reshape(-1, 1))
            except Exception as e:
                raise FitException.from_exception(e, has_pii=True, target="PowerTransformer"). \
                    with_generic_msg(_generic_fit_error_message.format(self.__class__.__name__))
        return self

    def transform(self, y):
        """
        Transform function for Power transform.

        :param y: Input data.
        :type y: numpy.ndarray
        :return: Power transform result.
        """
        if self.y_min is None and not (self.power > 0 and self.power % 2 == 1):
            raise UntrainedModelException.create_without_pii(target='PowerTransformer')
        elif np.min(y) < self.y_min and not self.accept_negatives and np.min(
                self.scaler.transform(y.reshape(-1, 1)).reshape(-1, )) <= 0:
            if self.safe:
                warnings.warn(
                    "y_min greater than observed minimum in y, clipping y to "
                    "domain")
                y_copy = y.copy()
                y_copy[y < self.y_min] = self.y_min
                try:
                    return self.return_y(
                        self.scaler.transform(y_copy.reshape(-1, 1)).reshape(-1, ),
                        self.power, invert=False)
                except Exception as e:
                    raise TransformException.from_exception(
                        e, has_pii=True, target="PowerTransformer",
                        reference_code='model_wrappers.PowerTransformer.transform.y_min_greater'). \
                        with_generic_msg(_generic_transform_error_message.format(self.__class__.__name__))
            else:
                raise DataException._with_error(
                    AzureMLError.create(
                        TransformerYMinGreater, target="PowerTransformer", transformer_name="PowerTransformer"
                    )
                )
        else:
            try:
                return self.return_y(
                    self.scaler.transform(y.reshape(-1, 1)).reshape(-1, ),
                    self.power, invert=False)
            except Exception as e:
                raise TransformException.from_exception(
                    e, has_pii=True, target="PowerTransformer",
                    reference_code='model_wrappers.PowerTransformer.transform'). \
                    with_generic_msg(_generic_transform_error_message.format(self.__class__.__name__))

    def inverse_transform(self, y):
        """
        Inverse transform function for Power transform.

        :param y: Input data.
        :type y: numpy.ndarray
        :return: Inverse Power transform result.
        """
        if self.y_min is None and \
                not (self.power > 0 and self.power % 2 == 1):
            raise UntrainedModelException.create_without_pii(target="PowerTransformer")
        elif not self.accept_negatives and np.min(y) <= 0:
            if self.safe:
                warnings.warn(
                    "y_min greater than observed minimum in y, clipping y to "
                    "domain")
                transformed_min = np.min(y[y > 0])
                y_copy = y.copy()
                y_copy[y < transformed_min] = transformed_min
                return self.return_y(y_copy, 1 / self.power, invert=True)
            else:
                raise DataException._with_error(
                    AzureMLError.create(PowerTransformerInverseTransform, target="PowerTransformer")
                )
        else:
            return self.return_y(y, 1 / self.power, invert=True)


class BoxCoxTransformerScipy(BaseEstimator, TransformerMixin):
    """
    Box Cox transformer class for normalizing non-normal data.

    :param lambda_val:
        Lambda value for Box Cox transform, will be inferred if not set.
    :type lambda_val: float
    :param safe:
        If true, truncate values outside the transformer's domain to
        the nearest point in the domain.
    :type safe: bool
    """

    def __init__(self, lambda_val=None, safe=True):
        """
        Initialize function for Box Cox transformer.

        :param lambda_val:
            Lambda value for Box Cox transform, will be inferred if not set.
        :type lambda_val: float
        :param safe:
            If true, truncate values outside the transformer's domain
            to the nearest point in the domain.
        :type safe: bool
        """
        # can also use lambda_val = 0 as equivalent to natural log transformer
        self.lambda_val = lambda_val
        self.lower_range = 1e-5
        self.y_min = None
        self.scaler = None
        self.fitted = False
        self.safe = safe

    def get_params(self, deep: bool = True) -> Dict[str, Any]:
        return {
            "lambda_val": self.lambda_val,
            "safe": self.safe
        }

    def __repr__(self):
        params = self.get_params(deep=False)
        return _codegen_utilities.generate_repr_str(self.__class__, params)

    def __str__(self):
        """
        Return transformer details into string.

        return: String representation of Box Cox transform.
        """
        return ("BoxCoxTransformer(lambda=%.3f, y_min=%.5f, scaler=%s, "
                "safe=%s)" %
                (self.lambda_val if self.lambda_val is not None else 0,
                 self.y_min if self.y_min is not None else 0,
                 self.scaler,
                 self.safe))

    def fit(self, y, y_min=None):
        """
        Fit function for Box Cox transform.

        :param y: Input training data.
        :type y: numpy.ndarray
        :param y_min: Minimum value of y, will be inferred if not set.
        :type y_min: float
        :return: Returns an instance of the BoxCoxTransformerScipy model.
        """
        self.fitted = True
        if y_min is None:
            self.y_min = np.min(y)
        else:
            if (y_min is not None) and y_min <= np.min(y):
                self.y_min = y_min
            else:
                self.y_min = np.min(y)
                warnings.warn(
                    'Caution: y_min greater than observed minimum in y')
        if self.y_min > self.lower_range:
            self.y_min = self.lower_range
            try:
                self.scaler = preprocessing.StandardScaler(
                    copy=False,
                    with_mean=False,
                    with_std=False).fit(y.reshape(-1, 1))
            except Exception as e:
                raise FitException.from_exception(e, has_pii=True, target="BoxCoxTransformer"). \
                    with_generic_msg(_generic_fit_error_message.format(self.__class__.__name__))
        else:
            y_max = np.max(y)
            try:
                self.scaler = preprocessing.MinMaxScaler(
                    feature_range=(self.lower_range, 1)).fit(
                    np.array([y_max, self.y_min]).reshape(-1, 1))
            except Exception as e:
                raise FitException.from_exception(e, has_pii=True, target="BoxCoxTransformer"). \
                    with_generic_msg(_generic_fit_error_message.format(self.__class__.__name__))

        # reset if already fitted
        if self.lambda_val is None or self.fitted:
            try:
                y, self.lambda_val = boxcox(
                    self.scaler.transform(y.reshape(-1, 1)).reshape(-1, ))
            except Exception as e:
                raise TransformException.from_exception(
                    e, has_pii=True, target="BoxCoxTransformer",
                    reference_code='model_wrappers.BoxCoxTransformer.fit'). \
                    with_generic_msg(_generic_transform_error_message.format(self.__class__.__name__))
        return self

    def transform(self, y):
        """
        Transform function for Box Cox transform.

        :param y: Input data.
        :type y: numpy.ndarray
        :return: Box Cox transform result.
        """
        if self.lambda_val is None:
            raise UntrainedModelException.create_without_pii(target="BoxCoxTransformer")
        elif np.min(y) < self.y_min and \
                np.min(
                    self.scaler.transform(y.reshape(-1, 1)).reshape(-1, )) <= 0:
            if self.safe:
                warnings.warn("y_min greater than observed minimum in y, "
                              "clipping y to domain")
                y_copy = y.copy()
                y_copy[y < self.y_min] = self.y_min
                try:
                    return boxcox(
                        self.scaler.transform(y_copy.reshape(-1, 1)).reshape(-1, ),
                        self.lambda_val)
                except Exception as e:
                    raise TransformException.from_exception(
                        e, has_pii=True, target="BoxCoxTransformer",
                        reference_code='model_wrappers.BoxCoxTransformer.transform.y_min_greater'). \
                        with_generic_msg(_generic_transform_error_message.format(self.__class__.__name__))
            else:
                raise DataException._with_error(
                    AzureMLError.create(
                        TransformerYMinGreater, target="BoxCoxTransformer", transformer_name="BoxCoxTransformer"
                    )
                )
        else:
            try:
                return boxcox(
                    self.scaler.transform(y.reshape(-1, 1)).reshape(-1, ),
                    self.lambda_val)
            except Exception as e:
                raise TransformException.from_exception(
                    e, has_pii=True, target="BoxCoxTransformer",
                    reference_code='model_wrappers.BoxCoxTransformer.transform'). \
                    with_generic_msg(_generic_transform_error_message.format(self.__class__.__name__))

    def inverse_transform(self, y):
        """
        Inverse transform function for Box Cox transform.

        :param y: Input data.
        :type y: numpy.ndarray
        :return: Inverse Box Cox transform result.
        """
        # inverse box_cox can take any number
        if self.lambda_val is None:
            raise UntrainedModelException.create_without_pii(target="BoxCoxTransformer_Inverse")
        else:
            try:
                return self.scaler.inverse_transform(
                    inv_boxcox(y, self.lambda_val).reshape(-1, 1)).reshape(-1, )
            except Exception as e:
                raise TransformException.from_exception(
                    e, has_pii=True, target="BoxCoxTransformer_Inverse",
                    reference_code='model_wrappers.BoxCoxTransformerScipy.inverse_transform'). \
                    with_generic_msg(_generic_transform_error_message.format(self.__class__.__name__))


class TargetTypeTransformer(BaseEstimator, TransformerMixin):

    """
    Target Type Transformer class for post-processing the target column.

    :param target_type:
        Prediction Transform Type to be used for casting the target column.
    :type safe: str
    :return: Object of class TargetTypeTransformer.

    """

    def __init__(self, target_type):
        self.target_type = target_type

    """
    Fit function for Target Type transform.

    :param y: Input training data.
    :type y: numpy.ndarray
    :return: Returns an instance of the TargetTypeTransformer model.
    """

    def fit(self, y):
        return self

    """
    Transform function for Target Type transform.

    :param y: Input data.
    :type y: numpy.ndarray
    :return: TargetType transform result.
     """

    def transform(self, y):
        return y

    """
    Inverse transform function for TargetType transform.

    :param y: Input data.
    :type y: numpy.ndarray
    :return: Inverse TargetType transform result.
    """

    def inverse_transform(self, y):
        if (self.target_type == _PredictionTransformTypes.INTEGER):
            return y.astype(int)
        # No need to force float casting since default target column type is float.
        return y


class PreFittedSoftVotingClassifier(VotingClassifier):
    """
    Pre-fitted Soft Voting Classifier class.

    :param estimators: Models to include in the PreFittedSoftVotingClassifier
    :type estimators: list
    :param weights: Weights given to each of the estimators
    :type weights: numpy.ndarray
    :param flatten_transform:
        If True, transform method returns matrix with
        shape (n_samples, n_classifiers * n_classes).
        If False, it returns (n_classifiers, n_samples,
        n_classes).
    :type flatten_transform: bool
    """

    def __init__(
            self, estimators, weights=None, flatten_transform=None,
            classification_labels=None):
        """
        Initialize function for Pre-fitted Soft Voting Classifier class.

        :param estimators:
            Models to include in the PreFittedSoftVotingClassifier
        :type estimators: list
        :param weights: Weights given to each of the estimators
        :type weights: numpy.ndarray
        :param flatten_transform:
            If True, transform method returns matrix with
            shape (n_samples, n_classifiers * n_classes).
            If False, it returns (n_classifiers, n_samples, n_classes).
        :type flatten_transform: bool
        """
        super().__init__(estimators=estimators,
                         voting='soft',
                         weights=weights,
                         flatten_transform=flatten_transform)
        try:
            self.estimators_ = [est[1] for est in estimators]
            self._labels = classification_labels
            if classification_labels is None:
                self.le_ = LabelEncoder().fit([0])
            else:
                self.le_ = LabelEncoder().fit(classification_labels)
        except Exception as e:
            raise FitException.from_exception(e, has_pii=True, target="PreFittedSoftVotingClassifier"). \
                with_generic_msg(_generic_fit_error_message.format(self.__class__.__name__))
        # Fill the classes_ property of VotingClassifier which is calculated
        # during fit.
        # This is important for the ONNX convert, when parsing the model object.
        self.classes_ = self.le_.classes_

    def __setstate__(self, state):
        if "_labels" not in state:
            state["_labels"] = state["le_"].classes_
        super().__setstate__(state)

    def get_params(self, deep: bool = True) -> Dict[str, Any]:
        params = super().get_params(deep)
        new_params = {
            "estimators": params.get("estimators"),
            "weights": params.get("weights"),
            "flatten_transform": params.get("flatten_transform"),
            "classification_labels": self._labels
        }
        return new_params

    def _get_imports(self) -> List[Tuple[str, str, Any]]:
        return [
            _codegen_utilities.get_import(estimator) for estimator in self.estimators_
        ] + [
            (np.array.__module__, "array", np.array)
        ]

    def __repr__(self) -> str:
        params = self.get_params(deep=False)
        return _codegen_utilities.generate_repr_str(self.__class__, params)

    def _collect_probas(self, X):
        """
        Collect predictions from the ensembled models.

        See base implementation and use here:
        https://github.com/scikit-learn/scikit-learn/blob/master/sklearn/ensemble/_voting.py

        This method is overloaded from scikit-learn implementation based on version 0.22.
        This overload is necessary because scikit-learn assumes ensembled models are all
        trained on the same classes. However, AutoML may ensemble models which have been
        trained on different subsets of data (due to subsampling) resulting in different
        train class labels and brings the need to pad predictions.
        """
        probas = [
            _scoring_utilities.pad_predictions(clf.predict_proba(X), clf.classes_, self.classes_)
            for clf in self.estimators_
        ]
        return np.asarray(probas)


if sklearn.__version__ >= '0.21.0':
    from sklearn.ensemble import VotingRegressor

    class PreFittedSoftVotingRegressor(VotingRegressor):
        """
        Pre-fitted Soft Voting Regressor class.

        :param estimators: Models to include in the PreFittedSoftVotingRegressor
        :type estimators: list
        :param weights: Weights given to each of the estimators
        :type weights: numpy.ndarray
        :param flatten_transform:
            If True, transform method returns matrix with
            shape (n_samples, n_classifiers). If False, it
            returns (n_classifiers, n_samples, 1).
        :type flatten_transform: bool
        """

        def __init__(self, estimators, weights=None):
            """
            Initialize function for Pre-fitted Soft Voting Regressor class.

            :param estimators:
                Models to include in the PreFittedSoftVotingRegressor
            :type estimators: list
            :param weights: Weights given to each of the estimators
            :type weights: numpy.ndarray
            :param flatten_transform:
                If True, transform method returns matrix with
                shape (n_samples, n_classifiers). If False, it
                returns (n_classifiers, n_samples, 1).
            :type flatten_transform: bool
            """
            self.estimators_ = [est[1] for est in estimators]
            self._wrappedEnsemble = VotingRegressor(estimators, weights)
            self._wrappedEnsemble.estimators_ = self.estimators_

        def __repr__(self) -> str:
            params = self.get_params(deep=False)
            return _codegen_utilities.generate_repr_str(self.__class__, params)

        def _get_imports(self) -> List[Tuple[str, str, Any]]:
            return [
                _codegen_utilities.get_import(estimator) for estimator in self._wrappedEnsemble.estimators_
            ]

        def fit(self, X, y, sample_weight=None):
            """
            Fit function for PreFittedSoftVotingRegressor model.

            :param X: Input data.
            :type X: numpy.ndarray or scipy.sparse.spmatrix
            :param y: Input target values.
            :type y: numpy.ndarray
            :param sample_weight: If None, then samples are equally weighted. This is only supported if all
                underlying estimators support sample weights.
            """
            try:
                return self._wrappedEnsemble.fit(X, y, sample_weight)
            except Exception as e:
                raise FitException.from_exception(e, has_pii=True, target="PreFittedSoftVotingRegressor"). \
                    with_generic_msg(_generic_fit_error_message.format(self.__class__.__name__))

        def predict(self, X):
            """
            Predict function for Pre-fitted Soft Voting Regressor class.

            :param X: Input data.
            :type X: numpy.ndarray
            :return: Weighted average of predicted values.
            """
            try:
                return self._wrappedEnsemble.predict(X)
            except Exception as e:
                raise PredictionException.from_exception(e, has_pii=True, target='PreFittedVotingRegressor'). \
                    with_generic_msg(_generic_prediction_error_message.format(self.__class__.__name__))

        def get_params(self, deep=True):
            """
            Return parameters for Pre-fitted Soft Voting Regressor model.

            :param deep:
                If True, will return the parameters for this estimator
                and contained subobjects that are estimators.
            :type deep: bool
            :return: dictionary of parameters
            """
            state = {
                "estimators": self._wrappedEnsemble.estimators,
                "weights": self._wrappedEnsemble.weights
            }
            return state

        def set_params(self, **params):
            """
            Set the parameters of this estimator.

            :return: self
            """
            return super(PreFittedSoftVotingRegressor, self).set_params(**params)

        def __setstate__(self, state):
            """
            Set state for object reconstruction.

            :param state: pickle state
            """
            if '_wrappedEnsemble' in state:
                self._wrappedEnsemble = state['_wrappedEnsemble']
            else:
                # ensure we can load state from previous version of this class
                self._wrappedEnsemble = PreFittedSoftVotingRegressor(state['estimators'], state['weights'])
else:
    class PreFittedSoftVotingRegressor(BaseEstimator, RegressorMixin):  # type: ignore
        """
        Pre-fitted Soft Voting Regressor class.

        :param estimators: Models to include in the PreFittedSoftVotingRegressor
        :type estimators: list
        :param weights: Weights given to each of the estimators
        :type weights: numpy.ndarray
        :param flatten_transform:
            If True, transform method returns matrix with
            shape (n_samples, n_classifiers). If False, it
            returns (n_classifiers, n_samples, 1).
        :type flatten_transform: bool
        """

        def __init__(self, estimators, weights=None, flatten_transform=None):
            """
            Initialize function for Pre-fitted Soft Voting Regressor class.

            :param estimators:
                Models to include in the PreFittedSoftVotingRegressor
            :type estimators: list
            :param weights: Weights given to each of the estimators
            :type weights: numpy.ndarray
            :param flatten_transform:
                If True, transform method returns matrix with
                shape (n_samples, n_classifiers). If False, it
                returns (n_classifiers, n_samples, 1).
            :type flatten_transform: bool
            """
            self._wrappedEnsemble = PreFittedSoftVotingClassifier(
                estimators, weights, flatten_transform, classification_labels=[0])

        def __repr__(self) -> str:
            params = self.get_params(deep=False)
            return _codegen_utilities.generate_repr_str(self.__class__, params)

        def _get_imports(self) -> List[Tuple[str, str, Any]]:
            return [
                _codegen_utilities.get_import(estimator) for estimator in self._wrappedEnsemble.estimators_
            ]

        def fit(self, X, y, sample_weight=None):
            """
            Fit function for PreFittedSoftVotingRegressor model.

            :param X: Input data.
            :type X: numpy.ndarray or scipy.sparse.spmatrix
            :param y: Input target values.
            :type y: numpy.ndarray
            :param sample_weight: If None, then samples are equally weighted. This is only supported if all
                underlying estimators support sample weights.
            """
            try:
                # We cannot directly call into the wrapped model as the VotingClassifier will label
                # encode y. We get around this problem in the training case by passing in a single
                # classification label [0]. This is also only a problem on scikit-learn<=0.20. On
                # scikit-learn>=0.21, we rely on the VotingRegressor which correctly handles fitting
                # base learners. Imports are intentionally kept within this funciton to ensure compatibility
                # if scikit-learn>0.20 is installed (where this class is unused).

                # This implementation is based on the fit implementation of the VotingClassifier on
                # scikit-learn version 0.20. More information can be found on this branch:
                # https://github.com/scikit-learn/scikit-learn/blob/0.20.X/sklearn/ensemble/voting_classifier.py
                from joblib import Parallel, delayed
                from sklearn.utils import Bunch
                names, clfs = zip(*self._wrappedEnsemble.estimators)

                def _parallel_fit_estimator(estimator, X, y, sample_weight=None):
                    """Private function used to fit an estimator within a job."""
                    if sample_weight is not None:
                        estimator.fit(X, y, sample_weight=sample_weight)
                    else:
                        estimator.fit(X, y)
                    return estimator

                self._wrappedEnsemble.estimators_ = Parallel(n_jobs=self._wrappedEnsemble.n_jobs)(
                    delayed(_parallel_fit_estimator)(clone(clf), X, y, sample_weight=sample_weight)
                    for clf in clfs if clf is not None)

                self._wrappedEnsemble.named_estimators_ = Bunch(**dict())
                for k, e in zip(self._wrappedEnsemble.estimators, self._wrappedEnsemble.estimators_):
                    self._wrappedEnsemble.named_estimators_[k[0]] = e
                return self
            except Exception as e:
                raise FitException.from_exception(e, has_pii=True, target="PreFittedSoftVotingRegressor"). \
                    with_generic_msg(_generic_fit_error_message.format(self.__class__.__name__))

        def predict(self, X):
            """
            Predict function for Pre-fitted Soft Voting Regressor class.

            :param X: Input data.
            :type X: numpy.ndarray
            :return: Weighted average of predicted values.
            """
            try:
                predicted = self._wrappedEnsemble._predict(X)
                return np.average(predicted, axis=1, weights=self._wrappedEnsemble.weights)
            except Exception as e:
                raise PredictionException.from_exception(e, has_pii=True, target='PreFittedVotingRegressor'). \
                    with_generic_msg(_generic_prediction_error_message.format(self.__class__.__name__))

        def get_params(self, deep=True):
            """
            Return parameters for Pre-fitted Soft Voting Regressor model.

            :param deep:
                If True, will return the parameters for this estimator
                and contained subobjects that are estimators.
            :type deep: bool
            :return: dictionary of parameters
            """
            state = {
                "estimators": self._wrappedEnsemble.estimators,
                "weights": self._wrappedEnsemble.weights,
                "flatten_transform": self._wrappedEnsemble.flatten_transform
            }
            return state

        def set_params(self, **params):
            """
            Set the parameters of this estimator.

            :return: self
            """
            return super(PreFittedSoftVotingRegressor, self).set_params(**params)  # type: ignore

        def __setstate__(self, state):
            """
            Set state for object reconstruction.

            :param state: pickle state
            """
            if '_wrappedEnsemble' in state:
                self._wrappedEnsemble = state['_wrappedEnsemble']
            else:
                # ensure we can load state from previous version of this class
                self._wrappedEnsemble = PreFittedSoftVotingClassifier(
                    state['estimators'], state['weights'], state['flatten_transform'], classification_labels=[0])


class StackEnsembleBase(ABC, _BaseComposition):
    """StackEnsemble class. Represents a 2 layer Stacked Ensemble."""

    def __init__(self, base_learners, meta_learner, training_cv_folds=5):
        """
        Initialize function for StackEnsemble.

        :param base_learners:
            The collection of (name, estimator) for the base layer of the Ensemble
        :type base_learners: list
        :param meta_learner:
            The model used in the second layer of the Stack to generate the final predictions.
        :type meta_learner: Estimator / Pipeline
        :param training_cv_folds:
            The number of cross validation folds to be used during fitting of this Ensemble.
        :type training_cv_folds: int
        """
        super().__init__()
        self._base_learners = base_learners
        self._meta_learner = meta_learner
        self._training_cv_folds = training_cv_folds

    def __repr__(self) -> str:
        params = self.get_params(deep=False)
        return _codegen_utilities.generate_repr_str(self.__class__, params)

    def _get_imports(self) -> List[Tuple[str, str, Any]]:
        return [
            _codegen_utilities.get_import(learner[1]) for learner in self._base_learners
        ] + [
            _codegen_utilities.get_import(self._meta_learner)
        ]

    def fit(self, X: DataInputType, y: np.ndarray) -> 'StackEnsembleBase':
        """
        Fit function for StackEnsemble model.

        :param X: Input data.
        :param y: Input target values.
        :type y: numpy.ndarray
        :return: Returns self.
        """
        predictions = None  # type: np.ndarray

        # cache the CV split indices into a list
        cv_indices = list(self._get_cv_split_indices(X, y))

        y_out_of_fold_concat = None
        for _, test_indices in cv_indices:
            y_test = y[test_indices]
            if y_out_of_fold_concat is None:
                y_out_of_fold_concat = y_test
            else:
                y_out_of_fold_concat = np.concatenate((y_out_of_fold_concat, y_test))

        for index, (_, learner) in enumerate(self._base_learners):
            temp = None  # type: np.ndarray
            for train_indices, test_indices in cv_indices:
                if isinstance(X, pd.DataFrame):
                    X_train, X_test = X.iloc[train_indices], X.iloc[test_indices]
                else:
                    X_train, X_test = X[train_indices], X[test_indices]
                y_train, y_test = y[train_indices], y[test_indices]
                cloned_learner = clone(learner)
                try:
                    cloned_learner.fit(X_train, y_train)
                except Exception as e:
                    raise FitException.from_exception(e, has_pii=True, target='StackEnsemble'). \
                        with_generic_msg(_generic_fit_error_message.format(self.__class__.__name__))
                model_predictions = self._get_base_learner_predictions(cloned_learner, X_test)

                if temp is None:
                    temp = model_predictions
                else:
                    temp = np.concatenate((temp, model_predictions))

                if len(temp.shape) == 1:
                    predictions = np.zeros((y.shape[0], 1, len(self._base_learners)))
                else:
                    predictions = np.zeros((y.shape[0], temp.shape[1], len(self._base_learners)))

            if len(temp.shape) == 1:
                # add an extra dimension so that we can reuse the predictions array
                # across multiple training types
                temp = temp[:, None]
            predictions[:, :, index] = temp

        all_out_of_fold_predictions = []
        for idx in range(len(self._base_learners)):
            # get the vertical concatenation of the out of fold predictions from the selector
            # as they were already computed during the selection phase
            model_predictions = predictions[:, :, idx]
            all_out_of_fold_predictions.append(model_predictions)

        meta_learner_training = self._horizontal_concat(all_out_of_fold_predictions)
        cloned_meta_learner = clone(self._meta_learner)
        try:
            cloned_meta_learner.fit(meta_learner_training, y_out_of_fold_concat)
        except Exception as e:
            raise FitException.from_exception(e, has_pii=True, target='StackEnsemble'). \
                with_generic_msg(_generic_fit_error_message.format(self.__class__.__name__))

        final_base_learners = []
        for name, learner in self._base_learners:
            final_learner = clone(learner)
            final_learner.fit(X, y)
            final_base_learners.append((name, final_learner))

        self._base_learners = final_base_learners
        self._meta_learner = cloned_meta_learner

        return self

    def predict(self, X):
        """
        Predict function for StackEnsemble class.

        :param X: Input data.
        :return: Weighted average of predicted values.
        """
        predictions = self._get_base_learners_predictions(X)
        try:
            return self._meta_learner.predict(predictions)
        except Exception as e:
            raise PredictionException.from_exception(e, has_pii=True, target='StackEnsembleBase'). \
                with_generic_msg(_generic_prediction_error_message.format(self.__class__.__name__))

    @staticmethod
    def _horizontal_concat(predictions_list: List[np.ndarray]) -> Optional[np.ndarray]:
        """
        Concatenate multiple base learner predictions horizontally.

        Given a list of out-of-fold predictions from base learners, it concatenates these predictions
        horizontally to create one 2D matrix which will be used as training set for the meta learner.
        In case we're dealing with a classification problem, we need to drop one column out of each
        element within the input list, so that the resulting matrix is not collinear (because the sum of all class
        probabilities would be equal to 1 )
        """
        if len(predictions_list) == 0:
            return None
        preds_shape = predictions_list[0].shape
        if len(preds_shape) == 2 and preds_shape[1] > 1:
            # remove first class prediction probabilities so that the matrix isn't collinear
            predictions_list = [np.delete(pred, 0, 1) for pred in predictions_list]
        elif len(preds_shape) == 1:
            # if we end up with a single feature, we'd have a single dimensional array, so we'll need to reshape it
            # in order for SKLearn to accept it as input
            predictions_list = [pred.reshape(-1, 1) for pred in predictions_list if pred.ndim == 1]

        # now let's concatenate horizontally all the predictions
        predictions = np.hstack(predictions_list)
        return cast(np.ndarray, predictions)

    def _get_base_learners_predictions(self, X: List[np.ndarray]) -> Optional[np.ndarray]:
        predictions = [self._get_base_learner_predictions(estimator, X) for _, estimator in self._base_learners]
        return StackEnsembleBase._horizontal_concat(predictions)

    @abstractmethod
    def _get_cv_split_indices(self, X, y):
        pass

    @abstractmethod
    def _get_base_learner_predictions(self, model, X):
        pass

    def get_params(self, deep=True):
        """
        Return parameters for StackEnsemble model.

        :param deep:
                If True, will return the parameters for this estimator
                and contained subobjects that are estimators.
        :type deep: bool
        :return: Parameters for the StackEnsemble model.
        """
        result = {
            "base_learners": self._base_learners,
            "meta_learner": self._meta_learner,
            "training_cv_folds": self._training_cv_folds
        }

        if not deep:
            return result

        base_layer_params = super(StackEnsembleBase, self)._get_params("_base_learners", deep=True)
        result.update(base_layer_params)
        meta_params = self._meta_learner.get_params(deep=True)
        for key, value in meta_params.items():
            result['%s__%s' % ("metalearner", key)] = value

        return result


class StackEnsembleClassifier(StackEnsembleBase, ClassifierMixin):
    """StackEnsembleClassifier class using 2 layers."""

    def __init__(self, base_learners, meta_learner, training_cv_folds=5):
        """
        Initialize function for StackEnsembleClassifier.

        :param base_learners:
            The collection of (name, estimator) for the base layer of the Ensemble
        :type base_learners: list
        :param meta_learner:
            The model used in the second layer of the Stack to generate the final predictions.
        :type meta_learner: Estimator / Pipeline
        :param training_cv_folds:
            The number of cross validation folds to be used during fitting of this Ensemble.
        :type training_cv_folds: int
        """
        super().__init__(base_learners, meta_learner, training_cv_folds=training_cv_folds)
        if hasattr(meta_learner, "classes_"):
            self.classes_ = meta_learner.classes_
        else:
            self.classes_ = None

    def fit(self, X: DataInputType, y: np.ndarray) -> 'StackEnsembleClassifier':
        """
        Fit function for StackEnsembleClassifier model.

        :param X: Input data.
        :param y: Input target values.
        :type y: numpy.ndarray
        :return: Returns self.
        """
        self.classes_ = np.unique(y)
        return super().fit(X, y)

    def predict_proba(self, X):
        """
        Prediction class probabilities for X from StackEnsemble model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return: Prediction probability values from StackEnsemble model.
        """
        predictions = self._get_base_learners_predictions(X)
        try:
            result = self._meta_learner.predict_proba(predictions)
        except Exception as e:
            raise PredictionException.from_exception(e, has_pii=True, target='StackEnsembleClassifier'). \
                with_generic_msg(_generic_prediction_error_message.format(self.__class__.__name__))
        # let's make sure the meta learner predictions have same number of columns as classes
        # During AutoML training, both base learners and the meta learner can potentially see less classes than
        # what the whole dataset contains, so, we rely on padding at each layer (base learners, meta learner)
        # to have a consistent view over the classes of the dataset. The classes_ attributes from base_learners
        # and meta learner are being determined during fit time based on what were trained on, while the Stack
        # Ensemble's classes_ attribute is being set based on the entire dataset which was passed to AutoML.
        if self.classes_ is not None and hasattr(self._meta_learner, "classes_"):
            result = _scoring_utilities.pad_predictions(result, self._meta_learner.classes_, self.classes_)
        return result

    def _get_cv_split_indices(self, X, y):
        result = None
        try:
            kfold = StratifiedKFold(n_splits=self._training_cv_folds)
            result = kfold.split(X, y)
        except Exception as ex:
            print("Error trying to perform StratifiedKFold split. Falling back to KFold. Exception: {}".format(ex))
            # StratifiedKFold fails when there is a single example for a given class
            # so if that happens will fallback to regular KFold
            kfold = KFold(n_splits=self._training_cv_folds)
            result = kfold.split(X, y)

        return result

    def _get_base_learner_predictions(self, model, X):
        result = model.predict_proba(X)
        # let's make sure all the predictions have same number of columns
        if self.classes_ is not None and hasattr(model, "classes_"):
            result = _scoring_utilities.pad_predictions(result, model.classes_, self.classes_)
        return result


class StackEnsembleRegressor(StackEnsembleBase, RegressorMixin):
    """StackEnsembleRegressor class using 2 layers."""

    def __init__(self, base_learners, meta_learner, training_cv_folds=5):
        """
        Initialize function for StackEnsembleRegressor.

        :param base_learners:
            The collection of (name, estimator) for the base layer of the Ensemble
        :type base_learners: list
        :param meta_learner:
            The model used in the second layer of the Stack to generate the final predictions.
        :type meta_learner: Estimator / Pipeline
        :param training_cv_folds:
            The number of cross validation folds to be used during fitting of this Ensemble.
        :type training_cv_folds: int
        """
        super().__init__(base_learners, meta_learner, training_cv_folds=training_cv_folds)

    def _get_base_learner_predictions(self, model, X):
        try:
            return model.predict(X)
        except Exception as e:
            raise PredictionException.from_exception(e, has_pii=True, target='StackEnsembleRegressor'). \
                with_generic_msg(_generic_prediction_error_message.format(self.__class__.__name__))

    def _get_cv_split_indices(self, X, y):
        kfold = KFold(n_splits=self._training_cv_folds)
        return kfold.split(X, y)


class GPUHelper(object):
    """Helper class for adding GPU support."""

    @staticmethod
    def xgboost_add_gpu_support(problem_info, xgboost_args):
        """Add GPU for XGBOOST."""
        if problem_info is not None and problem_info.gpu_training_param_dict is not None and \
                problem_info.gpu_training_param_dict.get("processing_unit_type", "cpu") == "gpu":
            if xgboost_args.get('tree_method') == 'hist':
                xgboost_args['tree_method'] = 'gpu_hist'

                # to make sure user can still use cpu machine for inference
                xgboost_args['predictor'] = 'cpu_predictor'
        return xgboost_args
