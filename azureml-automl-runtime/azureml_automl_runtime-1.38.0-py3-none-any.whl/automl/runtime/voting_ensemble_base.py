# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Base module for ensembling previous AutoML iterations."""
from typing import Any, Dict, Type, Union
from abc import ABC

import numpy as np

from azureml.automl.core.automl_base_settings import AutoMLBaseSettings
from azureml.automl.runtime.experiment_store import ExperimentStore
from azureml.automl.core.shared import constants
from azureml.automl.core.shared.exceptions import AutoMLEnsembleException

from azureml.automl.runtime import ensemble_base
from azureml.automl.runtime.shared import model_wrappers


class VotingEnsembleBase(ensemble_base.EnsembleBase, ABC):
    """
    Class for ensembling previous AutoML iterations.

    The ensemble pipeline is initialized from a collection of already fitted pipelines.
    """

    CV_DOWNLOAD_RETURNED_LESS_MODELS_MSG = "Could not download all the models required for constructing the \
        final Ensemble. This can happen if the download of models didn't finish within the default timeout. \
        Please use `ensemble_download_models_timeout_sec` parameter in AutoMLConfig to set a larger timeout"

    def __init__(self, automl_settings: Union[str, Dict[str, Any], AutoMLBaseSettings],
                 settings_type: 'Type[ensemble_base.SettingsType]') -> None:
        """Create an Ensemble pipeline out of a collection of already fitted pipelines.

        :param automl_settings: settings for the AutoML experiments.
        :param settings_type: the type for the settings object.
        """
        super(VotingEnsembleBase, self).__init__(automl_settings, settings_type)

    def _create_ensembles(self, fitted_pipelines, selector):
        """
        Create an ensemble estimator using the given pipelines and selector.

        :param fitted_pipelines: list of trained models to select from
        :param selector: ensemble selector object
        :return: a voting ensemble estimator plus estimators for cross validations
        """
        expr_store = ExperimentStore.get_instance()
        if selector.training_type == constants.TrainingType.MeanCrossValidation:
            use_cross_validation = True
            ensemble_estimator_tuples = self._create_fully_fitted_ensemble_estimator_tuples(
                fitted_pipelines,
                selector.unique_ensemble)
            if self._automl_settings.task_type == constants.Tasks.CLASSIFICATION:
                trained_labels = expr_store.metadata.classification.class_labels
            else:
                trained_labels = None
        else:
            use_cross_validation = False
            ensemble_estimator_tuples = [(
                str(fitted_pipelines[i][self.PIPELINES_TUPLES_ITERATION_INDEX]),
                fitted_pipelines[i][self.PIPELINES_TUPLES_PIPELINE_INDEX]) for i in selector.unique_ensemble]
            if self._automl_settings.task_type == constants.Tasks.CLASSIFICATION:
                _, y_train, _ = expr_store.data.materialized.get_train()
                trained_labels = np.unique(y_train)
            else:
                trained_labels = None

        # ensemble_estimator_tuples represents a list of tuples (iteration_index, fitted_pipeline)
        if len(ensemble_estimator_tuples) != len(selector.unique_weights):
            raise AutoMLEnsembleException(self.CV_DOWNLOAD_RETURNED_LESS_MODELS_MSG,
                                          has_pii=False, target=AutoMLEnsembleException.MISSING_MODELS)
        final_ensemble = self._get_voting_ensemble(trained_labels,
                                                   ensemble_estimator_tuples,
                                                   selector.unique_weights)

        cross_folded_ensembles = None
        if use_cross_validation:
            # for computing all the scores of the Ensemble we'll need the ensembles of cross-validated models.
            cross_folded_ensembles = []
            for fold_index, cv_split in enumerate(expr_store.data.materialized.get_CV_splits()):
                partial_fitted_estimators = [(
                    str(fitted_pipelines[i][self.PIPELINES_TUPLES_ITERATION_INDEX]),
                    fitted_pipelines[i][self.PIPELINES_TUPLES_PIPELINE_INDEX][fold_index])
                    for i in selector.unique_ensemble]

                y_train = cv_split._y_train
                cv_train_labels = np.unique(y_train)
                cross_folded_ensemble = self._get_voting_ensemble(cv_train_labels,
                                                                  partial_fitted_estimators,
                                                                  selector.unique_weights)
                cross_folded_ensembles.append(cross_folded_ensemble)
        return final_ensemble, cross_folded_ensembles

    def _get_voting_ensemble(self, trained_labels, ensemble_estimator_tuples, unique_weights):
        if self._automl_settings.task_type == constants.Tasks.CLASSIFICATION:
            estimator = model_wrappers.PreFittedSoftVotingClassifier(estimators=ensemble_estimator_tuples,
                                                                     weights=unique_weights,
                                                                     classification_labels=trained_labels)
        elif self._automl_settings.task_type == constants.Tasks.REGRESSION:
            estimator = model_wrappers.PreFittedSoftVotingRegressor(estimators=ensemble_estimator_tuples,
                                                                    weights=unique_weights)
        else:
            raise AutoMLEnsembleException('Invalid task_type ({0})'.format(self._automl_settings.task_type),
                                          target=AutoMLEnsembleException.CONFIGURATION)\
                .with_generic_msg("Invalid task type.")
        return estimator
