# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines scoring models for approximating feature importance values.

For more information about using scoring models, see [Interpretability during inference]
(https://docs.microsoft.com/azure/machine-learning/how-to-machine-learning-interpretability-automl#interpretability-during-inference)
"""

import joblib
import logging
import numpy as np
from scipy.sparse import issparse
import os
import warnings

from abc import ABCMeta, abstractmethod

from azureml._common._error_definition import AzureMLError
from azureml._logging import ChainedIdentity
from azureml.interpret.common.constants import LoggingNamespace, Scoring, Serialization
from azureml.interpret.mimic_wrapper import MimicWrapper
from azureml.interpret.common.exceptions import (
    DirectoryExistsException, MissingRawTransformationsException,
    InitDatasetMissingException, UnsupportedModelException)

from interpret_community._internal.raw_explain import DataMapper
from azureml.interpret.common._errors.error_definitions import (
    DirectoryAlreadyExists, InitDatasetMissing,
    MissingFeatureMapGettingRaw, ModelNotSerializable)
from interpret_community.common.constants import ShapValuesOutput
from interpret_community.common.explanation_utils import (
    _get_raw_feature_importances, _get_dense_examples,
    _fix_linear_explainer_shap_values, _scale_tree_shap)
from interpret_community.dataset.dataset_wrapper import DatasetWrapper

with warnings.catch_warnings():
    warnings.filterwarnings('ignore', 'Starting from version 2.2.1', UserWarning)
    import shap

SCORING_FILE = 'scoring_explainer.pkl'
DEPENDENCIES = 'dependencies'
DEEP_EXPLAINER = '_deep_explainer'
MODEL = '_model'
MODEL_TREE_EXPLAINER = '_tree_explainer'
SURROGATE_MODEL = 'surrogate_model'


def _transform_data(data, data_mapper=None):
    """Use mapper or transformer to convert raw data to engineered before explanation.

    :param data: The raw data to transform.
    :type data: numpy, pandas, dense, sparse data matrix
    :param data_mapper: A list of lists of generated feature indices for each raw feature.
    :type data_mapper: list[list[]]
    :return: The transformed data.
    :rtype: numpy, pandas, dense, sparse data matrix
    """
    if data_mapper is not None:
        return data_mapper.transform(data)
    return data


# Note: this method is actually publicly exposed and re-imported as a public function in the init file
def _save(scoring_explainer, directory='.', exist_ok=False):
    """Save the scoring explainer to disk.

    :param scoring_explainer: The scoring explainer object which is to be saved. The explainer will be written out to
        [directory]/scoring_explainer.pkl.
    :type name: ScoringExplainer
    :param directory: The directory under which the serialized explainer should be stored.
        If the directory doesn't exist, it will be created.
    :type directory: str
    :param exist_ok: If False (the default state), a warning will be thrown if the directory given already exists. If
        True, the current directory will be used and any overlapping contents will be overwritten.
    :type exist_ok: bool
    :return: The path to the scoring explainer pickle file.
    :rtype: str
    """
    # general check on path existence and creation
    if not os.path.exists(directory):
        os.makedirs(directory)
    elif not exist_ok:
        raise DirectoryExistsException._with_error(
            AzureMLError.create(
                DirectoryAlreadyExists, path=directory,
                target="directory"
            )
        )

    # save scoring explainer to the given directory
    outpath = os.path.join(directory, SCORING_FILE)
    with open(outpath, 'wb') as stream:
        joblib.dump(scoring_explainer, stream)

    return outpath


# Note: this method is actually publicly exposed and re-imported as a public function in the init file
def _load(directory):
    """Load the scoring explainer from disk.

    :param directory: The directory under which the serialized explainer is stored. Assumes that
        scoring_explainer.pkl is available at the top level of the directory.
    :type directory: str
    :return: The scoring explainer from an explanation, loaded from disk.
    :rtype: azureml.interpret.scoring.scoring_explainer.ScoringExplainer
    """
    with open(os.path.join(directory, SCORING_FILE), 'rb') as stream:
        scoring_explainer = joblib.load(stream)
    return scoring_explainer


def _unwrap(explainer):
    """Remove the tabular layer or mimic wrapper around a direct explainer.

    :param explainer: An explainer.
    :type explainer: interpret_community.common.base_explainer.BaseExplainer
    :return: An explainer, which will be a direct explainer if the original was a TabularExplainer or MimicWrapper.
    :rtype: interpret_community.common.base_explainer.BaseExplainer
    """
    if 'TabularExplainer' in str(type(explainer)):
        explainer = explainer.explainer
    elif 'MimicWrapper' in str(type(explainer)):
        explainer = explainer._internal_explainer
    return explainer


class ScoringExplainer(ChainedIdentity):
    """Defines a scoring model.

    If `transformations` was passed in on `original_explainer`, those transformations will be carried through to
    the scoring explainer, it will expect raw data, and by default importances will be returned for raw features.
    If `feature_maps` are passed in here (NOT intended to be used at the same time as `transformations`), the
    explainer will expect transformed data, and by default importances will be returned for transformed data. In
    either case, the output can be specified by setting `get_raw` explicitly to True or False on the explainer's
    `explain` method.

    :param original_explainer: The training time explainer originally used to explain the model.
    :type original_explainer: interpret_community.common.base_explainer.BaseExplainer
    :param feature_maps: A list of feature maps from raw to generated feature.
        The list can be numpy arrays or sparse matrices where each array entry
        (raw_index, generated_index) is the weight for each raw, generated feature pair. The other entries are set
        to zero. For a sequence of transformations [t1, t2, ..., tn] generating generated features from raw
        features, the list of feature maps correspond to the raw to generated maps in the same order as t1, t2,
        etc. If the overall raw to generated feature map from t1 to tn is available, then just that feature map
        in a single element list can be passed.
    :type feature_maps: list[numpy.ndarray] or list[scipy.sparse.csr_matrix]
    """

    __metaclass__ = ABCMeta

    def __init__(self, original_explainer, feature_maps=None, **kwargs):
        """Initialize the ScoringExplainer.

        If `transformations` was passed in on `original_explainer`, those transformations will be carried through to
        the scoring explainer, it will expect raw data, and by default importances will be returned for raw features.
        If `feature_maps` are passed in here (NOT intended to be used at the same time as `transformations`), the
        explainer will expect transformed data, and by default importances will be returned for transformed data. In
        either case, the output can be specified by setting `get_raw` explicitly to True or False on the explainer's
        `explain` method.

        :param original_explainer: The training time explainer originally used to explain the model.
        :type original_explainer: interpret_community.common.base_explainer.BaseExplainer
        :param feature_maps: A list of feature maps from raw to generated feature.
            The list can be numpy arrays or sparse matrices where each array entry
            (raw_index, generated_index) is the weight for each raw, generated feature pair. The other entries are set
            to zero. For a sequence of transformations [t1, t2, ..., tn] generating generated features from raw
            features, the list of feature maps correspond to the raw to generated maps in the same order as t1, t2,
            etc. If the overall raw to generated feature map from t1 to tn is available, then just that feature map
            in a single element list can be passed.
        :type feature_maps: list[numpy.ndarray] or list[scipy.sparse.csr_matrix]
        """
        super(ScoringExplainer, self).__init__(**kwargs)
        self._logger.debug('Initializing ScoringExplainer')

        if isinstance(original_explainer, MimicWrapper):
            original_explainer = original_explainer.explainer

        if original_explainer.transformations is not None:
            self._data_mapper = DataMapper(original_explainer.transformations)
        else:
            self._data_mapper = None
        self._feature_maps = feature_maps

        self._function = None
        # If the original was a MimicExplainer, we need custom logic to pull the model out
        if hasattr(original_explainer, Scoring.SURROGATE_MODEL):
            self._model = original_explainer.surrogate_model.model
        else:
            self._model = original_explainer.model
            if self._model is None:
                self._function = original_explainer.function
        self._features = original_explainer.features

    def fit(self, X, y=None):
        """Implement dummy method required to fit scikit-learn pipeline interface.

        :param X: Training data.
        :param y: Training targets.
        """
        return self

    @abstractmethod
    def explain(self, evaluation_examples, get_raw):
        """Use the model for scoring to approximate the feature importance values of data.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on
            which to explain the model's output.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :param get_raw: If True, importance values for raw features will be returned. If False, importance values
            for engineered features will be returned. If unspecified and `transformations` was passed into the
            original explainer, raw importance values will be returned. If unspecified and `feature_maps` was
            passed into the scoring explainer, engineered importance values will be returned.
        :type get_raw: bool
        :return: For a model with a single output such as regression,
            this method returns a matrix of feature importance values. For models with vector outputs
            this function returns a list of such matrices, one for each output. The dimension
            of this matrix is (# examples x # features).
        :rtype: list

        """
        pass

    @property
    def features(self):
        """Get the feature names passed into the original explainer.

        :return: The feature names, or None if none were given by the user.
        :rtype: list[str] or None
        """
        if self._features is not None and not isinstance(self._features, list):
            self._features = self._features.tolist()
        return self._features

    def _get_raw_importances(self, engineered_importances):
        """Convert from an explanation of engineered features to an explanation of raw features.

        :param engineered_importances: The results of calling .explain() on engineered data.
        :type engineered_importances: np.array
        :return: The importances for the raw features originally passed to the scoring explainer.
        :rtype: np.array
        """
        if self._data_mapper is not None:
            return _get_raw_feature_importances(engineered_importances, [self._data_mapper.feature_map])
        elif self._feature_maps is not None:
            return _get_raw_feature_importances(engineered_importances, self._feature_maps)
        else:
            raise MissingRawTransformationsException._with_error(
                AzureMLError.create(
                    MissingFeatureMapGettingRaw, target="engineered_importances"
                )
            )

    def predict(self, evaluation_examples):
        """Use the TreeExplainer and tree model for scoring to get the feature importance values of data.

        Wraps the .explain() function.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on
            which to explain the model's output.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :return: For a model with a single output such as regression,
            this returns a matrix of feature importance values. For models with vector outputs
            this function returns a list of such matrices, one for each output. The dimension
            of this matrix is (# examples x # features).
        :rtype: list
        """
        return self.explain(evaluation_examples)

    def __getstate__(self):
        """Influence how TreeScoringExplainer is pickled.

        Removes logger which is not serializable.

        :return state: The state to be pickled, with logger removed.
        :rtype state: dict
        """
        odict = self.__dict__.copy()
        del odict[Serialization.LOGGER]
        return odict

    def __setstate__(self, dict):
        """Influence how TreeScoringExplainer is unpickled.

        Re-adds logger which is not serializable.

        :param dict: A dictionary of deserialized state.
        :type dict: dict
        """
        self.__dict__.update(dict)
        parent = logging.getLogger(LoggingNamespace.AZUREML)
        self._logger = parent.getChild(self._identity)


class KernelScoringExplainer(ScoringExplainer):
    """Defines a scoring model based on KernelExplainer.

    If the original explainer was using a SHAP KernelExplainer and no initialization data was passed in,
    the core of the original explainer will be reused. If the original explainer used another method or new
    initialization data was passed in under `initialization_examples`, a new explainer will be created.

    If `transformations` was passed in on `original_explainer`, those transformations will be carried through to
    the scoring explainer, it will expect raw data, and by default importances will be returned for raw features.
    If `feature_maps` are passed in here (NOT intended to be used at the same time as `transformations`), the
    explainer will expected transformed data, and by default importances will be returned for transformed data. In
    either case, the output can be specified by setting `get_raw` explicitly to True or False on the explainer's
    `explain` method.

    :param original_explainer: The training time explainer originally used to explain the model.
    :type original_explainer: interpret_community.common.base_explainer.BaseExplainer
    :param initialization_examples: A matrix of feature vector examples (# examples x # features) for
        initializing the explainer.
    :type initialization_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
    """

    def __init__(self, original_explainer, initialization_examples=None, **kwargs):
        """Initialize the KernelScoringExplainer.

        If the original explainer was using a SHAP KernelExplainer and no initialization data was passed in,
        the core of the original explainer will be reused. If the original explainer used another method or new
        initialization data was passed in under initialization_examples, a new explainer will be created.

        If `transformations` was passed in on `original_explainer`, those transformations will be carried through to
        the scoring explainer, it will expect raw data, and by default importances will be returned for raw features.
        If `feature_maps` are passed in here (NOT intended to be used at the same time as `transformations`), the
        explainer will expected transformed data, and by default importances will be returned for transformed data. In
        either case, the output can be specified by setting `get_raw` explicitly to True or False on the explainer's
        `explain` method.

        :param original_explainer: The training time explainer originally used to explain the model.
        :type original_explainer: interpret_community.common.base_explainer.BaseExplainer
        :param initialization_examples: A matrix of feature vector examples (# examples x # features) for
            initializing the explainer.
        :type initialization_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        """
        super(KernelScoringExplainer, self).__init__(original_explainer, **kwargs)
        self._logger.debug('Initializing KernelScoringExplainer')
        if self._model is None:
            self._model_function = self._function
        else:
            try:
                self._model_function = self._model.predict_proba
            except Exception:
                self._model_function = self._model.predict

        original_explainer = _unwrap(original_explainer)

        self._kernel_explainer = None
        has_explainer = hasattr(original_explainer, Scoring.EXPLAINER)
        if initialization_examples is not None:
            # Create new explainer
            init_data = _transform_data(initialization_examples, data_mapper=self._data_mapper)
            self._kernel_explainer = shap.KernelExplainer(self._model_function, init_data)
        elif has_explainer and type(original_explainer.explainer) == shap.KernelExplainer:
            # Reuse core of original explainer
            self._kernel_explainer = original_explainer.explainer
        else:
            raise InitDatasetMissingException._with_error(
                AzureMLError.create(
                    InitDatasetMissing, target="initialization_examples"
                )
            )
        self._method = 'scoring.kernel'

    def explain(self, evaluation_examples, get_raw=None):
        """Use the TreeExplainer and tree model for scoring to get the feature importance values of data.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on
            which to explain the model's output.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :param get_raw: If True, importance values for raw features will be returned. If False, importance values
            for engineered features will be returned. If unspecified and `transformations` was passed into the
            original explainer, raw importance values will be returned. If unspecified and `feature_maps` was
            passed into the scoring explainer, engineered importance values will be returned.
        :type get_raw: bool
        :return: For a model with a single output such as regression,
            this method returns a matrix of feature importance values. For models with vector outputs
            this function returns a list of such matrices, one for each output. The dimension
            of this matrix is (# examples x # features).
        :rtype: list
        """
        # convert raw data to engineered before explaining
        data = _transform_data(evaluation_examples, data_mapper=self._data_mapper)

        values = self._kernel_explainer.shap_values(data)
        if get_raw or (get_raw is None and self._data_mapper is not None):
            values = np.array(values) if isinstance(values, list) else values
            return self._get_raw_importances(values).tolist()

        if not isinstance(values, list):
            values = values.tolist()
        # current slight hack for inconsistent shap deep explainer return type (list of numpy arrays)
        for i in range(len(values)):
            if not isinstance(values[i], list):
                values[i] = values[i].tolist()
        return values


class DeepScoringExplainer(ScoringExplainer):
    """Defines a scoring model based on DeepExplainer.

    If the original explainer was using a SHAP DeepExplainer and no initialization data was passed in,
    the core of the original explainer will be reused. If the original explainer used another method or new
    initialization data was passed in under `initialization_examples`, a new explainer will be created.

    If `transformations` was passed in on `original_explainer`, those transformations will be carried through to
    the scoring explainer, it will expect raw data, and by default importances will be returned for raw features.
    If `feature_maps` are passed in here (NOT intended to be used at the same time as `transformations`), the
    explainer will expected transformed data, and by default importances will be returned for transformed data. In
    either case, the output can be specified by setting `get_raw` explicitly to True or False on the explainer's
    `explain` method.

    :param original_explainer: The training time deep explainer originally used to explain the model.
    :type original_explainer: interpret_community.common.base_explainer.BaseExplainer
    :param initialization_examples: A matrix of feature vector examples (# examples x # features) for
        initializing the explainer.
    :type initialization_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
    :param serializer: Picklable custom serializer with save and load methods defined for model
        that is not serializable. The save method returns a dictionary state and load method returns the model.
    :type serializer: object
    """

    def __init__(self, original_explainer, initialization_examples=None, serializer=None, **kwargs):
        """Initialize the DeepScoringExplainer.

        If the original explainer was using a SHAP DeepExplainer and no initialization data was passed in,
        the core of the original explainer will be reused. If the original explainer used another method or new
        initialization data was passed in under `initialization_examples`, a new explainer will be created.

        If `transformations` was passed in on `original_explainer`, those transformations will be carried through to
        the scoring explainer, it will expect raw data, and by default importances will be returned for raw features.
        If `feature_maps` are passed in here (NOT intended to be used at the same time as `transformations`), the
        explainer will expected transformed data, and by default importances will be returned for transformed data. In
        either case, the output can be specified by setting `get_raw` explicitly to True or False on the explainer's
        `explain` method.

        :param original_explainer: The training time deep explainer originally used to explain the model.
        :type original_explainer: interpret_community.common.base_explainer.BaseExplainer
        :param initialization_examples: A matrix of feature vector examples (# examples x # features) for
            initializing the explainer.
        :type initialization_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :param serializer: Picklable custom serializer with save and load methods defined for model
            that is not serializable.
        :type serializer: object with save method that returns a dictionary state and load method that
            returns the model.
        """
        super(DeepScoringExplainer, self).__init__(original_explainer,
                                                   **kwargs)
        self._logger.debug('Initializing DeepScoringExplainer')

        original_explainer = _unwrap(original_explainer)

        self._deep_explainer = None
        self._serializer = serializer
        has_explainer = hasattr(original_explainer, Scoring.EXPLAINER)
        if initialization_examples is not None:
            # Create new explainer
            init_data = _transform_data(initialization_examples, data_mapper=self._data_mapper)
            self._deep_explainer = shap.DeepExplainer(self._model, init_data)
            self._initialization_examples = init_data
        elif has_explainer and type(original_explainer.explainer) == shap.DeepExplainer:
            # Reuse core of original explainer
            self._deep_explainer = original_explainer.explainer
            self._initialization_examples = original_explainer.initialization_examples
            if isinstance(self._initialization_examples, DatasetWrapper):
                self._initialization_examples = self._initialization_examples.dataset
        else:
            raise InitDatasetMissingException._with_error(
                AzureMLError.create(
                    InitDatasetMissing, target="initialization_examples"
                )
            )
        self._method = 'scoring.deep'

    def explain(self, evaluation_examples, get_raw=None):
        """Use the DeepExplainer and deep model for scoring to get the feature importance values of data.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on
            which to explain the model's output.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :param get_raw: If True, importance values for raw features will be returned. If False, importance values
            for engineered features will be returned. If unspecified and `transformations` was passed into the
            original explainer, raw importances will be returned. If unspecified and `feature_maps` was passed
            into the scoring explainer, engineered importance values will be returned.
        :type get_raw: bool
        :return: For a model with a single output such as regression,
            this returns a matrix of feature importance values. For models with vector outputs
            this function returns a list of such matrices, one for each output. The dimension
            of this matrix is (# examples x # features).
        :rtype: list
        """
        # convert raw data to engineered before explaining
        data = _transform_data(evaluation_examples, data_mapper=self._data_mapper)

        values = self._deep_explainer.shap_values(data)
        if get_raw or (get_raw is None and self._data_mapper is not None):
            values = np.array(values) if isinstance(values, list) else values
            return self._get_raw_importances(values).tolist()
        if not isinstance(values, list):
            values = values.tolist()
        # current slight hack for inconsistent shap deep explainer return type (list of numpy arrays)
        for i in range(len(values)):
            if not isinstance(values[i], list):
                values[i] = values[i].tolist()
        return values

    def __getstate__(self):
        """Influence how DeepScoringExplainer is pickled.

        Removes logger which is not serializable.
        Performs a custom serialization of TensorFlow Keras models to string using the Keras API.
        Removes DeepExplainer local variable to recreate it on deserialization.

        :return state: The state to be pickled, with logger removed.
        :rtype state: dict
        """
        state = super(DeepScoringExplainer, self).__getstate__()
        if self._serializer is not None:
            state.update(self._serializer.save(self._model))
            del state[MODEL]
        elif not (hasattr(self._model, '__setstate__') and hasattr(self._model, '__getstate__')):
            raise UnsupportedModelException._with_error(AzureMLError.create(ModelNotSerializable))
        del state[DEEP_EXPLAINER]
        return state

    def __setstate__(self, dict):
        """Influence how DeepScoringExplainer is unpickled.

        Re-adds logger which is not serializable.
        Deserializes TensorFlow Keras models from string using the Keras API.
        Re-initializes the DeepExplainer.

        :param dict: A dictionary of deserialized state.
        :type dict: dict
        """
        super(DeepScoringExplainer, self).__setstate__(dict)
        if self._serializer is not None:
            self._model = self._serializer.load(dict)
        # Note: Assume model was deserialized correctly
        # Rehydrate deep explainer here from the model
        self._deep_explainer = shap.DeepExplainer(self._model, self._initialization_examples)


class TreeScoringExplainer(ScoringExplainer):
    """Defines a scoring model based on TreeExplainer.

    If the original explainer was using a SHAP TreeExplainer, the core of the original explainer will be reused.
    If the original explainer used another method, a new explainer will be created.

    If `transformations` was passed in on `original_explainer`, those transformations will be carried through to
    the scoring explainer, it will expect raw data, and by default importances will be returned for raw features.
    If `feature_maps` are passed in here (NOT intended to be used at the same time as `transformations`), the
    explainer will expected transformed data, and by default importances will be returned for transformed data. In
    either case, the output can be specified by setting `get_raw` explicitly to True or False on the explainer's
    `explain` method.

    :param original_explainer: The training time tree explainer originally used to explain the model.
    :type original_explainer: interpret_community.common.base_explainer.BaseExplainer
    """

    def __init__(self, original_explainer, **kwargs):
        """Initialize the TreeScoringExplainer.

        If the original explainer was using a SHAP TreeExplainer, the core of the original explainer will be reused.
        If the original explainer used another method, a new explainer will be created.

        If `transformations` was passed in on `original_explainer`, those transformations will be carried through to
        the scoring explainer, it will expect raw data, and by default importances will be returned for raw features.
        If `feature_maps` are passed in here (NOT intended to be used at the same time as `transformations`), the
        explainer will expected transformed data, and by default importances will be returned for transformed data. In
        either case, the output can be specified by setting `get_raw` explicitly to True or False on the explainer's
        `explain` method.

        :param original_explainer: The training time tree explainer originally used to explain the model.
        :type original_explainer: interpret_community.common.base_explainer.BaseExplainer
        """
        super(TreeScoringExplainer, self).__init__(original_explainer, **kwargs)
        self._logger.debug('Initializing TreeScoringExplainer')

        original_explainer = _unwrap(original_explainer)

        has_explainer = hasattr(original_explainer, Scoring.EXPLAINER)
        self._shap_values_output = original_explainer._shap_values_output
        if has_explainer and type(original_explainer.explainer) == shap.TreeExplainer:
            # Reuse core of original explainer
            self._tree_explainer = original_explainer.explainer
        else:
            # check for existing explainer on model
            has_model_explainer = (hasattr(original_explainer, SURROGATE_MODEL) and
                                   hasattr(original_explainer.surrogate_model, MODEL_TREE_EXPLAINER))
            if has_model_explainer:
                original_explainer.surrogate_model._init_tree_explainer()
                self._tree_explainer = original_explainer.surrogate_model._tree_explainer
            else:
                # Create new explainer
                self._tree_explainer = shap.TreeExplainer(self._model)

        # Only lightgbm and xgboost models don't directly fail with sparse data currently
        model_type_str = str(type(self._model))
        self._convert_to_dense = not ("xgboost" in model_type_str or "lightgbm" in model_type_str)
        self._method = 'scoring.tree'

    def explain(self, evaluation_examples, get_raw=None):
        """Use the TreeExplainer and tree model for scoring to get the feature importance values of data.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on
            which to explain the model's output.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :param get_raw: If True, importance values for raw features will be returned. If False, importance values
            for engineered features will be returned. If unspecified and `transformations` was passed into the
            original explainer, raw importance values will be returned. If unspecified and `feature_maps` was
            passed into the scoring explainer, engineered importances will be returned. If unspecified and neither
            is passed, explanations will be given for the data as it was passed in.
        :type get_raw: bool
        :return: For a model with a single output such as regression,
            this returns a matrix of feature importance values. For models with vector outputs
            this function returns a list of such matrices, one for each output. The dimension
            of this matrix is (# examples x # features).
        :rtype: list
        """
        if self._convert_to_dense:
            evaluation_examples = _get_dense_examples(evaluation_examples)

        # convert raw data to engineered before explaining
        data = _transform_data(evaluation_examples, data_mapper=self._data_mapper)

        values = self._tree_explainer.shap_values(data)
        classification = isinstance(values, list)
        expected_values = self._tree_explainer.expected_value
        if str(type(self._model)).endswith("XGBClassifier'>") and not classification:
            # workaround for XGBoost binary classifier output from SHAP
            classification = True
            values = [-values, values]
            expected_values = np.array((-expected_values, expected_values))
        if classification and self._shap_values_output == ShapValuesOutput.PROBABILITY:
            values = _scale_tree_shap(values, expected_values, self._model.predict_proba(data))
        if get_raw or (get_raw is None and self._data_mapper is not None):
            values = np.array(values) if isinstance(values, list) else values
            return self._get_raw_importances(values).tolist()
        if not isinstance(values, list) and not issparse(values):
            values = values.tolist()
        return values


class LinearScoringExplainer(ScoringExplainer):
    """Defines a scoring model based on LinearExplainer.

    If the original explainer was using a SHAP LinearExplainer and no initialization data was passed in,
    the core of the original explainer will be reused. If the original explainer used another method or new
    initialization data was passed in under `initialization_examples`, a new explainer will be created.

    If `transformations` was passed in on `original_explainer`, those transformations will be carried through to
    the scoring explainer, it will expect raw data, and by default importances will be returned for raw features.
    If `feature_maps` are passed in here (NOT intended to be used at the same time as `transformations`), the
    explainer will expected transformed data, and by default importances will be returned for transformed data. In
    either case, the output can be specified by setting `get_raw` explicitly to True or False on the explainer's
    `explain` method.

    :param original_explainer: The training time explainer originally used to explain the linear model.
    :type original_explainer: interpret_community.common.base_explainer.BaseExplainer
    :param initialization_examples: A matrix of feature vector examples (# examples x # features) for
        initializing the explainer.
    :type initialization_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
    """

    def __init__(self, original_explainer, initialization_examples=None, **kwargs):
        """Initialize the LinearScoringExplainer.

        If the original explainer was using a SHAP LinearExplainer and no initialization data was passed in,
        the core of the original explainer will be reused. If the original explainer used another method or new
        initialization data was passed in under `initialization_examples`, a new explainer will be created.

        If `transformations` was passed in on `original_explainer`, those transformations will be carried through to
        the scoring explainer, it will expect raw data, and by default importances will be returned for raw features.
        If `feature_maps` are passed in here (NOT intended to be used at the same time as `transformations`), the
        explainer will expected transformed data, and by default importances will be returned for transformed data. In
        either case, the output can be specified by setting `get_raw` explicitly to True or False on the explainer's
        `explain` method.

        :param original_explainer: The training time explainer originally used to explain the linear model.
        :type original_explainer: interpret_community.common.base_explainer.BaseExplainer
        :param initialization_examples: A matrix of feature vector examples (# examples x # features) for
            initializing the explainer.
        :type initialization_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        """
        super(LinearScoringExplainer, self).__init__(original_explainer, **kwargs)
        self._logger.debug('Initializing LinearScoringExplainer')
        original_explainer = _unwrap(original_explainer)

        has_explainer = hasattr(original_explainer, Scoring.EXPLAINER)
        if initialization_examples is not None:
            # Create new explainer
            init_data = _transform_data(initialization_examples, data_mapper=self._data_mapper)
            self._linear_explainer = shap.LinearExplainer(self._model, init_data)
        elif has_explainer and type(original_explainer.explainer) == shap.LinearExplainer:
            # Reuse core of original explainer
            self._linear_explainer = original_explainer.explainer
        else:
            raise InitDatasetMissingException._with_error(
                AzureMLError.create(
                    InitDatasetMissing, target="initialization_examples"
                )
            )
        self._method = 'scoring.linear'

    def explain(self, evaluation_examples, get_raw=None):
        """Use the LinearExplainer for scoring to get the feature importance values of data.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on
            which to explain the model's output.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :param get_raw: If True, importance values for raw features will be returned. If False, importance values
            for engineered features will be returned. If unspecified and `transformations` was passed into the
            original explainer, raw importance values will be returned. If unspecified and `feature_maps` was
            passed into the scoring explainer, engineered importances will be returned.
        :type get_raw: bool
        :return: For a model with a single output such as regression,
            this returns a matrix of feature importance values. For models with vector outputs
            this function returns a list of such matrices, one for each output. The dimension
            of this matrix is (# examples x # features).
        :rtype: list
        """
        data = evaluation_examples

        # convert raw data to engineered before explaining
        data = _transform_data(evaluation_examples, data_mapper=self._data_mapper)

        values = self._linear_explainer.shap_values(data)
        # Temporary fix for a bug in shap for regression models
        values = _fix_linear_explainer_shap_values(self._model, values)
        values = np.array(values)
        if get_raw or (get_raw is None and self._data_mapper is not None):
            return self._get_raw_importances(values).tolist()
        if not isinstance(values, list):
            values = values.tolist()
        return values
