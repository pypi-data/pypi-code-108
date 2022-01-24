# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import collections
import json
import logging
import os

import azureml._vendor.ruamel.yaml as ruamelyaml
from azureml._base_sdk_common.abstract_run_config_element import _AbstractRunConfigElement
from azureml._base_sdk_common.field_info import _FieldInfo
from azureml._base_sdk_common.common import get_run_config_dir_name
from azureml.core._serialization_utils import _serialize_to_dict, _check_before_comment, \
    _yaml_set_comment_before_after_key_with_error, _deserialize_and_add_to_object
from azureml.core.compute_target import AbstractComputeTarget
from azureml.core.compute import ComputeTarget
from azureml.train._estimator_helper import _create_conda_dependencies

from azureml.core.environment import _DEFAULT_SHM_SIZE
from azureml.exceptions import UserErrorException
from azureml.core.runconfig import EnvironmentDefinition, HistoryConfiguration, Data, DataReferenceConfiguration, \
    RunConfiguration, OutputData
from azureml.core._experiment_method import experiment_method

from azureml.contrib.train.rl._rl_environment_helper import _setup_environment
module_logger = logging.getLogger(__name__)


def submit(rl_config, workspace, experiment_name, run_id=None):
    """Launch a Reinforcement Learning run with the given configuration.

    :param rl_config: A `ReinforcementLearningConfiguration` that defines the configuration for this run.
    :type rl_config: azureml.contrib.train.rl.ReinforcementLearningConfiguration
    :param workspace: The workspace in which to run the experiment.
    :type workspace: azureml.core.workspace.Workspace
    :param experiment_name: The name of the experiment.
    :type experiment_name: str
    :param run_id: The run ID to use for the created run.
    :type run_id: str
    :return: A `ReinforcementLearningRun` object.
    :rtype: azureml.contrib.train.rl.ReinforcementLearningRun
    """
    from azureml.core import Experiment
    from azureml._project.project import Project
    from azureml.contrib._rlservice import _commands
    from azureml._base_sdk_common.tracking import global_tracking_info_registry

    experiment = Experiment(workspace, experiment_name)
    project = Project(directory=rl_config._source_directory, experiment=experiment)

    run_config_copy = ReinforcementLearningConfiguration._get_run_config_object(rl_config)

    run = _commands.start_run(project, run_config_copy,
                              telemetry_values=rl_config._telemetry_values,
                              run_id=run_id)

    run.add_properties(global_tracking_info_registry.gather_all(rl_config._source_directory))

    return run


