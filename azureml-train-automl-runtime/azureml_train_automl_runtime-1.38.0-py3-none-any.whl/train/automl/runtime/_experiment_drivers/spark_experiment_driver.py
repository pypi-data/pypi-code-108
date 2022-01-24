# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import logging
import threading
from typing import Any, Dict, List, Optional, Union

from azureml._common._error_definition import AzureMLError
from azureml._restclient.service_context import ServiceContext
from azureml.core import Run
from azureml.core.authentication import AzureMLTokenAuthentication
from azureml.core.experiment import Experiment
from azureml.core.runconfig import RunConfiguration
from azureml.core.workspace import Workspace

from azureml.automl.core import dataprep_utilities, dataset_utilities
from azureml.automl.core._experiment_drivers.base_experiment_driver import BaseExperimentDriver
from azureml.automl.core._run import run_lifecycle_utilities
from azureml.automl.core._run.types import RunType
from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared._diagnostics.automl_error_definitions import RunInterrupted
from azureml.automl.core.shared.exceptions import ClientException, ConfigException
from azureml.train.automl._azure_experiment_state import AzureExperimentState
from azureml.train.automl._experiment_drivers import driver_utilities
from azureml.train.automl._remote_console_interface import RemoteConsoleInterface
from azureml.train.automl.automl_adb_run import AutoMLADBRun
from azureml.train.automl.runtime._entrypoints import spark_worker_node_entrypoint

logger = logging.getLogger(__name__)


class SparkExperimentDriver(BaseExperimentDriver):
    def __init__(self,
                 experiment_state: AzureExperimentState) -> None:
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
        driver_utilities.create_remote_parent_run(
            self.experiment_state,
            run_configuration, X=X, y=y, sample_weight=sample_weight, X_valid=X_valid, y_valid=y_valid,
            sample_weight_valid=sample_weight_valid, cv_splits_indices=cv_splits_indices,
            training_data=training_data, validation_data=validation_data, test_data=test_data)
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
        self._init_spark_driver_run(
            run_configuration,
            X,
            y,
            sample_weight,
            X_valid,
            y_valid,
            sample_weight_valid,
            cv_splits_indices,
            training_data,
            validation_data,
            self.experiment_state.console_writer.show_output,
            existing_run
        )
        assert self.experiment_state.current_run
        return self.experiment_state.current_run

    def _init_spark_driver_run(
            self,
            run_configuration=None,
            X=None,
            y=None,
            sample_weight=None,
            X_valid=None,
            y_valid=None,
            sample_weight_valid=None,
            cv_splits_indices=None,
            training_data=None,
            validation_data=None,
            show_output=False,
            existing_run=False,
    ):

        self.experiment_state.console_writer.println(
            "Running an experiment on spark cluster: {0}.\n".format(self.experiment_state.experiment.name)
        )

        driver_utilities.check_package_compatibilities(self.experiment_state, is_managed_run=False)

        try:
            if not existing_run:
                driver_utilities.start_remote_run(
                    self.experiment_state,
                    run_configuration
                )
            # This should be refactored to have RunHistoryClient and make call on it to get token
            # use Experiment object to get name and other parameters
            token_res = self.experiment_state.experiment_client._client.run.get_token(
                experiment_name=self.experiment_state.experiment.name,
                resource_group_name=self.experiment_state.experiment.workspace.resource_group,
                subscription_id=self.experiment_state.experiment.workspace.subscription_id,
                workspace_name=self.experiment_state.experiment.workspace.name,
                run_id=self.experiment_state.current_run.run_id,
            )
            aml_token = token_res.token
            aml_token_expiry = token_res.expiry_time_utc

            service_context = ServiceContext(
                subscription_id=self.experiment_state.experiment.workspace.subscription_id,
                resource_group_name=self.experiment_state.experiment.workspace.resource_group,
                workspace_name=self.experiment_state.experiment.workspace.name,
                workspace_id=self.experiment_state.experiment.workspace._workspace_id,
                workspace_discovery_url=self.experiment_state.experiment.workspace.discovery_url,
                authentication=self.experiment_state.experiment.workspace._auth_object,
            )

            run_history_url = service_context._get_run_history_url()
            fn_script = None
            if self.experiment_state.automl_settings.data_script:
                with open(self.experiment_state.automl_settings.data_script, "r") as f:
                    fn_script = f.read()

            training_data, validation_data = dataset_utilities.convert_inputs_dataset(
                training_data,
                validation_data
            )
            if training_data is None and validation_data is None:
                dataprep_json = dataprep_utilities.get_dataprep_json(
                    X=X,
                    y=y,
                    sample_weight=sample_weight,
                    X_valid=X_valid,
                    y_valid=y_valid,
                    sample_weight_valid=sample_weight_valid,
                    cv_splits_indices=cv_splits_indices,
                )
            else:
                dataprep_json = dataprep_utilities.get_dataprep_json_dataset(
                    training_data=training_data, validation_data=validation_data
                )

            # Remove path when creating the DTO
            settings_dict = self.experiment_state.automl_settings.as_serializable_dict()
            settings_dict["path"] = None

            # build dictionary of context
            run_context = {
                "subscription_id": self.experiment_state.experiment.workspace.subscription_id,
                "resource_group": self.experiment_state.experiment.workspace.resource_group,
                "location": self.experiment_state.experiment.workspace.location,
                "workspace_name": self.experiment_state.experiment.workspace.name,
                "experiment_name": self.experiment_state.experiment.name,
                "experiment_id": self.experiment_state.experiment.id,
                "parent_run_id": self.experiment_state.current_run.run_id,
                "aml_token": aml_token,
                "aml_token_expiry": aml_token_expiry,
                "service_url": run_history_url,
                "discovery_url": service_context._get_discovery_url(),
                "automl_settings_str": json.dumps(settings_dict),
                "dataprep_json": dataprep_json,
                "get_data_content": fn_script,
            }
            adb_automl_context = [
                (index, run_context)
                for index in range(0, self.experiment_state.automl_settings.max_concurrent_iterations)
            ]

            if not hasattr(self.experiment_state.automl_settings, "is_run_from_test"):
                adb_thread = AdbDriverThread(
                    "AutoML on Spark Experiment: {0}".format(self.experiment_state.experiment.name),
                    adb_automl_context,
                    self.experiment_state.automl_settings.spark_context,
                    self.experiment_state.automl_settings.max_concurrent_iterations,
                    self.experiment_state.current_run.run_id,
                )
                adb_thread.start()
                self.experiment_state.current_run = AutoMLADBRun(
                    self.experiment_state.experiment, self.experiment_state.parent_run_id, adb_thread
                )
            else:
                automlRDD = self.experiment_state.automl_settings. \
                    spark_context.parallelize(adb_automl_context,
                                              self.experiment_state.automl_settings.max_concurrent_iterations)

                # first schedule the setup and train iterations to run in parallel
                # then run the model explain iteration on a single worker
                automlRDD.map(spark_worker_node_entrypoint.run_setup_and_train_iterations).collect()
                adb_modelexp_context = [adb_automl_context[0]]
                automlRDD = self.experiment_state.automl_settings.spark_context.parallelize(adb_modelexp_context, 1)
                automlRDD.map(spark_worker_node_entrypoint.run_model_explain_iteration).collect()

            if show_output:
                RemoteConsoleInterface._show_output(
                    self.experiment_state.current_run,
                    self.experiment_state.console_writer,
                    logger,
                    self.experiment_state.automl_settings.primary_metric,
                )
        except Exception as ex:
            logging_utilities.log_traceback(ex, logger)
            raise

        assert self.experiment_state.current_run
        return self.experiment_state.current_run

    def cancel(self):
        run_lifecycle_utilities.cancel_run(
            self.experiment_state.current_run,
            warning_string=AzureMLError.create(RunInterrupted).error_message
        )


