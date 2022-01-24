# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utility methods used in local managed submission for automated ML in Azure Machine Learning."""
import logging
import os
import pickle as pkl
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any, cast, Dict, List, Optional, Tuple

from azureml.train.automl._experiment_drivers import driver_utilities
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml._common.exceptions import AzureMLException
from azureml._common._error_definition import AzureMLError
from azureml._restclient.constants import RunStatus
from azureml.exceptions import ServiceException as AzureMLServiceException
from azureml.automl.core.console_writer import ConsoleWriter
from azureml.automl.core.package_utilities import _validate_package
from azureml.automl.core._run import run_lifecycle_utilities
from azureml.automl.core.shared.constants import SupportedInputDatatypes, TelemetryConstants
from azureml.automl.core.shared.pickler import DefaultPickler
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    AutoMLInternal, InvalidInputDatatype, ManagedLocalUserError)
from azureml.automl.core.shared import logging_utilities
from azureml.core.experiment import Experiment
from azureml.core.runconfig import RunConfiguration
from azureml.core.workspace import Workspace
from azureml.core import Dataset, Environment
from azureml.core import ScriptRunConfig, Run
from azureml.data.abstract_dataset import AbstractDataset
from azureml.automl.core.shared.exceptions import AutoMLException, UserException, ValidationException
from azureml.train.automl._constants_azureml import CodePaths
from azureml.train.automl.constants import _DataArgNames
from azureml.train.automl._environment_utilities import modify_run_configuration
from azureml.train.automl._azure_experiment_state import AzureExperimentState
from azureml.train.automl._remote_console_interface import RemoteConsoleInterface
from azureml.train.automl import _azureautomlsettings, _logging
from .exceptions import ClientException
from . import constants
from .run import AutoMLRun

logger = logging.getLogger(__name__)


def get_data_args(fit_params: Dict[str, Any], local_path: str) -> \
        Tuple[Dict[str, Any], List[str]]:
    """
    Extract data parameters, pickle them, and get args to pass to local managed script.
    This will either be Dataset IDs, or paths to pickle objects.
    """
    fit_params, data_dict = _extract_data(fit_params)
    dataset_args = handle_data(data_dict, local_path)

    return fit_params, dataset_args


def _save_inmem(path: str, name: str, data: Any) -> str:
    file_name = name + ".pkl"
    file_path = os.path.join(path, file_name)
    pickler = DefaultPickler()
    pickler.dump(data, file_path)
    return file_name


def _compose_args(dataset_args: List[Any], name: str, data_type: str, value: Optional[Any]) -> List[str]:
    arg = "--{}"
    arg_type = "--{}-dtype"

    if value is not None:
        dataset_args.append(arg.format(name))
        dataset_args.append(value)
        dataset_args.append(arg_type.format(name))
        dataset_args.append(data_type)

    return dataset_args


