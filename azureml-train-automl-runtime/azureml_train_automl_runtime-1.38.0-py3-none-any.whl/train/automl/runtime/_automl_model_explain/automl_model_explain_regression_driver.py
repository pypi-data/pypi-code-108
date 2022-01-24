# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azureml.core import Run
from azureml.train.automl.runtime._automl_model_explain.automl_model_explain_driver import AutoMLModelExplainDriver


class AutoMLModelExplainRegressionDriver(AutoMLModelExplainDriver):
    def __init__(self, automl_child_run: Run,
                 max_cores_per_iteration: int):
        """
        Class for model explain configuration for AutoML regression models.

        :param automl_child_run: The automated ML child run.
        :type automl_child_run: azureml.core.Run
        :param max_cores_per_iteration: Number of cores configuration used for AutoML models.
        :type max_cores_per_iteration: int
        """
        super().__init__(automl_child_run=automl_child_run,
                         max_cores_per_iteration=max_cores_per_iteration)

    def setup_model_explain_data(self) -> None:
        """Generate the model explanations data."""
        self.setup_estimator_pipeline()
        self.setup_model_explain_train_data(False)
        self.setup_model_explain_metadata()
        self.setup_class_labels()
        self.setup_surrogate_model_and_params()
