# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Experiment launcher for local managed experiments."""
import logging
import os
import pickle as pkl
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any, Dict, List, Optional, Tuple

import pkg_resources as pkgr
from azureml._base_sdk_common._docstring_wrapper import experimental
from azureml._common._error_definition import AzureMLError
from azureml._restclient.constants import RunStatus
from azureml.core import Dataset, Environment, Run, ScriptRunConfig
from azureml.core.experiment import Experiment
from azureml.core.runconfig import RunConfiguration
from azureml.core.workspace import Workspace
from azureml.data.abstract_dataset import AbstractDataset

from azureml.automl.core._experiment_drivers.base_experiment_driver import BaseExperimentDriver
from azureml.automl.core._run import RunType, run_lifecycle_utilities
from azureml.automl.core.console_writer import ConsoleWriter
from azureml.automl.core.package_utilities import _validate_package, DISABLE_ENV_MISMATCH
from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    AutoMLInternal,
    InvalidInputDatatype,
    ManagedLocalUserError,
    RunInterrupted,
)
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.constants import SupportedInputDatatypes, TelemetryConstants
from azureml.automl.core.shared.exceptions import ClientException, UserException, ValidationException
from azureml.automl.core.shared.pickler import DefaultPickler
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.train.automl import _azureautomlsettings, _local_managed_utils, _logging, constants
from azureml.train.automl._azure_experiment_state import AzureExperimentState
from azureml.train.automl._environment_utilities import modify_run_configuration
from azureml.train.automl._remote_console_interface import RemoteConsoleInterface
from azureml.train.automl.constants import _DataArgNames
from azureml.train.automl.run import AutoMLRun

logger = logging.getLogger(__name__)


class LocalManagedExperimentLauncher(BaseExperimentDriver):

    def __init__(self, experiment_state: AzureExperimentState):
        self.experiment_state = experiment_state

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
        data_params_transformed = {
            'training_data': training_data,
            'validation_data': validation_data,
            'X': X,
            'y': y,
            'sample_weight': sample_weight,
            'X_valid': X_valid,
            'y_valid': y_valid,
            'sample_weight_valid': sample_weight_valid,
            'cv_splits_indices': cv_splits_indices,
            'test_data': test_data
        }

        try:
            self.experiment_state.current_run = _local_managed_utils.create_parent_run_for_local_managed(
                self.experiment_state, data_params_transformed)
            self.experiment_state.parent_run_id = self.experiment_state.current_run.id
        except Exception as e:
            logging_utilities.log_traceback(e, logger)
            _local_managed_utils.handle_script_run_error(parent_run=self.experiment_state.current_run, script_run=None)
            raise

        assert self.experiment_state.current_run

    def start(
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
        """
        Saves data to user workspace and submits a script run that runs an AutoML Local run in an isolated
        conda or docker environment on the user's local compute.
        """
        assert self.experiment_state.current_run
        if not isinstance(self.experiment_state.current_run, AutoMLRun):
            self.experiment_state.current_run = AutoMLRun(
                self.experiment_state.experiment, self.experiment_state.current_run.id)

        data_params = {}
        if kwargs is not None:
            data_params = kwargs.get("data_params", {})

        show_output = self.experiment_state.console_writer.show_output

        terminal_states = [RunStatus.COMPLETED, RunStatus.FAILED, RunStatus.CANCELED]
        # if we're in running state, automl execution has started and can return
        automl_started_states = terminal_states + [RunStatus.RUNNING]

        script_run = None
        try:
            with tempfile.TemporaryDirectory() as local_path:
                dataset_args, settings, run_configuration = _local_managed_utils.prepare_managed_inputs(
                    self.experiment_state, local_path, data_params, run_configuration)
                run_configuration.script = constants.LOCAL_SCRIPT_NAME

                logger.info("Submitting script run for local managed.")
                src = ScriptRunConfig(source_directory=local_path,
                                      run_config=run_configuration,
                                      arguments=dataset_args
                                      )

                script_run = self.experiment_state.experiment.submit(src)
                logger.info("Script run {} submitted for local managed.".format(script_run.id))
            self.experiment_state.current_run.add_properties({constants.SCRIPT_RUN_ID_PROPERTY: script_run.id})

            with logging_utilities.log_activity(
                    logger,
                    activity_name=TelemetryConstants.ScriptRunStarting,
                    custom_dimensions={
                        'run_id': self.experiment_state.current_run.id, "script_run_id": script_run.id}):
                while script_run.get_status() not in automl_started_states:
                    time.sleep(5)
            # Adding a long wait to make sure that it goes through or finishes failing the script run
            # normally this takes 4-8 seconds, a 30 second sleep should be sufficient
            time.sleep(30)
            _local_managed_utils.handle_script_run_error(self.experiment_state.current_run, script_run)

            if show_output:
                print("Creating or loading environment on local compute.")  # TODO: need better wording for this
                print("Starting AutoML run.")
                console_writer = ConsoleWriter(sys.stdout)
                RemoteConsoleInterface._show_output(self.experiment_state.current_run,
                                                    console_writer,
                                                    None,
                                                    settings['primary_metric'])
            logger.info("Local managed run returning to user {}.".format(self.experiment_state.current_run.id))
            return self.experiment_state.current_run
        except Exception as e:
            logging_utilities.log_traceback(e, logger)
            _local_managed_utils.handle_script_run_error(self.experiment_state.current_run, script_run)
            raise

    def cancel(self) -> None:
        run_lifecycle_utilities.cancel_run(
            self.experiment_state.current_run,
            warning_string=AzureMLError.create(RunInterrupted).error_message
        )
