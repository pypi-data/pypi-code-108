# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging

from typing import cast

from azureml.automl.runtime.experiment_store import ExperimentStore
from azureml.automl.core.shared import constants
from azureml.automl.runtime.streaming_pipeline_wrapper import StreamingPipelineWrapper
from azureml.core import Run
from azureml.train.automl.runtime._automl_model_explain.automl_model_explain_driver import AutoMLModelExplainDriver
from azureml.train.automl.runtime._automl_model_explain.automl_model_explain_helper import (
    _automl_auto_mode_get_explainer_data_streaming, _automl_pick_evaluation_samples_explanations,
    _automl_auto_mode_get_raw_data_streaming)
from azureml.train.automl.runtime.automl_explain_utilities import _get_unique_classes, _get_estimator_streaming


logger = logging.getLogger(__name__)


class AutoMLModelExplainStreamingDriver(AutoMLModelExplainDriver):
    def __init__(self,
                 automl_child_run: Run,
                 max_cores_per_iteration: int,
                 task_type: str):
        """
        Class for model explain configuration for AutoML streaming models.

        :param automl_child_run: The automated ML child run.
        :type automl_child_run: azureml.core.Run
        :param max_cores_per_iteration: Number of cores configuration used for AutoML models.
        :type max_cores_per_iteration: int
        :param task_type: 'classification'/'regression'.
        :type task_type: str
        """
        super().__init__(automl_child_run=automl_child_run,
                         max_cores_per_iteration=max_cores_per_iteration)
        self._task_type = task_type

    def setup_model_explain_data(self) -> None:
        """Generate the model explanations data."""
        is_classification = self._task_type == constants.Tasks.CLASSIFICATION
        self.setup_estimator_pipeline()
        self.setup_model_explain_train_data(is_classification)
        self.setup_model_explain_metadata()
        self.setup_class_labels()
        self.setup_surrogate_model_and_params()

    def setup_model_explain_train_data(self, is_classification: bool) -> None:
        """Training/Evaluation data to explain and down-sampling if configured."""
        # Setup the training and test samples for explanations
        explainer_train_data, explainer_test_data, explainer_data_y, explainer_data_y_valid = \
            _automl_auto_mode_get_explainer_data_streaming()

        # Subsample the validation set for the explanations
        explainer_test_data, _ = _automl_pick_evaluation_samples_explanations(
            explainer_train_data, explainer_data_y, explainer_test_data, explainer_data_y_valid,
            is_classification=is_classification)

        self._automl_explain_config_obj._X_transform = explainer_train_data
        self._automl_explain_config_obj._X_test_transform = explainer_test_data
        self._automl_explain_config_obj._y = explainer_data_y

        logger.info("Preparation of training data for model explanations completed.")

        if self._should_upload_raw_eval_dataset:
            # Setup the raw data for uploading with the explanations
            raw_train_data, raw_test_data, raw_y, raw_y_test = \
                _automl_auto_mode_get_raw_data_streaming()

            # Subsample the raw data validation set for the explanations upload
            raw_test_data, raw_y_test = _automl_pick_evaluation_samples_explanations(
                raw_train_data, raw_y, raw_test_data, raw_y_test,
                is_classification=is_classification)
            self._automl_explain_config_obj._X_test_raw = raw_test_data
            self._automl_explain_config_obj._y_test_raw = raw_y_test

            logger.info("Preparation of raw data for model explanations completed.")

    def setup_estimator_pipeline(self) -> None:
        """Estimator pipeline."""
        super()._rehydrate_automl_fitted_model()
        self._automl_explain_config_obj._automl_estimator = _get_estimator_streaming(
            cast(StreamingPipelineWrapper, self._automl_explain_config_obj._automl_pipeline),
            self._task_type)

    def setup_class_labels(self) -> None:
        """Return the unique classes in y or obtain classes from inverse transform using y_transformer."""
        if self._task_type == constants.Tasks.CLASSIFICATION:
            expr_store = ExperimentStore.get_instance()
            self._automl_explain_config_obj._classes = _get_unique_classes(
                y=self._automl_explain_config_obj._y,
                automl_estimator=self._automl_explain_config_obj._automl_estimator,
                y_transformer=expr_store.transformers.get_y_transformer())
        else:
            self._automl_explain_config_obj._classes = None
