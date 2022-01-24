# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Common utilities across tasks."""

import json
import logging
import os
import sys
from typing import Dict, Optional, Union

from azureml.automl.core.inference import inference
from azureml.automl.core.shared import log_server
from azureml.automl.core.shared.logging_fields import TELEMETRY_AUTOML_COMPONENT_KEY

from azureml.automl.dnn.nlp.common.constants import LoggingLiterals, OutputLiterals, SystemSettings

from azureml.core.experiment import Experiment
from azureml.core.run import Run, _OfflineRun
from azureml.telemetry import INSTRUMENTATION_KEY, get_diagnostics_collection_info
from azureml.train.automl import constants
from azureml.train.automl._logging import set_run_custom_dimensions
from azureml.train.automl.constants import ComputeTargets, Tasks
from azureml.train.automl.runtime._azureautomlruncontext import AzureAutoMLRunContext


logger = logging.getLogger(__name__)


class AzureAutoMLSettingsStub:
    """Stub for AzureAutoMLSettings class to configure logging."""
    is_timeseries = False
    task_type = None
    compute_target = None
    name = None
    subscription_id = None
    region = None
    verbosity = None
    telemetry_verbosity = None
    send_telemetry = None
    azure_service = None


def _set_logging_parameters(task_type: constants.Tasks,
                            settings: Dict,
                            output_dir: Optional[str] = None,
                            azureml_run: Optional[Run] = None):
    """Sets the logging parameters so that we can track all the training runs from
    a given project.

    :param task_type: The task type for the run.
    :type task_type: constants.Tasks
    :param settings: All the settings for this run.
    :type settings: Dict
    :param output_dir: The output directory.
    :type Optional[str]
    :param azureml_run: The run object.
    :type Optional[Run]
    """
    log_server.update_custom_dimensions({LoggingLiterals.TASK_TYPE: task_type})

    if LoggingLiterals.PROJECT_ID in settings:
        project_id = settings[LoggingLiterals.PROJECT_ID]
        log_server.update_custom_dimensions({LoggingLiterals.PROJECT_ID: project_id})

    if LoggingLiterals.VERSION_NUMBER in settings:
        version_number = settings[LoggingLiterals.VERSION_NUMBER]
        log_server.update_custom_dimensions({LoggingLiterals.VERSION_NUMBER: version_number})

    _set_automl_run_custom_dimensions(task_type, output_dir, azureml_run)


def prepare_run_properties(run: Run,
                           model_name: str):
    """
    Add the run properties needed to display the run in UI

    :param run: Run object to add properties to
    :param model_name: Model being trained on this run
    """
    properties_to_add = {
        "runTemplate": "automl_child",
        "run_algorithm": model_name
    }
    run.add_properties(properties_to_add)


def prepare_post_run_properties(run: Run,
                                model_file: str,
                                model_size: int,
                                environment_file: str,
                                deploy_file: str,
                                primary_metric: str,
                                score: float):
    """Save model and weights to artifacts, conda environment yml,
       and save run properties needed for model export

    :param run: The current azureml run object
    :type run: azureml.core.Run
    :param model_file: The pytorch model saved after training
    :type model_file: str
    :type model_size: int
    :param model_size: size of the model in bytes
    :param environment_file: The environment file that can be used in inferencing environments
    :type environment_file: str
    :param deploy_file: Score script used in deployment
    :type deploy_file: str
    :param primary_metric: The primary metric used for the task
    :type primary_metric: str
    :param score: The score of the primary metric used for the task
    :type score: float
    """
    automl_run_context = AzureAutoMLRunContext(run)
    run_id = automl_run_context.run_id
    artifact_id = "aml://artifact/ExperimentRun/dcid.{}/".format(run_id)

    # Get model artifacts file paths
    conda_env_data_loc = os.path.join(artifact_id, environment_file)
    scoring_data_loc = os.path.join(artifact_id, deploy_file)
    model_artifacts_file = os.path.join(artifact_id, model_file)
    model_id = inference._get_model_name(run_id)

    # Add paths to run properties for model deployment
    properties_to_add = {
        inference.AutoMLInferenceArtifactIDs.ScoringDataLocation: scoring_data_loc,
        inference.AutoMLInferenceArtifactIDs.ScoringDataLocationV2: scoring_data_loc,
        inference.AutoMLInferenceArtifactIDs.CondaEnvDataLocation: conda_env_data_loc,
        inference.AutoMLInferenceArtifactIDs.ModelDataLocation: model_artifacts_file,
        inference.AutoMLInferenceArtifactIDs.ModelName: model_id,
        inference.AutoMLInferenceArtifactIDs.ModelSizeOnDisk: model_size,
        "score": score,
        "primary_metric": primary_metric
    }
    run.add_properties(properties_to_add)


