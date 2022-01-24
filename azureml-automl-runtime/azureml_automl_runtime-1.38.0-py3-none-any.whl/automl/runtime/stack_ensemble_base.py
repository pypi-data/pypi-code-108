# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Base module for ensembling previous AutoML iterations."""
from typing import Any, Dict, Tuple, Type, Union
from abc import ABC
import json
import logging
import numpy as np
import pandas as pd
import typing

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared._diagnostics.automl_error_definitions import InvalidArgumentWithSupportedValues
from azureml.automl.runtime._data_definition import MaterializedTabularData
from sklearn import base
from sklearn import linear_model
from sklearn import model_selection

from azureml.automl.runtime import ensemble_base
from azureml.automl.runtime._ml_engine.ensemble import EnsembleSelector
from azureml.automl.core import _codegen_utilities
from azureml.automl.core.automl_base_settings import AutoMLBaseSettings
from azureml.automl.core.shared import constants
from azureml.automl.core.shared import utilities
from azureml.automl.core.shared.exceptions import ConfigException
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.runtime import _ml_engine
from azureml.automl.runtime.experiment_store import ExperimentStore
from azureml.automl.runtime.featurizer.transformer.timeseries import timeseries_transformer
from azureml.automl.runtime.shared import model_wrappers
from azureml.automl.runtime.shared import pipeline_spec as pipeline_spec_module
from azureml.automl.runtime.shared.score import _scoring_utilities
from azureml.automl.runtime.shared.time_series_data_frame import construct_tsdf
from azureml.automl.runtime.shared.types import DataInputType, DataSingleColumnInputType
from azureml.automl.runtime.subsample_utilities import subsample_train_valid_set


logger = logging.getLogger(__name__)