class WorkerConfiguration(_AbstractRunConfigElement):
    """ WorkerConfiguration is the class that holds all the necessary information for the workers to run.

    :param node_count: Number of worker nodes to be initialized, one worker will run per machine in the
        compute target.
    :type node_count: int
    :param compute_target: The compute target where the workers will run. This can either be an object or the
        the compute target's name.
    :type compute_target: azureml.core.compute_target.AbstractComputeTarget or str
    :param environment: The environment definition for the workers. It includes
        PythonSection, DockerSection, and environment variables. Any environment option not directly
        exposed through other parameters to the WorkerConfiguration construction can be set using this
        parameter. If this parameter is specified, it will be used as a base upon which packages specified in
        ``pip_packages`` and ``conda_packages`` will be added.
    :type environment: azureml.core.Environment
    :param shm_size: The docker shm_size configuration for the worker.
    :type shm_size: str
    :param history: History configuration for the worker's run, this controls which logs folders will be monitored
    :type history: azureml.core.runconfig.HistoryConfiguration
    :param use_gpu: Parameter used to signal whether the default base image should have the packages for
        gpu added. This parameter is ignored if ``environment`` is set.
    :type use_gpu: bool
    :param conda_packages: A list of strings representing conda packages to be added to the Python environment
        for the workers.
    :type conda_packages: list
    :param pip_packages: A list of strings representing pip packages to be added to the Python environment
        for the workers
    :type pip_packages: list
    :param pip_requirements_file: The relative path to the workers' pip requirements text file.
            This can be provided in combination with the ``pip_packages`` parameter.
    :type pip_requirements_file: str
    :param conda_dependencies_file: The relative path to the workers' conda dependencies
        yaml file.
    :type conda_dependencies_file: str
    """

    _field_to_info_dict = collections.OrderedDict([
        ("_target", _FieldInfo(str, "The name of the compute target to use.", serialized_name="target")),
        ("node_count", _FieldInfo(int, "Number of compute nodes to run the job on.", serialized_name="nodecount")),
        ("environment", _FieldInfo(EnvironmentDefinition, "The environment definition.")),
        ("shm_size", _FieldInfo(str, "Docker shm_size configuration.")),
        ("history", _FieldInfo(HistoryConfiguration, "History details."))
    ])

    def __init__(self, node_count, compute_target=None, environment=None, shm_size=_DEFAULT_SHM_SIZE,
                 history=None, use_gpu=False, pip_packages=None, conda_packages=None,
                 conda_dependencies_file=None, pip_requirements_file=None):

        """Initialize the WorkerConfiguration

        :param node_count: Number of worker nodes to be initialized, one worker will run per machine in the
            compute target.
        :type node_count: int
        :param compute_target: The compute target where the workers will run. This can either be an object or the
            the compute target's name.
        :type compute_target: azureml.core.compute_target.ComputeTarget or str
        :param environment: The environment definition for the workers. It includes
            PythonSection, DockerSection, and environment variables. Any environment option not directly
            exposed through other parameters to the WorkerConfiguration construction can be set using this
            parameter. If this parameter is specified, it will be used as a base upon which packages specified in
            ``pip_packages`` and ``conda_packages`` will be added.
        :type environment: azureml.core.Environment
        :param shm_size: The docker shm_size configuration for the worker.
        :type shm_size: str
        :param history: History configuration for the worker's run, this controls which logs folders will be monitored
        :type azureml.core.runconfig.HistoryConfiguration
        :param use_gpu: Prameter used to signal whether the default base image should have the packages for
            gpu added. This parameter is ignored if ``environment`` is set.
        :type is_gpu_enable: bool
        :param conda_packages: A list of strings representing conda packages to be added to the Python environment
            for the workers.
        :type conda_packages: list
        :param pip_packages: A list of strings representing pip packages to be added to the Python environment
            for the workers
        :type pip_packages: list
        :param pip_requirements_file: The relative path to the workers' pip requirements text file.
            This can be provided in combination with the ``pip_packages`` parameter.
        :type pip_requirements_file: str
        :param conda_dependencies_file: The relative path to the workers' conda dependencies
        yaml file.
        :type conda_dependencies_file: str
        """

        super(WorkerConfiguration, self).__init__()
        self.target = compute_target
        self.environment = environment
        self.history = history if history else HistoryConfiguration()
        # TODO add validators
        self.node_count = node_count
        self._use_gpu = use_gpu
        self._pip_packages = pip_packages
        self._conda_packages = conda_packages
        self._pip_requirements_file = pip_requirements_file
        self._conda_dependencies_file = conda_dependencies_file
        self.shm_size = shm_size
        self._initialized = True

    def __repr__(self):
        """Return the string representation of the WorkerConfiguration object.

        :return: String representation of the WorkerConfiguration object
        :rtype: str
        """
        run_config_dict = _serialize_to_dict(self)
        return json.dumps(run_config_dict, indent=4)

    @property
    def target(self):
        """Get the compute target where the worker run is scheduled for execution.

        Available cloud compute targets can be found using the function
        :attr:`azureml.core.Workspace.compute_targets`

        :return: The target name
        :rtype: str
        """
        return self._target

    @target.setter
    def target(self, target):
        """Set the compute target where the worker run is scheduled for execution.

        :param target:
        :type target: str
        """
        if isinstance(target, (AbstractComputeTarget, ComputeTarget)):
            self._target = target.name
        elif isinstance(target, str):
            self._target = target
        else:
            self._target = None

    def _is_environment_initialized(self):
        if self.environment:
            return True
        return False

    def _are_extra_dependencies_specified(self):
        return self._pip_packages or self._pip_requirements_file \
            or self._conda_dependencies_file or self._conda_packages

    def _initialize_env_for_framework(self, framework, source_directory):
        conda_dependencies = None
        if self._are_extra_dependencies_specified():
            conda_dependencies = _create_conda_dependencies(source_directory=source_directory,
                                                            pip_packages=self._pip_packages,
                                                            pip_requirements_file=self._pip_requirements_file,
                                                            conda_packages=self._conda_packages,
                                                            conda_dependencies_file=self._conda_dependencies_file)
        self.environment = _setup_environment(framework=framework, use_gpu=self._use_gpu,
                                              conda_dependencies=conda_dependencies)

    def _initialize_custom_env(self, head_environment, source_directory):
        conda_dependencies = None
        if self._are_extra_dependencies_specified():
            conda_dependencies = _create_conda_dependencies(source_directory=source_directory,
                                                            pip_packages=self._pip_packages,
                                                            pip_requirements_file=self._pip_requirements_file,
                                                            conda_packages=self._conda_packages,
                                                            conda_dependencies_file=self._conda_dependencies_file)
        self.environment = _setup_environment(base_env=head_environment, framework=None,
                                              use_gpu=self._use_gpu,
                                              conda_dependencies=conda_dependencies)