class AdbDriverThread(threading.Thread):
    """This code initiates the experiments to be run on worker nodes by calling adb map and collect."""

    def __init__(self, name, input_data, spark_context, partition_count, run_id):
        """
        Initialize the AdbDriverThread class.

        :param name: Name of the experiment run.
        :type name: string
        :param input_data: Input context data for the worker node run.
        :type input_data: Array of tuple [(worker_id, context_dictionary),(worker_id, context_dictionary)]
        :param spark_context: Spark context.
        :type spark_context: spark context.
        :param partition_count: Partition count.
        :type partition_count: int
        :param run_id: Run id.
        :type run_id: string
        """
        super().__init__()
        self.name = name
        self.input_data = input_data
        self.spark_context = spark_context
        self.partition_count = partition_count
        self.run_id = run_id

    def run(self):
        if not hasattr(self.spark_context, 'setJobGroup'):
            raise ConfigException.create_without_pii(
                "Invalid spark context object in AutoML Config.\
                     sc should be set to spark context object to run on spark cluster")

        self.spark_context.setJobGroup(self.run_id, "AutoML Run on spark", True)
        automlRDD = self.spark_context.parallelize(self.input_data, self.partition_count)
        automlRDD.map(spark_worker_node_entrypoint.run_setup_and_train_iterations).collect()
        # model explain iteration should have only one partition/worker
        adb_modelexp_context = [self.input_data[0]]
        automlRDD = self.spark_context.parallelize(adb_modelexp_context, 1)
        automlRDD.map(spark_worker_node_entrypoint.run_model_explain_iteration).collect()

    def cancel(self):
        try:
            self.spark_context.cancelJobGroup(self.run_id)
        except Exception:
            raise ClientException.create_without_pii("Failed to cancel spark job with id: {}".format(self.run_id))

    def _rehydrate_experiment(self, run_context):
        subscription_id = run_context.get('subscription_id', None)
        resource_group = run_context.get('resource_group', None)
        workspace_name = run_context.get('workspace_name', None)
        location = run_context.get('location', None)
        aml_token = run_context.get('aml_token', None)
        aml_token_expiry = run_context.get('aml_token_expiry', None)
        experiment_name = run_context.get('experiment_name', None)
        parent_run_id = run_context.get('parent_run_id', None)
        service_url = run_context.get('service_url', None)
        auth = AzureMLTokenAuthentication.create(aml_token,
                                                 AzureMLTokenAuthentication._convert_to_datetime(aml_token_expiry),
                                                 service_url,
                                                 subscription_id,
                                                 resource_group,
                                                 workspace_name,
                                                 experiment_name,
                                                 parent_run_id)
        workspace = Workspace(subscription_id,
                              resource_group, workspace_name,
                              auth=auth,
                              _location=location,
                              _disable_service_check=True)
        experiment = Experiment(workspace, experiment_name)
        return experiment

    def _rehydrate_parent_run(self, run_context):
        parent_run_id = run_context.get('parent_run_id', None)
        return Run(self._rehydrate_experiment(run_context), parent_run_id)
