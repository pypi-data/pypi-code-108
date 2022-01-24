# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Helper methods to execute an AutoML pipeline fit."""
import copy
import json
import logging
import os
from typing import cast, Any, Dict, List, Optional, Tuple, Union

import numpy as np
import sklearn.pipeline
from sklearn.pipeline import Pipeline as SKPipeline

from azureml.automl.runtime.experiment_store import ExperimentStore
from azureml.automl.core.constants import SupportedTransformersInternal
from azureml.automl.core.shared import constants, logging_utilities, utilities
from azureml.automl.core.shared.activity_logger import ActivityLogger
from azureml.automl.core.shared.constants import TrainingResultsType
from azureml.automl.core.shared.exceptions import PipelineRunException, AutoMLException
from azureml.automl.runtime.shared import metrics
from azureml.automl.runtime.shared import pipeline_spec as pipeline_spec_module
from azureml.automl.runtime.shared.execution_context import ExecutionContext
from azureml.automl.runtime.shared.catindicators_utilities import get_column_transformer_pipeline
from azureml.automl.runtime.shared.model_wrappers import \
    RegressionPipeline, PipelineWithYTransformations, ForecastingPipelineWrapper
from azureml.automl.runtime.shared.problem_info import ProblemInfo
from azureml.automl.runtime.shared.resource_limits import DEFAULT_RESOURCE_LIMITS
from azureml.automl.runtime.shared.runner import ClientRunner
from azureml.automl.core.automl_base_settings import AutoMLBaseSettings
from .automl_pipeline import AutoMLPipeline
from .featurization.streaming import StreamingFeaturizationTransformer
from .streaming_pipeline_wrapper import StreamingPipelineWrapper
from azureml.automl.runtime._runtime_params import ExperimentControlSettings, ExperimentResourceSettings, \
    ExperimentOrchestrationSettings
from azureml.automl.runtime.automl_run_context import AutoMLAbstractRunContext
from azureml.automl.runtime.shared.score._regression import Residuals
from azureml.automl.runtime.shared.score._metric_base import NonScalarMetric

SOURCE_WRAPPER_MODULE = 'automl.client.core.runtime.model_wrappers'


logger = logging.getLogger(__name__)