class HeadConfiguration(_AbstractRunConfigElement):
    """HeadConfiguration is the class that holds all the necessary information for the head to run.

    :param script: The relative path to the file containing the training script.
    :type script: str

    :param arguments: Command line arguments for the python script file.
    :type arguments: builtin.list[str]

    :param compute_target: The compute target where the head run will execute. This can either be an object or the
        the compute target's name.
    :type compute_target: azureml.core.compute_target.ComputeTarget or str

    :param environment: The environment definition for the head. It includes
        PythonSection, DockerSection, and environment variables.
    :type environment: azureml.core.Environment

    :param shm_size: The docker shm_size configuration for the head.
    :type shm_size: str

    :param history: History configuration for the head run, this controls which logs folders will be monitored
    :type azureml.core.runconfig.HistoryConfiguration

    :param data_references: All the data sources are available to the run during execution based
        on each configuration. For each item of the dictionary, the key is a name given to the
        data source and the value is a DataReferenceConfiguration.
    :type data_references: azureml.core.runconfig.DataReferenceConfiguration

    :param data: All the data to make available to the run during execution.
    :type data: azureml.core.runconfig.Data
    """

    _field_to_info_dict = collections.OrderedDict([
        ("script", _FieldInfo(str, "The relative path to the python script file. \
            The file path is relative to the source_directory.")),
        ("arguments", _FieldInfo(list, "The arguments to the script file.", list_element_type=str)),
        ("_target", _FieldInfo(str, "The name of the compute target to use.", serialized_name="target")),
        ("_snapshot_id", _FieldInfo(str, "The snapshot that contains the code that will be used for head run",
                                    serialized_name="snapshotid")),
        ("data_references", _FieldInfo(dict, "data reference configuration details",
                                       list_element_type=DataReferenceConfiguration)),
        ("data", _FieldInfo(dict, "The configuration details for data.", list_element_type=Data)),
        ("environment", _FieldInfo(EnvironmentDefinition, "The environment definition.")),
        ("shm_size", _FieldInfo(str, "Docker shm_size configuration")),
        ("history", _FieldInfo(HistoryConfiguration, "History details.")),
        ("_output_data", _FieldInfo(dict, "The configuration that describes how to save and track outputs for the run",
                                    list_element_type=OutputData, serialized_name="output_data"))
    ])

    def __init__(self, script=None, arguments=None, compute_target=None,
                 environment=None, shm_size=_DEFAULT_SHM_SIZE, history=None,
                 data_references=None, data=None, output_data={}):

        """Initialize the HeadConfiguration.

        :param script: The relative path to the file containing the training script.
        :type script: str

        :param arguments: Command line arguments for the python script file.
        :type arguments: builtin.list[str]

        :param compute_target: The compute target where the head run will execute. This can either be an object or the
            the compute target's name.
        :type compute_target: azureml.core.compute_target.ComputeTarget or str

        :param environment: The environment definition for the head. It includes
            PythonSection, DockerSection, and environment variables.
        :type environment: azureml.core.Environment

        :param shm_size: The docker shm_size configuration for the head.
        :type shm_size: str

        :param history: History configuration for the head run, this controls which logs folders will be monitored
        :type azureml.core.runconfig.HistoryConfiguration

        :param data_references: All the data sources are available to the run during execution based
            on each configuration. For each item of the dictionary, the key is a name given to the
            data source and the value is a DataReferenceConfiguration.
        :type data_references: azureml.core.runconfig.DataReferenceConfiguration

        :param data: All the data to make available to the run during execution.
        :type data: azureml.core.runconfig.Data

        :param output_data: All the data to be copied to storage during execution.
        :type output_data: azureml.core.runconfig.OutputData
        """

        super(HeadConfiguration, self).__init__()
        # TODO do we want to keep this default.
        self.script = script if script else "train.py"
        self.arguments = arguments if arguments else []
        self.target = compute_target
        self._snapshot_id = ""
        self.environment = environment if environment else EnvironmentDefinition()
        self.history = history if history else HistoryConfiguration()
        self.data_references = data_references
        self.data = data
        self.output_data = output_data
        self.shm_size = shm_size
        self._initialized = True

    def __repr__(self):
        """Return the string representation of the HeadConfiguration object.

        :return: String representation of the HeadConfiguration object
        :rtype: str
        """
        run_config_dict = _serialize_to_dict(self)
        return json.dumps(run_config_dict, indent=4)

    @property
    def target(self):
        """Get target.

        Target refers to compute where the job is scheduled for execution.
        Available cloud compute targets can be found using the function
        :attr:`azureml.core.Workspace.compute_targets`

        :return: The target name
        :rtype: str
        """
        return self._target

    @target.setter
    def target(self, target):
        """Set target.

        :param target:
        :type target: str
        """
        if isinstance(target, (AbstractComputeTarget, ComputeTarget)):
            self._target = target.name
        elif isinstance(target, str):
            self._target = target
        else:
            self._target = None

    @property
    def snapshot_id(self):
        """Get the snapshot ID used by head.

        :return: The snapshot id.
        :rtype: str
        """
        return self._snapshot_id

    @snapshot_id.setter
    def snapshot_id(self, snapshot_id):
        """Set the snapshot ID used by head.

        :param snapshot_id: The snapshot id.
        :type snapshot_id: str
        """
        self._snapshot_id = snapshot_id


