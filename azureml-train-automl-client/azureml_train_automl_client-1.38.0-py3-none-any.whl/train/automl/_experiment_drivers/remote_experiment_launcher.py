# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
from typing import Any, Dict, List, Optional, Union, cast

from azureml._common._error_definition import AzureMLError
from azureml.core import Run
from azureml.core.runconfig import RunConfiguration

from azureml.automl.core._experiment_drivers.base_experiment_driver import BaseExperimentDriver
from azureml.automl.core._run import run_lifecycle_utilities
from azureml.automl.core._run.types import RunType
from azureml.automl.core.shared._diagnostics.automl_error_definitions import RunInterrupted

from .._azure_experiment_state import AzureExperimentState
from .._remote_console_interface import RemoteConsoleInterface
from ..run import AutoMLRun
from . import driver_utilities

logger = logging.getLogger(__name__)


class RemoteExperimentLauncher(BaseExperimentDriver):
    def __init__(self,
                 experiment_state: AzureExperimentState) -> None:
        self.experiment_state = experiment_state
        self.experiment_state.automl_settings.debug_log = "azureml_automl.log"

    def create_parent_run(
            self,
            run_configuration: Optional[RunConfiguration] = None,
            compute_target: Optional[Any] = None,
            X: Optional[Any] = None,
            y: Optional[Any] = None,
            sample_weight: Optional[Any] = None,
            X_valid: Optional[Any] = None,
            y_valid: Optional[Any] = None,
            sample_weight_valid: Optional[Any] = None,
            cv_splits_indices: Optional[List[Any]] = None,
            existing_run: bool = False,
            training_data: Optional[Any] = None,
            validation_data: Optional[Any] = None,
            test_data: Optional[Any] = None,
            _script_run: Optional[Run] = None,
            parent_run_id: Optional[str] = None,
            kwargs: Optional[Dict[str, Any]] = None
    ) -> None:
        if run_configuration is None:
            run_configuration = RunConfiguration()
            run_configuration.target = compute_target
        self.experiment_state.console_writer.println(
            "Running on remote compute: " + str(run_configuration.target)
        )
        driver_utilities.create_remote_parent_run(
            self.experiment_state,
            run_configuration, X=X, y=y, sample_weight=sample_weight, X_valid=X_valid, y_valid=y_valid,
            sample_weight_valid=sample_weight_valid, cv_splits_indices=cv_splits_indices,
            training_data=training_data, validation_data=validation_data, test_data=test_data)
        assert self.experiment_state.current_run

    def start(
            self,
            run_configuration: RunConfiguration = None,
            compute_target: Optional[Any] = None,
            X: Optional[Any] = None,
            y: Optional[Any] = None,
            sample_weight: Optional[Any] = None,
            X_valid: Optional[Any] = None,
            y_valid: Optional[Any] = None,
            sample_weight_valid: Optional[Any] = None,
            cv_splits_indices: Optional[List[Any]] = None,
            existing_run: bool = False,
            training_data: Optional[Any] = None,
            validation_data: Optional[Any] = None,
            test_data: Optional[Any] = None,
            _script_run: Optional[Run] = None,
            parent_run_id: Optional[str] = None,
            kwargs: Optional[Dict[str, Any]] = None
    ) -> RunType:
        """
        Start an experiment using this driver.
        :param run_configuration: the run configuration for the experiment
        :param compute_target: the compute target to run on
        :param X: Training features
        :param y: Training labels
        :param sample_weight:
        :param X_valid: validation features
        :param y_valid: validation labels
        :param sample_weight_valid: validation set sample weights
        :param cv_splits_indices: Indices where to split training data for cross validation
        :param existing_run: Flag whether this is a continuation of a previously completed experiment
        :param training_data: Training dataset
        :param validation_data: Validation dataset
        :param test_data: Test dataset
        :param _script_run: Run to associate with parent run id
        :param parent_run_id: The parent run id for an existing experiment
        :return: AutoML parent run
        """

        driver_utilities.start_remote_run(self.experiment_state, run_configuration)

        if self.experiment_state.console_writer.show_output:
            RemoteConsoleInterface._show_output(
                cast(AutoMLRun, self.experiment_state.current_run),
                self.experiment_state.console_writer,
                logger,
                self.experiment_state.automl_settings.primary_metric,
            )

        assert self.experiment_state.current_run
        return self.experiment_state.current_run

    def cancel(self) -> None:
        run_lifecycle_utilities.cancel_run(
            self.experiment_state.current_run,
            warning_string=AzureMLError.create(RunInterrupted).error_message
        )