def _set_automl_run_custom_dimensions(task_type: Tasks,
                                      output_dir: Optional[str] = None,
                                      azureml_run: Optional[Run] = None):
    if output_dir is None:
        output_dir = SystemSettings.LOG_FOLDER
    os.makedirs(output_dir, exist_ok=True)

    if azureml_run is None:
        azureml_run = Run.get_context()

    name = "not_available_offline"
    subscription_id = "not_available_offline"
    region = "not_available_offline"
    parent_run_id = "not_available_offline"
    child_run_id = "not_available_offline"
    if not isinstance(azureml_run, _OfflineRun):
        # If needed in the future, we can replace with a uuid5 based off the experiment name
        # name = azureml_run.experiment.name
        name = "online_scrubbed_for_compliance"
        subscription_id = azureml_run.experiment.workspace.subscription_id
        region = azureml_run.experiment.workspace.location
        parent_run_id = azureml_run.parent.id if azureml_run.parent is not None else None
        child_run_id = azureml_run.id

    # Build the automl settings expected by the logger
    send_telemetry, level = get_diagnostics_collection_info(component_name=TELEMETRY_AUTOML_COMPONENT_KEY)
    automl_settings = AzureAutoMLSettingsStub
    automl_settings.is_timeseries = False
    automl_settings.task_type = task_type
    automl_settings.compute_target = ComputeTargets.AMLCOMPUTE
    automl_settings.name = name
    automl_settings.subscription_id = subscription_id
    automl_settings.region = region
    automl_settings.telemetry_verbosity = level
    automl_settings.send_telemetry = send_telemetry

    log_server.set_log_file(os.path.join(output_dir, SystemSettings.LOG_FILENAME))
    if send_telemetry:
        log_server.enable_telemetry(INSTRUMENTATION_KEY)
    log_server.set_verbosity(level)

    set_run_custom_dimensions(
        automl_settings=automl_settings,
        parent_run_id=parent_run_id,
        child_run_id=child_run_id)

    # Add console handler
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    log_server.add_handler('stdout', stdout_handler)


def _get_language_code(featurization: Union[str, Dict]):
    """Return user language code if provided, else return 'eng'

    :param featurization: FeaturizationConfig of run
    :return 3 letter language code
    """
    if isinstance(featurization, dict) and featurization.get("_dataset_language", "eng") is not None:
        return featurization.get("_dataset_language", "eng")
    else:
        return "eng"


def get_run_by_id(run_id: str, experiment_name: Optional[str] = None):
    """Get a Run object.

    :param run_id: run id of the run that produced the model
    :param experiment_name: name of experiment that contained the run id
    :return: Run object
    :rtype: Run
    """
    experiment = Run.get_context().experiment
    if experiment_name is not None:
        workspace = experiment.workspace
        experiment = Experiment(workspace, experiment_name)
    return Run(experiment=experiment, run_id=run_id)


def save_script(script, score_script_dir=None):
    """Save a script file to outputs directory.

    :param script: The script to be saved
    :param score_script_dir: Path to save location
    :type score_script_dir: string
    """
    if score_script_dir is None:
        score_script_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(score_script_dir, script)) as source_file:
        save_location = os.path.join(OutputLiterals.OUTPUT_DIR, script)
        with open(save_location, "w") as output_file:
            output_file.write(source_file.read())
    return save_location


def save_conda_yml(environment):
    """Save score_script file to outputs directory.

    :param score_script_dir: Path to save location
    :type score_script_dir: string
    """
    conda_deps = environment.python.conda_dependencies
    training_only_packages = ["horovod"]
    for package in training_only_packages:
        conda_deps.remove_pip_package(package)

    conda_deps._conda_dependencies['name'] = 'project_environment'
    conda_file_path = os.path.join(OutputLiterals.OUTPUT_DIR, OutputLiterals.CONDA_ENV_NAME)
    with open(conda_file_path, "w") as output_file:
        output_file.write(conda_deps.serialize_to_string())

    return conda_file_path


def is_main_process():
    """
    Function for determining whether the current process is master.
    :return: Boolean for whether this process is master.
    """
    return os.environ.get('AZUREML_PROCESS_NAME', 'main') in {'main', 'rank_0'}


def is_data_labeling_run(current_run: Run):
    """
    Check whether the run is for labeling service.

    If the run is submitted through data labeling service, the runsource will be marked as "Labeling"
    :param current_run: current run context
    :return: whether run is from data labeling
    """
    # current run id: AutoML_<guid>_HD_0
    # parent HD run id: run.parent AutoML_<guid>_HD
    # original parent AutoML run: run.parent.parent AutoML_<guid>
    run_source = current_run.parent.parent.properties.get(Run._RUNSOURCE_PROPERTY, None)
    is_labeling_run = True if run_source == SystemSettings.LABELING_RUNSOURCE else False
    return is_labeling_run


def is_data_labeling_run_with_file_dataset(current_run: Run):
    """
    Check whether the run is for labeling service.

    If the run is from labeling service and input is from file dataset, it needs extra input data conversion.
    :param current_run: current run context
    :return: whether run is from data labeling
    """
    # current run id: AutoML_<guid>_HD_0
    # parent HD run id: run.parent AutoML_<guid>_HD
    # original parent AutoML run: run.parent.parent AutoML_<guid>
    data_type = json.loads(
        current_run.parent.parent.properties.get("AMLSettingsJsonString")
    ).get(SystemSettings.LABELING_DATASET_TYPE, None)

    is_file_dataset = data_type == SystemSettings.LABELING_DATASET_TYPE_FILEDATSET

    return is_data_labeling_run(current_run) and is_file_dataset
