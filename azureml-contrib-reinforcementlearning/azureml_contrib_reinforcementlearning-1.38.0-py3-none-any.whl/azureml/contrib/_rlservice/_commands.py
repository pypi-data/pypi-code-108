# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from __future__ import print_function

import os
import time
import uuid
import sys
import platform
import re

from azureml._base_sdk_common.common import give_warning
from azureml._file_utils.file_utils import get_directory_size
from azureml.core._serialization_utils import _serialize_to_dict
from azureml._project.ignore_file import get_project_ignore_file
from azureml._restclient.run_client import RunClient
from azureml.exceptions import WebserviceException
from azureml._execution._commands import _max_zip_size_bytes, _num_max_mbs
import azureml.contrib.train.rl._client as ReinforcementLearningClient


def start_run(project_object, run_config_object,
              run_id=None, telemetry_values=None):
    """
    This method calls the Reinforcement Learning service to start a run with the given run id, or
    generates one if needed.
    Returns a ReinforcementLearning run object.
    :param project_object: Project object.
    :type project_object: azureml.core.project.Project
    :param run_config_object: The run configuration object.
    :type run_config_object: azureml.contrib.train.rl._rl_runconfig.ReinforcementLearningConfiguration
    :param run_id: A users specified run id.
    :type run_id: str
    :return: A Reinforcement Learning run object.
    :rtype: azureml.contrib.train.rl._rl_run.ReinforcementLearningRun
    """

    _validate_run(project_object, run_config_object)
    # Collect common telemetry information for client side.
    telemetry_values = _get_telemetry_values(telemetry_values)

    """Submits an experiment."""
    if not run_id:
        run_id = _get_project_run_id(project_object)

    shared_start_run_kwargs = {"run_id": run_id}
    if telemetry_values is not None:
        shared_start_run_kwargs["telemetry_values"] = telemetry_values

    return _start_run_internal(project_object, run_config_object,
                               **shared_start_run_kwargs)


def _validate_run(project_object, run_config_object):
    # TODO add pertinent valdiations.
    return True


def _serialize_run_config_to_dict(run_config_object):
    result = _serialize_to_dict(run_config_object)
    return result


def _start_run_internal(project_object, run_config_object,
                        run_id=None, telemetry_values=None):
    """
    :param project_object: Project object
    :type project_object: azureml.core.project.Project
    :param run_config_object: The Reinforcement Learining configuration object.
    :type run_config_object: azureml.core._rl_runconfig.ReinforcementLearningConfiguration
    :param run_id:
    :param telemetry_values:
    :rtype: azureml.contrib.train.rl._rl_run.ReinforcementLearningRun
    """
    service_context = project_object.workspace.service_context
    auth_object = project_object.workspace._auth_object

    service_address = service_context._get_rl_service_url()

    ignore_file = get_project_ignore_file(project_object.project_directory)

    directory_size = get_directory_size(
        project_object.project_directory,
        _max_zip_size_bytes,
        exclude_function=ignore_file.is_file_excluded)

    if directory_size >= _max_zip_size_bytes:
        give_warning("Submitting {} directory for run. "
                     "The size of the directory >= {} MB, "
                     "so it can take a few minutes.".format(project_object.project_directory,
                                                            _num_max_mbs))
    rl_service_client = ReinforcementLearningClient \
        .ReinforcementLearningServiceAPI(auth_object, service_address).reinforcement_learning

    try:
        rl_service_client.start_run(subscription_id=service_context.subscription_id,
                                    resource_group_name=service_context.resource_group_name,
                                    workspace_name=service_context.workspace_name,
                                    experiment_name=project_object.history.name,
                                    config=_serialize_run_config_to_dict(run_config_object),
                                    run_id=run_id)
    except Exception as ex:
        raise WebserviceException("Failed to submit run with id: {0}".format(run_id),
                                  inner_exception=ex)

    return _get_run_details(project_object, run_config_object, run_id)


def _get_run_details(project_object, run_config_object, run_id, snapshot_id=None):
    """
    Returns a run object
    :param project_object:
    :type project_object: azureml.core.project.Project
    :param run_config_object:
    :type run_config_object: azureml.contrib.train.rl.ReinforcementLearningConfiguration
    :return:
    :rtype: azureml.contrib.train.rl._rl_run.ReinforcementLearningRun
    """
    from azureml.contrib.train.rl._rl_run import ReinforcementLearningRun
    client = RunClient(project_object.workspace.service_context, project_object.history.name, run_id,
                       experiment_id=project_object.history.id)

    run_dto = client.get_run()
    experiment = project_object.history
    return ReinforcementLearningRun(experiment, run_id,
                                    directory=project_object.project_directory,
                                    _run_config=run_config_object, _run_dto=run_dto)


def _get_project_run_id(project_object):
    project_name = project_object.experiment.name
    run_id = project_name + "_" + str(int(time.time())) + "_" + str(uuid.uuid4())[:8]
    return run_id


def _get_telemetry_values(telemetry_values):
    try:
        if telemetry_values is None:
            telemetry_values = {}

        # Collect common client info
        telemetry_values["amlClientOSVersion"] = platform.platform()
        telemetry_values["amlClientPythonVersion"] = sys.version

        # notebookvm related...
        notebook_instance_file = "/mnt/azmnt/.nbvm"
        is_notebook_vm = False
        if not (os.path.exists(notebook_instance_file) and os.path.isfile(notebook_instance_file)):
            return None

        envre = re.compile(r'''^([^\s=]+)=(?:[\s"']*)(.+?)(?:[\s"']*)$''')
        result = {}
        with open(notebook_instance_file) as nbvm_variables:
            for line in nbvm_variables:
                match = envre.match(line)
                if match is not None:
                    result[match.group(1)] = match.group(2)

        if "instance" in result:
            telemetry_values["notebookInstanceName"] = result["instance"]
        if "domainsuffix" in result:
            telemetry_values["notebookInstanceDomainSuffix"] = result["domainsuffix"]

        telemetry_values["notebookVM"] = is_notebook_vm

        # Do not override client type if it already exists
        telemetry_values.setdefault("amlClientType", "azureml-contrib-reinforcementlearning")
    except Exception:
        pass

    return telemetry_values