class PipelineRunOutput:
    """Data class used to encapsulate return values from calling run_pipeline."""

    def __init__(self, task_type: str, enable_streaming: bool, pipeline_obj: SKPipeline, training_type: str):
        """
        Initialize a PipelineRunOutput object.

        :param pipeline_obj: the pipeline being executed
        :param training_type: the training type
        """
        self._training_type = training_type
        self._run_template = 'automl_child'
        self._run_preprocessor, self._run_algorithm = self._get_preprocessor_and_algorithm(task_type,
                                                                                           enable_streaming,
                                                                                           pipeline_obj)
        self._fit_time = 0.0
        self._scores = constants.Defaults.INVALID_PIPELINE_VALIDATION_SCORES
        self._fitted_pipeline = constants.Defaults.INVALID_PIPELINE_OBJECT  # type: Optional[SKPipeline]
        self._fitted_pipelines_train = constants.Defaults.INVALID_PIPELINE_OBJECT  # type: Optional[List[SKPipeline]]
        self._training_percent = 100

    def record_pipeline_output(self,
                               scores: Dict[str, Any],
                               fit_time: float,
                               fitted_pipeline: SKPipeline,
                               fitted_pipelines_train: Optional[List[SKPipeline]],
                               training_percent: int) -> None:
        """
        Save output from a successful pipeline execution.

        :param scores: a dictionary containing metric scores
        :param fit_time: the time taken to execute the pipeline, in seconds
        :param fitted_pipeline: the fitted model
        :param fitted_pipelines_train: the partially trained pipelines when using cross validation
        :param training_percent: percent of data that was used for training
        :return:
        """
        self._scores = scores
        self._fit_time = fit_time
        self._fitted_pipeline = fitted_pipeline
        self._fitted_pipelines_train = fitted_pipelines_train
        self._training_percent = training_percent

    @property
    def fit_time(self) -> float:
        """
        Get the fit time in seconds.

        TODO: when Jasmine PR #181653 goes in, this will only describe the fit time, not fit + predict time.
        """
        return self._fit_time

    @property
    def scores(self) -> Dict[str, Any]:
        """Get the scores."""
        return self._scores

    @property
    def fitted_pipeline(self) -> Optional[SKPipeline]:
        """Get the fitted model."""
        return self._fitted_pipeline

    @property
    def fitted_pipelines_train(self) -> Optional[List[SKPipeline]]:
        """Get the partially trained fitted models."""
        return self._fitted_pipelines_train

    @property
    def run_properties(self) -> Optional[str]:
        """Get the pipeline run properties."""
        if self.fitted_pipeline is None:
            return None
        try:
            pipeline_step_str = str(self.fitted_pipeline.steps[1][1])
            return pipeline_step_str[pipeline_step_str.find("(") + 1:
                                     pipeline_step_str.find(")")]
        except IndexError:
            return None

    @property
    def training_type(self) -> str:
        """Get the training type."""
        return self._training_type

    @property
    def training_percent(self) -> int:
        """Get the training percent used for this pipeline"""
        return self._training_percent

    @property
    def pretrain_props(self) -> Dict[str, Optional[str]]:
        """Get the pretrain properties."""
        return {
            'run_preprocessor': self._run_preprocessor,
            'run_algorithm': self._run_algorithm
        }

    @property
    def pretrain_props_sanitized(self) -> Dict[str, str]:
        """Get the pretrain properties with None converted to empty string."""
        return utilities.convert_dict_values_to_str(self.pretrain_props)

    @classmethod
    def _get_preprocessor_and_algorithm(cls,
                                        task_type: str,
                                        enable_streaming: bool,
                                        pipeline_obj: SKPipeline) -> Tuple[Optional[str], Optional[str]]:
        """
        Given a sklearn pipeline, retrieve the preprocessor and algorithm names.

        :param pipeline_obj: sklearn.pipeline.Pipeline
        :return: a tuple of preprocessor and algorithm names
        """
        try:
            preprocessor = None
            model_tag = None
            # for the Ensemble pipelines we will not have any preprocessors
            if len(pipeline_obj.steps) == 1:
                algorithm = pipeline_obj.steps[0][0]
            else:
                if not enable_streaming:
                    preprocessor = pipeline_obj.steps[0][0]

                # if the first one in the pipeline is the column transformer skip it
                index = 0
                if preprocessor == SupportedTransformersInternal.DropColumnsTransformer:
                    if pipeline_obj.steps[1][0] not in ('TabnetRegressor', 'TabnetClassifier'):
                        index = 1
                        preprocessor = pipeline_obj.steps[1][0]
                    else:
                        # for tabnet, there is no preprocessor
                        preprocessor = None

                algorithm = pipeline_obj.steps[1 + index][0]
                actual_model = pipeline_obj.steps[1 + index][1]
                if hasattr(actual_model, 'model_name'):
                    model_tag = actual_model.model_name
            return preprocessor, cls._map_algorithm_name(task_type, algorithm, model_tag)
        except Exception:
            return None, None

    @staticmethod
    def _map_algorithm_name(task_type: str, run_algorithm: str, model_tag: Optional[str] = None) -> str:
        assert task_type in [constants.Tasks.CLASSIFICATION, constants.Tasks.REGRESSION], \
            "Invalid task_type specified. This should have been identified at config validation time."

        if task_type == constants.Tasks.CLASSIFICATION:
            classification_algo_name = constants.ModelNameMappings.ClassNameToCustomerFacingModelMapClassification.get(
                run_algorithm, run_algorithm)
            if model_tag is not None and model_tag == constants.MULTINOMIAL_ALGO_TAG:
                classification_algo_name = constants.SupportedModels.Classification.MultinomialNB
            return cast(str, classification_algo_name)
        else:
            # task_type is constants.Tasks.REGRESSION:
            return constants.ModelNameMappings.ClassNameToCustomerFacingModelMapRegression.get(run_algorithm,
                                                                                               run_algorithm)


