# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Class for running experiments."""
import copy
import datetime
import logging
import os
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, cast

import numpy as np
import pandas as pd
import scipy
import sklearn.pipeline

from azureml._tracing._tracer_factory import get_tracer
from azureml.automl.runtime.experiment_store import ExperimentStore
from azureml.automl.core.shared import constants
from azureml.automl.core.shared import logging_utilities as log_utils
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.constants import TrainingResultsType, TrainingType
from azureml.automl.runtime import _ml_engine
from azureml.automl.runtime._data_definition import LazyTabularData, MaterializedTabularData
from azureml.automl.runtime.featurizer.transformer.timeseries.timeseries_transformer import TimeSeriesTransformer
from azureml.automl.runtime.shared.catindicators_utilities import update_problem_info_preprocess_pipelines
from azureml.automl.runtime.shared.pipeline_spec import PROPHET_MODEL_NAME
from azureml.automl.runtime.subsample_utilities import subsample_train_valid_set

from . import resource_limits
from .execution_context import ExecutionContext
from .metrics_utilities import predict_and_compute_metrics_expr_store
from .nimbus_wrappers import NimbusMlPipelineWrapper
from .pipeline_spec import PipelineSpec
from .problem_info import ProblemInfo
from .resource_limits import SafeEnforceLimits
from .score import scoring
from .score import utilities as scoring_utilities

logger = logging.getLogger(__name__)
tracer = get_tracer(__name__)


