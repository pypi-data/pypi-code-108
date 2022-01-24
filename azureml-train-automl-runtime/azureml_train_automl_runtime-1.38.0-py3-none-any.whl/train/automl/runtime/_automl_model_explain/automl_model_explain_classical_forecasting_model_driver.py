# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Optional

from azureml.core import Run
from azureml.train.automl.runtime._automl_model_explain.automl_model_explain_forecasting_driver import (
    AutoMLModelExplainForecastingDriver)
from azureml.train.automl.runtime.automl_explain_utilities import (
    _DummyTargetColumn,
    _setup_explain_config_estimator_forecasting_model,
    _setup_explain_config_train_data_forecasting_use_only_y,
    _setup_explain_config_meta_data_forecasting_use_only_y
)


class AutoMLModelExplainClassicalFCModelUseOnlyTargetColDriver(AutoMLModelExplainForecastingDriver):

    def __init__(self, automl_child_run: Run,
                 max_cores_per_iteration: int,
                 target_column_name: Optional[str] = ''):
        """
        Class for model explain configuration for AutoML forecasting models which use all the columns of the
        training and test data.

        :param automl_child_run: The automated ML child run.
        :type automl_child_run: azureml.core.Run
        :param max_cores_per_iteration: Number of cores configuration used for AutoML models.
        :type max_cores_per_iteration: int
        :param target_column_name: The target column name.
        :type target_column_name: str
        """
        super().__init__(automl_child_run=automl_child_run,
                         max_cores_per_iteration=max_cores_per_iteration)
        if not target_column_name:
            target_column_name = _DummyTargetColumn
        self._target_column_name = target_column_name

    def setup_estimator_pipeline(self) -> None:
        """Estimator pipeline."""
        self._rehydrate_automl_fitted_model()
        exp_cfg = self._automl_explain_config_obj
        target_column_name = self._target_column_name
        _setup_explain_config_estimator_forecasting_model(
            exp_cfg=exp_cfg,
            target_column_name=target_column_name
        )

    def setup_model_explain_data(self) -> None:
        """Generate the model explanations data."""
        self.setup_estimator_pipeline()
        self.setup_model_explain_train_data(False)
        self.setup_model_explain_metadata()
        self.setup_class_labels()
        self.setup_surrogate_model_and_params()

    def setup_model_explain_train_data(self, is_classification: bool = False) -> None:
        """Training/Evaluation data to explain and down-sampling if configured."""
        # Setup the explain config object's properties with super class method.
        super(AutoMLModelExplainForecastingDriver, self).setup_model_explain_train_data(False)

        exp_cfg = self._automl_explain_config_obj
        target_column_name = self._target_column_name
        _setup_explain_config_train_data_forecasting_use_only_y(
            exp_cfg=exp_cfg,
            target_column_name=target_column_name
        )

    def setup_model_explain_metadata(self) -> None:
        """Engineered, raw feature names and feature maps."""
        exp_cfg = self._automl_explain_config_obj
        target_column_name = self._target_column_name
        _setup_explain_config_meta_data_forecasting_use_only_y(
            exp_cfg=exp_cfg,
            target_column_name=target_column_name
        )