class _PipelineOutputInternal:
    """A data structure to map the results from the runner down to required properties."""

    def __init__(self, scores: Dict[str, Any], train_time: float, training_percent: int, model: Any):
        self.scores = scores
        self.train_time = train_time
        self.training_percent = training_percent
        self.model = model

    @staticmethod
    def map_from_results(
            results: Union[Dict[str, Any]],
            training_type: str) -> '_PipelineOutputInternal':
        if len(results) <= 2:
            raise PipelineRunException(
                "Expected to get at least 3 values from training but only got {}.".format(
                    len(results)), target=PipelineRunException.PIPELINE_OUTPUT, has_pii=False)

        if not results.get(TrainingResultsType.TRAIN_PERCENT, None):
            raise PipelineRunException(
                "Key {} is missing from the training results.".format(TrainingResultsType.TRAIN_PERCENT),
                target=PipelineRunException.PIPELINE_OUTPUT, has_pii=False)

        training_percent = results[TrainingResultsType.TRAIN_PERCENT]
        training_types = constants.TrainingType

        if training_type in [training_types.TrainAndValidation, training_types.TrainValidateTest]:
            scores = results[TrainingResultsType.VALIDATION_METRICS]
            train_time = results[TrainingResultsType.VALIDATION_METRICS][TrainingResultsType.TRAIN_TIME]
            model = results[TrainingResultsType.MODELS][training_type]
        elif training_type == training_types.TrainFull:
            scores = results[TrainingResultsType.TRAIN_FROM_FULL_METRICS]
            train_time = results[TrainingResultsType.TRAIN_FROM_FULL_METRICS][TrainingResultsType.TRAIN_TIME]
            model = results[TrainingResultsType.MODELS][training_type]
        elif training_type == training_types.MeanCrossValidation:
            scores = results[TrainingResultsType.CV_MEAN_METRICS]
            train_time = results[TrainingResultsType.CV_MEAN_METRICS][TrainingResultsType.TRAIN_TIME]
            model = results[TrainingResultsType.MODELS][training_type]
        else:
            raise PipelineRunException('Invalid training type {} specified.'.format(training_type), has_pii=False)

        return _PipelineOutputInternal(scores, train_time, training_percent, model)


