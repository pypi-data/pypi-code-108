# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Dispatcher module for experiments."""
import logging
import os
import warnings
from typing import Any, Dict, List, Optional, Type, Union, cast

from azureml._common._error_definition import AzureMLError
from azureml.core import Run
from azureml.core.compute import ComputeTarget
from azureml.core.runconfig import RunConfiguration

from azureml.automl.core import dataset_utilities
from azureml.automl.core._experiment_drivers.base_experiment_driver import BaseExperimentDriver
from azureml.automl.core._run import run_lifecycle_utilities
from azureml.automl.core._run.types import RunType
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    AutoMLInternal,
    ExecutionFailure,
    InvalidArgumentType,
    InvalidArgumentWithSupportedValues,
    RuntimeModuleDependencyMissing,
    SnapshotLimitExceeded,
)
from azureml.automl.core.shared.exceptions import (
    AutoMLException,
    ClientException,
    ConfigException,
    ValidationException,
)
from azureml.train.automl.utilities import _InternalComputeTypes
from azureml.train.automl._constants_azureml import MLFlowSettings

from .. import constants
from .._azure_experiment_state import AzureExperimentState
from .._remote_console_interface import RemoteConsoleInterface
from ..run import AutoMLRun
from . import driver_utilities
from .local_managed_experiment_launcher import LocalManagedExperimentLauncher

logger = logging.getLogger(__name__)