class ClientRunner:
    """Runner which encapsulates the fit() method for various AutoML models."""

    def __init__(self,
                 metrics: Optional[Set[str]] = None,
                 task: str = constants.Tasks.CLASSIFICATION,
                 execution_context: Optional[ExecutionContext] = None,
                 use_binary_metrics: bool = False,
                 enable_metric_confidence: bool = False,
                 positive_label: Optional[Any] = None):
        """
        Construct the ClientRunner.

        :param metrics: The metrics that AutoML will optimize for model selection.
        :param task: string, 'classification' or 'regression'
        :param execution_context: ExecutionContext, the execution context from parent context
        :param use_binary_metrics: Compute metrics on only the second class for binary classification.
            This is usually the true class (when labels are 0 and 1 or false and true).
        :param enable_metric_confidence: Used to score confidence intervals while computing metrics
        :param positive_label: class designed as positive class in binary classification metrics.
        """
        Contract.assert_true(task in ['classification', 'regression'] is not None,
                             "An invalid task was selected.", log_safe=True)
        self.task = task

        self.metrics = scoring_utilities.get_scalar_metrics(self.task) if metrics is None else list(metrics)

        self.execution_context = execution_context
        self._use_binary_metrics = use_binary_metrics
        self._enable_metric_confidence = enable_metric_confidence
        self._positive_label = positive_label

    def _run_train_valid(self, pipeline_spec,
                         problem_info,
                         random_state=None):
        """
        Run the training and validation.

        :param pipeline_spec: The PipelineSpec object used for the run.
        :return: A dictionary of metric name -> score, fit time and the instantiated pipeline.
        """
        expr_store = ExperimentStore.get_instance()
        with log_utils.log_activity(logger,
                                    activity_name=constants.TelemetryConstants.RUN_TRAIN_VALID_NAME):

            preprocess_pipelines = []   # type: List[Tuple[str, Any]]

            problem_info, preprocess_pipelines = update_problem_info_preprocess_pipelines(pipeline_spec, problem_info,
                                                                                          preprocess_pipelines, "X")

            preproc = expr_store.transformers.get_nimbus_preprocessor_pipeline_step()
            if preproc:
                preprocess_pipelines.append(preproc)

            pipeline = pipeline_spec.instantiate_pipeline_spec(
                problem_info,
                random_state=random_state,
                is_sparse=expr_store.metadata.is_sparse,
                preprocess_pipelines=preprocess_pipelines,
                dataset_metadata=expr_store.metadata.nimbus)

            if isinstance(pipeline, NimbusMlPipelineWrapper):
                X_train, y_train, _ = expr_store.data.lazy.get_train()
                X_valid, y_valid, sample_weight_valid = expr_store.data.lazy.get_valid()
                training_data, label_column_name, weight_column_name = expr_store.data.lazy.get_training_dataset()

                fit_time = _ml_engine.train(pipeline, LazyTabularData(training_data,
                                                                      label_column_name,
                                                                      weight_column_name))
            else:
                X_train, y_train, sample_weight_train = _get_materialized_with_training_perc(
                    problem_info,
                    random_state
                )
                X_valid, y_valid, sample_weight_valid = expr_store.data.materialized.get_valid()

                # Timeseries training data preprocessing steps that depend on the components of the pipeline
                # e.g. remove imputed rows and remove nans from look-back features for regression learners.
                X_train, y_train = ClientRunner._prepare_timeseries_data_for_pipeline(X_train, y_train, pipeline_spec)
                # Validation data doesn't contain any imputed rows for target values, and we don't expect
                # look-back features to bring NA's to validation data, so no need to pre-process validation
                # data.

                fit_time = _ml_engine.train(pipeline, MaterializedTabularData(X_train,
                                                                              y_train,
                                                                              sample_weight_train))

            score_valid = predict_and_compute_metrics_expr_store(
                X_valid, y_valid, X_train, y_train, pipeline,
                self.task, self.metrics, self._use_binary_metrics,
                sample_weight=sample_weight_valid, problem_info=problem_info,
                positive_label=self._positive_label
            )
            return score_valid, fit_time, pipeline

    def _run_train_full(self, pipeline_spec,
                        problem_info,
                        random_state=None,
                        compute_metrics=True):
        """
        Run the full training.

        :param pipeline_spec: The PipelineSpec object used for the run.
        :param compute_metrics: Get predictions and metrics on full train set
        :return: A dictionary of metric name -> score, fit time and the instantiated pipeline.
        """
        with log_utils.log_activity(logger,
                                    activity_name=constants.TelemetryConstants.RUN_TRAIN_FULL_NAME):
            expr_store = ExperimentStore.get_instance()
            preprocess_pipelines = []  # type: List[Tuple[str, Any]]

            if expr_store.metadata.dataset_categoricals_dict:
                X_valid, _, _ = expr_store.data.materialized.get_valid()
                if X_valid is None:
                    problem_info, preprocess_pipelines = update_problem_info_preprocess_pipelines(pipeline_spec,
                                                                                                  problem_info,
                                                                                                  preprocess_pipelines,
                                                                                                  "X")

            preproc = expr_store.transformers.get_nimbus_preprocessor_pipeline_step()
            if preproc:
                preprocess_pipelines.append(preproc)

            pipeline = pipeline_spec.instantiate_pipeline_spec(
                problem_info,
                random_state=random_state,
                is_sparse=expr_store.metadata.is_sparse,
                preprocess_pipelines=preprocess_pipelines,
                dataset_metadata=expr_store.metadata.nimbus
            )

            if isinstance(pipeline, NimbusMlPipelineWrapper):
                X_full, y_full, sample_weight_full = expr_store.data.lazy.get_train()
                training_data, label_column_name, weight_column_name = expr_store.data.lazy.get_training_dataset()
                fit_time = _ml_engine.train(pipeline, LazyTabularData(training_data,
                                                                      label_column_name,
                                                                      weight_column_name))
            else:
                X_train, y_train, sample_weight_train = _get_materialized_with_training_perc(
                    problem_info,
                    random_state
                )
                X_valid, y_valid, sample_weight_valid = expr_store.data.materialized.get_valid()
                if X_valid is not None:
                    X_full = (
                        scipy.sparse.vstack((X_train, X_valid))
                        if scipy.sparse.issparse(X_train)
                        else np.concatenate((X_train, X_valid)))
                    y_full = np.concatenate((y_train, y_valid))

                    if sample_weight_valid is not None:
                        sample_weight_full = np.concatenate(
                            (sample_weight_train, sample_weight_valid))
                    else:
                        sample_weight_full = None
                else:
                    X_full, y_full, sample_weight_full = X_train, y_train, sample_weight_train

                # Timeseries training data preprocessing steps that depend on the components of the pipeline
                # e.g. remove imputed rows for regression learners
                X_full, y_full = ClientRunner._prepare_timeseries_data_for_pipeline(X_full, y_full, pipeline_spec)

                fit_time = _ml_engine.train(pipeline, MaterializedTabularData(X_full,
                                                                              y_full,
                                                                              sample_weight_full))

            if compute_metrics:
                # Note that y_full is passed here as both validation targets
                # and as training targets because the full set is used for
                # training and validation.
                score_full = predict_and_compute_metrics_expr_store(
                    X_full, y_full, X_full, y_full, pipeline,
                    self.task, self.metrics, self._use_binary_metrics,
                    sample_weight=sample_weight_full,
                    positive_label=self._positive_label,
                    problem_info=problem_info
                )
            else:
                score_full = {metric_name: np.nan for metric_name in self.metrics}
                score_full[TrainingResultsType.PREDICT_TIME] = 0

            return score_full, fit_time, pipeline, X_full, y_full

    def _run_cv(self, pipeline_spec, problem_info,
                random_state=None):
        """
        Run the fit of given pipeline spec with CV splits of the input dataset.

        :param pipeline_spec: The PipelineSpec object used for the run.
        :param problem_info: The ProblemInfo object used for the run.
        :param random_state: RandomState instance or None, optional, default = None.
        :return: Dictionaries of metric name -> score, fit times and the instantiated pipelines.
        """
        with log_utils.log_activity(logger, activity_name=constants.TelemetryConstants.RUN_CV_NAME):
            scores = []
            fit_times = []
            models = []

            expr_store = ExperimentStore.get_instance()
            for idx, split in enumerate(expr_store.data.materialized.get_CV_splits()):

                X_train = split._X_train_transformed
                y_train = split._y_train
                sample_wt_train = split._sample_wt_train
                X_test = split._X_test_transformed
                y_test = split._y_test
                sample_wt_test = split._sample_wt_test

                preprocess_pipelines = []  # type: List[Tuple[str, Any]]

                data_type = expr_store.data.materialized.cv_splits._keys[idx]
                problem_info, preprocess_pipelines = update_problem_info_preprocess_pipelines(pipeline_spec,
                                                                                              problem_info,
                                                                                              preprocess_pipelines,
                                                                                              data_type)

                if problem_info.training_percent != 100:
                    n_samples = y_train.shape[0]
                    subsample_n = int(n_samples * problem_info.training_percent)
                    X_train = X_train[:subsample_n]
                    y_train = y_train[:subsample_n]
                    if sample_wt_train:
                        sample_wt_train = sample_wt_train[:subsample_n]

                new_problem_info = copy.deepcopy(problem_info)
                m = pipeline_spec.instantiate_pipeline_spec(
                    new_problem_info, random_state=random_state, is_sparse=expr_store.metadata.is_sparse,
                    preprocess_pipelines=preprocess_pipelines)

                # Timeseries training data preprocessing steps that depend on the components of the pipeline
                # e.g. remove imputed rows for regression learners
                X_train, y_train = ClientRunner._prepare_timeseries_data_for_pipeline(X_train, y_train, pipeline_spec)
                # Validation data doesn't contain any imputed rows for target values, and we don't expect
                # look-back features to bring NA's to validation data, so no need to pre-process validation
                # data.
                fit_time = _ml_engine.train(m, MaterializedTabularData(X_train, y_train, sample_wt_train))
                score = predict_and_compute_metrics_expr_store(
                    X_test, y_test, X_train, y_train, m,
                    self.task, self.metrics, self._use_binary_metrics,
                    sample_weight=sample_wt_test,
                    positive_label=self._positive_label,
                    problem_info=new_problem_info
                )

                scores.append(score)
                fit_times.append(fit_time)
                models.append(m)

            return scores, fit_times, models

    def _run_cv_mean(self, pipeline_spec, problem_info,
                     cv_results=None,
                     random_state=False):
        """
        Run the fit to get the mean of scores and fit time, with CV splits of the input dataset.

        :param pipeline_spec: The PipelineSpec object used for the run.
        :param problem_info: The ProblemInfo object used for the run.
        :param cv_results: The result of a _run_cv method.
        :param random_state: RandomState instance or None, optional, default = None.
        :return: Mean values of the scores and fit times, and the instantiated pipelines.
        """
        with log_utils.log_activity(logger,
                                    activity_name=constants.TelemetryConstants.RUN_CV_MEAN_NAME):
            if cv_results is None:
                scores, fit_times, fit_models = self._run_cv(
                    pipeline_spec, problem_info, random_state=random_state)
            else:
                scores, fit_times, fit_models = cv_results

            mean_scores = scoring.aggregate_scores(scores, self.metrics)
            mean_fit_time = float(np.mean(fit_times))
            return mean_scores, mean_fit_time, fit_models

    def _run(self, pipeline_spec, problem_info, sets_to_run,
             subsample_percent=None, random_state=None, include_models=False,
             subsample_seed=0, compute_metrics_for_train_full=True):
        """
        Run the fit with different purpose with specific run sets.

        :param pipeline_spec: A pipeline specification (obtained from the API).
        :param problem_info: A ProblemInfo object.
        :param sets_to_run: Which experiment types to run (e.g. CV,
            train_valid, etc).
        :param subsample_percent: The percentage of training data to use for training. Ranges from (0, 100]
            with decimal or integer values.
        :param random_state: int or RandomState object to seed random
            operations.
        :param include_models:
        :param compute_metrics_for_train_full: Get predictions and metrics on full train set for TrainFull activity
        :return: train, validation, and test scores for the experiments
            specified in sets_to_run.
        """
        expr_store = ExperimentStore.get_instance()
        with log_utils.log_activity(logger, activity_name=constants.TelemetryConstants.RUN_NAME):
            results = {TrainingResultsType.MODELS: {}}  # type: Dict[str, Any]
            # TODO: we should unify these two modes of setting training_percent
            training_percent = subsample_percent or problem_info.training_percent
            if training_percent is not None and training_percent < 100:
                # train on a subset of the training dataset.
                results[TrainingResultsType.TRAIN_PERCENT] = training_percent
            else:
                training_percent = 100
                results[TrainingResultsType.TRAIN_PERCENT] = training_percent

            # ensure problem info contains the correct integer setting of training percent.
            problem_info.training_percent = training_percent

            if constants.TrainingType.TrainAndValidation in sets_to_run:
                results[TrainingResultsType.TRAIN_VALIDATE_STATUS] = 0
                try:
                    score_full, fit_time, fit_model = self._run_train_valid(
                        pipeline_spec, problem_info, random_state=random_state)
                    results[TrainingResultsType.VALIDATION_METRICS] = score_full
                    results[TrainingResultsType.MODELS][
                        constants.TrainingType.TrainAndValidation] = fit_model
                    results[TrainingResultsType.VALIDATION_METRICS][
                        TrainingResultsType.FIT_TIME] = fit_time
                    results[TrainingResultsType.VALIDATION_METRICS][TrainingResultsType.TRAIN_TIME] = \
                        results[TrainingResultsType.VALIDATION_METRICS][TrainingResultsType.FIT_TIME] + \
                        results[TrainingResultsType.VALIDATION_METRICS][TrainingResultsType.PREDICT_TIME]
                except Exception as e:
                    log_utils.log_traceback(e, logger)
                    raise

            if constants.TrainingType.TrainValidateTest in sets_to_run:
                results[TrainingResultsType.TRAIN_VALIDATE_STATUS] = 0
                try:
                    score_full, fit_time, fit_model = self._run_train_valid(
                        pipeline_spec, problem_info, random_state=random_state)
                    results[TrainingResultsType.VALIDATION_METRICS] = score_full
                    results[TrainingResultsType.MODELS][
                        constants.TrainingType.TrainValidateTest] = fit_model
                    # TODO: make this compatible for streaming
                    X_train, y_train, sample_weight_train = expr_store.data.materialized.get_train()
                    scores = predict_and_compute_metrics_expr_store(
                        X_train, y_train, X_train, y_train, fit_model,
                        self.task, self.metrics, self._use_binary_metrics,
                        sample_weight=sample_weight_train,
                        positive_label=self._positive_label
                    )
                    results[TrainingResultsType.TRAIN_METRICS] = scores
                    results[TrainingResultsType.TRAIN_METRICS][
                        TrainingResultsType.FIT_TIME] = fit_time
                    results[TrainingResultsType.TRAIN_METRICS][TrainingResultsType.TRAIN_TIME] = \
                        results[TrainingResultsType.TRAIN_METRICS][TrainingResultsType.FIT_TIME] + \
                        results[TrainingResultsType.TRAIN_METRICS][TrainingResultsType.PREDICT_TIME]
                    X_test, y_test, sample_weight_test = expr_store.data.materialized.get_test()
                    scores = predict_and_compute_metrics_expr_store(
                        X_test, y_test, X_train, y_train, fit_model,
                        self.task, self.metrics, self._use_binary_metrics,
                        sample_weight=sample_weight_test,
                        positive_label=self._positive_label
                    )
                    results[TrainingResultsType.TEST_METRICS] = scores
                except Exception as e:
                    log_utils.log_traceback(e, logger)
                    raise

            if constants.TrainingType.TrainFull in sets_to_run:
                results[TrainingResultsType.TRAIN_FULL_STATUS] = 0
                try:
                    score_full, fit_time, fit_model, X_full, y_full = self._run_train_full(
                        pipeline_spec, problem_info, random_state=random_state,
                        compute_metrics=compute_metrics_for_train_full)

                    results[TrainingResultsType.MODELS][
                        constants.TrainingType.TrainFull] = fit_model
                    results[TrainingResultsType.TRAIN_FROM_FULL_METRICS] = score_full
                    results[TrainingResultsType.TRAIN_FROM_FULL_METRICS][
                        TrainingResultsType.FIT_TIME] = fit_time
                    results[TrainingResultsType.TRAIN_FROM_FULL_METRICS][TrainingResultsType.TRAIN_TIME] = \
                        results[TrainingResultsType.TRAIN_FROM_FULL_METRICS][TrainingResultsType.FIT_TIME] + \
                        results[TrainingResultsType.TRAIN_FROM_FULL_METRICS][TrainingResultsType.PREDICT_TIME]

                    X_test, y_test, sample_weight_test = expr_store.data.materialized.get_test()
                    if X_test is not None:
                        scores = predict_and_compute_metrics_expr_store(
                            X_test, y_test, X_full, y_full, fit_model,
                            self.task, self.metrics, self._use_binary_metrics,
                            sample_weight=sample_weight_test,
                            positive_label=self._positive_label
                        )
                        results[TrainingResultsType.TEST_FROM_FULL_METRICS] = scores
                except Exception as e:
                    log_utils.log_traceback(e, logger)
                    raise

            if constants.TrainingType.MeanCrossValidation in sets_to_run:
                results[TrainingResultsType.CV_STATUS] = 0
                try:
                    scores, fit_times, fit_model = self._run_cv(
                        pipeline_spec, problem_info, random_state=random_state)
                    results[TrainingResultsType.MODELS][
                        constants.TrainingType.MeanCrossValidation] = fit_model

                    for i in range(len(scores)):
                        score = scores[i]
                        fit_time = fit_times[i]
                        score[TrainingResultsType.FIT_TIME] = fit_time
                        score[TrainingResultsType.TRAIN_TIME] = score[TrainingResultsType.FIT_TIME] + score[
                            TrainingResultsType.PREDICT_TIME]
                    results[TrainingResultsType.CV_METRICS] = scores

                    mean_scores, mean_time, fit_model = self._run_cv_mean(
                        pipeline_spec, problem_info, cv_results=(scores, fit_times, fit_model))

                    results[TrainingResultsType.CV_MEAN_METRICS] = mean_scores
                except Exception as e:
                    log_utils.log_traceback(e, logger)
                    raise

            if not include_models:
                del results[TrainingResultsType.MODELS]

            return results

    def run(self,
            pipeline_spec: PipelineSpec,
            problem_info: ProblemInfo,
            sets_to_run: Optional[List[str]] = None,
            subsample_percent: Optional[float] = None,
            enforce_limits: bool = True,
            is_ensemble_iteration: bool = False,
            random_state: Optional[int] = None,
            include_models: bool = False,
            subsample_seed: Optional[int] = 0,
            working_dir: Optional[str] = None,
            compute_metrics_for_train_full: bool = True) -> Tuple[Any, Optional[BaseException]]:
        """
        Run the specific run task.

        :param pipeline_spec: A pipeline specification (obtained from the API).
            Not to be confused with a sklearn Pipeline object.
        :param problem_info:
        :param sets_to_run:
        :param subsample_percent: The percentage of training data to use for training. Ranges from (0, 100]
            with decimal or integer values.
        :param enforce_limits: If true, run in a subprocess.
        :param is_ensemble_iteration: bool to indicate whether
            it is an ensemble iteration
        :param random_state: random_state for random operations
        :param include_models:
        :param subsample_seed: a int for seeding subsample operations
        :param compute_metrics_for_train_full: Get predictions and metrics on full train set for TrainFull activity
        :return: A dict of results, filled in with TrainingResultsType keys.
        """
        if sets_to_run is None:
            sets_to_run = list(constants.TrainingType.FULL_SET)

        if working_dir is None:
            working_dir = os.getcwd()

        expr_store = ExperimentStore.get_instance()

        kwargs = {
            "sets_to_run": sets_to_run,
            "subsample_percent": subsample_percent,
            "random_state": random_state,
            "subsample_seed": subsample_seed,
            "include_models": include_models,
            "compute_metrics_for_train_full": compute_metrics_for_train_full,
            "cache_store": expr_store.data._cache
        }

        func = cast('Callable[..., Any]', self._run_ensembling_internal if is_ensemble_iteration else self._run)

        pinfo_copy = copy.deepcopy(problem_info)
        if (pipeline_spec.supports_constrained_fit()
                or (hasattr(pipeline_spec, 'pipeline_name')
                    and ('Tabnet' in pipeline_spec.pipeline_name
                    or 'AutoGluon' in pipeline_spec.pipeline_name))):
            constraints = resource_limits.DEFAULT_RESOURCE_LIMITS
            enforce_limits = False
        else:
            constraints = problem_info.runtime_constraints

        limiter = SafeEnforceLimits(enable_limiting=enforce_limits, **constraints)
        result, exit_status, _ = limiter.execute(working_dir, func, *(pipeline_spec, pinfo_copy),
                                                 **kwargs)
        return result, exit_status

    def _run_ensembling_internal(self, pipeline_spec, problem_info, sets_to_run, **kwargs):
        expr_store = ExperimentStore.get_instance()
        with log_utils.log_activity(logger,
                                    activity_name=constants.TelemetryConstants.RUN_ENSEMBLING_NAME):
            pipeline = pipeline_spec.instantiate_pipeline_spec(
                problem_info, is_sparse=expr_store.metadata.is_sparse)
            if TrainingType.MeanCrossValidation in sets_to_run:
                training_type = constants.TrainingType.MeanCrossValidation
            else:
                training_type = constants.TrainingType.TrainAndValidation

            # Need to remove nans that were brought by look-back features for time series data.
            timeseries_transformer = None
            if expr_store.metadata.is_timeseries:
                timeseries_transformer = expr_store.transformers.get_timeseries_transformer()

            fit_time, fitted_ensemble_model, scoring_ensembles = \
                self.time_fit_ensemble(pipeline, training_type)
            fitted_pipeline = sklearn.pipeline.make_pipeline(fitted_ensemble_model)

            if training_type == TrainingType.TrainAndValidation:
                X_train, y_train, _ = expr_store.data.materialized.get_train()
                X_valid, y_valid, sample_weight_valid = expr_store.data.materialized.get_valid()

                if timeseries_transformer is not None:
                    X_train, y_train = timeseries_transformer._remove_nans_from_look_back_features(
                        X_train, y_train)
                    # Validation data doesn't contain any imputed rows for target values, and we don't expect
                    # look-back features to bring NA's to validation data, so no need to pre-process validation
                    # data.

                # voting ensemble will use the same final model for scoring and inferencing
                scoring_ensemble = fitted_ensemble_model

                # for stack ensembles we have a separate ensemble to be used for scoring.
                if scoring_ensembles is not None:
                    scoring_ensemble = scoring_ensembles[0]

                score_valid = predict_and_compute_metrics_expr_store(
                    X_valid, y_valid, X_train, y_train, scoring_ensemble,
                    self.task, self.metrics, self._use_binary_metrics,
                    sample_weight=sample_weight_valid,
                    positive_label=self._positive_label
                )
            elif training_type == TrainingType.MeanCrossValidation:
                fold_index = 0
                scores = []
                cv_models = []
                for split in expr_store.data.materialized.get_CV_splits():
                    X_train = split._X_train_transformed
                    y_train = split._y_train
                    X_test = split._X_test_transformed
                    y_test = split._y_test
                    sample_wt_test = split._sample_wt_test

                    m = scoring_ensembles[fold_index]
                    cv_models.append(sklearn.pipeline.make_pipeline(m))
                    if timeseries_transformer is not None:
                        X_train, y_train = timeseries_transformer._remove_nans_from_look_back_features(
                            X_train, y_train)
                        # Validation data doesn't contain any imputed rows for target values, and we don't expect
                        # look-back features to bring NA's to validation data, so no need to pre-process validation
                        # data.
                    score = predict_and_compute_metrics_expr_store(
                        X_test, y_test, X_train, y_train, m,
                        self.task, self.metrics, self._use_binary_metrics,
                        sample_weight=sample_wt_test,
                        positive_label=self._positive_label
                    )
                    scores.append(score)
                    fold_index += 1

                score_valid = scoring.aggregate_scores(scores, self.metrics)
                score_valid[TrainingResultsType.MODELS] = {
                    constants.TrainingType.MeanCrossValidation: cv_models
                }

            return score_valid, fit_time, fitted_pipeline

    def time_fit_ensemble(self, m, training_type):
        """
        Run the ensemble fit of the given model.

        :param m: The model to run the fit.
        :param X: Input data.
        :param y: Target values.
        :return: Elapsed time in seconds, the fitted ensemble with all the selected models.
        """
        with log_utils.log_activity(logger,
                                    activity_name=constants.TelemetryConstants.TIME_FIT_ENSEMBLE_NAME):
            t = datetime.datetime.utcnow()  # time.process_time()
            fitted_ensemble_model, scoring_ensembles = m._final_estimator.fit_ensemble(training_type)
            elapsed_time = datetime.datetime.utcnow() - t
            return elapsed_time.seconds, fitted_ensemble_model, scoring_ensembles

    @staticmethod
    def _prepare_timeseries_data_for_pipeline(X: pd.DataFrame,
                                              y: np.ndarray,
                                              pipeline_spec: PipelineSpec) -> Tuple[pd.DataFrame, np.ndarray]:
        expr_store = ExperimentStore.get_instance()
        if not expr_store.metadata.is_timeseries:
            return X, y

        X_prep, y_prep = X.copy(), y.copy()

        # What kind of pipeline is this?
        is_classical_timeseries_model = False
        is_prophet = False
        is_ensemble = False
        for o in pipeline_spec.objects:
            if o.class_name in constants.ModelCategories.CLASSICAL_TIMESERIES_MODELS:
                is_classical_timeseries_model = True
            elif o.class_name == 'VotingEnsemble' or o.class_name == 'StackEnsemble':
                is_ensemble = True
            elif o.class_name == PROPHET_MODEL_NAME:
                is_prophet = True

        if not is_classical_timeseries_model:
            # Either regression/Miro based models, ensemble models, or Prophet.
            tst_key = constants.Transformers.TIMESERIES_TRANSFORMER
            dataset_transformers = expr_store.transformers.get_transformers()
            if dataset_transformers is not None and tst_key in dataset_transformers and \
               isinstance(dataset_transformers[tst_key], TimeSeriesTransformer):
                timeseries_transformer = dataset_transformers[tst_key]
                if not is_ensemble:
                    # Regression/MIRO based model or Prophet. Retrieve a transform that removes rows where the
                    # target value has been imputed, for training data.
                    X_prep, y_prep = timeseries_transformer.remove_rows_with_imputed_target(X, y)
                if not is_prophet:
                    # Need to remove nans from look-back features for both regression and ensemble models.
                    X_prep, y_prep = timeseries_transformer._remove_nans_from_look_back_features(X_prep, y_prep)
            else:
                logger.warning('Could not retrieve timeseries transformer from the ExperimentStore.')

        return X_prep, y_prep


def _get_materialized_with_training_perc(problem_info, random_state):
    """Get the materialized data and subsample if training_percent < 100."""
    expr_store = ExperimentStore.get_instance()
    if problem_info.training_percent == 100:
        X_train, y_train, sample_weight_train = expr_store.data.materialized.get_train()
    else:
        X_train, y_train, sample_weight_train = subsample_train_valid_set(
            problem_info.training_percent,
            random_state
        )
    return X_train, y_train, sample_weight_train


if __name__ == '__main__':
    pass