def run_pipeline(
    control_settings: ExperimentControlSettings,
    resource_settings: ExperimentResourceSettings,
    automl_pipeline: AutoMLPipeline,
    automl_run_context: AutoMLAbstractRunContext,
    iteration_timeout_min: Optional[int],
) -> PipelineRunOutput:
    """
    Run a pipeline using the given settings and context.

    :param pipeline_run_params: settings object to use for this job.
    :param automl_pipeline: the pipeline definition to use for this job.
    :param automl_run_context: the run context to use for this job.
    :param iteration_timeout_min: upper bound for how long this job can take. Passing None disables timeout.
    :return: a PipelineRunOutput object containing the results
    """
    is_timeseries = control_settings.is_timeseries
    task_type = control_settings.task_type
    subsample_seed = control_settings.subsample_seed
    enable_streaming = control_settings.enable_streaming
    enable_metric_confidence = control_settings.enable_metric_confidence
    positive_label = control_settings.positive_label

    path = resource_settings.path
    max_cores_per_iteration = resource_settings.max_cores_per_iteration
    mem_in_mb = resource_settings.mem_in_mb

    gpu_training_param_dict = control_settings.gpu_training_param_dict

    with logging_utilities.log_activity(logger, activity_name=constants.TelemetryConstants.RUN_PIPELINE_NAME,
                                        custom_dimensions={'run_id': automl_run_context.run_id}):
        expr_store = ExperimentStore.get_instance()
        execution_context = ExecutionContext(run_id=automl_run_context.run_id)

        # for CV, we'll save the partially trained models on each split,
        # along with the model trained on full set

        pipeline_spec, training_type, problem_info = \
            _get_training_args(pipeline_script=automl_pipeline.pipeline_script,
                               max_cores_per_iteration=max_cores_per_iteration)

        metrics_to_calculate = metrics.get_default_metrics(task_type)
        if is_timeseries:
            metrics_to_calculate += metrics.get_default_metrics(constants.Subtasks.FORECASTING)
            problem_info.timeseries_param_dict = \
                expr_store.metadata.timeseries.timeseries_param_dict or control_settings.timeseries_param_dict

        problem_info.gpu_training_param_dict = gpu_training_param_dict

        preprocess_pipelines = []
        if expr_store.metadata.dataset_categoricals_dict:
            column_transformer_pipeline = get_column_transformer_pipeline(pipeline_spec, "X")
            if column_transformer_pipeline:
                preprocess_pipelines.append(column_transformer_pipeline)

        preproc = expr_store.transformers.get_nimbus_preprocessor_pipeline_step()
        if preproc:
            preprocess_pipelines.append(preproc)

        pipeline_obj = pipeline_spec.instantiate_pipeline_spec(
            problem_info,
            preprocess_pipelines=preprocess_pipelines,
            dataset_metadata=expr_store.metadata.nimbus)
        pipeline_run_output = PipelineRunOutput(task_type, enable_streaming, pipeline_obj, training_type)

        with automl_run_context.get_run() as run:
            run.add_properties(pipeline_run_output.pretrain_props_sanitized)

        # min to sec conversion
        timeout = None
        if iteration_timeout_min is not None:
            timeout = iteration_timeout_min * 60
            logger.debug("Remaining time for iteration: {} s.".format(timeout))

        runtime_constraints = DEFAULT_RESOURCE_LIMITS.copy()
        runtime_constraints['mem_in_mb'] = mem_in_mb
        runtime_constraints['wall_time_in_s'] = timeout
        problem_info.runtime_constraints = runtime_constraints

        runner = ClientRunner(metrics=metrics_to_calculate,
                              task=task_type,
                              execution_context=execution_context,
                              enable_metric_confidence=enable_metric_confidence,
                              positive_label=positive_label)
        enforce_limits = timeout is not None
        results, status = runner.run(pipeline_spec,
                                     problem_info,
                                     sets_to_run=[training_type],
                                     is_ensemble_iteration=automl_pipeline.is_ensemble_pipeline,
                                     subsample_percent=automl_pipeline.training_percent,
                                     subsample_seed=subsample_seed,
                                     enforce_limits=enforce_limits,
                                     include_models=True,
                                     working_dir=path)

        if isinstance(status, AutoMLException):
            raise status.with_traceback(status.__traceback__)
        if isinstance(status, BaseException):
            raise PipelineRunException.from_exception(status)
        if results is None:
            pipeline_spec_details = "Pipeline Class Names: {}".format(pipeline_spec.pipeline_name)
            pipeline_id_details = "Pipeline ID: {}".format(pipeline_spec.pipeline_id)
            pipeline_run_error_msg = "Failed to train pipeline. Status: {}".format(status)
            error_msg = ' '.join([pipeline_run_error_msg, pipeline_spec_details, pipeline_id_details])
            raise PipelineRunException(error_msg, target=PipelineRunException.PIPELINE_OUTPUT, has_pii=False)

        fitted_pipelines_train = constants.Defaults.INVALID_PIPELINE_OBJECT

        if automl_pipeline.is_ensemble_pipeline:
            pipeline_output_internal = _PipelineOutputInternal(results[0], results[1], 100, results[2])

            # Set the fitted_pipelines_train from cv training when possible.
            # This is done to ensure ensemble models have the same behavior
            # with respect to models uploaded (in the case of cv both final
            # model and cross validated models list).
            models = results[0].get(constants.TrainingResultsType.MODELS, {})
            fitted_pipelines_train = \
                models.get(constants.TrainingType.MeanCrossValidation, constants.Defaults.INVALID_PIPELINE_OBJECT)
        else:
            # for cross validation train the model on full data set.
            pipeline_output_internal = _PipelineOutputInternal.map_from_results(results, training_type)
            # If the current training happened on partial data (e.g. CV), train again on the full set of training data
            if training_type == constants.TrainingType.MeanCrossValidation:
                result_full, status = runner.run(
                    pipeline_spec, problem_info, sets_to_run=[constants.TrainingType.TrainFull],
                    enforce_limits=enforce_limits,
                    include_models=True,
                    compute_metrics_for_train_full=False)
                if isinstance(status, AutoMLException):
                    raise status.with_traceback(status.__traceback__)
                if isinstance(status, BaseException):
                    raise PipelineRunException.from_exception(status)
                if result_full is None:
                    pipeline_spec_details = "Pipeline Class Names: {}".format(pipeline_spec.pipeline_name)
                    pipeline_id_details = "Pipeline ID: {}".format(pipeline_spec.pipeline_id)
                    pipeline_run_error_msg = "Failed while training full result. Status: {}.".format(status)
                    error_msg = ' '.join([pipeline_run_error_msg, pipeline_spec_details, pipeline_id_details])
                    raise PipelineRunException(error_msg, target=PipelineRunException.PIPELINE_OUTPUT, has_pii=False)

                # Update the final model with the results of the model trained on full set of training data
                pipeline_output_internal_train_full = _PipelineOutputInternal.map_from_results(
                    result_full, constants.TrainingType.TrainFull)
                fitted_pipelines_train = pipeline_output_internal.model
                pipeline_output_internal.model = pipeline_output_internal_train_full.model

        fitted_pipeline = pipeline_output_internal.model
        if isinstance(fitted_pipeline, list) and len(fitted_pipeline):
            fitted_pipeline = fitted_pipeline[0]

        if enable_streaming:
            fitted_pipeline = StreamingPipelineWrapper(
                cast(StreamingFeaturizationTransformer, expr_store.transformers.get_nimbus_preprocessor()),
                fitted_pipeline)

        if task_type == constants.Tasks.REGRESSION and not is_timeseries and not enable_streaming:
            # add stddev to regression pipelines for error bars on predictions
            residuals = pipeline_output_internal.scores[constants.Metric.Residuals]
            try:
                stddev = residuals[NonScalarMetric.DATA][Residuals.STDDEV]
            except KeyError:
                # this could happen when calculation of residuals failed
                # give a default value for stddev
                stddev = np.nan
            fitted_pipeline = RegressionPipeline(fitted_pipeline, stddev)

        augmented_pipeline, augmented_pipelines_train = _augment_transformers(
            task_type,
            fitted_pipeline,
            fitted_pipelines_train
        )

        # Forecasting pipeline require all transformers to be on their place
        # that is why we are creating it on the augmented pipeline.
        if is_timeseries:
            stddevs = []
            # add stddev to regression pipelines for error bars on predictions
            residuals = pipeline_output_internal.scores[constants.Metric.ForecastResiduals]
            for horizon in residuals[NonScalarMetric.DATA].keys():
                stddev = residuals[NonScalarMetric.DATA][horizon][Residuals.STDDEV]
                stddevs.append(stddev)
            augmented_pipeline = ForecastingPipelineWrapper(augmented_pipeline, stddev=stddevs)

        pipeline_run_output.record_pipeline_output(pipeline_output_internal.scores,
                                                   pipeline_output_internal.train_time,
                                                   augmented_pipeline,
                                                   augmented_pipelines_train,
                                                   pipeline_output_internal.training_percent)
        return pipeline_run_output


