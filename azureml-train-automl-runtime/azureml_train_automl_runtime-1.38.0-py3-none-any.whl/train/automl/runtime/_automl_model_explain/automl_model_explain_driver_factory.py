# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import ast
import logging
from typing import cast, Optional

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared import constants
from azureml.automl.core.shared._diagnostics.automl_error_definitions import InvalidArgumentWithSupportedValues
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.exceptions import ValidationException
from azureml.core import Run
from azureml.train.automl.runtime._automl_model_explain.automl_model_explain_classical_forecasting_model_driver \
    import (AutoMLModelExplainClassicalFCModelUseOnlyTargetColDriver)
from azureml.train.automl.runtime._automl_model_explain.automl_model_explain_classification_driver import (
    AutoMLModelExplainClassificationDriver)
from azureml.train.automl.runtime._automl_model_explain.automl_model_explain_driver import (
    AutoMLModelExplainDriver)
from azureml.train.automl.runtime._automl_model_explain.automl_model_explain_forecasting_driver import (
    AutoMLModelExplainForecastingDriver)
from azureml.train.automl.runtime._automl_model_explain.automl_model_explain_regression_driver import (
    AutoMLModelExplainRegressionDriver)
from azureml.train.automl.runtime._automl_model_explain.automl_model_explain_streaming_driver import (
    AutoMLModelExplainStreamingDriver)
from azureml.train.automl.runtime.automl_explain_utilities import TimeseriesClassicalModelTypeChecker

logger = logging.getLogger(__name__)


class AutoMLModelExplainDriverFactory:

    @staticmethod
    def _get_model_explain_driver(
            automl_child_run: Run,
            task_type: str,
            is_timeseries: bool,
            enable_streaming: bool,
            max_cores_per_iteration: int = -1,
            label_column_name: Optional[str] = ''
    ) -> AutoMLModelExplainDriver:
        """
        Get the model explain driver for a given type of AutoML model.

        :param automl_child_run: The automated ML child run.
        :type automl_child_run: azureml.core.Run
        :param task_type: The task type of the experiment.
        :type task_type: str
        :param is_timeseries: If the experiment is a timeseries/forecasting task.
        :type is_timeseries: bool
        :param enable_streaming: If the streaming is enabled.
        :type enable_streaming: bool
        :param max_cores_per_iteration: The maximum number of threads to use for a given training iteration.
        :type max_cores_per_iteration: int
        :param label_column_name: The label/target column name.
        :type label_column_name: str
        :return: driver class for explaining a given AutoML model.
        """
        if enable_streaming:

            logger.info("Constructing model explain config for streaming with task " + task_type)
            return AutoMLModelExplainStreamingDriver(
                automl_child_run=automl_child_run,
                max_cores_per_iteration=max_cores_per_iteration,
                task_type=task_type)
        elif task_type == constants.Tasks.CLASSIFICATION:
            logger.info("Constructing model explain config for classification")
            return AutoMLModelExplainClassificationDriver(
                automl_child_run=automl_child_run,
                max_cores_per_iteration=max_cores_per_iteration)
        elif task_type == constants.Tasks.REGRESSION:
            if not is_timeseries:
                logger.info("Constructing model explain config for regression")
                return AutoMLModelExplainRegressionDriver(
                    automl_child_run=automl_child_run,
                    max_cores_per_iteration=max_cores_per_iteration)
            else:
                return AutoMLModelExplainDriverFactory._get_model_explain_forecasting_driver(
                    automl_child_run=automl_child_run,
                    max_cores_per_iteration=max_cores_per_iteration,
                    label_column_name=label_column_name
                )
        else:
            raise ValidationException._with_error(
                AzureMLError.create(
                    InvalidArgumentWithSupportedValues, target="task",
                    arguments="task ({})".format(task_type),
                    supported_values=", ".join(
                        [constants.Tasks.CLASSIFICATION, constants.Tasks.REGRESSION, constants.Subtasks.FORECASTING]
                    )
                )
            )

    @staticmethod
    def _get_model_explain_forecasting_driver(
            automl_child_run: Run,
            max_cores_per_iteration: int = -1,
            label_column_name: Optional[str] = ''
    ) -> AutoMLModelExplainDriver:
        """
        Get the model explain driver for the forecasting task.

        :param automl_child_run: The automated ML child run.
        :type automl_child_run: azureml.core.Run
        :param max_cores_per_iteration: The maximum number of threads to use for a given training iteration.
        :type max_cores_per_iteration: int
        :param label_column_name: The label/target column name.
        :type label_column_name: str
        :return: driver class for explaining a given AutoML model.
        """
        logger.info("Constructing model explain config for forecasting task.")

        automl_algo_name = automl_child_run.properties.get('run_algorithm')
        ensemble_algo_names_list_str = automl_child_run.properties.get('ensembled_algorithms')
        if ensemble_algo_names_list_str is not None:
            ensembled_algorithms = ast.literal_eval(ensemble_algo_names_list_str)
        else:
            ensembled_algorithms = []

        all_mdls_are_fc_only_use_y = TimeseriesClassicalModelTypeChecker._check_classical_forecast_model_type(
            automl_algo_name, ensembled_algorithms
        )

        if all_mdls_are_fc_only_use_y:
            return AutoMLModelExplainClassicalFCModelUseOnlyTargetColDriver(
                automl_child_run=automl_child_run,
                max_cores_per_iteration=max_cores_per_iteration,
                target_column_name=label_column_name)
        else:
            return AutoMLModelExplainForecastingDriver(
                automl_child_run=automl_child_run,
                max_cores_per_iteration=max_cores_per_iteration)