class ReinforcementLearningConfiguration(_AbstractRunConfigElement):
    """Represents configuration for reinforcement learning runs targeting Azure Machine Learning compute targets.

    ReinforcementLearningConfiguration object encapsulates the information necessary to submit a reinforcement learning
    run in an experiment. It includes information about head, workers and compute targets to execute
    experiment runs on.

    :param head_configuration: The configuration for head.
    :type worker_configuration: azureml.contrib.train.rl.HeadConfiguration
    :param worker_configuration: The configuration for the workers.
    :type worker_configuration: azureml.contrib.train.rl.WorkerConfiguration
    :param max_run_duration_seconds: The maximum allowed time for the run in seconds. Azure ML
        will attempt to automatically cancel the job if it takes longer than this value.
    :type max_run_duration_seconds: int
    :param cluster_coordination_timeout_seconds: The maximum time in seconds that the job can take to start once
        it has passed the queued state.
    :type cluster_coordination_timeout_seconds: int
    :param source_directory: The directory containing code or configuration for the head run.
    :type source_directory: str
    :param framework: Orchestration framework to be used in the experiment. The default is Ray version 0.8.0
    :type framework: azureml.contrib.train.rl.RLFramework
    """

    _field_to_info_dict = collections.OrderedDict([
        ("framework", _FieldInfo(str, "RL framework to use")),
        ("framework_arguments", _FieldInfo(list, "Additional arguments for the RL Framework", list_element_type=str)),
        ("head", _FieldInfo(HeadConfiguration, "Configuration for the head's run")),
        ("workers", _FieldInfo(WorkerConfiguration, "Configuration for the workers' run")),
        ("max_run_duration_seconds", _FieldInfo(int, "Maximum allowed duration for the run",
                                                serialized_name="maxRunDurationSeconds")),
        ("cluster_coordination_timeout_seconds", _FieldInfo(int,
                                                            ('The maximum allowed time for nodes in a cluster'
                                                             'to be in running state before all clusters are'
                                                             'in running state.'),
                                                            serialized_name="clusterCoordinationTimeoutSeconds"))
    ])

    @experiment_method(submit_function=submit)
    def __init__(self, head_configuration, worker_configuration,
                 max_run_duration_seconds=None, cluster_coordination_timeout_seconds=None,
                 source_directory=None, _path=None, _name=None, framework=None):
        super(ReinforcementLearningConfiguration, self).__init__()

        """Initialize the ReinforcementLearningConfiguration

        :param head_configuration: The configuration for head.
        :type worker_configuration: azureml.contrib.train.rl.HeadConfiguration
        :param worker_configuration: The configuration for the workers.
        :type worker_configuration: azureml.contrib.train.rl.WorkerConfiguration
        :param max_run_duration_seconds: The maximum allowed time for the run in seconds. Azure ML
            will attempt to automatically cancel the job if it takes longer than this value.
        :type max_run_duration_seconds: int
        :param cluster_coordination_timeout_seconds: The maximum time in seconds that the job can take to start once
            it has passed the queued state.
        :type cluster_coordination_timeout_seconds: int
        :param source_directory: The directory containing code or configuration for the head run.
        :type source_directory: str
        :param framework: Orchestration framework to be used in the experiment. The default is Ray version 0.8.0
        :type framework: azureml.contrib.train.rl.RLFramework
        """

        DEFAULT_RUN_DURATION = None   # TODO define defaults
        DEFAULT_COORDINATION_PERIOD = None
        self.framework = framework.name if framework else None
        self.framework_arguments = framework.framework_arguments if framework and framework.framework_arguments\
            else []
        self._name = _name
        self._path = _path
        self._source_directory = source_directory
        self._telemetry_values = None
        self.head = head_configuration if head_configuration else HeadConfiguration()
        self.workers = worker_configuration

        self.max_run_duration_seconds = max_run_duration_seconds if max_run_duration_seconds else DEFAULT_RUN_DURATION
        self.cluster_coordination_timeout_seconds = cluster_coordination_timeout_seconds \
            if cluster_coordination_timeout_seconds else DEFAULT_COORDINATION_PERIOD
        self._initialized = True

    def __repr__(self):
        """Return the string representation of the ReinforcementLearningConfiguration object.

        :return: String representation of the ReinforcementLearningConfiguration object
        :rtype: str
        """
        run_config_dict = _serialize_to_dict(self)
        return json.dumps(run_config_dict, indent=4)

    @classmethod
    def _load_from_file_init(cls, _path, _name, has_head, has_workers):
        head_config = HeadConfiguration() if has_head else None
        worker_config = WorkerConfiguration(node_count=None) if has_workers else None
        return cls(head_configuration=head_config, worker_configuration=worker_config,
                   _path=_path, _name=_name, framework=None)

    @staticmethod
    def _get_run_config_object(rl_config, path=None):
        """Return the reinforcement learning configuration object.

        :param path: The path in which the saved rl config file to be loaded is located.
        :type path: str
        :param rl_config: The reinforcement learning configuration or the name with which it was saved.
        :type rl_config: azureml.contrib.train.rl.ReinforcementLearningConfiguration or str
        :return: Returns the `ReinforcementLearningConfiguration` object.
        :rtype: azureml.contrib.train.rl.ReinforcementLearningConfiguration
        """
        if isinstance(rl_config, str):
            return ReinforcementLearningConfiguration.load(path, rl_config)
        elif isinstance(rl_config, ReinforcementLearningConfiguration):
            # TODO: Deep copy of project and auth object too.
            import copy
            return copy.deepcopy(rl_config)
        else:
            raise UserErrorException("Unsupported rl_config type {}."
                                     "rl_config can be of str or "
                                     "azureml.contrib.train.rl.ReinforcementLearningConfiguration"
                                     "type.".format(type(rl_config)))

    def save(self, path=None, name=None, separate_environment_yaml=False):
        """Save the ReinforcementLearningConfiguration to a file on disk.

        A :class:`azureml.exceptions.UserErrorException` is raised when:

        * The ReinforcementLearningConfiguration can't be saved with the name specified.
        * No ``name`` parameter was specified.
        * No ``path`` parameter is invalid.

        If ``path`` is of the format <dir_path>/<file_name> where <dir_path> is a valid directory, then the
        ReinforcementLearningConfiguration is saved at <dir_path>/<file_name>.

        If ``path`` points to a directory, which should be a project directory, then the
        ReinforcementLearningConfiguration is saved at
        &lt;path&gt;/.azureml/&lt;name&gt; or &lt;path&gt;/aml_config/&lt;name&gt;.

        This method is useful when editing the configuration manually or when sharing the configuration with the CLI.

        :param separate_environment_yaml: Indicates whether to save the Conda environment configuration.
            If True, the Conda environment configuration is saved to a YAML file named '<type>_environment.yml'.
        :type separate_environment_yaml: bool
        :param path: A user selected root directory for run configurations. Typically this is the Git Repository
            or the Python project root directory. The configuration is saved to a sub directory named .azureml.
        :type path: str
        :param name: [Required] The configuration file name.
        :type name: str
        :return:
        :rtype: None
        """

        if not path:
            if self._path:
                path = self._path
            else:
                path = os.getcwd()

        is_path_a_dir = True

        if os.path.exists(path) and os.path.isdir(path):
            if name is None and self._name is None and not name and not self._name:
                raise UserErrorException("Cannot save a reinforcement learning configuration without"
                                         "a name specified")
            name = name if name else self._name
        else:
            parent_dir = os.path.dirname(path)
            if os.path.exists(parent_dir) and os.path.isdir(parent_dir):
                is_path_a_dir = False
            else:
                raise UserErrorException("{} argument is invalid".format(path))

        commented_map_dict = _serialize_to_dict(self, use_commented_map=True)

        if self.head is not None:
            self._save_conda_dependencies_for_component("head", commented_map_dict, path, is_path_a_dir)
        if self.workers is not None:
            self._save_conda_dependencies_for_component("workers", commented_map_dict, path, is_path_a_dir)

        if separate_environment_yaml:
            if self.head is not None:
                self._save_separate_env_file_for_component("head", commented_map_dict, path, name, is_path_a_dir)
            if self.workers is not None:
                self._save_separate_env_file_for_component("workers", commented_map_dict, path, name, is_path_a_dir)
        if is_path_a_dir:
            run_config_dir_name = get_run_config_dir_name(path) + "/"
            full_runconfig_path = os.path.join(path, run_config_dir_name + name)
        else:
            run_config_dir_name = ""
            full_runconfig_path = path

        with open(full_runconfig_path, 'w') as outfile:
            ruamelyaml.round_trip_dump(commented_map_dict, outfile)

    def _save_conda_dependencies_for_component(self, component, map_node, path, is_path_a_dir):
        """Saves the conda_dependencies in
            a separate yaml file. The dependencies file name will be ``component``_conda_dependencies.yml

        :param component: The component to be saved.
        :type component: str
        :param path: The path of the rl configuration.
        :type path: str
        :param name: The name of the rl configuration.
        :type name: str
        :param is_path_a_dir: If True, the dependencies file will be saved in path/.azureml folder.
        If False, dependencies file will be saved in the parent dir of the file specified by path.
        :type is_path_a_dir: bool
        :return:
        :rtype: None
        """
        components = {
            "head": self.head,
            "workers": self.workers,
        }
        run_config_dir_name = get_run_config_dir_name(path)
        del map_node[component]["environment"]["python"]["condaDependencies"]
        conda_file_path = map_node[component]["environment"]["python"]["condaDependenciesFile"]

        if conda_file_path is None:
            if is_path_a_dir:
                # Doesn't use os.path.join to make these files cross-platform compatible.
                conda_file_path = run_config_dir_name + "/{}_conda_dependencies.yml".format(component)
            else:
                conda_file_path = "{}_conda_dependencies.yml".format(component)

            map_node[component]["environment"]["python"]["condaDependenciesFile"] = conda_file_path

        if is_path_a_dir:
            components[component].environment.python.conda_dependencies.save_to_file(path,
                                                                                     conda_file_path=conda_file_path)
        else:
            components[component].environment.python.conda_dependencies.save_to_file(os.path.dirname(path),
                                                                                     conda_file_path=conda_file_path)

    def _save_separate_env_file_for_component(self, component, commented_map_dict, path, name,
                                              is_path_a_dir=True):

        """Saves the environment configuration in
            a separate yaml file. The environment file name will be ``component``_environment.yml

        :param component: The component to be saved.
        :type component: str
        :param path: The path of the rl configuration.
        :type path: str
        :param name: The name of the rl configuration.
        :type name: str
        :param is_path_a_dir: If True, the environment will be saved in path/.azureml folder.
        If False, environment will be saved in the parent dir of the file specified by path.
        :type is_path_a_dir: bool
        :return:
        :rtype: None
        """
        component_node = commented_map_dict[component]
        if is_path_a_dir:
            run_config_dir_name = get_run_config_dir_name(path) + "/"
            full_env_path = os.path.join(path, run_config_dir_name + "{}_environment.yml".format(component))
        else:
            run_config_dir_name = ""
            full_env_path = os.path.join(os.path.dirname(path), "{}_environment.yml".format(component))

        environment_commented_map = component_node.get("environment")
        component_node["environment"] = run_config_dir_name + "{}_environment.yml".format(component)

        if not _check_before_comment(component_node, "environment"):
            _yaml_set_comment_before_after_key_with_error(
                component_node, "environment", "The file path that contains the environment configuration.")

        with open(full_env_path, 'w') as outfile:
            ruamelyaml.round_trip_dump(environment_commented_map, outfile)

    @staticmethod
    def load(path=None, name=None):
        """Load a previously saved reinforcement learning run configuration file from an on-disk file.

        If ``path`` points to a file, the ReinforcementLearningConfiguration is loaded from that file.

        If ``path`` points to a directory, which should be a project directory, then the
        ReinforcementLearningConfiguration is loaded from
        &lt;path&gt;/.azureml/&lt;name&gt; or &lt;path&gt;/aml_config/&lt;name&gt;.

        :param path: A user selected root directory for run configurations. Typically this is the Git Repository
            or the Python project root directory. For backward compatibility, the configuration will also be
            loaded from .azureml or aml_config sub directory. If the file is not in those directories, the file is
            loaded from the specified path. Path defaults to current working directory if not provided.
        :type path: str
        :param name: The configuration file name.
        :type name: str
        :return: The reinforcement learning run configuration object.
        :rtype: azureml.contrib.train.rl.ReinforcementLearningConfiguration
        """

        if not path:
            path = os.getcwd()

        is_path_a_dir = True
        if os.path.isfile(path):
            full_runconfig_path = path
            is_path_a_dir = False
        else:
            # Project directory case.
            run_config_dir_name = get_run_config_dir_name(path) + "/"
            full_runconfig_path = os.path.join(path, run_config_dir_name + name)

        if os.path.isfile(full_runconfig_path):
            return ReinforcementLearningConfiguration._load_from_path(full_runconfig_path=full_runconfig_path,
                                                                      path=path,
                                                                      name=name,
                                                                      is_path_a_dir=is_path_a_dir)
        else:
            raise UserErrorException("Failed to load RunConfiguration from path={} name={}".format(path, name))

    @staticmethod
    def _load_from_path(full_runconfig_path, path, name, is_path_a_dir):
        """Load runconfig from serialized_dict and returns a ReinforcementLearningConfiguration object.

        :param full_runconfig_path: full file path to load ReinforcementLearningConfiguration from
        :type full_runconfig_path: str
        :param path: directory of runconfig file
        :type path: str
        :param name: The run config name.
        :type name: str
        :param project_dir_case: If the reinforcement learning runconfig file is in a project directory
        :type project_dir_case: bool
        :return: The reinforcement learning run configuration object.
        :rtype: azureml.contrib.train.rl.ReinforcementLearningConfiguration
        """
        with open(full_runconfig_path, "r") as run_config:
            # Loads with all the comments intact.
            commented_map_dict = ruamelyaml.round_trip_load(run_config)
            return ReinforcementLearningConfiguration._get_runconfig_using_dict(commented_map_dict,
                                                                                path=path, name=name,
                                                                                is_path_a_dir=is_path_a_dir)

    @staticmethod
    def _load_environment_for_component(component, commented_map, dir_to_load):
        component_map_node = commented_map[component]
        if "environment" in component_map_node and type(component_map_node["environment"]) == str:
            environment_path = os.path.join(dir_to_load,
                                            component_map_node["environment"])
            with open(environment_path, "r") as environment_config:
                # Replacing string path with the actual environment serialized dictionary.
                component_map_node["environment"] = ruamelyaml.round_trip_load(environment_config)

    @staticmethod
    def _load_conda_dependencies_from_file(component, dir_to_load):
        from azureml.core.conda_dependencies import CondaDependencies
        if hasattr(component.environment, "python"):
            if component.environment.python.conda_dependencies_file is not None:
                conda_dependencies = CondaDependencies(
                    os.path.join(dir_to_load, component.environment.python.conda_dependencies_file))
                component.environment.python.conda_dependencies = conda_dependencies
                component.environment.python.conda_dependencies_file = None

    @classmethod
    def _get_runconfig_using_dict(cls, commented_map_or_dict, path=None, name=None,
                                  is_path_a_dir=True):
        """Construct the reinforcement learning config object from the serialized commented_map_or_dict.

        :param commented_map_or_dict:
        :type commented_map_or_dict: dict
        :param path:
        :type path: str
        :param name:
        :type name: str
        :param project_dir_case:
        :type project_dir_case: bool
        :return: The reinforcement learning run configuration object.
        :rtype: azureml.contrib.train.rl.ReinforcementLearningConfiguration
        """
        all_camel_case, new_commented_map = RunConfiguration._check_camel_case_keys(commented_map_or_dict, cls)
        if not all_camel_case:
            # Replacing with the new map that has keys in camelCase
            commented_map_or_dict = new_commented_map

        if is_path_a_dir:
            dir_to_load = path
        else:
            dir_to_load = os.path.dirname(path)
        has_head = False
        has_workers = False
        if "head" in commented_map_or_dict and commented_map_or_dict.get("head"):
            cls._load_environment_for_component("head", commented_map_or_dict, dir_to_load)
            has_head = True
        if "workers" in commented_map_or_dict and commented_map_or_dict.get("workers"):
            cls._load_environment_for_component("workers", commented_map_or_dict, dir_to_load)
            has_workers = True
        if "simulators" in commented_map_or_dict and commented_map_or_dict.get("simulators"):
            raise ValueError("Simulator runs are not supported.")

        rl_config_object = cls._load_from_file_init(_path=path, _name=name, has_head=has_head,
                                                    has_workers=has_workers)

        # Only wants to preserve the comments if it is a commented map.
        if type(commented_map_or_dict) == ruamelyaml.comments.CommentedMap:
            rl_config_object._loaded_commented_map = commented_map_or_dict

        _deserialize_and_add_to_object(
            cls, commented_map_or_dict, object_to_populate=rl_config_object)

        # Loading the conda file as conda object and setting that in the runconfig.
        # this method gets invoked when trying to load the run config from a file on disk
        # the conda dependencies file should already be populated to the correct value
        # Default to use the new .azureml path
        if rl_config_object.head is not None:
            cls._load_conda_dependencies_from_file(rl_config_object.head, dir_to_load)
        if rl_config_object.workers is not None:
            cls._load_conda_dependencies_from_file(rl_config_object.workers, dir_to_load)
        return rl_config_object