def _get_pipeline(pipeline_script, problem_info):
    """
    Get the Pipeline object.

    :param pipeline_script: returned from service that is a dictionary of pipeline
    : spec
    : or for backward compatibility a dictionary of normal and sparse pipeline
    : definition that can be eval'd
    :param problem_info: The metadata on the dataset.
    :return: a tuple of ProblemInfo object and a PipelineSpec object.
    """
    pipeline_dict = json.loads(pipeline_script)

    # Wrap the standard scaler.
    scaler = [o for o in pipeline_dict["objects"]
              if o['spec_class'] == pipeline_spec_module.PREPROC_NAME and o['class_name'] == 'StandardScaler']
    if len(scaler) == 1:
        scaler[0]['class_name'] = 'StandardScalerWrapper'
        scaler[0]['module'] = SOURCE_WRAPPER_MODULE

    # rename the Ensemble class name to VotingEnsemble to distinguish from other Ensemble implementations
    voting_ensemble = [o for o in pipeline_dict["objects"]
                       if o['spec_class'] == pipeline_spec_module.SKLEARN_NAME and o['class_name'] == 'Ensemble']
    if len(voting_ensemble) == 1:
        voting_ensemble[0]['class_name'] = 'VotingEnsemble'

    # If there are any single threaded pipelines, force the number of threads to 1.
    pinfo = problem_info
    if problem_info.num_threads != 1:
        stmodel = [o for o in pipeline_dict["objects"]
                   if o['spec_class'] == pipeline_spec_module.SKLEARN_NAME
                   and any([(algo_name in o['class_name']) for algo_name in constants.SINGLE_THREADED_ALGORITHMS])]
        if len(stmodel) == 1:
            pinfo = copy.deepcopy(problem_info)
            pinfo.num_threads = 1
            logger.warning("resetting the number of threads to 1\
                           for pipeline with {0}".
                           format(stmodel[0]['class_name']))
    spec = pipeline_spec_module.PipelineSpec.from_dict(pipeline_dict)
    return pinfo, spec