class ExperimentDriver(BaseExperimentDriver):

    def __init__(self,
                 experiment_state: AzureExperimentState) -> None:
        self.experiment_state = experiment_state
        self.driver = None  # type: Optional[BaseExperimentDriver]

        # Check and create folders as needed
        if self.experiment_state.automl_settings.path is None:
            self.experiment_state.automl_settings.path = os.getcwd()
        # Expand out the path because os.makedirs can't handle '..' properly
        aml_config_path = os.path.abspath(os.path.join(self.experiment_state.automl_settings.path, '.azureml'))
        os.makedirs(aml_config_path, exist_ok=True)

        if not self.experiment_state.automl_settings.show_warnings:
            # sklearn forces warnings, so we disable them here
            warnings.simplefilter("ignore", DeprecationWarning)
            warnings.simplefilter("ignore", RuntimeWarning)
            warnings.simplefilter("ignore", UserWarning)
            warnings.simplefilter("ignore", FutureWarning)

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
    ) -> Dict[str, Any]:
        """
        Create a parent run using this driver.
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
        :return: Dictionary of updated input parameters. This will contain a run_configuration for all runs,
            and untransformed data for local managed runs.
        """
        if kwargs is None:
            kwargs = {}
        if run_configuration is None:
            run_configuration = RunConfiguration()
            if compute_target is not None:
                # this will handle str or compute_target
                run_configuration.target = compute_target
                self.experiment_state.console_writer.println(
                    "No run_configuration provided, running on {0} with default configuration".format(
                        run_configuration.target
                    )
                )
            else:
                self.experiment_state.console_writer.println(
                    "No run_configuration provided, running locally with default configuration"
                )
            if run_configuration.target != "local":
                run_configuration.docker.use_docker = True
        if run_configuration.framework.lower() not in list(constants.Framework.FULL_SET):
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentWithSupportedValues, target="run_configuration",
                    arguments=run_configuration.framework,
                    supported_values=list(constants.Framework.FULL_SET)
                )
            )

        self.experiment_state.automl_settings.compute_target = run_configuration.target

        self.experiment_state.automl_settings.azure_service = _InternalComputeTypes.identify_compute_type(
            compute_target=self.experiment_state.automl_settings.compute_target,
            azure_service=self.experiment_state.automl_settings.azure_service,
        )

        driver_constructor = self._select_driver(self.experiment_state.automl_settings.compute_target)
        self.driver = driver_constructor(self.experiment_state)

        # Save the Dataset to Workspace so that its saved id will be logged for telemetry and lineage
        dataset_utilities.ensure_saved(
            self.experiment_state.experiment.workspace,
            X=X,
            y=y,
            sample_weight=sample_weight,
            X_valid=X_valid,
            y_valid=y_valid,
            sample_weight_valid=sample_weight_valid,
            training_data=training_data,
            validation_data=validation_data,
            test_data=test_data,
        )

        dataset_utilities.collect_usage_telemetry(
            compute=self.experiment_state.automl_settings.compute_target,
            spark_context=self.experiment_state.automl_settings.spark_context,
            X=X,
            y=y,
            sample_weight=sample_weight,
            X_valid=X_valid,
            y_valid=y_valid,
            sample_weight_valid=sample_weight_valid,
            training_data=training_data,
            validation_data=validation_data,
            test_data=test_data,
        )

        if isinstance(self.driver, LocalManagedExperimentLauncher):
            kwargs["data_params"] = {
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

        X, y, sample_weight, X_valid, y_valid, sample_weight_valid = dataset_utilities.convert_inputs(
            X, y, sample_weight, X_valid,
            y_valid, sample_weight_valid
        )

        updated_params = {
            "X": X,
            "y": y,
            "sample_weight": sample_weight,
            "X_valid": X_valid,
            "y_valid": y_valid,
            "sample_weight_valid": sample_weight_valid,
            "cv_splits_indices": cv_splits_indices,
            "training_data": training_data,
            "validation_data": validation_data,
            "test_data": test_data,
            "run_configuration": run_configuration,
            "kwargs": kwargs
        }

        self.driver.create_parent_run(
            run_configuration,
            compute_target,
            X,
            y,
            sample_weight,
            X_valid,
            y_valid,
            sample_weight_valid,
            cv_splits_indices,
            existing_run,
            training_data,
            validation_data,
            test_data,
            _script_run,
            parent_run_id,
            kwargs)
        assert self.experiment_state.current_run
        self.experiment_state.parent_run_id = self.experiment_state.current_run.id
        self.experiment_state.console_writer.print_run_info(self.experiment_state.current_run)
        return updated_params

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
        if not self.driver:
            driver_constructor = self._select_driver(self.experiment_state.automl_settings.compute_target)
            self.driver = driver_constructor(self.experiment_state)
        if kwargs is None:
            kwargs = {}
        try:
            self.experiment_state.current_run = self.driver.start(
                run_configuration=run_configuration,
                compute_target=self.experiment_state.automl_settings.compute_target,
                X=X,
                y=y,
                sample_weight=sample_weight,
                X_valid=X_valid,
                y_valid=y_valid,
                sample_weight_valid=sample_weight_valid,
                cv_splits_indices=cv_splits_indices,
                existing_run=existing_run,
                training_data=training_data,
                validation_data=validation_data,
                test_data=test_data,
                _script_run=_script_run,
                parent_run_id=parent_run_id,
                kwargs=kwargs
            )
            assert self.experiment_state.current_run
            return self.experiment_state.current_run
        except Exception as e:
            driver_utilities.fail_parent_run(
                self.experiment_state,
                error_details=e,
                is_aml_compute=self.experiment_state.automl_settings.compute_target != "local")
            raise

    def cancel(self) -> None:
        if self.driver:
            self.driver.cancel()

    def _select_driver(self, compute_target: Union[str, ComputeTarget]) -> "Type[BaseExperimentDriver]":
        if self.experiment_state.automl_settings.spark_context:
            try:
                from azureml.train.automl.runtime._experiment_drivers.spark_experiment_driver import (
                    SparkExperimentDriver,
                )
                return cast("Type[BaseExperimentDriver]", SparkExperimentDriver)
            except ImportError as e:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        RuntimeModuleDependencyMissing, target="compute_target", module_name=e.name),
                    inner_exception=e
                ) from e
        elif compute_target == constants.ComputeTargets.LOCAL:
            if self.experiment_state.automl_settings.enable_local_managed:
                # local managed
                return cast("Type[BaseExperimentDriver]", LocalManagedExperimentLauncher)
            else:
                try:
                    # legacy local
                    from azureml.train.automl.runtime._experiment_drivers.local_experiment_driver import (
                        LocalExperimentDriver,
                    )
                    return cast("Type[BaseExperimentDriver]", LocalExperimentDriver)
                except ImportError as e:
                    raise ConfigException._with_error(
                        AzureMLError.create(
                            RuntimeModuleDependencyMissing, target="compute_target", module_name=e.name),
                        inner_exception=e
                    ) from e
        else:
            from .remote_experiment_launcher import RemoteExperimentLauncher
            return cast("Type[BaseExperimentDriver]", RemoteExperimentLauncher)
