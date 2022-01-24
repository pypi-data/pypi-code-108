# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Proxy for models produced by AutoML."""
import logging
import os
import pickle
import shutil
import tempfile
from typing import Any, Optional, Tuple, TYPE_CHECKING, Union, Dict


from azureml._base_sdk_common._docstring_wrapper import experimental
from azureml._common._error_definition import AzureMLError
from azureml._common._error_definition.user_error import (
    ArgumentBlankOrEmpty, ComputeNotFound)
from azureml._restclient.constants import RunStatus
from azureml._restclient.jasmine_client import JasmineClient
from azureml._restclient.models import ModelTest
from azureml.automl.core import dataprep_utilities, dataset_utilities
from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared.constants import SupportedInputDatatypes, TelemetryConstants
from azureml.automl.core.shared.exceptions import ConfigException
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    InvalidArgumentType, InvalidInputDatatype, InvalidOperationOnRunState,
    LocalInferenceUnsupported, RemoteInferenceUnsupported)
from azureml.core import Dataset, Datastore, Run, RunConfiguration, ScriptRunConfig
from azureml.core.compute import ComputeTarget
from azureml.core.compute_target import LocalTarget
from azureml.data.abstract_dataset import AbstractDataset
from azureml.data.constants import WORKSPACE_BLOB_DATASTORE
from azureml.data.tabular_dataset import TabularDataset
from azureml.exceptions import ServiceException as AzureMLServiceException
from .constants import LOCAL_PREDICT_NAME, SCRIPT_RUN_ID_PROPERTY
from .utilities import _InternalComputeTypes
from ._local_managed_utils import handle_data
if TYPE_CHECKING:
    from pandas import Timestamp
else:
    Timestamp = Any


PREDICT = "predict"
PREDICT_PROBA = "predict_proba"
FORECAST = "forecast"
FORECAST_QUANTILES = "forecast_quantiles"
RESULTS_PROPERTY = "inference_results"


logger = logging.getLogger(__name__)