def _get_training_args(pipeline_script=None,
                       max_cores_per_iteration=None):
    expr_store = ExperimentStore.get_instance()
    problem_info = cast(ProblemInfo, expr_store.metadata.problem_info)
    problem_info.num_threads = max_cores_per_iteration
    pipeline_spec = None
    if pipeline_script:
        problem_info, pipeline_spec = _get_pipeline(pipeline_script, problem_info)

    return pipeline_spec, expr_store.metadata.training_type, problem_info


def _augment_transformers(task_type, fitted_pipeline, fitted_pipelines_train):
    expr_store = ExperimentStore.get_instance()
    transformers = expr_store.transformers.get_transformers()
    x_transformer = transformers.get(constants.Transformers.X_TRANSFORMER)
    ts_transformer = transformers.get(constants.Transformers.TIMESERIES_TRANSFORMER)
    y_transformer = transformers.get(constants.Transformers.Y_TRANSFORMER)

    # Augment the pipeline with our own transformers
    if (x_transformer is not None or ts_transformer is not None) and \
            fitted_pipeline != constants.Defaults.INVALID_PIPELINE_OBJECT:
        fitted_pipeline = _add_transformer_x(
            x_transformer, ts_transformer, fitted_pipeline)
        if fitted_pipelines_train != constants.Defaults.INVALID_PIPELINE_OBJECT:
            transformed_train_pipelines = []
            for pipe in fitted_pipelines_train:
                transformed_train_pipelines.append(
                    _add_transformer_x(x_transformer, ts_transformer, pipe))
            fitted_pipelines_train = transformed_train_pipelines

    # if y_transformer is not None, add a wrapper of the fitted model with transformer.
    if y_transformer is not None:
        if(task_type == constants.Tasks.CLASSIFICATION):
            y_trans_name = "LabelEncoder"
        else:
            y_trans_name = "TargetTypeTransformer"

        if isinstance(fitted_pipeline, sklearn.pipeline.Pipeline) and \
                fitted_pipeline != constants.Defaults.INVALID_PIPELINE_OBJECT:
            fitted_pipeline = PipelineWithYTransformations(
                fitted_pipeline, y_trans_name, y_transformer)
        if isinstance(fitted_pipelines_train, sklearn.pipeline.Pipeline) and \
                fitted_pipelines_train != constants.Defaults.INVALID_PIPELINE_OBJECT:
            fitted_pipeline = PipelineWithYTransformations(
                fitted_pipelines_train, y_trans_name, y_transformer)

    return fitted_pipeline, fitted_pipelines_train


def _add_transformer_x(transformer, ts_transformer, pipeline_spec):
    """
    Add transformer as first step of the pipeline.

    :param pipeline_spec: pipeline to which the transformer should be added
    :param transformer: a pipeline compatible transformation that implements fit, transform and predict
    :return: pipeline with transformer prepended
    """
    insert_at = 0
    if transformer is not None:
        pipeline_spec.steps.insert(insert_at, (constants.Transformers.X_TRANSFORMER, transformer))
        insert_at += 1
    if ts_transformer is not None:
        pipeline_spec.steps.insert(insert_at, (constants.Transformers.TIMESERIES_TRANSFORMER, ts_transformer))
        insert_at += 1

    return pipeline_spec
