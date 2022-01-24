# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Objects that can be instantiated into model objects.

Used for generic serialization and deserialization for models,
which can be used for communication purposes.
"""

import copy
import importlib
import inspect
import json
import logging
import os
import pickle
from typing import Any, Dict, List, Optional, Type, Union, Tuple

import nimbusml as nml
import numpy as np
from sklearn import linear_model, pipeline, preprocessing

from azureml._common._error_definition.azureml_error import AzureMLError
from azureml.automl.core.shared import constants
from azureml.automl.core.shared._diagnostics.automl_error_definitions import ModelNotSupported
from azureml.automl.core.shared.logging_utilities import log_traceback
from azureml.automl.core.shared.exceptions import ClientException,\
    ConfigException
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.runtime.shared import model_wrappers, tf_wrappers
from azureml.automl.runtime.shared.nimbus_wrappers import AveragedPerceptronBinaryClassifier, \
    AveragedPerceptronMulticlassClassifier, NimbusMlClassifierMixin, NimbusMlRegressorMixin
from azureml.automl.runtime.shared.problem_info import ProblemInfo


logger = logging.getLogger(__name__)


PREPROC_NAME = 'preproc'
SKLEARN_NAME = 'sklearn'
TF_NAME = 'tf'
YTRANS_NAME = 'y_transformer'
ENSEMBLE_NAME = 'ensemble'
SDK_ENSEMBLE_NAME = "sdk_ensemble"
NIMBUSML_NAME = 'nimbusml'
TIMESERIES_NAME = 'timeseries'
SK_PIPELINE_TYPE = SKLEARN_NAME
NIMBUSML_PIPELINE_TYPE = NIMBUSML_NAME

COMMON_MODULE = "automl.client.core.common"
RUNTIME_MODULE = "automl.client.core.runtime"
COMMON_TRAIN_MODULE = "azureml.train.automl"
RUNTIME_TRAIN_MODULE = "azureml.train.automl.runtime"
WRAPPERS_MODULE = 'automl.client.core.runtime.model_wrappers'
SK_PIPELINE_MODULE = "sklearn.pipeline"
SK_PIPELINE_CLASS_NAME = "Pipeline"
NIMBUSML_PIPELINE_MODULE = "nimbusml.pipeline"
NIMBUSML_PIPELINE_CLASS_NAME = "Pipeline"
FORECASTING_MODELS = 'automl.client.core.runtime.forecasting_models'
ARIMA_MODEL = 'automl.client.core.runtime._auto_arima'
PROPHET_MODEL = 'automl.client.core.runtime._prophet_model'
PROPHET_MODEL_NAME = 'ProphetModel'
EXPOSMOOTHING_MODEL = 'automl.client.core.runtime._exponential_smoothing'
EXPOSMOOTHING_MODEL_NAME = 'ExponentialSmoothing'


class ObjectSpec:
    """Metaobject for serialization and deserialization."""

    def __init__(self, spec_class, module, class_name,
                 *param_args, **param_kwargs):
        """Create an ObjectSpec."""
        self.spec_class = spec_class
        self.module = module
        self.class_name = class_name
        self.param_args = param_args
        self.param_kwargs = param_kwargs
        self.prepared_kwargs = {}   # type: Dict[str, Any]

    @classmethod
    def from_dict(cls: Type['ObjectSpec'], d: Dict[str, Any]) -> 'ObjectSpec':
        """Deserialize an ObjectSpec from a dictionary.

        :param cls: the class of the object to create
        :param d: the dictionary to deserialize
        :return: ObjectSpec for the dictionary
        """
        ret = cls.__new__(cls)  # type: ObjectSpec
        ret.__dict__ = copy.deepcopy(d)
        return ret

    def to_dict(self):
        """Serialize an ObjectSpec to a dictionary.

        :return: the dictionary of ObjectSpec attributes
        """
        self.prepared_kwargs = {}
        d = copy.deepcopy(self.__dict__)
        return d

    def supports_constrained_fit(self):
        """
        Check if ObjectSpec supports constrained fit.

        Returns whether the pipeline step can stop given a time constraint
        Returns false for the ObjectSpec parent class
        """
        return False

    def prepare_kwargs(self, cls, problem_info,
                       random_state=None, num_threads=1,
                       dataset_metadata=None):
        """Set self.prepared_kwargs, a modified copy of param_kwargs."""
        raise NotImplementedError()

    def instantiate(self, problem_info, random_state=None, num_threads=1, dataset_metadata=None):
        """Create a new object with additional parameters.

        :param problem_info:
        :param random_state:
        :param num_threads:
        :param dataset_metadata:
        :return: a new object from the module and class from the constructor
        :raises: ConfigException
        """
        self.module = self.module.replace(COMMON_MODULE, RUNTIME_MODULE)
        if RUNTIME_TRAIN_MODULE not in self.module:
            self.module = self.module.replace(COMMON_TRAIN_MODULE, RUNTIME_TRAIN_MODULE)
        # Todo: Remove this and modify Miro to send wrapper module for tabnet
        if self.module == "tabularnetworks.trainer":
            self.module = WRAPPERS_MODULE
        mod = importlib.import_module(self.module)
        try:
            cls = getattr(mod, self.class_name)
        except AttributeError as e:
            log_traceback(e, logger)
            raise ConfigException._with_error(
                AzureMLError.create(
                    ModelNotSupported, target="model", model_name=self.class_name,
                    reference_code=ReferenceCodes._MODEL_NOT_SUPPORTED
                )
            )

        self.prepare_kwargs(cls, problem_info, random_state=random_state,
                            num_threads=num_threads, dataset_metadata=dataset_metadata)

        return cls(*self.param_args, **self.prepared_kwargs)


class PreprocessorObject(ObjectSpec):
    """Serializable pipeline preprocessing step."""

    def __init__(self, *args, **kwargs):
        """Create a PreprocessorObject."""
        super(PreprocessorObject, self).__init__(
            PREPROC_NAME, *args, **kwargs)

    def prepare_kwargs(self, cls, problem_info,
                       random_state=None, num_threads=1, dataset_metadata=None):
        """Save parameters to be serialized.

        :param problem_info:
        :param random_state:
        :param num_threads:
        :param dataset_metadata:
        """
        self.prepared_kwargs = copy.deepcopy(self.param_kwargs)


class SklearnObject(ObjectSpec):
    """Serializable pipeline model step."""

    def __init__(self, *args, **kwargs):
        """Create a SklearnObject."""
        super(SklearnObject, self).__init__(SKLEARN_NAME, *args, **kwargs)

    def prepare_kwargs(self, cls, problem_info,
                       random_state=None, num_threads=1, dataset_metadata=None):
        """Set self.prepared_kwargs, a modified copy of param_kwargs."""
        self.prepared_kwargs = copy.deepcopy(self.param_kwargs)
        argspec = inspect.getfullargspec(cls)
        if argspec.args:
            if 'random_state' in argspec.args:
                self.prepared_kwargs['random_state'] = random_state

            if 'n_jobs' in argspec.args:
                self.prepared_kwargs['n_jobs'] = num_threads

            if 'problem_info' in argspec.args:
                self.prepared_kwargs['problem_info'] = problem_info

            # n_iter was deprecated from sklearn 0.19 onward and removed in sklearn 0.21
            # this code will handle the value and move it to max_iter as needed
            if 'n_iter' not in argspec.args and 'n_iter' in self.prepared_kwargs:
                self.prepared_kwargs['max_iter'] = self.prepared_kwargs['n_iter']
                del self.prepared_kwargs['n_iter']


class NimbusMLObject(ObjectSpec):
    """Serializable NimbusML pipeline model step."""

    def __init__(self, *args, **kwargs):
        """Create a NimbusMLObject."""
        super(NimbusMLObject, self).__init__(NIMBUSML_NAME, *args, **kwargs)

    def prepare_kwargs(self, cls, problem_info,
                       random_state=None, num_threads=1, dataset_metadata=None):
        """Set self.prepared_kwargs, a modified copy of param_kwargs."""
        self.prepared_kwargs = copy.deepcopy(self.param_kwargs)
        if problem_info.enable_streaming and (
                issubclass(cls, NimbusMlClassifierMixin) or issubclass(cls, NimbusMlRegressorMixin)):
            if problem_info.feature_column_names is not None:
                self.prepared_kwargs['feature'] = problem_info.feature_column_names
            if problem_info.label_column_name is not None:
                self.prepared_kwargs['label'] = problem_info.label_column_name
            if problem_info.weight_column_name is not None:
                self.prepared_kwargs['weight'] = problem_info.weight_column_name
            self.prepared_kwargs['caching'] = 'None'

        if (issubclass(cls, AveragedPerceptronBinaryClassifier)
                or issubclass(cls, AveragedPerceptronMulticlassClassifier)):
            # map legacy hyperparameter names (from an old version of nimbusml) to updated hyperparameter names
            # (in newest version of nimbusml)
            hyperparam_names_old_to_new = {
                'init_wts_diameter': 'initial_weights_diameter',
                'l2_regularizer_weight': 'l2_regularization',
                'num_iterations': 'number_of_iterations'
            }
            for old_name, new_name in hyperparam_names_old_to_new.items():
                if old_name in self.prepared_kwargs:
                    self.prepared_kwargs[new_name] = self.prepared_kwargs.pop(old_name)

    def instantiate(self, problem_info, random_state=None, num_threads=1, dataset_metadata=None):
        """Create a new object with additional parameters.

        :param problem_info:
        :param random_state:
        :param num_threads:
        :param dataset_metadata:
        :return: a new object from the module and class from the constructor
        """
        return super().instantiate(problem_info, random_state=random_state, dataset_metadata=dataset_metadata)


class TFObject(ObjectSpec):
    """TF Object."""

    def __init__(self, *args, **kwargs):
        """Create a TFOBject."""
        super(TFObject, self).__init__(TF_NAME, *args, **kwargs)

    def prepare_kwargs(self, cls, problem_info,
                       random_state=None, num_threads=1,
                       dataset_metadata=None):
        """Set self.prepared_kwargs, a modified copy of param_kwargs."""
        self.prepared_kwargs = copy.deepcopy(self.param_kwargs)

        if random_state is not None:
            self.prepared_kwargs['seed'] = random_state

        if 'optimizer' in self.prepared_kwargs:
            opt_name = self.prepared_kwargs.pop('optimizer')
            if opt_name not in tf_wrappers.OPTIMIZERS:
                err_msg = 'Optimizer {0} not known for TFObject.'
                raise ClientException(err_msg.format(opt_name)).with_generic_msg(err_msg.format("['MASKED']"))

            if 'learning_rate' not in self.prepared_kwargs:
                raise ClientException('Optimizer requires learning rate.', has_pii=False)

            if opt_name == 'momentum':
                opt = tf_wrappers.OPTIMIZERS[opt_name](
                    self.prepared_kwargs.pop('learning_rate'),
                    self.prepared_kwargs['momentum'])
            else:
                opt = tf_wrappers.OPTIMIZERS[opt_name](
                    self.prepared_kwargs.pop('learning_rate'))
            self.prepared_kwargs['optimizer'] = opt

            if 'momentum' in self.prepared_kwargs:
                self.prepared_kwargs.pop('momentum')

        self.prepared_kwargs['max_time'] = problem_info.get_time_constraint()

        if 'activation_fn' in self.prepared_kwargs:
            if (self.prepared_kwargs['activation_fn'] not in
                    tf_wrappers.ACTIVATION_FNS):
                err_msg = 'Unknown activation function for TFObject: {}'
                raise ClientException(err_msg.format(self.prepared_kwargs['activation_fn']))\
                    .with_generic_msg(err_msg.format("['MASKED']"))
            self.prepared_kwargs['activation_fn'] = tf_wrappers.ACTIVATION_FNS[
                self.prepared_kwargs['activation_fn']]
        if problem_info.task == constants.Tasks.CLASSIFICATION:
            self.prepared_kwargs['n_classes'] = problem_info.dataset_classes

    def supports_constrained_fit(self):
        """Check if model supports constrained fit."""
        return True


class EnsembleObject(ObjectSpec):
    """The Ensemble Object."""

    MODEL_KEY = 'models'
    CLF_KEY = 'clf'
    WEIGHTS_KEY = 'weights'
    LGBM_KEY = 'lgbm'
    LGBM_FILE = 'lgbm.pkl'

    def __init__(self, task=constants.Tasks.CLASSIFICATION, **kwargs):
        """Create and ensemble object."""
        self.task = task
        super(EnsembleObject, self).__init__(
            ENSEMBLE_NAME, WRAPPERS_MODULE, 'EnsembleWrapper', **kwargs)

    @staticmethod
    def model_to_json(model):
        """Convert a model object to JSON."""
        # TODO refactor ensembles
        data = {}
        data['init_params'] = model.get_params()
        data['model_params'] = mp = {}
        for p in [key for key in model.__dict__ if (
                key[-1] == '_'
                and 'path' not in key
                and key not in ['Cs_', 'alphas_', 'scores_'])]:
            try:
                mp[p] = getattr(model, p).tolist()
            except Exception:
                mp[p] = getattr(model, p)
        return json.dumps(data)

    @staticmethod
    def elastic_net_from_json(jstring):
        """Create a elasticnet regresion object from JSON."""
        data = json.loads(jstring)
        model = linear_model.ElasticNetCV(**data['init_params'])
        for name, p in data['model_params'].items():
            setattr(model, name, np.array(p))
        return model

    @staticmethod
    def logistic_regression_from_json(jstring):
        """Create a logistic regression object from JSON."""
        data = json.loads(jstring)
        model = linear_model.LogisticRegressionCV(**data['init_params'])
        for name, p in data['model_params'].items():
            setattr(model, name, np.array(p))
        return model

    @staticmethod
    def _lgbm_to_tmp(model):
        with open(os.path.join(os.getcwd(), EnsembleObject.LGBM_FILE), 'wb') as f:
            pickle.dump(model, f)
        return EnsembleObject.LGBM_KEY

    @staticmethod
    def _lgbm_from_tmp():
        with open(os.path.join(os.getcwd(), EnsembleObject.LGBM_FILE), 'rb') as f:
            model = pickle.load(f)
        return model

    def prepare_kwargs(self, cls, problem_info,
                       random_state=None, num_threads=1,
                       dataset_metadata=None):
        """Set self.prepared_kwargs, a modified copy of param_kwargs."""
        self.prepared_kwargs = copy.deepcopy(self.param_kwargs)
        # Turn object dicts into specs so they get passed to wrapper
        # as instantiated objects.
        self.prepared_kwargs[EnsembleObject.MODEL_KEY] = [
            PipelineSpec.from_dict(
                obj_dict).instantiate_pipeline_spec(
                    problem_info, random_state=random_state)
            for obj_dict in self.param_kwargs[EnsembleObject.MODEL_KEY]]
        if EnsembleObject.CLF_KEY in self.prepared_kwargs:
            if (self.prepared_kwargs[EnsembleObject.CLF_KEY
                                     ] != EnsembleObject.LGBM_KEY):
                if self.task == constants.Tasks.CLASSIFICATION:
                    self.prepared_kwargs[EnsembleObject.CLF_KEY] = (
                        EnsembleObject.logistic_regression_from_json(
                            self.prepared_kwargs[EnsembleObject.CLF_KEY]))
                elif self.task == constants.Tasks.REGRESSION:
                    self.prepared_kwargs[EnsembleObject.CLF_KEY] = (
                        EnsembleObject.elastic_net_from_json(
                            self.prepared_kwargs[EnsembleObject.CLF_KEY]))
            else:
                self.prepared_kwargs[EnsembleObject.CLF_KEY] = (
                    EnsembleObject._lgbm_from_tmp())

    def instantiate(self, problem_info, random_state=None, num_threads=1, dataset_metadata=None):
        """Create a new object with additional parameters.

        :param problem_info:
        :param random_state:
        :param num_threads:
        :param dataset_metadata:
        :return: a new object from the module and class from the constructor
        """
        self.module = self.module.replace(COMMON_MODULE, RUNTIME_MODULE)
        if RUNTIME_TRAIN_MODULE not in self.module:
            self.module = self.module.replace(COMMON_TRAIN_MODULE, RUNTIME_TRAIN_MODULE)
        mod = importlib.import_module(self.module)
        cls = getattr(mod, self.class_name)

        self.prepare_kwargs(cls, problem_info, random_state=random_state,
                            num_threads=num_threads, dataset_metadata=None)

        # only difference between this and inherited function is that this includes task
        return cls(*self.param_args, task=self.task, **self.prepared_kwargs)


class SdkEnsembleObject(ObjectSpec):
    """The object spec representing an Ensemble created through the SDK."""

    def __init__(self, *args, **kwargs):
        """Create an ensemble object for using it through AutoML SDK."""
        super(SdkEnsembleObject, self).__init__(
            SDK_ENSEMBLE_NAME,
            *args,
            **kwargs)

    def prepare_kwargs(self, cls, problem_info,
                       random_state=None, num_threads=1, dataset_metadata=None):
        """Set self.prepared_kwargs, a modified copy of param_kwargs."""
        self.prepared_kwargs = copy.deepcopy(self.param_kwargs)
        argspec = inspect.getfullargspec(cls)
        if argspec.args:
            if 'random_state' in argspec.args:
                self.prepared_kwargs['random_state'] = random_state

            if 'n_jobs' in argspec.args:
                self.prepared_kwargs['n_jobs'] = num_threads


class TimeseriesObject(ObjectSpec):
    """Pipeline object for timeseries."""

    def __init__(self, *args, **kwargs):
        """Create a TimeseriesObject object."""
        super(TimeseriesObject, self).__init__(
            TIMESERIES_NAME,
            *args,
            **kwargs)

    def prepare_kwargs(self, cls, problem_info, random_state=None, num_threads=1, dataset_metadata=None):
        """Set self.prepared_kwargs, a modified copy of param_kwargs."""
        self.prepared_kwargs = copy.deepcopy(self.param_kwargs)
        self.prepared_kwargs[constants.TimeSeriesInternal.TIMESERIES_PARAM_DICT] = problem_info.timeseries_param_dict


class PipelineSpec:
    """Serializable pipeline."""

    CLASS_MAP = {
        PREPROC_NAME: PreprocessorObject,
        SKLEARN_NAME: SklearnObject,
        TF_NAME: TFObject,
        YTRANS_NAME: PreprocessorObject,
        ENSEMBLE_NAME: EnsembleObject,
        SDK_ENSEMBLE_NAME: SdkEnsembleObject,
        NIMBUSML_NAME: NimbusMLObject,
        TIMESERIES_NAME: TimeseriesObject
    }   # type: Dict[str, Type[ObjectSpec]]

    def __init__(self, objects, pid, module=SK_PIPELINE_MODULE, class_name=SK_PIPELINE_CLASS_NAME):
        """Create a PipelineSpec.

        :param objects: a list of ObjectSpecs
        :param pid: the pipeline ID
        :param type: the type of Pipeline (SKLearn or Nimbus or something else.)
        """
        self.objects = objects
        self.pipeline_id = pid
        # Model namespaces migrated to RUNTIME_MODULE
        self.module = module.replace(COMMON_MODULE, RUNTIME_MODULE)
        if RUNTIME_TRAIN_MODULE not in self.module:
            self.module = module.replace(COMMON_TRAIN_MODULE, RUNTIME_TRAIN_MODULE)
        self.class_name = class_name
        self.pipeline_name = self.summary()

    @staticmethod
    def from_dict(d: Dict[Any, Any]) -> 'PipelineSpec':
        """Deserializes a PipelineSpec from a dictionary.

        :param d: the dictionary to deserialize
        :return: the PipelineSpec created from d
        """
        objs = [PipelineSpec.CLASS_MAP[o['spec_class']].from_dict(o)
                for o in d['objects']]
        module = d.get('module', SK_PIPELINE_MODULE)
        class_name = d.get('class_name', SK_PIPELINE_CLASS_NAME)
        ret = PipelineSpec(objs, d['pipeline_id'], module=module, class_name=class_name)

        return ret

    def to_dict(self) -> Dict[Any, Any]:
        """Serialize a PipelineSpec to a dictionary.

        :return: the dictionary containing the steps of the pipeline serialized
            as dictionaries
        """
        d = copy.deepcopy(self.__dict__)
        d['objects'] = [o.to_dict() for o in self.objects]
        return d

    def class_strings(self) -> List[str]:
        """Return a list of class names for each step in the pipeline."""
        return [o.class_name for o in self.objects]

    def summary(self) -> str:
        """Return a string representation of the pipeline (via class names)."""
        return '{ ' + ', '.join(self.class_strings()) + ' }'

    def supports_constrained_fit(self) -> bool:
        """Indicate if the model can stop itself according to time constraint.

        Currently implemented as an any(), which is just a
        concise way to find the model object.
        """
        return any([o.supports_constrained_fit() for o in self.objects])

    def instantiate_pipeline_spec(self,
                                  problem_info: ProblemInfo,
                                  random_state: Optional[int] = None,
                                  is_sparse: bool = False,
                                  preprocess_pipelines: Optional[List[Tuple[str, Any]]] = None,
                                  dataset_metadata: Optional[Any] = None) ->\
            Union[pipeline.Pipeline, 'nml.Pipeline']:
        """Create a new PipelineSpec given extra parameters.

        :param problem_info:
        :param random_state:
        :param is_sparse:
        :param preprocess_pipelines: Any optional preprocessing pipelines that should be prepended to the pipeline
        :return: a new PipelineSpec
        """
        # TODO: having a different pipeline class for ones with a y_transformer
        # is a bit ugly.
        objs = self.objects
        y_trans_objs = [o for o in self.objects if o.spec_class == YTRANS_NAME]
        if y_trans_objs:
            objs = [o for o in self.objects if o.spec_class != YTRANS_NAME]

        pipe = PipelineSpec._instantiate_steps(objs, problem_info, random_state=random_state,
                                               pipeline_module=self.module, pipeline_class_name=self.class_name,
                                               dataset_metadata=dataset_metadata)

        if y_trans_objs:
            for ytrans in y_trans_objs:
                pipe = model_wrappers.PipelineWithYTransformations(
                    pipe, ytrans.class_name, ytrans.instantiate(
                        problem_info,
                        random_state=random_state,
                        num_threads=problem_info.num_threads,
                        dataset_metadata=dataset_metadata))

        if preprocess_pipelines:
            if not isinstance(preprocess_pipelines, list):
                pipe.steps = [preprocess_pipelines] + pipe.steps
            else:
                pipe.steps = preprocess_pipelines + pipe.steps

        return pipe

    def accepts_categoricals(self) -> bool:
        for o in self.objects:
            if o.class_name in constants.SupportedCategoricals.CATEGORICAL_LEARNERS:
                logger.info("pipeline {} accepts categoricals".format(self.pipeline_name))
                return True

        logger.info("pipeline {} does not accept categoricals".format(self.pipeline_name))
        return False

    def is_ensemble_pipeline(self) -> bool:
        logger.info('is ensemble pipeline {}'.format(
                    self.pipeline_id in constants.EnsembleConstants.ENSEMBLE_PIPELINE_IDS))
        return self.pipeline_id in constants.EnsembleConstants.ENSEMBLE_PIPELINE_IDS

    @staticmethod
    def _instantiate_steps(spec_steps: List[ObjectSpec],
                           problem_info: ProblemInfo,
                           random_state: Optional[int] = None,
                           pipeline_module: str = SK_PIPELINE_MODULE,
                           pipeline_class_name: str = SK_PIPELINE_CLASS_NAME,
                           dataset_metadata: Optional[Any] = None) -> Union[pipeline.Pipeline, Any]:
        """
        Instantiate all steps in the pipeline.

        This function ensures that preprocessors ignore categorical columns when
        they are in problem info and the final estimator of the pipeline can
        accept categorical columns.

        :param spec_steps: List of steps in the pipeline spec.
        :param problem_info: Problem metadata
        :param random_state:
        :param dataset_metadata: Metadata about the dataset.
        :return: List of instantiated pipeline steps.
        """
        has_categoricals = problem_info.dataset_categoricals is not None
        categorical_params = constants.ModelParameters.CATEGORICAL_FEATURES
        accepts_categoricals = spec_steps[-1].class_name in categorical_params

        steps = []
        for spec_step in spec_steps:
            class_name = spec_step.class_name

            # Check if the dataset has categoricals, the pipeline accepts categorical indicators,
            # and this is a preprocessing step, not the final estimator
            if has_categoricals and accepts_categoricals and class_name not in categorical_params:
                preprocessor = PipelineSpec._instantiate_step(spec_step, problem_info, random_state)
                step = PipelineSpec._wrap_categorical_preprocessor(preprocessor, problem_info)
            else:
                step = PipelineSpec._instantiate_step(spec_step, problem_info, random_state, dataset_metadata)

            steps.append((class_name, step))

        pipeline_module = pipeline_module.replace(COMMON_MODULE, RUNTIME_MODULE)
        if RUNTIME_TRAIN_MODULE not in pipeline_module:
            pipeline_module = pipeline_module.replace(COMMON_TRAIN_MODULE, RUNTIME_TRAIN_MODULE)
        # Load Arima, Prophet and ExponentialSmoothing from the separate files to avoid collisions.
        if FORECASTING_MODELS in pipeline_module:
            if pipeline_class_name == constants.SupportedModels.Forecasting.AutoArima:
                pipeline_module = ARIMA_MODEL
            elif pipeline_class_name == PROPHET_MODEL_NAME:
                pipeline_module = PROPHET_MODEL
            elif pipeline_class_name == EXPOSMOOTHING_MODEL_NAME:
                pipeline_module = EXPOSMOOTHING_MODEL
        mod = importlib.import_module(pipeline_module)
        cls = getattr(mod, pipeline_class_name)
        return cls(steps)

    @staticmethod
    def _instantiate_step(spec_step: ObjectSpec,
                          problem_info: ProblemInfo,
                          random_state: Optional[int],
                          dataset_metadata: Optional[Any] = None) -> Any:
        return spec_step.instantiate(problem_info,
                                     random_state=random_state,
                                     num_threads=problem_info.num_threads,
                                     dataset_metadata=dataset_metadata)

    @staticmethod
    def _make_categoricals(n_categorical, n_numerical):
        a = np.full((n_categorical,), True)
        b = np.full((n_numerical,), False)
        return np.concatenate((a.view(dtype=bool), b.view(dtype=bool)), axis=0)

    @staticmethod
    def _wrap_categorical_preprocessor(preprocessor: Any,
                                       problem_info: ProblemInfo) -> Any:
        """
        Wrap a preprocessor so that all categorical columns are ignored.

        :param preprocessor: Preprocessor wrapper object.
        :param problem_info: Problem metadata that hold the categorical indicators.
        :return: New pipeline step, conditional on the types of features.
        """
        numericals = ~problem_info.dataset_categoricals
        categorical_indices = np.where(problem_info.dataset_categoricals)[0]
        numerical_indices = np.where(numericals)[0]

        def get_categorical_columns(X):
            return X[:, problem_info.dataset_categoricals]

        def get_numerical_columns(X):
            return X[:, numericals]

        # 1) Split the features into categorical and numerical
        # 2) Apply the preprocessor only to the numerical features
        # 3) Merge the features back together, categorical first and then numerical
        # NOTE: LightGBMClassifier/Regressor assume that categorical features are first and that the number of them
        #  does not change. Be careful when breaking these assumptions
        func_trans = preprocessing.FunctionTransformer
        id_trans = model_wrappers.IdentityTransformer()
        parts = []
        if categorical_indices.shape[0] != 0:
            parts.append(pipeline.make_pipeline(func_trans(get_categorical_columns, validate=True), id_trans))
        if numerical_indices.shape[0] != 0:
            parts.append(pipeline.make_pipeline(func_trans(get_numerical_columns, validate=True), preprocessor))
        union_pipe = pipeline.make_union(*parts)
        return union_pipe