def _extract_data(fit_params: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Remove data params from fit params."""
    data_dict = {_DataArgNames.X: fit_params.pop(_DataArgNames.X, None),
                 _DataArgNames.y: fit_params.pop(_DataArgNames.y, None),
                 _DataArgNames.sample_weight: fit_params.pop(_DataArgNames.sample_weight, None),
                 _DataArgNames.X_valid: fit_params.pop(_DataArgNames.X_valid, None),
                 _DataArgNames.y_valid: fit_params.pop(_DataArgNames.y_valid, None),
                 _DataArgNames.sample_weight_valid: fit_params.pop(_DataArgNames.sample_weight_valid, None),
                 _DataArgNames.training_data: fit_params.pop(_DataArgNames.training_data, None),
                 _DataArgNames.validation_data: fit_params.pop(_DataArgNames.validation_data, None)}
    return fit_params, data_dict


def handle_data(data_dict: Dict[str, Any],
                local_path: str) -> List[str]:
    """
    Register datasets and create script arguments to pass to the child job.

    :param data_dict: Dictionary of names of data inputs and corresponding data.
    :param local_path: The path to save pickled data to.
    :return: List of arguments to pass to a ScriptRun with locations/ids of all data needed.
    """
    dataset_args = []  # type: List[str]
    has_pandas = False
    has_numpy = False
    try:
        import pandas as pd
        has_pandas = True
    except ImportError:
        pass
    try:
        import numpy as np
        has_numpy = True
    except ImportError:
        pass
    logger.info("Pandas present: {}. Numpy present: {}".format(has_pandas, has_numpy))
    for data_name, data_value in data_dict.items():
        if isinstance(data_value, AbstractDataset):
            logger.info("Saving Dataset for script run submission.")
            # ScriptRunConfig will translate the DatasetConsumptionConfig into a dataset id
            dataset_args = _compose_args(dataset_args,
                                         data_name,
                                         "dataset",
                                         data_value.as_named_input(data_name))
        elif has_pandas and isinstance(data_value, pd.DataFrame):
            _validate_package("pandas")
            logger.info("Saving Pandas for script run submission.")

            dataset_args = _compose_args(dataset_args,
                                         data_name,
                                         "pandas",
                                         _save_inmem(local_path, data_name, data_value))
        elif has_numpy and isinstance(data_value, np.ndarray):
            _validate_package("numpy")
            logger.info("Saving Numpy for script run submission.")
            dataset_args = _compose_args(dataset_args,
                                         data_name,
                                         "numpy",
                                         _save_inmem(local_path, data_name, data_value))
        elif data_value is not None:
            raise ValidationException._with_error(
                AzureMLError.create(
                    InvalidInputDatatype, target=data_name, input_type=type(data_value),
                    supported_types=", ".join(SupportedInputDatatypes.ALL)
                )
            )

    return dataset_args


def modify_managed_run_config(run_config, parent_run, experiment, settings_obj):
    _logging.set_run_custom_dimensions(
        automl_settings=settings_obj,
        parent_run_id=parent_run.id,
        child_run_id=None,
        code_path=CodePaths.LOCAL_MANAGED)

    if run_config is None:
        run_config = RunConfiguration()

    properties = parent_run.get_properties()
    env_name = properties.get("environment_cpu_name")
    env_version = properties.get("environment_cpu_version")
    if env_version == "":
        env_version = None
    logger.info("Running local managed run on curated environment: {} version: {}".format(env_name, env_version))
    is_docker = run_config.docker.use_docker  # We want to honor the original user input
    if env_name is None or env_name == "":
        run_config.environment.python.user_managed_dependencies = False
        run_config = modify_run_configuration(settings_obj, run_config, logger)
    else:
        run_config.environment = Environment.get(experiment.workspace, env_name, env_version)
    run_config.docker.use_docker = is_docker
    # since we may have a different docker flag, ES doesn't like the "AzureML-" prefix
    if run_config.environment.name and run_config.environment.name.startswith("AzureML"):
        run_config.environment.name = "AutoML-" + run_config.environment.name
    return run_config


def prepare_managed_inputs(experiment_state, local_path, data_params, run_config):
    """
    :param experiment_state: The state of the experiment in the driver
    :param local_path: The local folder to stage files in.
    :param settings_obj: The AutoMLSettings.
    :param data_params: All the data parameters passed in to fit().
    :param run_config: The run config for this run.
    :return: A tuple containing the parent run, the dataset arguments for use with the scriptrunconfig,
        the automl settings, and the run configuration
    """
    package_dir = os.path.dirname(os.path.abspath(__file__))

    script_path = os.path.join(package_dir, constants.LOCAL_SCRIPT_NAME)
    shutil.copy(script_path, os.path.join(local_path, constants.LOCAL_SCRIPT_NAME))

    logger.info("Pickling data and settings for local managed.")

    settings = experiment_state.automl_settings.as_serializable_dict()

    settings[constants.MANAGED_RUN_ID_PARAM] = experiment_state.current_run.id
    fit_params, dataset_args = get_data_args(data_params, local_path)

    run_config = modify_managed_run_config(run_config, experiment_state.current_run, experiment_state.experiment,
                                           experiment_state.automl_settings)
    with open(os.path.join(local_path, constants.AUTOML_SETTINGS_PATH), 'wb') as fp:
        pkl.dump(settings, fp)

    return dataset_args, settings, run_config


def create_parent_run_for_local_managed(
        experiment_state: AzureExperimentState, data_params: Dict[str, Any], parent_run_id: Optional[str] = None) \
        -> Run:
    """
    Create parent run in Run History containing AutoML experiment information for a local docker or conda run.
    Local managed runs will go through typical _create_parent_run_for_local workflow which will do the validation
    steps.

    :return: AutoML parent run
    :rtype: azureml.core.Run
    """
    in_mem_data = False
    for param in data_params:
        if not isinstance(param, AbstractDataset):
            in_mem_data = True

    if in_mem_data:
        parent_run_dto = driver_utilities.create_parent_run_dto(
            experiment_state, target=constants.ComputeTargets.LOCAL, parent_run_id=parent_run_id
        )
    else:
        parent_run_dto = driver_utilities.create_and_validate_parent_run_dto(
            experiment_state, target=constants.ComputeTargets.LOCAL, parent_run_id=parent_run_id, **data_params
        )

    try:
        logger.info("Start creating parent run")
        experiment_state.parent_run_id = experiment_state.jasmine_client.post_parent_run(parent_run_dto)

        Contract.assert_value(experiment_state.parent_run_id, "parent_run_id")

        logger.info("Successfully created a parent run with ID: {}".format(experiment_state.parent_run_id))

        _logging.set_run_custom_dimensions(
            automl_settings=experiment_state.automl_settings,
            parent_run_id=experiment_state.parent_run_id,
            child_run_id=None,
            code_path=CodePaths.LOCAL_MANAGED
        )
    except (AutoMLException, AzureMLException, AzureMLServiceException):
        raise
    except Exception as e:
        logging_utilities.log_traceback(e, logger)
        raise ClientException.from_exception(e, target="_create_parent_run_for_local_managed").with_generic_msg(
            "Error when trying to create parent run in automl service."
        )

    logger.info("Setting Run {} status to: {}".format(
        str(experiment_state.parent_run_id), constants.RunState.PREPARE_RUN))
    experiment_state.jasmine_client.set_parent_run_status(
        experiment_state.parent_run_id, constants.RunState.PREPARE_RUN
    )

    experiment_state.current_run = Run(experiment_state.experiment, experiment_state.parent_run_id)

    return experiment_state.current_run


def handle_script_run_error(parent_run: Run, script_run: Optional[Run]) -> None:
    bad_states = [RunStatus.FAILED, RunStatus.CANCELED]
    terminal_states = bad_states + [RunStatus.COMPLETED]
    is_running = parent_run is not None and parent_run.get_status() not in terminal_states

    if parent_run is None:
        return

    if script_run is None:
        ex_wrapped = ClientException._with_error(
            AzureMLError.create(
                AutoMLInternal,
                error_details="Local managed failed before submission.",
            )
        )
        if is_running and parent_run is not None:
            run_lifecycle_utilities.fail_run(parent_run, ex_wrapped, is_aml_compute=False)
        raise ex_wrapped

    # Wait for the script_run to propagate all of the errors
    with logging_utilities.log_activity(
            logger,
            activity_name=TelemetryConstants.ScriptRunFinalizing,
            custom_dimensions={'run_id': parent_run.id, "script_run_id": script_run.id}):
        while script_run.get_status() == "Finalizing":
            time.sleep(5)

    failed = script_run.get_status() in bad_states

    error = script_run.get_details().get('error')

    if failed and error is not None:
        failed_in_wrapper_error = 'Local execution of User Script failed.'
        error_message = error.get('error', {}).get('message', '')
        if failed_in_wrapper_error in error_message:
            error_string = "Local managed run failed with an internal error: {}.".format(error["error"])
            error = AzureMLError.create(
                AutoMLInternal, error_details=error_string, reference_code=ReferenceCodes._LOCAL_MANAGED_INTERNAL_ERROR
            )
            ex_wrapped = ClientException(azureml_error=error)

            if is_running and parent_run is not None:
                run_lifecycle_utilities.fail_run(parent_run, ex_wrapped, is_aml_compute=False)
            raise ex_wrapped
        else:
            # let the script_run error handling take over as we know this issue wasn't caused by local managed wrapper.
            error_type = error["error"].get("code")
            user_exception = UserException._with_error(
                AzureMLError.create(
                    ManagedLocalUserError,
                    error_type=error_type
                )
            )
            if is_running and parent_run is not None:
                run_lifecycle_utilities.fail_run(parent_run, user_exception, is_aml_compute=False)
            # wait for completion will throw the original script run failure to the user
            script_run.wait_for_completion()


def _get_dataset(workspace: Workspace, dataset_id: str) -> Optional[AbstractDataset]:
    try:
        logger.info("Fetching dataset {}.".format(dataset_id))
        return Dataset.get_by_id(workspace=workspace, id=dataset_id)
    except Exception:
        logger.info("Failed to fetch dataset {}.".format(dataset_id))
        return None


def _get_inmem(file_path):
    logger.info("Fetching in memory data.")
    pickler = DefaultPickler()
    return pickler.load(file_path)


def get_data(workspace: Workspace, location: str, dtype: str) -> Any:
    if dtype == "numpy" or dtype == "pandas":
        return _get_inmem(file_path=location)
    else:
        return _get_dataset(workspace, dataset_id=location)


def is_docker_installed() -> bool:
    try:
        version = subprocess.check_output(["docker", "--version"]).decode('utf8')
        logger.info("Docker is installed with {}.".format(version))
    except Exception:
        logger.info("Docker is not installed.")
        return False
    return True