@experimental
class ModelProxy:
    """Proxy object for AutoML models that enables inference on remote compute."""

    def __init__(self, child_run, compute_target=None):
        """
        Create an AutoML ModelProxy object to submit inference to the training environment.

        :param child_run: The child run from which the model will be downloaded.
        :param compute_target: Overwrite for the target compute to inference on.
        """
        if not isinstance(child_run, Run):
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentType, target="child_run",
                    argument="child_run", actual_type=type(child_run), expected_types="azureml.core.Run")
            )

        self.run = child_run
        if compute_target is not None:
            if isinstance(compute_target, ComputeTarget):
                self.compute_target = compute_target.name
            elif isinstance(compute_target, str):
                self.compute_target = compute_target
            else:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        InvalidArgumentType, target="compute_target",
                        argument="compute_target", actual_type=type(compute_target),
                        expected_types="str, azureml.core.compute.ComputeTarget"
                    )
                )
        else:
            self.compute_target = self.run._run_dto.get('target', LocalTarget())

        self._check_is_valid_compute()

        self._jasmine_client_instance = None

    def _fetch_env(self):
        script_run_id = self.run.parent.get_properties().get(SCRIPT_RUN_ID_PROPERTY)
        if script_run_id is None:
            try:
                env = self.run.get_environment()
            except Exception as e:
                if isinstance(e, KeyError) or \
                        "There is no run definition or environment specified for the run." in str(e) or \
                        "There is no environment specified for the run" in str(e):
                    raise ConfigException._with_error(
                        AzureMLError.create(
                            RemoteInferenceUnsupported, target="model_proxy"
                        )
                    )
                raise
        else:
            script_run = Run(self.run.experiment, script_run_id)
            env = script_run.get_environment()
        return env

    def _get_tabular_dataset_from_datastore(self, location: str) -> AbstractDataset:
        dataset = None
        workspace = self.run.experiment.workspace

        try:
            datastore = Datastore.get(workspace, WORKSPACE_BLOB_DATASTORE)
            dataset = Dataset.Tabular.from_delimited_files(path=[(datastore, location)])
        except Exception:
            # Currently, the first parameter in this warning message
            # is a log-safe value since it is created by the SDK using
            # a predefined template with no user identifiable information in it.
            # See _model_test_utilities.py::_save_results for more details.
            logger.warning("Did not find the delimited file {} in datastore: {}"
                           .format(location, WORKSPACE_BLOB_DATASTORE))

        if dataset is None:
            datastore = workspace.get_default_datastore()
            dataset = Dataset.Tabular.from_delimited_files(path=[(datastore, location)])

        return dataset

    def _fetch_results(self, run: Run) \
            -> Union[AbstractDataset, Tuple[AbstractDataset, AbstractDataset]]:
        results_locations = run.get_properties().get(RESULTS_PROPERTY)
        results_locations = eval(results_locations)

        if len(results_locations) == 1:
            returned_values = self._get_tabular_dataset_from_datastore(results_locations[0])
        else:
            # some inference methods can return tuples, format appropriately
            returned_values = ()
            for location in results_locations:
                returned_values += (self._get_tabular_dataset_from_datastore(location),)

        return returned_values

    @property
    def _jasmine_client(self):
        if not self._jasmine_client_instance:
            try:
                experiment = self.run.experiment
                self._jasmine_client_instance = JasmineClient(
                    experiment.workspace.service_context,
                    experiment.name,
                    experiment.id)
            except AzureMLServiceException as e:
                logging_utilities.log_traceback(e, logger)
                raise
        return self._jasmine_client_instance

    def _verify_run_completed(self):
        run_status = self.run.get_status()
        if run_status != RunStatus.COMPLETED:
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidOperationOnRunState, target="predict/test", operation_name="predict/test",
                    run_id=self.run.id, run_state=run_status
                )
            )

    def _check_is_valid_compute(self):
        if self.compute_target != _InternalComputeTypes.LOCAL and \
                not isinstance(self.compute_target, LocalTarget) and \
                self.compute_target not in self.run.experiment.workspace.compute_targets:
            raise ConfigException._with_error(
                AzureMLError.create(
                    ComputeNotFound,
                    target=self.compute_target,
                    compute_name=self.compute_target,
                    workspace_name=self.run.experiment.workspace.name
                )
            )

    def _inference(self,
                   function_name: str,
                   values: Any,
                   y_values: Optional[Any] = None,
                   forecast_destination: Optional[Timestamp] = None,
                   ignore_data_errors: bool = False) \
            -> Union[AbstractDataset, Tuple[AbstractDataset, AbstractDataset]]:
        logger.info("Submitting inference job.")

        self._verify_run_completed()

        with logging_utilities.log_activity(logger, activity_name=TelemetryConstants.REMOTE_INFERENCE):
            with tempfile.TemporaryDirectory() as project_folder:
                data_dict = {"values": values, "y_values": y_values}
                data_args = handle_data(data_dict, project_folder)

                run_configuration = RunConfiguration()

                env = self._fetch_env()

                run_configuration.environment = env
                run_configuration.target = self.run._run_dto.get('target', _InternalComputeTypes.LOCAL)
                run_configuration.script = LOCAL_PREDICT_NAME

                # TODO, how to enable docker for local inference?
                # run_configuration.docker.use_docker = docker

                if self.compute_target is not None:
                    run_configuration.target = self.compute_target

                run_configuration.docker.use_docker = True

                package_dir = os.path.dirname(os.path.abspath(__file__))
                script_path = os.path.join(package_dir, LOCAL_PREDICT_NAME)
                shutil.copy(script_path, os.path.join(project_folder, LOCAL_PREDICT_NAME))

                data_args.extend(["--child_run_id", self.run.id,
                                  "--function_name", function_name])

                if function_name == FORECAST_QUANTILES:
                    data_args.extend(["--forecast-destination", str(forecast_destination),
                                      "--ignore-data-errors", str(ignore_data_errors)])

                src = ScriptRunConfig(source_directory=project_folder,
                                      run_config=run_configuration,
                                      arguments=data_args)

                logger.info("Submitting script run for inferencing.")
                script_run = self.run.submit_child(src)

                logger.info("Waiting for script run for inferencing to complete.")
                script_run.wait_for_completion(show_output=False, wait_post_processing=True)

                logger.info("Inferencing complete.")
                return self._fetch_results(script_run)

    def predict(self, values: Any) -> AbstractDataset:
        """
        Submit a job to run predict on the model for the given values.

        :param values: Input test data to run predict on.
        :type values: azureml.data.abstract_dataset.AbstractDataset or pandas.DataFrame or numpy.ndarray
        :return: The predicted values.
        """
        return self._inference(PREDICT, values)

    def predict_proba(self, values: Any) -> AbstractDataset:
        """
        Submit a job to run predict_proba on the model for the given values.

        :param values: Input test data to run predict on.
        :type values: azureml.data.abstract_dataset.AbstractDataset or pandas.DataFrame or numpy.ndarray
        :return: The predicted values.
        """
        return self._inference(PREDICT_PROBA, values)

    def forecast(self, X_values: Any, y_values: Optional[Any] = None) -> Tuple[AbstractDataset, AbstractDataset]:
        """
        Submit a job to run forecast on the model for the given values.

        :param X_values: Input test data to run forecast on.
        :type X_values: azureml.data.abstract_dataset.AbstractDataset or pandas.DataFrame or numpy.ndarray
        :param y_values: Input y values to run the forecast on.
        :type y_values: azureml.data.abstract_dataset.AbstractDataset or pandas.DataFrame or numpy.ndarray
        :return: The forecast values.
        """
        return self._inference(FORECAST, X_values, y_values)

    def forecast_quantiles(self,
                           X_values: Any,
                           y_values: Optional[Any] = None,
                           forecast_destination: Optional[Timestamp] = None,
                           ignore_data_errors: bool = False) -> AbstractDataset:
        """
        Submit a job to run forecast_quantiles on the model for the given values.

        :param X_values: Input test data to run forecast on.
        :type X_values: azureml.data.abstract_dataset.AbstractDataset
        :param y_values: Input y values to run the forecast on.
        :param forecast_destination: Forecast_destination: a time-stamp value.
                                     Forecasts will be made all the way to the forecast_destination time,
                                     for all grains. Dictionary input { grain -> timestamp } will not be accepted.
                                     If forecast_destination is not given, it will be imputed as the last time
                                     occurring in X_pred for every grain.
        :type forecast_destination: pandas.Timestamp
        :param ignore_data_errors: Ignore errors in user data.
        :type ignore_data_errors: bool
        :return:
        """
        return self._inference(FORECAST_QUANTILES, X_values, y_values, forecast_destination, ignore_data_errors)

    def test(self,
             test_data: AbstractDataset,
             include_predictions_only: bool = False) -> Tuple[AbstractDataset, Dict[str, Any]]:
        """
        Retrieve predictions from the ``test_data`` and compute relevant metrics.

        :param test_data: The test dataset.
        :param include_predictions_only: Whether or not to only include the predictions
            as part of the predictions.csv output.

            If this parameter is ``True`` then the output CSV columns look like
            (forecasting is the same as regression):

                ``Classification => [predicted values], [probabilities]``

                ``Regression     => [predicted values]``

            else (default):

                ``Classification => [original test data labels], [predicted values], [probabilities], [features]``

                ``Regression     => [original test data labels], [predicted values], [features]``

            The ``[original test data labels]`` column name = ``[label column name] + "_orig"``.

            The ``[predicted values]`` column name = ``[label column name] + "_predicted"``.

            The ``[probabilities]`` column names = ``[class name] + "_predicted_proba"``.

            The ``[features]`` column names = ``[feature column name] + "_orig"``.

            If the ``test_data`` does not include a target column then ``[original test data labels]``
            will not be in the output dataframe.

        :return: A tuple containing the predicted values and the metrics.
        """
        if self.compute_target == _InternalComputeTypes.LOCAL:
            raise ConfigException._with_error(
                AzureMLError.create(
                    LocalInferenceUnsupported, target="model_proxy"
                )
            )

        if not isinstance(test_data, TabularDataset):
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidInputDatatype, target='test_data', input_type=str(type(test_data)),
                    supported_types=SupportedInputDatatypes.TABULAR_DATASET
                )
            )

        self._verify_run_completed()

        dataset_utilities.ensure_saved(self.run.experiment.workspace,
                                       test_data=test_data)

        dataprep_json = dataset_utilities.get_datasets_json(test_data=test_data)
        if dataprep_json is not None:
            # escape quotations in json_str before sending to jasmine
            dataprep_json = dataprep_json.replace('\\', '\\\\').replace('"', '\\"')

        model_test_dto = ModelTest(compute_target=self.compute_target,
                                   data_prep_json_string=dataprep_json,
                                   compute_metrics=True,
                                   include_predictions_only=include_predictions_only)

        test_run_id = self._jasmine_client.post_on_demand_model_test_run(self.run.id,
                                                                         model_test_dto)
        test_run = Run(experiment=self.run.experiment, run_id=test_run_id)
        test_run.wait_for_completion(show_output=False, wait_post_processing=True)

        output_dataset = self._fetch_results(test_run)
        metrics = test_run.get_metrics()
        return output_dataset, metrics
