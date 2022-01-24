# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for selecting algorithms for AutoMLs ensembling feature."""
from typing import Any, cast, List, Optional, Sized, Tuple, Union
from collections import Counter
import logging

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared._diagnostics.automl_error_definitions import InvalidArgumentWithSupportedValues
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.reference_codes import ReferenceCodes

from sklearn.base import TransformerMixin
from sklearn.pipeline import Pipeline
import numpy as np
from azureml.automl.core.shared import constants
from azureml.automl.core.shared.exceptions import ConfigException
from azureml.automl.runtime._data_definition import MaterializedTabularData
from azureml.automl.runtime.shared.score import _scoring_utilities
from azureml.automl.runtime import _ml_engine


logger = logging.getLogger(__name__)


class EnsembleSelector:
    """Ensembling Selection Algorithm following Caruana's Ensemble Selection from Library of Models paper."""

    # during the greedy selection phase, we will choose only the models within X % of the best score
    SELECTION_GREEDY_SCORE_THRESHOLD = 0.05
    # maximum number of pipelines to start the ensemble with
    MAXIMUM_PIPELINES_IN_GREEDY_PHASE = 5

    def __init__(self,
                 task_type: str,
                 training_type: constants.TrainingType,
                 fitted_models: List[Union[Pipeline, List[Pipeline]]],
                 validation_data: List[MaterializedTabularData],
                 metric: str,
                 class_labels: Optional[np.ndarray] = None,
                 y_transformer: Optional[TransformerMixin] = None,
                 y_min: Optional[float] = None,
                 y_max: Optional[float] = None,
                 selection_iterations: int = 10) -> None:
        """Create EnsembleSelector used for choosing the pipelines that should be part of an ensemble.

        Arguments:
            :param task_type: The ML Task type
            :type task_type: str
            :param training_type: Type of training (eg: TrainAndValidate split, CrossValidation split, etc.)
            :type training_type: constants.TrainingType enumeration
            :param fitted_models: A list containing the fitted pipelines associated to AutoML iterations
                The pipelines should be sorted based on their primary metric score.
            :type fitted_models: list of Pipeline or List of List of Pipeline (for CrossValidation)
            :param validation_data: List of 1 or more datasets to use during selection (not trained on by the models)
            :type validation_data: List of MaterializedTabularData
            :param metric: The metric that we're optimizing for during the selection algorithm
            :type metric: str

        Keyword Arguments:
            :param class_labels: The Array of classes for Classification task
            :type class_labels: numpy.ndarray
            :param y_transformer: Transformer for label column for Classification task
            :type y_transformer: TransformerMixin
            :param y_min: Minimum value of the target column for Regression tasks
            :type y_min: float
            :param y_max: Maximum value of the target column for Regression tasks
            :type y_max: float
            :type y_transformer: TransformerMixin
            :param selection_iterations: Number of iterations for Selection algorithm (default: {10})
            :type selection_iterations: int
        """
        # Ensembling is expected to only be called for classification and regression tasks, and is only called
        # by internal clients.
        self.task_type = self._get_validated_task_type(task_type)

        Contract.assert_true(
            selection_iterations >= 1,
            "Number of iterations ({}) is less than 1".format(selection_iterations),
            target="selection_iterations", log_safe=True)

        if training_type == constants.TrainingType.TrainAndValidation:
            Contract.assert_true(
                len(validation_data) == 1,
                message="When doing Train/Validation split, validation_data should contain a single element",
                target="validation_data",
                reference_code=ReferenceCodes._ENSEMBLE_SELECTOR_INVALID_VALIDATION_DATA,
                log_safe=True)

        self.validation_data = validation_data

        self.fitted_models = fitted_models
        self.training_type = training_type
        self.metric = metric
        self.metric_objective = EnsembleSelector._get_validated_metric_objective(self.task_type, metric)

        self.iterations = selection_iterations
        self.model_count = len(fitted_models)

        self.class_labels = None
        self.num_classes = 1
        self.y_min = None
        self.y_max = None
        if self.task_type == constants.Tasks.CLASSIFICATION:
            Contract.assert_value(class_labels, "class_labels",
                                  reference_code=ReferenceCodes._ENSEMBLE_SELECTOR_INVALID_CLASS_LABELS)
            self.class_labels = cast(np.ndarray, class_labels)
            self.num_classes = len(self.class_labels)
        else:
            self.y_min = y_min
            self.y_max = y_max

        self.y_transformer = y_transformer
        self.unique_ensemble = None  # type: Optional[List[int]]
        self.unique_weights = None  # type: Optional[List[float]]
        self.predictions = None  # type: Optional[np.ndarray]
        self.y_valid = None  # type: Optional[np.ndarray]
        self.sample_weight_valid = None  # type: Optional[np.ndarray]
        self.cross_validate_indices = None  # type: Optional[List[Tuple[int, int]]]

    def select(self) -> Tuple[List[int], List[float]]:
        """Select fitted pipelines that should be part of the Ensemble."""
        if self.iterations == 1:
            # short circuiting for the case of 1 iteration
            # so that we don't do any extra compute in the selection phases
            initial_size = 1
        else:
            initial_size = min(EnsembleSelector.MAXIMUM_PIPELINES_IN_GREEDY_PHASE, self.iterations // 2)

        logger.debug("Initial size {0}".format(initial_size))

        self._compute_models_predictions()

        # prime the ensemble list with the models having the best scores
        single_model_scores = np.zeros(self.model_count)
        for i in range(self.model_count):
            single_model_scores[i] = self._get_model_score(cast(np.ndarray, self.predictions)[:, :, i])
        logger.info("Single models scores: {0}".format(single_model_scores))

        # the fitted pipelines are already sorted based on their scores from best to worst
        # then we need to choose the best initial ones to start the ensemble with
        if self.metric_objective == constants.OptimizerObjectives.MAXIMIZE:
            # compute the threshold score based on the best individual score
            if single_model_scores[0] > 0:
                threshold_score = (1 - EnsembleSelector.SELECTION_GREEDY_SCORE_THRESHOLD) * single_model_scores[0]
            else:
                threshold_score = (1 + EnsembleSelector.SELECTION_GREEDY_SCORE_THRESHOLD) * single_model_scores[0]
            count = np.sum(single_model_scores >= threshold_score)
            initial_size = min(count, initial_size)
        else:
            # compute the threshold score based on the best individual score
            if single_model_scores[0] > 0:
                threshold_score = (1 + EnsembleSelector.SELECTION_GREEDY_SCORE_THRESHOLD) * single_model_scores[0]
            else:
                threshold_score = (1 - EnsembleSelector.SELECTION_GREEDY_SCORE_THRESHOLD) * single_model_scores[0]
            count = np.sum(single_model_scores <= threshold_score)

            initial_size = min(count, initial_size)
        # we'll just take the first elements within that list for starting the ensemble.
        ensemble = list(range(0, initial_size))
        # after priming the ensemble, we'll need to keep on adding
        # models to it until we reach the desired count
        number_of_models_needed = self.iterations - len(ensemble)

        # as we try to create ensembles, we'll maintain the one that had the best score
        best_ensemble = list(ensemble)
        best_ensemble_score = self._get_ensemble_score(best_ensemble)

        logger.info("Starting ensemble hill climbing. Current ensemble: {0}, current score: {1}"
                    .format(best_ensemble, best_ensemble_score))

        # Currently we only support ensemble selection with replacement.
        # This means we allow a model to be added multiple times to the ensemble during the selection steps.
        # In the end we extract the unique models and assign them weights based on how many times
        # they got added during selection.
        for iteration in range(number_of_models_needed):
            scores = np.zeros([self.model_count])
            for j in range(len(self.fitted_models)):
                # we'll temporarily add this model to the ensemble and will simulate
                # the overall score of the resulting ensemble
                ensemble.append(j)

                # get the score of this simulated ensemble
                scores[j] = self._get_ensemble_score(ensemble)

                logger.debug("Iteration {0}. Simulating ensemble: {1} yielded score {2}"
                             .format(iteration, ensemble, scores[j]))

                # remove this model from the ensemble and continue with another
                ensemble.pop()

            # after we've tried the end-score with each of the individual ensembles,
            # get the best one from this iteration
            best, current_ensemble_score = self._choose_best_model_for_ensemble(scores, single_model_scores)
            ensemble.append(best)
            logger.debug("Iteration {0}, current ensemble: {1}, current score :{2}"
                         .format(iteration, ensemble, current_ensemble_score))

            # if the current ensemble beats our best one, update our references
            if self._is_ensemble_improving(best_ensemble_score, current_ensemble_score):
                best_ensemble = list(ensemble)
                best_ensemble_score = current_ensemble_score
                logger.info("Iteration {0}, new best ensemble: {1}, new best score :{2}"
                            .format(iteration, ensemble, current_ensemble_score))

        weights = self._compute_weights(best_ensemble)
        logger.info("Final ensemble: {0}, score: {1}. Best individual model score: {2}"
                    .format(best_ensemble, best_ensemble_score, single_model_scores[ensemble[0]]))

        unique_ensemble = list(set(best_ensemble))

        unique_weights = [weights[i] for i in unique_ensemble if weights[i] > 0]

        logger.info("Unique models IDs in the ensemble: {0}. Weights: {1}"
                    .format(unique_ensemble, unique_weights))
        self.unique_ensemble = unique_ensemble
        self.unique_weights = unique_weights
        return self.unique_ensemble, self.unique_weights

    def _choose_best_model_for_ensemble(self, ensemble_scores, single_model_scores):
        best_score = None
        if self.metric_objective == constants.OptimizerObjectives.MAXIMIZE:
            # first we need to find what's the maximum score for the ensembles simulated
            best_score = np.nanmax(ensemble_scores)
            # then find the model indices that maximized the ensemble (there can be multiple)
            maximum_score_indices = np.where(ensemble_scores == best_score)[0]
            # if there are multiple single models, choose the best one (the one that has maximum individual score)
            best = maximum_score_indices[np.nanargmax(
                [single_model_scores[i] for i in maximum_score_indices])]
        else:
            # similarly if we need to minimize the score, do same thing but look for the minimum score
            best_score = np.nanmin(ensemble_scores)
            minimum_score_indices = np.where(ensemble_scores == best_score)[0]
            best = minimum_score_indices[np.nanargmin(
                [single_model_scores[i] for i in minimum_score_indices])]
        return best, best_score

    def _is_ensemble_improving(self, old_score, current_score):
        if self.metric_objective == constants.OptimizerObjectives.MAXIMIZE:
            return current_score > old_score
        else:
            return current_score < old_score

    def _compute_models_predictions(self):
        # 3 dimensional array [validationSetSize, numberOfClasses, numberOfModels]
        X_valid = None
        y_valid = None
        cross_validate_indices = None  # type: Optional[List[Tuple[int, int]]]

        if self.training_type == constants.TrainingType.TrainAndValidation:
            val_data = self.validation_data[0]
            X_valid = val_data.X
            y_valid = val_data.y
            sample_weight_valid = val_data.weights
            validation_set_size = X_valid.shape[0]
            predictions = np.zeros((validation_set_size, self.num_classes, self.model_count))

            for index, pipeline in enumerate(self.fitted_models):
                # the tuple is (iterationIndex, pipeline, algo_name)
                logger.info('Getting out of fold predictions of pipeline index {}.'.format(index))
                if pipeline is None:
                    logger.info('The fitted pipeline was found to be None for index {}'.format(index))
                    continue

                # In classification tasks, we need to check the train_labels per model
                # even during train/valid because models may have seen a subset of data
                # and classes may be missing. If the pipeline doesn't have a classes_
                # attribute, we assume regression and pass None (as trained_class_labels
                # is unused in the regression path).
                predictions[:, :, index] = self._get_model_predictions(pipeline,
                                                                       X_valid)

        elif self.training_type == constants.TrainingType.MeanCrossValidation:
            # we'll first arrange the y_valid and the weights to follow the same order as CV folds
            # we don't care about the X_valid, because we anyhow generate the predictions at this time
            # so we'll use them for computing the scores throughout the selection process.
            sample_weight_valid = None
            for split_index, val_data in enumerate(self.validation_data):
                y_valid_fold = val_data.y
                sample_wt_valid_fold = val_data.weights
                if split_index == 0:
                    cross_validate_indices = [(0, len(y_valid_fold))]
                    y_valid = y_valid_fold
                    sample_weight_valid = sample_wt_valid_fold
                else:
                    prev_length = len(cast(Sized, y_valid))
                    cast(List[Tuple[int, int]], cross_validate_indices)\
                        .append((prev_length, prev_length + len(y_valid_fold)))
                    y_valid = np.concatenate((y_valid, y_valid_fold))
                    if sample_wt_valid_fold is not None:
                        sample_weight_valid = np.concatenate((sample_weight_valid, sample_wt_valid_fold))

            predictions = np.zeros((cast(np.ndarray, y_valid).shape[0], self.num_classes, self.model_count))

            for index, cv_pipelines in enumerate(self.fitted_models):
                temp = None
                for split_index, val_data in enumerate(self.validation_data):
                    X_valid_fold = val_data.X
                    y_valid_fold = val_data.y
                    sample_wt_valid_fold = val_data.weights
                    logger.info('Getting out of fold predictions of pipeline index {} for CV fold {}'.format(
                        index, split_index))
                    pipeline = cv_pipelines[split_index]
                    model_predictions = self._get_model_predictions(pipeline,
                                                                    X_valid_fold)

                    if split_index == 0:
                        temp = model_predictions
                    else:
                        temp = np.concatenate((temp, model_predictions))
                predictions[:, :, index] = temp
        else:
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentWithSupportedValues, target="training_type",
                    arguments="training_type ({})".format(str(self.training_type)), supported_values=", ".join(
                        constants.TrainingType.FULL_SET),
                    reference_code=ReferenceCodes._ENSEMBLE_SELECTOR_INVALID_TRAINING_TYPE
                )
            )
        # store these as instance fields for later reuse inside this class' methods
        self.predictions = predictions
        self.y_valid = y_valid
        self.sample_weight_valid = sample_weight_valid
        self.cross_validate_indices = cross_validate_indices

    def _get_model_predictions(self, model, validation_set):
        if self.task_type == constants.Tasks.CLASSIFICATION:
            Contract.assert_true(
                hasattr(model, 'predict_proba'), message="model object {} doesn't expose predict_proba method".format(
                    type(model).__name__), log_safe=True)

            result = model.predict_proba(validation_set)
            # let's make sure all the predictions have same number of columns
            result = _scoring_utilities.pad_predictions(result, model.classes_, self.class_labels)
        else:
            # for regression models, we'll use predict method
            result = model.predict(validation_set)[:, None]
        return result

    def _get_ensemble_predictions(self, ensemble_list: List[int]) -> np.ndarray:
        # slice the predictions array to only contain the predictions for the
        # members of the ensemble
        assert self.predictions is not None
        predictions_sliced = self.predictions[:, :, np.array(ensemble_list)]
        if self.cross_validate_indices is None:
            return self._get_ensemble_predictions_simple(predictions_sliced)
        else:
            # we'll do similar procedure as above, but for each fold separately
            ensemble_predictions = None
            for cv_indices in self.cross_validate_indices:
                temp = self._get_ensemble_predictions_simple(predictions_sliced[cv_indices[0]:cv_indices[1]])
                if ensemble_predictions is None:
                    ensemble_predictions = temp
                else:
                    ensemble_predictions = np.concatenate((ensemble_predictions, temp))
            return cast(np.ndarray, ensemble_predictions)

    def _get_ensemble_predictions_simple(self, predictions: np.ndarray) -> np.ndarray:
        # predictions is 3 dimensional array [validationSetSize, numberOfClasses, numberOfModels]
        # we compute the average from the predictions of each model
        temp = predictions.mean(2)  # type: np.ndarray
        if self.task_type == constants.Tasks.CLASSIFICATION:
            # for classification we normalize the avg class probability.
            # this is to make sure they are summing up to 1 (or 100%)
            temp /= temp.sum(1)[:, None]
        else:
            temp = temp[:, None]
        return temp

    def _get_ensemble_score(self, ensemble_list):
        predictions = self._get_ensemble_predictions(ensemble_list)
        return self._get_model_score(predictions)

    def _get_model_score(self, model_predictions: np.ndarray) -> float:
        # compute scores on the predictions array slice corresponding to that model index
        if self.task_type == constants.Tasks.REGRESSION:
            y_pred = model_predictions[:, 0]
        else:
            y_pred = model_predictions

        # we shouldn't be passing the trained_class_labels to the metrics calculation,
        # because we've already padded the predictions inside this class.
        # otherwise, metrics calculation might be doing double padding.
        model_score = None
        if self.cross_validate_indices is None:
            # all the predictions are for a single model
            y_test = cast(np.ndarray, self.y_valid)
            if self.task_type == constants.Tasks.CLASSIFICATION:
                # Here we use class_labels for train_labels because the padding is already done by the ensemble.
                all_metrics = _ml_engine.evaluate_classifier(
                    y_test, y_pred, [self.metric],
                    cast(np.ndarray, self.class_labels), cast(np.ndarray, self.class_labels),
                    sample_weight=self.sample_weight_valid, y_transformer=self.y_transformer
                )
            else:
                # task_type is already validated in the constructor
                Contract.assert_true(self.task_type == constants.Tasks.REGRESSION, "Unexpected task_type ({})".format(
                    self.task_type), log_safe=True)
                all_metrics = _ml_engine.evaluate_regressor(
                    y_test, y_pred, [self.metric], y_min=self.y_min, y_max=self.y_max,
                    sample_weight=self.sample_weight_valid
                )

            model_score = cast(float, all_metrics[self.metric])
        else:
            cv_scores = []
            # we'll need to slice our predictions based on the CV splits indices
            for split_index, cv_indices in enumerate(self.cross_validate_indices):
                y_pred_slice = y_pred[cv_indices[0]:cv_indices[1]]
                y_valid_slice = cast(np.ndarray, self.y_valid)[cv_indices[0]:cv_indices[1]]
                sample_weight_slice = None if self.sample_weight_valid is None \
                    else self.sample_weight_valid[cv_indices[0]:cv_indices[1]]

                if self.task_type == constants.Tasks.CLASSIFICATION:
                    # Here we use class_labels for train_labels because the padding is already
                    # done by the ensemble.
                    all_metrics = _ml_engine.evaluate_classifier(
                        y_valid_slice, y_pred_slice, [self.metric],
                        cast(np.ndarray, self.class_labels), cast(np.ndarray, self.class_labels),
                        sample_weight=sample_weight_slice, y_transformer=self.y_transformer
                    )
                else:
                    # task_type is already validated in the constructor
                    Contract.assert_true(self.task_type == constants.Tasks.REGRESSION,
                                         "Unexpected task_type ({})".format(self.task_type), log_safe=True)
                    all_metrics = _ml_engine.evaluate_regressor(
                        y_valid_slice, y_pred_slice, [self.metric], y_min=self.y_min, y_max=self.y_max,
                        sample_weight=sample_weight_slice
                    )

                cv_scores.append(all_metrics[self.metric])
            model_score = float(np.nanmean(cv_scores))
        return model_score

    def _compute_weights(self, ensemble):
        # create a list with the count of occurrences of each model inside the
        # ensemble : Tuple<modelIndex, count>
        occurrences = Counter(ensemble).most_common()  # type: List[Any]
        weights = np.zeros(self.model_count, dtype=float)
        for occurrence_tuple in occurrences:
            weights[occurrence_tuple[0]] = float(occurrence_tuple[1]) / len(ensemble)

        return weights

    @staticmethod
    def _get_validated_task_type(task_type: str) -> str:
        """
        Validate and return the task type used for training.
        :param task_type: The ML Task type
        :return: The task type (i.e. 'classification' or 'regression')
        :raises ValidationError (with System error classification)
        """
        # Ensembling is expected to only be called for classification and regression tasks, and is only called
        # by internal clients.
        Contract.assert_true(task_type in [constants.Tasks.CLASSIFICATION, constants.Tasks.REGRESSION],
                             message="Ensembling unsupported for the given task_type ({})".format(task_type),
                             target="task_type",
                             reference_code=ReferenceCodes._ENSEMBLE_SELECTOR_INVALID_TASK_TYPE,
                             log_safe=True)
        return task_type

    @staticmethod
    def _get_validated_metric_objective(task_type: str, metric: str) -> str:
        """
        Validate and return the metric objective based on task type

        :param task_type: Either 'classification' or 'regression'
        :param metric: Metric to optimize for
        :return: Metric objective
        :raises ValidationError (with System error classification)
        """
        if task_type == constants.Tasks.CLASSIFICATION and metric in constants.Metric.CLASSIFICATION_SET:
            result = constants.MetricObjective.Classification[metric]
        else:
            Contract.assert_true(
                (task_type == constants.Tasks.REGRESSION and metric in constants.Metric.REGRESSION_SET),
                message="Ensembling unsupported for the given task_type/metric ({}/{}). Supported values: {}".format(
                    task_type, metric,
                    ", ".join(list(constants.Metric.CLASSIFICATION_SET | constants.Metric.REGRESSION_SET))
                ), target="metric", reference_code=ReferenceCodes._ENSEMBLE_SELECTOR_INVALID_METRIC, log_safe=True
            )
            result = constants.MetricObjective.Regression[metric]
        return result