class StackEnsembleBase(ensemble_base.EnsembleBase, ABC):
    """
    Class for creating a Stacked Ensemble based on previous AutoML iterations.

    The ensemble pipeline is initialized from a collection of already fitted pipelines.
    """

    def __init__(self, automl_settings: Union[str, Dict[str, Any], AutoMLBaseSettings],
                 settings_type: 'Type[ensemble_base.SettingsType]') -> None:
        """Create an Ensemble pipeline out of a collection of already fitted pipelines.

        :param automl_settings: settings for the AutoML experiments.
        :param settings_type: the type for the settings object.
        """
        super(StackEnsembleBase, self).__init__(automl_settings, settings_type)
        self._meta_learner_type = getattr(self._automl_settings, "stack_meta_learner_type", None)
        self._meta_learner_kwargs = getattr(self._automl_settings, "stack_meta_learner_kwargs", None)

    def _create_ensembles(self, fitted_pipelines, selector):
        """
        Create an ensemble estimator using the given pipelines and selector.

        :param fitted_pipelines: list of trained models to select from
        :param selector: ensemble selector object
        :return: a stack ensemble estimator plus estimators for cross validations/scoring set
        """
        logger.info("Creating a Stack Ensemble out of iterations: {}".format(selector.unique_ensemble))
        result = None
        if selector.training_type == constants.TrainingType.TrainAndValidation:
            result = self._create_stack_ensembles_train_validation(fitted_pipelines, selector)
        elif selector.training_type == constants.TrainingType.MeanCrossValidation:
            result = self._create_stack_ensembles_cross_validation(fitted_pipelines,
                                                                   selector)
        else:
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentWithSupportedValues, target="training_type",
                    arguments="training_type ({})".format(selector.training_type),
                    supported_values=", ".join(constants.TrainingType.FULL_SET)
                )
            )
        if selector.task_type == constants.Tasks.CLASSIFICATION:
            # For cases when the base learner predictions have been padded so that all models have the same
            # shape, we'll have to ensure the StackEnsemble is aware of all classes involved in the padding.
            # For that, we'll have to override the classes_ attribute so that when later predicting, it'll apply
            # the same padding logic as it was applied during training.
            # The padding cases can happen in case of doing Cross Validation, when different folds see different
            # subset of classes, or in case subsample kicks in.
            result[0].classes_ = selector.class_labels
            for scoring_ensemble in result[1]:
                scoring_ensemble.classes_ = selector.class_labels

        return result

    def _create_stack_ensembles_train_validation(
        self,
        fitted_pipelines,
        selector
    ):
        """
        Create an ensemble estimator using the given pipelines and selector.

        :param fitted_pipelines: list of trained models to select from
        :param selector: ensemble selector object
        :return: a stack ensemble estimator plus estimator for scoring set
        """
        expr_store = ExperimentStore.get_instance()
        logger.info('Splitting the StackEnsemble training set for fitting the meta learner.')
        X_base_train, X_meta_train, y_base_train, y_meta_train, sample_weight_base_train, sample_weight_meta_train = \
            self._split_train_set_for_scoring_train_valid()

        _, y_valid, sample_weight_valid = expr_store.data.materialized.get_valid()
        self._meta_learner_type, self._meta_learner_kwargs = self._determine_meta_learner_type([y_valid, y_meta_train])

        # for this type of training, we need the meta_model to be trained on the predictions
        # over the validation set from all the base learners.
        # This will be the ensemble returned for predictions on new data.
        all_prediction_list = []
        base_learners_tuples = []
        pipeline_spec_subsample_tuples = []
        for model_index in selector.unique_ensemble:
            base_learners_tuples.append(
                (str(fitted_pipelines[model_index][self.PIPELINES_TUPLES_ITERATION_INDEX]),
                 fitted_pipelines[model_index][self.PIPELINES_TUPLES_PIPELINE_INDEX]))
            pipeline_spec = fitted_pipelines[model_index][self.PIPELINES_TUPLES_PIPELINE_SPEC_INDEX]
            child_run = fitted_pipelines[model_index][self.PIPELINES_TUPLES_CHILD_RUN_INDEX]
            training_percent = float(child_run.get_properties().get('training_percent', '100'))

            pipeline_spec_subsample_tuples.append((pipeline_spec, training_percent))
            model_predictions = selector.predictions[:, :, model_index]
            # for regression we need to slice the matrix because there's a single "class" in the second dimension
            if selector.task_type == constants.Tasks.REGRESSION:
                model_predictions = model_predictions[:, 0]
            all_prediction_list.append(model_predictions)

        meta_learner_training_set = model_wrappers.StackEnsembleBase._horizontal_concat(all_prediction_list)
        meta_learner, meta_learner_supports_sample_weights = self._create_meta_learner()
        logger.info('Fitting the final meta learner of the Stack Ensemble.')
        self._fit_meta_learner(
            meta_learner, meta_learner_training_set, y_valid,
            sample_weight_valid, meta_learner_supports_sample_weights)

        fully_fitted_stack_ensemble = self._create_stack_ensemble(base_learners_tuples, meta_learner)

        scoring_meta_learner = self._train_meta_learner_for_scoring_ensemble_with_train_validate(
            X_base_train, X_meta_train, y_base_train, y_meta_train, sample_weight_base_train,
            sample_weight_meta_train, pipeline_spec_subsample_tuples)

        # after we've trained the meta learner, we can reuse the fully trained base learners (on 100% of train set)
        scoring_stack_ensemble = self._create_stack_ensemble(base_learners_tuples, scoring_meta_learner)

        return fully_fitted_stack_ensemble, [scoring_stack_ensemble]

    def _create_stack_ensembles_cross_validation(self,
                                                 fitted_pipelines,
                                                 selector):
        """
        Create an ensemble estimator using the given pipelines and selector.

        :param fitted_pipelines: list of trained models to select from
        :param selector: ensemble selector object
        :return: a stack ensemble estimator plus estimators for cross validations
        """
        # we'll need to fetch the fully fitted models for the models that will be part of the base learners
        # so far the selection algo has been using the partially fitted ones for each AUTO ML iteration
        fully_fitted_learners_tuples = self._create_fully_fitted_ensemble_estimator_tuples(fitted_pipelines,
                                                                                           selector.unique_ensemble)
        # fully_fitted_learners_tuples represents a list of tuples (iteration, fitted_pipeline)
        y_valid_full = selector.y_valid
        sample_weights_valid_full = selector.sample_weight_valid

        all_out_of_fold_predictions = []
        for model_index in selector.unique_ensemble:
            # get the vertical concatenation of the out of fold predictions from the selector
            # as they were already computed during the selection phase
            model_predictions = selector.predictions[:, :, model_index]
            if selector.task_type == constants.Tasks.REGRESSION:
                model_predictions = model_predictions[:, 0]
            all_out_of_fold_predictions.append(model_predictions)
        meta_learner_training = model_wrappers.StackEnsembleBase._horizontal_concat(all_out_of_fold_predictions)

        y_valid_folds = []
        for data_fold in selector.validation_data:
            y_valid_folds.append(data_fold.y)
        self._meta_learner_type, self._meta_learner_kwargs = self._determine_meta_learner_type(y_valid_folds)

        meta_learner, meta_learner_supports_sample_weights = self._create_meta_learner()
        self._fit_meta_learner(
            meta_learner, meta_learner_training, y_valid_full,
            sample_weights_valid_full, meta_learner_supports_sample_weights)

        fully_fitted_stack_ensemble = self._create_stack_ensemble(fully_fitted_learners_tuples, meta_learner)

        # Now we need to construct some Stack Ensembles to be used for computing the metric scores
        # we'll need to keep one fold out (holdout) from the CV folds and concatenate vertically those predictions.
        # The vertical concatenation has already happened within the EnsembleSelector.
        # The concatenated predictions will be used for training the meta model in a CV fashion
        # then we'll create a StackedEnsemble where the base learners are the partially fitted models
        # from the selected AutoML iteration which haven't seen the holdout set.
        # Again, we'll reuse the selector.predictions matrix along with the row ranges corresponding to each fold,
        # excluding each time a different range
        cross_validated_stack_ensembles = []
        # get the CV indices from selector
        # this represents the range of indices within the predictions matrix which contains
        # the partial model's (corresponding to this training fold) predictions on y_valid.
        for fold_index, cv_indices in enumerate(selector.cross_validate_indices):
            base_learners_tuples = []
            stacker_training_set = []
            # Fetch each train/validation fold from the CV splits. this will be used for training of the stacker.
            # The ensemble selector keeps track of the ranges of row indices that correspond to each out of fold
            # predictions slice within the selector.predictions matrix.
            # Here, cv_indices is an interval represented through a tuple(row_index_start, row_index_end).
            slice_to_exclude_from_predictions = range(cv_indices[0], cv_indices[1])
            for counter, model_index in enumerate(selector.unique_ensemble):
                # get the partially fitted model that hasn't been trained on this holdout set
                # this will be used as base learner for this scoring StackEnsemble
                base_learners_tuples.append(
                    (str(fitted_pipelines[model_index][self.PIPELINES_TUPLES_ITERATION_INDEX]),
                     fitted_pipelines[model_index][self.PIPELINES_TUPLES_PIPELINE_INDEX][fold_index]))
                # we'll grab all the out of fold predictions for this model excluding the holdout set.
                # these predictions will be used as training data for the meta_learner
                stacker_training_set.append(
                    np.delete(all_out_of_fold_predictions[counter],
                              slice_to_exclude_from_predictions, axis=0))
            # create the meta learner model and then fit it
            scoring_meta_learner = base.clone(meta_learner)
            meta_learner_training_set = model_wrappers.StackEnsembleBase._horizontal_concat(stacker_training_set)
            y_train_fold = np.delete(selector.y_valid, slice_to_exclude_from_predictions)
            if selector.sample_weight_valid is not None:
                sample_weights_train_fold = np.delete(selector.sample_weight_valid, slice_to_exclude_from_predictions)
            else:
                sample_weights_train_fold = None

            self._fit_meta_learner(
                scoring_meta_learner,
                meta_learner_training_set, y_train_fold,
                sample_weights_train_fold, meta_learner_supports_sample_weights)

            scoring_stack_ensemble = self._create_stack_ensemble(base_learners_tuples, scoring_meta_learner)

            cross_validated_stack_ensembles.append(scoring_stack_ensemble)

        return fully_fitted_stack_ensemble, cross_validated_stack_ensembles

    def _split_train_set_for_scoring_train_valid(self) -> Tuple[
            DataInputType, DataSingleColumnInputType, DataInputType, DataSingleColumnInputType,
            DataSingleColumnInputType, DataSingleColumnInputType]:
        expr_store = ExperimentStore.get_instance()
        # We'll need to retrain the base learners pipelines on 80% (the default) of the training set
        # and we'll use the remaining 20% to generate out of fold predictions which will
        # represent the input training set of the meta_learner.
        X, y, sample_weight = expr_store.data.materialized.get_train()

        meta_learner_train_percentage = getattr(
            self._automl_settings, "stack_meta_learner_train_percentage",
            constants.EnsembleConstants.DEFAULT_TRAIN_PERCENTAGE_FOR_STACK_META_LEARNER)

        if self._automl_settings.is_timeseries:
            ts_params_dict = utilities._get_ts_params_dict(self._automl_settings) or {}
            grains = ts_params_dict.get(constants.TimeSeries.GRAIN_COLUMN_NAMES)
            if grains is None:
                grains = [constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN]  # type: ignore
            if isinstance(grains, str):
                grains = [grains]  # type: ignore
            tsdf = construct_tsdf(
                X.reset_index(),
                y,
                constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN,
                ts_params_dict.get(constants.TimeSeries.TIME_COLUMN_NAME),  # type: ignore
                ts_params_dict.get(
                    constants.TimeSeriesInternal.ORIGIN_TIME_COLUMN_NAME,
                    constants.TimeSeriesInternal.ORIGIN_TIME_COLNAME_DEFAULT),
                grains,  # type: ignore
                timeseries_transformer.get_boolean_col_names(X)
            )

            train_data = pd.DataFrame()
            test_data = pd.DataFrame()

            for key, grp in tsdf.groupby_grain():
                size = grp.shape[0]
                train_size = int(size * meta_learner_train_percentage)
                train_data = pd.concat([train_data, grp.iloc[:train_size]])
                test_data = pd.concat([test_data, grp.iloc[train_size:]])

            y_base_train = train_data.pop(constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN)
            y_meta_train = test_data.pop(constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN)
            X_base_train, X_meta_train = train_data, test_data
            sample_weight_base_train, sample_weight_meta_train = None, None
        else:
            stratify = y if expr_store.metadata.task_type == constants.Tasks.CLASSIFICATION else None

            sample_weight_base_train = None
            sample_weight_meta_train = None
            if sample_weight is not None:
                try:
                    (X_base_train, X_meta_train, y_base_train, y_meta_train, sample_weight_base_train,
                        sample_weight_meta_train) = model_selection.train_test_split(
                            X, y, sample_weight, test_size=meta_learner_train_percentage, stratify=stratify)
                except ValueError:
                    # in case stratification fails, fall back to non-stratify train/test split
                    (X_base_train, X_meta_train, y_base_train, y_meta_train, sample_weight_base_train,
                        sample_weight_meta_train) = model_selection.train_test_split(
                            X, y, sample_weight, test_size=meta_learner_train_percentage, stratify=None)
            else:
                try:
                    X_base_train, X_meta_train, y_base_train, y_meta_train =\
                        model_selection.train_test_split(
                            X, y, test_size=meta_learner_train_percentage, stratify=stratify)
                except ValueError:
                    # in case stratification fails, fall back to non-stratify train/test split
                    X_base_train, X_meta_train, y_base_train, y_meta_train =\
                        model_selection.train_test_split(X, y, test_size=meta_learner_train_percentage, stratify=None)

        return (
            X_base_train, X_meta_train, y_base_train, y_meta_train,
            sample_weight_base_train, sample_weight_meta_train)

    def _train_meta_learner_for_scoring_ensemble_with_train_validate(
            self, X_base_train, X_meta_train, y_base_train, y_meta_train, sample_weight_base_train,
            sample_weight_meta_train, base_learners_pipeline_spec_subsample_tuples):
        logger.info('Beginning training the meta learner for the scoring Stack Ensemble.')
        meta_learner, meta_learner_supports_sample_weights = self._create_meta_learner()
        logger.info('Creating new base learner instances for the scoring Stack Ensemble.')
        expr_store = ExperimentStore.get_instance()
        scoring_base_learners_fraction_tuples = self._instantiate_pipelines_from_specs(
            base_learners_pipeline_spec_subsample_tuples, expr_store.metadata.problem_info)
        need_subsampling = False
        for _, training_fraction in base_learners_pipeline_spec_subsample_tuples:
            if training_fraction != 100:
                need_subsampling = True
                break

        # We can apply the same training fraction to the training data for the base learners
        # and get the subsampled training data for refitting the base learners.
        logger.info('Subsampling dataset for representing the training data for the scoring ensemble.')
        for i, (scoring_base_learner, train_fraction) in enumerate(scoring_base_learners_fraction_tuples):
            if need_subsampling:
                logger.info('Subsample {} % from the training dataset.'.format(train_fraction))
                # subsample the dataset with same percentage
                X_train_sampled, y_train_sampled, sample_weight_sampled = subsample_train_valid_set(
                    train_fraction, random_state=self._automl_settings.subsample_seed)
                logger.info('Refitting base learner {} on the subsampled training data.'.format(i))
                _ml_engine.train(
                    scoring_base_learner,
                    MaterializedTabularData(X_train_sampled, y_train_sampled, sample_weight_sampled))
            else:
                logger.info('Refitting base learner {} on its split of the training data.'.format(i))
                _ml_engine.train(
                    scoring_base_learner,
                    MaterializedTabularData(X_base_train, y_base_train, sample_weight_base_train))

        if expr_store.metadata.task_type == constants.Tasks.CLASSIFICATION:
            # use the predict probabilities to return the class because the meta_learner was trained on probabilities
            # when subsampling is enabled, it can be the case that different models have different views on the
            # class labels, so we're padding here the probabilities to the 'true' class labels (as identified from
            # dataset)
            predictions = []
            for estimator, _ in scoring_base_learners_fraction_tuples:
                predictions.append(
                    _scoring_utilities.pad_predictions(
                        estimator.predict_proba(X_meta_train),
                        estimator.classes_,
                        expr_store.metadata.classification.class_labels
                    )
                )

            concat_predictions = model_wrappers.StackEnsembleBase._horizontal_concat(predictions)
        else:
            predictions = [estimator.predict(X_meta_train) for estimator, _ in scoring_base_learners_fraction_tuples]
            concat_predictions = model_wrappers.StackEnsembleBase._horizontal_concat(predictions)
        logger.info('Fitting the scoring meta learner.')
        self._fit_meta_learner(
            meta_learner, concat_predictions, y_meta_train,
            sample_weight_meta_train, meta_learner_supports_sample_weights)
        logger.info('Finished fitting of the scoring meta learner.')
        return meta_learner

    def _determine_meta_learner_type(self, y_meta_list: typing.List[np.ndarray]) -> Tuple[str, Dict[str, Any]]:
        meta_learner_type = self._meta_learner_type
        meta_learner_kwargs = self._meta_learner_kwargs
        # if the user hasn't explicitly specified the learner type for the Stacker, we need to figure out a default
        if meta_learner_type is None:
            # instantiate a KFold instance to figure out how many folds are used by CV learners.
            required_cv_count = model_selection.KFold().n_splits

            if self._automl_settings.task_type == constants.Tasks.REGRESSION:
                # we'll iterate through all the sets of target values used for the meta learner to figure out if
                # we could use Cross Validation while training the ElasticNet or not.
                validation_sizes = [len(y) for y in y_meta_list]
                if not self._automl_settings.is_timeseries and (min(validation_sizes) > required_cv_count):
                    meta_learner_type = constants.EnsembleConstants.StackMetaLearnerAlgorithmNames.ElasticNetCV
                else:
                    meta_learner_type = constants.EnsembleConstants.StackMetaLearnerAlgorithmNames.ElasticNet
            elif self._automl_settings.task_type == constants.Tasks.CLASSIFICATION:
                # we want to see whether the current data allows us to do LogisticRegressionCV,
                # otherwise we'll fallback to simple LogisticRegression.
                # both learners have a common set of parameters
                meta_learner_kwargs = {}
                # for metrics where we would recommend using class_weights, set the parameter to balanced
                if self._automl_settings.primary_metric in constants.Metric.CLASSIFICATION_BALANCED_SET:
                    meta_learner_kwargs['class_weight'] = 'balanced'
                else:
                    meta_learner_kwargs['class_weight'] = None

                # First, compute the unique classes and return the inverse function to compute each class in y from
                # the list of unique classes
                can_use_cv = True
                # we'll iterate through all the sets of target values used for the meta learner
                # For Train/Validation we check the initial validation set which is used for th final StackEnsemble,
                # and also the split we take for training the meta learner inside the scoring StackEnsemble.
                # For CrossValidation, we'll have to check all the validation sets.
                for y_meta_train in y_meta_list:
                    y_meta_train_unique, y_meta_train_counts = np.unique(y_meta_train, return_counts=True)

                    if y_meta_train_counts.min() < required_cv_count:
                        can_use_cv = False
                        break
                if can_use_cv:
                    meta_learner_type = \
                        constants.EnsembleConstants.StackMetaLearnerAlgorithmNames.LogisticRegressionCV
                    # let's also try to set some defaults, unless the user overrides them
                    meta_learner_kwargs['refit'] = True

                else:
                    meta_learner_type = \
                        constants.EnsembleConstants.StackMetaLearnerAlgorithmNames.LogisticRegression

                if self._meta_learner_kwargs is not None:
                    meta_learner_kwargs.update(self._meta_learner_kwargs)
            else:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        InvalidArgumentWithSupportedValues, target="task_type",
                        arguments="task_type ({})".format(self._automl_settings.task_type),
                        supported_values=", ".join(constants.Tasks.ALL)
                    )
                )
        return meta_learner_type, meta_learner_kwargs

    def _create_meta_learner(self) -> typing.Tuple[base.BaseEstimator, bool]:
        meta_learner_ctor = None  # type: typing.Union[typing.Any, typing.Callable[..., typing.Any]]
        meta_learner_kwargs = {}  # type: typing.Dict[str, typing.Any]
        meta_learner_supports_sample_weights = True

        if self._meta_learner_type == constants.EnsembleConstants.StackMetaLearnerAlgorithmNames.LightGBMClassifier \
                or self._meta_learner_type == \
                constants.EnsembleConstants.StackMetaLearnerAlgorithmNames.LightGBMRegressor:
            if self._automl_settings.task_type == constants.Tasks.CLASSIFICATION:
                meta_learner_ctor = model_wrappers.LightGBMClassifier
            else:
                meta_learner_ctor = model_wrappers.LightGBMRegressor
            meta_learner_kwargs = {"min_child_samples": 10}
        elif self._meta_learner_type == constants.EnsembleConstants.StackMetaLearnerAlgorithmNames.LogisticRegression:
            meta_learner_ctor = linear_model.LogisticRegression
        elif self._meta_learner_type == \
                constants.EnsembleConstants.StackMetaLearnerAlgorithmNames.LogisticRegressionCV:
            meta_learner_ctor = linear_model.LogisticRegressionCV
            scorer = Scorer(self._automl_settings.primary_metric)
            meta_learner_kwargs = {'scoring': scorer}
        elif self._meta_learner_type == constants.EnsembleConstants.StackMetaLearnerAlgorithmNames.LinearRegression:
            meta_learner_ctor = linear_model.LinearRegression
        elif self._meta_learner_type == constants.EnsembleConstants.StackMetaLearnerAlgorithmNames.ElasticNet:
            meta_learner_ctor = linear_model.ElasticNet
            meta_learner_supports_sample_weights = False
        elif self._meta_learner_type == constants.EnsembleConstants.StackMetaLearnerAlgorithmNames.ElasticNetCV:
            meta_learner_ctor = linear_model.ElasticNetCV
            meta_learner_supports_sample_weights = False
        else:
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentWithSupportedValues, target="stack_meta_learner_type",
                    arguments="stack_meta_learner_type ({})".format(self._meta_learner_type),
                    supported_values=", ".join(constants.EnsembleConstants.StackMetaLearnerAlgorithmNames.ALL)
                )
            )

        if self._meta_learner_kwargs is not None:
            meta_learner_kwargs.update(self._meta_learner_kwargs)

        return (meta_learner_ctor(**meta_learner_kwargs), meta_learner_supports_sample_weights)

    def _create_stack_ensemble(self, base_layer_tuples, meta_learner):
        result = None
        if self._automl_settings.task_type == constants.Tasks.CLASSIFICATION:
            result = model_wrappers.StackEnsembleClassifier(base_learners=base_layer_tuples, meta_learner=meta_learner)
        else:
            result = model_wrappers.StackEnsembleRegressor(base_learners=base_layer_tuples, meta_learner=meta_learner)
        return result

    def _instantiate_pipelines_from_specs(self, pipeline_specs_tuples, problem_info):
        if self._automl_settings.is_timeseries:
            # for timeseries models, we need to carry over the related parameters (time column, grains, etc.)
            problem_info.timeseries_param_dict = utilities._get_ts_params_dict(self._automl_settings)
        pipelines = []
        for spec, train_fraction in pipeline_specs_tuples:
            pipeline_dict = json.loads(spec)
            spec_obj = pipeline_spec_module.PipelineSpec.from_dict(pipeline_dict)
            pipeline = spec_obj.instantiate_pipeline_spec(problem_info)
            pipelines.append((pipeline, train_fraction))
        return pipelines

    @staticmethod
    def _fit_meta_learner(meta_learner, X, y, sample_weight, learner_supports_sample_weights):
        if learner_supports_sample_weights:
            meta_learner.fit(X, y, sample_weight=sample_weight)
        else:
            meta_learner.fit(X, y)
        return meta_learner


class Scorer:
    """Scorer class that encapsulates our own metric computation."""

    def __init__(self, metric: str):
        """Create an AutoMLScorer for a particular metric.

        :param metric: The metric we need to calculate the score for.
        """
        self._metric = metric

    def __repr__(self) -> str:
        return _codegen_utilities.generate_repr_str(self.__class__, {"metric": self._metric})

    def __call__(self, estimator, X, y=None):
        """Return the score of the estimator.

        :param estimator: The estimator to score
        :param X: the input data to compute the score on
        :param y: the target values associate to the input
        """
        # The LogisticRegressionCV estimator transforms labels to -1 and 1 when multi_class is ovr.
        # We cannot use the original dataset class labels or sample weights here
        # and must rely on the sklearn scorer function interface.
        cv_labels = estimator.classes_
        if estimator.multi_class == 'ovr':
            cv_labels = cv_labels.astype(float)
        y_pred_proba = estimator.predict_proba(X)

        scores = _ml_engine.evaluate_classifier(y, y_pred_proba, [self._metric], cv_labels, cv_labels)
        return scores[self._metric]
