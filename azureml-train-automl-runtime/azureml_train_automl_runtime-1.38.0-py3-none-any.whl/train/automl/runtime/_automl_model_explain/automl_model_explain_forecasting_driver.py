# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging

from azureml.automl.core.shared import constants
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.runtime.experiment_store import ExperimentStore
from azureml.automl.runtime.featurizer.transformer.timeseries.timeseries_transformer import TimeSeriesTransformer
from azureml.core import Run
from azureml.train.automl.runtime._automl_model_explain.automl_model_explain_driver import AutoMLModelExplainDriver
from azureml.train.automl.runtime._automl_model_explain.automl_model_explain_helper import (
    _automl_pick_evaluation_samples_explanations, _automl_auto_mode_get_explainer_data,
    _automl_auto_mode_get_raw_data)
from azureml.train.automl.runtime.automl_explain_utilities import _prepare_time_series_data_with_look_back_features, \
    _should_set_reset_index


logger = logging.getLogger(__name__)


class AutoMLModelExplainForecastingDriver(AutoMLModelExplainDriver):
    def __init__(self, automl_child_run: Run,
                 max_cores_per_iteration: int):
        """
        Class for model explain configuration for AutoML forecasting task.
        This driver only handles the models that are not classical forecasting models (typically regression models),
        and the ensemble model that contains only non-classical forecasting models.

        :param automl_child_run: The automated ML child run.
        :type automl_child_run: azureml.core.Run
        :param max_cores_per_iteration: Number of cores configuration used for AutoML models.
        :type max_cores_per_iteration: int
        """
        super().__init__(automl_child_run=automl_child_run,
                         max_cores_per_iteration=max_cores_per_iteration)

        # Disable raw data upload for explanations of forecasting models
        # This is because the codepath for forecasting data cleaning is not aligned
        # with those of classification and regression.
        # Refactoring data cleaning will be required to enable raw forecasting explanations.
        self._should_upload_raw_eval_dataset = False

    def setup_model_explain_train_data(self, is_classification: bool = False) -> None:
        """Training/Evaluation data to explain and down-sampling if configured."""
        expr_store = ExperimentStore.get_instance()
        # Setup the training and test samples for explanations
        explainer_train_data, explainer_test_data, explainer_data_y, explainer_data_y_test = \
            _automl_auto_mode_get_explainer_data()

        # For timeseries data, we need to check if look-back features are enabled, and prepare the data if that is the
        # case, for model explanation to work.
        timeseries_transformer = None
        timeseries_transformer = expr_store.transformers.get_timeseries_transformer()
        Contract.assert_value(timeseries_transformer, 'timeseries_transformer')
        Contract.assert_type(
            timeseries_transformer,
            'timeseries_transformer',
            expected_types=TimeSeriesTransformer)
        if explainer_train_data is not None and explainer_data_y is not None:
            explainer_train_data, explainer_data_y = \
                _prepare_time_series_data_with_look_back_features(
                    timeseries_transformer,
                    self._automl_child_run.properties['run_algorithm'],
                    explainer_train_data,
                    explainer_data_y
                )
        if explainer_test_data is not None and explainer_data_y_test is not None:
            explainer_test_data, explainer_data_y_test = \
                _prepare_time_series_data_with_look_back_features(
                    timeseries_transformer,
                    self._automl_child_run.properties['run_algorithm'],
                    explainer_test_data,
                    explainer_data_y_test
                )

        # Sub-sample the validation set for the explanations
        explainer_test_data, _ = _automl_pick_evaluation_samples_explanations(
            explainer_train_data, explainer_data_y, explainer_test_data, explainer_data_y_test)

        # Setup the featurized data for training the explainer
        self._automl_explain_config_obj._X_transform = explainer_train_data
        self._automl_explain_config_obj._X_test_transform = explainer_test_data
        self._automl_explain_config_obj._y = explainer_data_y

        logger.info("Preparation of forecasting training data for model explanations completed.")

        if self._should_upload_raw_eval_dataset:
            # Setup the raw data for uploading with the explanations
            raw_train_data, raw_test_data, raw_y, raw_y_test = \
                _automl_auto_mode_get_raw_data()

            if raw_train_data is not None and raw_y is not None:
                raw_train_data, raw_y = \
                    _prepare_time_series_data_with_look_back_features(
                        timeseries_transformer,
                        self._automl_child_run.properties['run_algorithm'],
                        raw_train_data,
                        raw_y
                    )
            if raw_test_data is not None and raw_y_test is not None:
                raw_test_data, raw_y_test = \
                    _prepare_time_series_data_with_look_back_features(
                        timeseries_transformer,
                        self._automl_child_run.properties['run_algorithm'],
                        raw_test_data,
                        raw_y_test
                    )

            # Sub-sample the raw data validation set for the explanations upload
            raw_test_data, raw_y_test = _automl_pick_evaluation_samples_explanations(
                raw_train_data, raw_y, raw_test_data, raw_y_test)
            self._automl_explain_config_obj._X_test_raw = raw_test_data
            self._automl_explain_config_obj._y_test_raw = raw_y_test

            logger.info("Preparation of forecasting raw data for model explanations completed.")

    def setup_surrogate_model_and_params(self, should_reset_index: bool = False) -> None:
        super().setup_surrogate_model_and_params(
            should_reset_index=_should_set_reset_index(automl_run=self._automl_child_run))

    def setup_model_explain_data(self) -> None:
        """Generate the model explanations data."""
        self.setup_estimator_pipeline()
        self.setup_model_explain_train_data(False)
        self.setup_model_explain_metadata()
        self.setup_class_labels()
        self.setup_surrogate_model_and_params()
