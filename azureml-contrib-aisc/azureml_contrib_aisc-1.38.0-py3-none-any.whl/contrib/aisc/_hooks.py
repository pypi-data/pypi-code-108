# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
""""Contains hooks for k8s compute related functions
The class and module function's name is the specific one with 'Hook' suffix."""

try:
    from abc import ABCMeta

    ABC = ABCMeta('ABC', (), {})
except ImportError:
    from abc import ABC

import logging
from azureml.core.runconfig import RunConfiguration
from azureml._base_sdk_common.field_info import _FieldInfo
from .aiscrunconfig import AISuperComputerConfiguration
from .aisc_run import AISCRun
from azureml._restclient.run_client import RunClient
from azureml._restclient.models.create_run_dto import CreateRunDto
import azureml._execution._commands as commands
from azureml.core.run import Run
from azureml.core.script_run import ScriptRun
from azureml.core.conda_dependencies import CondaDependencies
from azureml.core.runconfig import AmlComputeConfiguration, ParallelTaskConfiguration, MpiConfiguration, \
    TensorflowConfiguration, HdiConfiguration, SparkConfiguration, HistoryConfiguration, EnvironmentDefinition, \
    PyTorchConfiguration, DockerConfiguration


LOCAL_RUNCONFIG_NAME = "local"
module_logger = logging.getLogger(__name__)

RunConfiguration._field_to_info_dict['aisupercomputer'] = _FieldInfo(AISuperComputerConfiguration,
                                                                     "AISuperComputer specific details.")
setattr(RunConfiguration, 'aisupercomputer', AISuperComputerConfiguration())


def __runconfig_init__(self, script=None, arguments=None, framework=None, communicator=None, conda_dependencies=None,
                       _history_enabled=None, _path=None, _name=None, command=None):
    """Initialize a RunConfiguration with the default settings."""
    super(RunConfiguration, self).__init__()

    # patch `environment_variables`
    # https://teams.microsoft.com/l/message/19:3b207825eaec452b8f0235e5d0881039@thread.skype/1632172267552?tenantId=72f988bf-86f1-41af-91ab-2d7cd011db47&groupId=88aa174e-6310-4634-bfcb-5761e1a1190a&parentMessageId=1632172267552&teamName=ML%20Platform&channelName=AML%20Breaking%20Changes&createdTime=1632172267552
    self.environment_variables = {}

    # Used for saving to local file
    self._name = _name
    self._path = _path

    # Default values
    self.script = script
    self.command = command if command else ""
    self.arguments = arguments if arguments else []
    self._target = LOCAL_RUNCONFIG_NAME
    self.framework = framework if framework else "Python"
    self.communicator = communicator if communicator else "None"
    self.max_run_duration_seconds = None
    self.node_count = 1
    self.priority = None

    self.environment = EnvironmentDefinition()
    self.history = HistoryConfiguration()
    self.spark = SparkConfiguration()
    self.docker = DockerConfiguration()

    self.hdi = HdiConfiguration()
    self.tensorflow = TensorflowConfiguration()
    self.mpi = MpiConfiguration()
    self.pytorch = PyTorchConfiguration()
    self.paralleltask = ParallelTaskConfiguration()
    self.data_references = {}
    self.data = {}
    self.output_data = {}
    self.environment_variables = {}
    self.amlcompute = AmlComputeConfiguration()
    self.services = {}
    self.aisupercomputer = AISuperComputerConfiguration()
    self.source_directory_data_store = None
    if _history_enabled:
        self.history.output_collection = _history_enabled

    conda_dependencies = conda_dependencies if conda_dependencies else CondaDependencies()
    self.environment.python.conda_dependencies = conda_dependencies
    self.credential_passthrough = False
    self._initialized = True


RunConfiguration.__init__ = __runconfig_init__


def _get_run_details_hook(project_object, run_config_object, run_id, snapshot_id=None):
    """
    Returns a run object or bool in case prepare_check=True
    :param project_object:
    :type project_object: azureml.core.project.Project
    :param run_config_object:
    :type run_config_object: azureml.core.runconfig.RunConfiguration
    :return:
    :rtype: azureml.core.script_run.ScriptRun
    """
    from azureml.core.script_run import ScriptRun
    client = RunClient(project_object.workspace.service_context, project_object.history.name, run_id,
                       experiment_id=project_object.history.id)

    run_properties = {
        "ContentSnapshotId": snapshot_id,
    }
    create_run_dto = CreateRunDto(run_id, properties=run_properties)
    run_dto = client.patch_run(create_run_dto)
    experiment = project_object.history
    if run_config_object.target == "aisupercomputer":
        from azureml.contrib.aisc.aisc_run import AISCRun
        return AISCRun(experiment, run_id,
                       directory=project_object.project_directory,
                       _run_config=run_config_object, _run_dto=run_dto)

    return ScriptRun(experiment, run_id,
                     directory=project_object.project_directory,
                     _run_config=run_config_object, _run_dto=run_dto)


commands._get_run_details = _get_run_details_hook


def _rehydrate_runs_hook(experiment, run_dtos):
    """Rehydrate runs.

    :param experiment: The containing experiment.
    :param run_dtos:
    :type run_dtos: azureml._restclient.models.run_dto.RunDto
    """
    module_logger.debug("Available factories for run types {0}".format(Run._run_source_initializers))
    for run_dto in run_dtos:
        run_id = run_dto.run_id

        # TODO: Run source is around for backward compatibility. Delete after PuP
        run_properties = getattr(run_dto, "properties", {})
        run_source = run_properties.get(Run._RUNSOURCE_PROPERTY, 'None')
        runtype = run_dto.run_type if run_dto.run_type is not None else run_source
        if runtype == ScriptRun.RUN_TYPE and run_dto.target == "aisupercomputer":
            runtype = AISCRun.RUN_TYPE

        module_logger.debug("Initializing Run {0} from type {1}".format(run_id, runtype))

        factory = Run._run_source_initializers.get(runtype, None)
        if factory is None and (runtype and not runtype.strip()):
            warnmsg = "Run {0} has type {1} but has no client type registered. " \
                      "Entire functionality might not be available."
            module_logger.warning(warnmsg.format(run_id, runtype))
        if factory is None:
            factory = Run._dto_to_run

        yield factory(experiment, run_dto)


Run._rehydrate_runs = _rehydrate_runs_hook
