# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Base module for ensembling previous AutoML iterations."""
from typing import Any, cast, Dict, List, Optional, Tuple, Type, TypeVar, Union
import datetime

from abc import ABC, abstractmethod
import logging
import os
import pickle
import uuid
from sklearn.base import BaseEstimator
from sklearn.pipeline import make_pipeline

from azureml.core import Run

from azureml.automl.core.automl_base_settings import AutoMLBaseSettings
from azureml.automl.runtime.experiment_store import ExperimentStore
from azureml.automl.core.shared import constants
from azureml.automl.core.shared import logging_utilities as log_utils
from azureml.automl.core.shared.exceptions import AutoMLEnsembleException
from azureml.automl.runtime._data_definition import MaterializedTabularData
from azureml.automl.runtime._ml_engine import run_ensemble_selection
from azureml.automl.runtime._ml_engine.ensemble import EnsembleSelector
from azureml.automl.runtime._run_history.offline_automl_run import OfflineAutoMLRun, OfflineAutoMLRunUtil
from azureml.automl.runtime.shared import metrics


SettingsType = TypeVar('SettingsType', bound=AutoMLBaseSettings)
logger = logging.getLogger(__name__)


class EnsembleBase(BaseEstimator, ABC):
    """
    Class for ensembling previous AutoML iterations.

    The ensemble pipeline is initialized from a collection of already fitted pipelines.
    """

    MAXIMUM_MODELS_FOR_SELECTION = 50
    PIPELINES_TUPLES_ITERATION_INDEX = 0
    PIPELINES_TUPLES_PIPELINE_INDEX = 1
    PIPELINES_TUPLES_ALGORITHM_INDEX = 2
    PIPELINES_TUPLES_CHILD_RUN_INDEX = 3
    PIPELINES_TUPLES_PIPELINE_SPEC_INDEX = 4
    DOWNLOAD_RETURNED_NO_MODELS_MSG = "Could not find any models for running ensembling. \
        This can happen if the download of models required for ensembling procedure didn't finish within the default \
        timeout. Please use `ensemble_download_models_timeout_sec` parameter in AutoMLConfig to set a larger timeout"

    def convert_settings(self, automl_settings: Union[str, Dict[str, Any], AutoMLBaseSettings],
                         settings_type: 'Type[SettingsType]') -> SettingsType:
        """Convert settings into a settings object.

        :param automl_settings: settings for the AutoML experiments.
        :param settings_type: the type for the settings object.
        """
        if isinstance(automl_settings, str):
            automl_settings = cast(Dict[str, Any], eval(automl_settings))

        if isinstance(automl_settings, dict):
            automl_settings['debug_log'] = None
            return settings_type(**automl_settings)
        elif isinstance(automl_settings, settings_type):
            return automl_settings
        else:
            raise AutoMLEnsembleException(
                '`automl_settings` object has an invalid type {}'.format(automl_settings.__class__.__name__),
                target=AutoMLEnsembleException.CONFIGURATION)\
                .with_generic_msg('`automl_settings` object has an invalid type.')

    def __init__(self, automl_settings: Union[str, Dict[str, Any], AutoMLBaseSettings],
                 settings_type: 'Type[SettingsType]') -> None:
        """Create an Ensemble pipeline out of a collection of already fitted pipelines.

        :param automl_settings: settings for the AutoML experiments.
        :param settings_type: the type for the settings object.
        """
        self._automl_settings = self.convert_settings(automl_settings, settings_type)
        self.estimator = None   # type: Optional[BaseEstimator]

    def fit(self, X: Optional[Any], y: Optional[Any]) -> None:
        """Fit method not implemented.

        Use the `fit_ensemble` method instead

        Raises:
            NotImplementedError -- Not using this API for ensemble training

        """
        raise NotImplementedError("call fit_ensemble instead")  # PII safe to raise directly

    def fit_ensemble(
        self,
        training_type: constants.TrainingType,
        **kwargs: Any
    ) -> Tuple[BaseEstimator, List[BaseEstimator]]:
        """
        Fit the ensemble based on the existing fitted pipelines.

        :param training_type: Type of training (eg: TrainAndValidate, MeanCrossValidation, etc.)
        :type training_type: constants.TrainingType
        :return: Returns a fitted ensemble including all the selected models.
        """
        ensemble_iterations = cast(int, self._automl_settings.ensemble_iterations)

        ensemble_run, parent_run = self._get_ensemble_and_parent_run()
        child_runs = EnsembleBase._get_child_runs(parent_run, ensemble_run)

        primary_metric = self._automl_settings.primary_metric

        if training_type == constants.TrainingType.MeanCrossValidation:
            model_artifact_name = constants.MODEL_PATH_TRAIN
        else:
            model_artifact_name = constants.MODEL_PATH
        goal = metrics.minimize_or_maximize(task=self._automl_settings.task_type, metric=primary_metric)
        start = datetime.datetime.utcnow()

        fitted_pipelines = self._fetch_fitted_pipelines(child_runs, model_artifact_name, goal)

        elapsed = datetime.datetime.utcnow() - start
        total_pipelines_for_ensembling = len(fitted_pipelines)
        logger.info("Fetched {} fitted pipelines in {} seconds".format(total_pipelines_for_ensembling,
                                                                       elapsed.seconds))

        if total_pipelines_for_ensembling == 0:
            raise AutoMLEnsembleException(self.DOWNLOAD_RETURNED_NO_MODELS_MSG,
                                          has_pii=False, target=AutoMLEnsembleException.MISSING_MODELS)

        start = datetime.datetime.utcnow()
        selector = self._run_ensemble_selection(
            fitted_models=fitted_pipelines,
            training_type=training_type,
            primary_metric=primary_metric,
            ensemble_iterations=ensemble_iterations)

        elapsed = datetime.datetime.utcnow() - start
        logger.info("Selected the pipelines for the ensemble in {0} seconds".format(elapsed.seconds))

        # selector has selected, so ensemble/weights should not be none
        self._save_ensemble_metrics(
            ensemble_run,
            cast(List[int], selector.unique_ensemble),
            cast(List[float], selector.unique_weights),
            fitted_pipelines)
        self.estimator, scoring_ensembles = self._create_ensembles(fitted_pipelines, selector)
        return self.estimator, scoring_ensembles

    def predict(self, X):
        """
        Predicts the target for the provided input.

        :param X: Input test samples.
        :type X: numpy.ndarray or scipy.sparse.spmatrix
        :return: Prediction values.
        """
        if self.estimator is None:
            raise AutoMLEnsembleException('Ensemble must be fitted first before calling predict using fit_ensemble().',
                                          target=AutoMLEnsembleException.MODEL_NOT_FIT, has_pii=False)

        return self.estimator.predict(X)

    def predict_proba(self, X):
        """
        Return the probability estimates for the input dataset.

        :param X: Input test samples.
        :type X: numpy.ndarray or scipy.sparse.spmatrix
        :return: Prediction probabilities values.
        """
        if self.estimator is None:
            raise AutoMLEnsembleException('Ensemble must be fitted first before calling predict using fit_ensemble().',
                                          target=AutoMLEnsembleException.MODEL_NOT_FIT, has_pii=False)

        if not hasattr(self.estimator, 'predict_proba'):
            raise AutoMLEnsembleException("Estimator doesn't have a predict_proba method.", has_pii=False)

        return self.estimator.predict_proba(X)

    def _fetch_fitted_pipelines(self, child_runs: List[Run], model_artifact_name: str, goal: str) -> \
            List[Tuple[int, Any, str, Run, str]]:
        """
        Download and deserialize models from the given child runs.

        :param child_runs: list of child runs to download models for
        :param model_artifact_name: name of the model filename in artifact store
        :param goal: the training goal to check score against
        :return: a list of trained models with supporting metadata
        """
        # first we'll filter out any other Ensemble iteration models or failed iterations (with score = nan)
        run_scores = []
        for child in child_runs:
            properties = child.get_properties()
            if properties.get('pipeline_id', "") in constants.EnsembleConstants.ENSEMBLE_PIPELINE_IDS or \
                    properties.get('score', 'nan') == 'nan':
                continue
            run_scores.append((child, float(properties.get('score'))))
        num_models_for_ensemble = min(self.MAXIMUM_MODELS_FOR_SELECTION, len(run_scores))

        sort_reverse_order = False
        if goal == constants.OptimizerObjectives.MAXIMIZE:
            sort_reverse_order = True
        # we'll sort the iterations based on their score from best to worst depending on the goal
        # and then we'll prune the list
        candidates = sorted(run_scores, key=lambda tup: tup[1], reverse=sort_reverse_order)[0:num_models_for_ensemble]
        logger.info("Fetching fitted models for best {0} previous iterations".format(num_models_for_ensemble))

        with log_utils.log_activity(logger=logger,
                                    activity_name=constants.TelemetryConstants.DOWNLOAD_ENSEMBLING_MODELS):
            results = self._download_fitted_models_for_child_runs([run for run, score in candidates],
                                                                  model_artifact_name)

        fitted_pipelines = []
        for (child_run, fitted_pipeline, ex) in results:
            if ex is not None:
                logger.warning("Failed to read the fitted pipeline for iteration {0}".format(child_run.id))
                log_utils.log_traceback(ex, logger)
                continue
            properties = child_run.get_properties()
            iteration = int(properties.get('iteration', 0))
            algo_name = properties.get('run_algorithm', 'Unknown')
            pipeline_spec = properties.get('pipeline_spec', None)
            if fitted_pipeline is None:
                logger.error("The fitted pipeline for iteration {0} was None.".format(child_run.id))
            fitted_pipelines.append((iteration, fitted_pipeline, algo_name, child_run, pipeline_spec))
        return fitted_pipelines

    def _download_fitted_models_for_child_runs(self, child_runs: List[Run], model_remote_path: str) -> \
            List[Tuple[Run, Optional[Any], Optional[BaseException]]]:
        """
        Download models for all given child runs.

        :param child_runs: list of child runs to download models for
        :param model_remote_path: name of the model filename in artifact store
        :return: a list of trained models
        """
        # return result of type tuple(child_run, fitted_pipeline, ex)
        result = []
        for index, run in enumerate(child_runs):
            result.append(self._download_model(run, index, model_remote_path))
        return result

    def _create_fully_fitted_ensemble_estimator_tuples(
            self, fitted_pipelines: List[Any], unique_ensemble: List[int]) -> List[Tuple[str, Any]]:
        """
        Get supporting metadata for all pipelines in the given ensemble.

        :param fitted_pipelines: list of all previous fitted pipelines
        :param unique_ensemble: list of indices for models which will be used in the ensemble
        :return: a list of (iteration, pipeline) tuples for models used in the ensemble
        """
        ensemble_estimator_tuples = []
        # we need to download the fully trained models
        ensemble_child_runs = [fitted_pipelines[index][self.PIPELINES_TUPLES_CHILD_RUN_INDEX]
                               for index in unique_ensemble]
        results = self._download_fitted_models_for_child_runs(ensemble_child_runs, constants.MODEL_PATH)

        for (child_run, fitted_pipeline, ex) in results:
            if ex is not None:
                logger.warning("Failed to read the fully fitted model for iteration {0}".format(child_run.id))
                log_utils.log_traceback(ex, logger)
                continue
            properties = child_run.get_properties()
            iteration = properties.get('iteration')
            ensemble_estimator_tuples.append((str(iteration), fitted_pipeline))
        return ensemble_estimator_tuples

    @staticmethod
    def _download_model(child_run: Run, index: int, remote_path: str) -> \
            Tuple[Run, Optional[Any], Optional[BaseException]]:
        """
        Download the model for the given child run.

        :param child_run: the child run object
        :param index: the iteration number of the child run
        :param remote_path: the remote path of the model file
        :return: a tuple of the run object, the model file, and an exception object if any
        """
        local_model_file = 'model_{}.pkl'.format(uuid.uuid4())
        e = None  # type: Optional[Exception]
        fitted_pipeline = None
        try:
            child_run.download_file(
                name=remote_path, output_file_path=local_model_file, _validate_checksum=True)
            logger.info("Downloaded fitted pipeline(s) of size {0} for child run {1}".format(
                os.path.getsize(local_model_file), child_run.id))
            with open(local_model_file, "rb") as model_file:
                fitted_pipeline = pickle.load(model_file)

            if isinstance(fitted_pipeline, list):
                # for the case of CV split trained pipeline list
                fitted_pipeline = list([EnsembleBase._transform_single_fitted_pipeline(pip) for pip
                                        in fitted_pipeline])
                logger.info("Finished transforming the fitted pipelines for child run {} with {} elements.".format(
                    child_run.id, len(fitted_pipeline)))
            else:
                fitted_pipeline = EnsembleBase._transform_single_fitted_pipeline(fitted_pipeline)
                logger.info("Finished transforming the fitted pipeline for child run {}.".format(
                    child_run.id))
        except EOFError as ex:
            e = AutoMLEnsembleException.from_exception(
                ex, "EOFError for child_run {0} at remote path {1}".format(child_run.id, remote_path), has_pii=False)
        except Exception as ex:
            e = ex
        finally:
            try:
                if local_model_file is not None:
                    os.remove(local_model_file)
            except Exception as ex:
                logger.warning("Failed to cleanup temp model file: {0}".format(local_model_file))
                log_utils.log_traceback(ex, logger)

        return child_run, fitted_pipeline, e

    def _save_ensemble_metrics(
            self,
            ensemble_run: Run,
            unique_ensemble: List[int],
            unique_weights: List[float],
            fitted_pipelines: List[Any]
    ) -> None:
        """
        Save information for the given ensemble to tags.

        :param ensemble_run: the ensemble run object
        :param unique_ensemble: the list of iteration numbers used in the ensemble
        :param unique_weights: the list of model weights used in the ensemble
        :param fitted_pipelines: the list of models used in the ensemble
        :return:
        """
        try:
            chosen_iterations = []
            chosen_algorithms = []
            chosen_run_ids = []
            for index in unique_ensemble:
                chosen_iterations.append(fitted_pipelines[index][self.PIPELINES_TUPLES_ITERATION_INDEX])
                chosen_algorithms.append(fitted_pipelines[index][self.PIPELINES_TUPLES_ALGORITHM_INDEX])
                chosen_run_ids.append(fitted_pipelines[index][self.PIPELINES_TUPLES_CHILD_RUN_INDEX].id)

            # because the pipelines are sorted based on their score, we can get the best individual iteration easily
            best_individual_pipeline = fitted_pipelines[0][self.PIPELINES_TUPLES_CHILD_RUN_INDEX]
            ensemble_properties = {}
            str_chosen_iterations = str(chosen_iterations)
            str_chosen_algorithms = str(chosen_algorithms)
            str_chosen_run_ids = str(chosen_run_ids)
            ensemble_properties['ensembled_iterations'] = str_chosen_iterations
            ensemble_properties['ensembled_algorithms'] = str_chosen_algorithms
            ensemble_properties['ensembled_run_ids'] = str_chosen_run_ids
            ensemble_properties['ensemble_weights'] = str(unique_weights)

            best_individual_score = best_individual_pipeline.get_properties().get('score', 'nan')
            best_individual_iteration = best_individual_pipeline.get_properties().get('iteration', '-1')
            ensemble_properties['best_individual_pipeline_score'] = best_individual_score
            ensemble_properties['best_individual_iteration'] = best_individual_iteration
            ensemble_run.add_properties(ensemble_properties)
            logger.info("Ensembled iterations: {0}. Ensembled algos: {1}"
                        .format(str_chosen_iterations, str_chosen_algorithms))
        except Exception:
            logger.warning("Failed to save the ensemble metrics into the ensemble Run instance")

    def _run_ensemble_selection(self,
                                fitted_models: List[Any],
                                training_type: constants.TrainingType,
                                primary_metric: str,
                                ensemble_iterations: int) -> EnsembleSelector:
        """
        Select which models to run ensembling on from the given models.

        :param fitted_models: the list of fitted models to select from
        :param training_type: the training type
        :param primary_metric: the metric to check against
        :param ensemble_iterations: the number of iterations to run ensembling on
        :return:
        """
        expr_store = ExperimentStore.get_instance()
        # encapsulated into own method for easier testing
        pipelines = [model_tuple[self.PIPELINES_TUPLES_PIPELINE_INDEX] for model_tuple in fitted_models]
        validation_data = []  # type: List[MaterializedTabularData]
        if training_type == constants.TrainingType.TrainAndValidation:
            X, y, weights = expr_store.data.materialized.get_valid()
            validation_data.append(MaterializedTabularData(X, y, weights))
        else:
            # CV case
            for split in expr_store.data.materialized.get_CV_splits():
                X = split._X_test_transformed
                y = split._y_test
                weights = split._sample_wt_test
                validation_data.append(MaterializedTabularData(X, y, weights))

        if expr_store.metadata.task_type == constants.Tasks.CLASSIFICATION:
            return run_ensemble_selection(
                task_type=expr_store.metadata.task_type,
                training_type=training_type,
                fitted_models=pipelines,
                validation_data=validation_data,
                metric_to_optimize=primary_metric,
                class_labels=expr_store.metadata.classification.class_labels,
                y_transformer=expr_store.transformers.get_y_transformer(),
                y_min=None,
                y_max=None,
                selection_iterations=ensemble_iterations
            )
        else:
            return run_ensemble_selection(
                task_type=expr_store.metadata.task_type,
                training_type=training_type,
                fitted_models=pipelines,
                validation_data=validation_data,
                metric_to_optimize=primary_metric,
                class_labels=None,
                y_transformer=None,
                y_min=expr_store.metadata.regression.get_y_range()[0],
                y_max=expr_store.metadata.regression.get_y_range()[1],
                selection_iterations=ensemble_iterations
            )

    @staticmethod
    def _get_child_runs(parent_run, ensemble_run):
        """Get the child runs to ensemble."""
        if isinstance(ensemble_run, OfflineAutoMLRun):
            return OfflineAutoMLRunUtil.get_all_sibling_child_runs(ensemble_run)
        else:
            childrenToReturn = []
            for child in parent_run.get_children():
                # if child level run is hyperparameter tuning run, we need to fetch its children to ensemble
                pipeline_id = child.get_properties().get('pipeline_id', "")
                if pipeline_id == constants.HyperparameterSweepingConstants.AutoHPTuningParentPipelineId:
                    childrenToReturn += child.get_children()
                else:
                    childrenToReturn.append(child)
            return childrenToReturn

    @staticmethod
    def _transform_single_fitted_pipeline(fitted_pipeline):
        # for performance reasons we'll transform the data only once inside the ensemble,
        # by adding the transformers to the ensemble pipeline (as preprocessor steps, inside _automl.py).
        # Because of this, we need to remove any AutoML transformers from all the fitted pipelines here.
        modified_steps = [step[1] for step in fitted_pipeline.steps
                          if step[0] not in constants.Transformers.ALL]
        if len(modified_steps) != len(fitted_pipeline.steps):
            return make_pipeline(*[s for s in modified_steps])
        else:
            return fitted_pipeline

    @abstractmethod
    def _get_ensemble_and_parent_run(self):
        pass

    @abstractmethod
    def _create_ensembles(self, fitted_pipelines, selector):
        pass
