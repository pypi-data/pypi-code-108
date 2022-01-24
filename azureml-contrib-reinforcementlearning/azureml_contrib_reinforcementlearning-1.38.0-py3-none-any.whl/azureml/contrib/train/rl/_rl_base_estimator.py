# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""The Reinforcement Learning Base Estimator class."""

import os
from abc import ABC
from azureml.contrib.train.rl._rl_runconfig import ReinforcementLearningConfiguration, \
    HeadConfiguration, WorkerConfiguration
from azureml.train._estimator_helper import _get_arguments, _get_data_inputs, _get_data_configuration, _get_outputs
from azureml.train._telemetry_logger import _TelemetryLogger as TelemetryLogger
from azureml._restclient.snapshots_client import SnapshotsClient
from azureml.core.experiment import Experiment
from azureml.exceptions import AzureMLException, TrainingException
from multiprocessing.dummy import Pool
import uuid
from azureml._base_sdk_common import _ClientSessionId
from azureml.core.conda_dependencies import CondaDependencies
from azureml.contrib.train.rl._rl_environment_helper import _setup_environment

from azureml.exceptions import UserErrorException

from azureml.core._experiment_method import experiment_method
from azureml.core.script_run_config import _update_args_and_io


# Get information about the currently running notebook vm. Like its name and prefix.
def _load_nbvm():
    if not os.path.isfile("/mnt/azmnt/.nbvm"):
        raise UserErrorException("This is not a compute instance.")
    with open("/mnt/azmnt/.nbvm", 'r') as file:
        return {key: value for (key, value) in [line.strip().split('=') for line in file]}


# Get infomation about the capabiliteis of an  azureml.core.compute.AmlCompute target
# In particular how much ram + gpu + hdd it has.
def _get_compute_size(compute, workspace):
    for size in compute.supported_vmsizes(workspace):
        if(size['name'].upper() == compute.vm_size.upper()):
            return size


def _rl_estimator_smart_defaults(self, workspace, experiment_name, **kwargs):
    workspace_compute_targets = workspace.compute_targets
    compute_taget = self._compute_target or workspace_compute_targets.get(_load_nbvm().get('instance'))

    if compute_taget is None:
        raise UserErrorException("You must provide a compute target or be running on a compute instance")

    missing_attributes = (self._use_gpu is None) or (self._shm_size is None)

    if isinstance(compute_taget, str):
        compute_taget = workspace_compute_targets[compute_taget]

    if missing_attributes:
        size = _get_compute_size(compute_taget, workspace)
        memory_gb = size.get("memoryGB")
        gpus = size.get("gpus")
        has_gpus = gpus is not None and gpus > 0
        self._shm_size = self._shm_size or str(memory_gb / 2) + "g"
        self._use_gpu = self._use_gpu or has_gpus

    still_missing_attributes = (self._use_gpu is None) or (self._shm_size is None)

    if still_missing_attributes:
        self._use_gpu = self._use_gpu or False
        self._shm_size = self._shm_size or "4g"
    if self._user_provided_environment:
        self._environment = _setup_environment(
            base_env=self._original_user_env, framework=self.framework,
            use_gpu=self._use_gpu,
            conda_dependencies=self._conda_dependencies,
            environment_variables=self._environment_variables)
    else:
        self._environment = _setup_environment(
            framework=self.framework, use_gpu=self._use_gpu,
            conda_dependencies=self._conda_dependencies,
            environment_variables=self._environment_variables)
    self.head_configuration = self._get_head_configuration()


def _rl_estimator_submit_method(estimator, workspace, experiment_name, **kwargs):
    if kwargs:
        unexpected_params = set(kwargs.keys())
        if unexpected_params:
            raise TrainingException("{} parameters cannot be overridden. "
                                    "Currently there are no parameters that can be overridden for this estimator."
                                    .format(list(unexpected_params)))

    _rl_estimator_smart_defaults(estimator, workspace, experiment_name)
    _update_args_and_io(workspace, estimator.head_configuration)
    rl_run = estimator._submit(workspace, experiment_name)

    return rl_run


class _RLBaseEstimator(ABC):
    """Abstract base class for Reinforcement Learning estimators"""

    _worker_configuration = None
    _head_configuration = None
    _source_directory = None
    _estimator_config = None
    _rl_framework = None

    @experiment_method(submit_function=_rl_estimator_submit_method)
    def __init__(self,
                 source_directory,
                 *,
                 environment=None,
                 entry_script=None,
                 script_params=None,
                 compute_target=None,
                 use_gpu=None,
                 conda_dependencies=None,
                 rl_framework=None,
                 worker_configuration=None,
                 max_run_duration_seconds=None,
                 cluster_coordination_timeout_seconds=None,
                 environment_variables=None,
                 shm_size=None,
                 inputs=None):
        """Initialize properties common to all RL estimators.

        :param source_directory: The directory containing code or configuration for the estimator.
        :type source_directory: str
        :param environment: The environment definition for the experiment. It includes
            PythonSection, DockerSection, and environment variables. Any environment option not directly
            exposed through other parameters to the Estimator construction can be set using this
            parameter. If this parameter is specified, it will be used as a base upon which packages specified in
            ``pip_packages`` and ``conda_packages`` will be added.
        :type environment: azureml.core.Environment
        :param entry_script: The relative path to the file containing the training script.
        :type entry_script: str
        :param script_params: A dictionary of command-line arguments to pass to the training script specified in
            ``entry_script``.
        :type script_params: dict
        :param compute_target: The compute target where the head script will run. This can either be an object or the
            compute target name.
        :type compute_target: azureml.core.compute_target.AbstractComputeTarget or str
        :param use_gpu: Specifies whether the environment should support GPUs.
            If true, a GPU-based default Docker image will be used in the environment. If false, a CPU-based
            image will be used. If not set, we decide based on compute target. Default docker images (CPU or GPU)
            will be used only if the ``environment`` parameter is not set.
        :type use_gpu: bool
        :param conda_dependencies: A CondaDependencies object representing conda and pip packages to be added
            to the head's Python environment for the experiment.
        :type conda_dependencies: azureml.core.conda_dependencies.CondaDependencies
        :param rl_framework: Orchestration framework to be used in the experiment. The default is Ray version 0.8.0
        :type rl_framework: azureml.contrib.train.rl.RLFramework
        :param cluster_coordination_timeout_seconds: The maximum time in seconds that the job can take to start once
            it has passed the queued state.
        :type cluster_coordination_timeout_seconds: int
        :param max_run_duration_seconds: The maximum allowed time for the run in seconds. Azure ML
            will attempt to automatically cancel the job if it takes longer than this value.
        :type max_run_duration_seconds: int
        :param worker_configuration: The configuration for the workers.
        :type worker_configuration: azureml.contrib.train.rl.WorkerConfiguration
        :param environment_variables: A dictionary of environment variables names and values.
            These environment variables are set on the head process, where the ``entry_script`` being executed.
        :type environment_variables: dict
        :param shm_size: The size of the Docker container's shared memory block. If not set, it will use 1/2 of ram
            For more information, see  `Docker run reference <https://docs.docker.com/engine/reference/run/>`_.
        :type shm_size: str
        :param inputs: A list of :class:`azureml.data.data_reference.DataReference` or
            :class:`azureml.data.dataset_consumption_config.DatasetConsumptionConfig` objects to use as input.
        :type inputs: list
        """
        self._source_directory = source_directory if source_directory else "."
        self._compute_target = compute_target
        self._rl_framework = rl_framework
        self._inputs = inputs

        self._original_user_env = environment

        self._use_gpu = use_gpu
        self._shm_size = shm_size
        self._conda_dependencies = conda_dependencies
        self._environment_variables = environment_variables
        self._environment = None

        if environment:
            self._user_provided_environment = True
            self._environment = _setup_environment(
                base_env=self._original_user_env, framework=self.framework,
                use_gpu=self._use_gpu or False,
                conda_dependencies=self._conda_dependencies,
                environment_variables=self._environment_variables)
        else:
            self._user_provided_environment = False
            self._environment = _setup_environment(
                framework=self.framework, use_gpu=self._use_gpu or False,
                conda_dependencies=self._conda_dependencies,
                environment_variables=self._environment_variables)

        self._entry_script = entry_script
        self._script_params = script_params

        self._coordination_timeout = cluster_coordination_timeout_seconds
        self._max_run_duration_seconds = max_run_duration_seconds

        self._estimator_config = self._init_rl_config()
        self.worker_configuration = worker_configuration
        self.head_configuration = self._get_head_configuration()

        self._logger = TelemetryLogger.get_telemetry_logger(__name__)

    @property
    def source_directory(self):
        """Return the path to the source directory.

        :return: The source directory path.
        :rtype: str
        """
        return self._source_directory

    @property
    def rl_config(self):
        """Return `ReinforcementLearningConfiguration` object for this estimator.

        :return: The run configuration.
        :rtype: azureml.contrib.train.rl.ReinforcementLearningConfiguration
        """
        return self._estimator_config

    @property
    def framework(self):
        """Return the reinforcement learning framework specified for the estimator.

        :return: The reinforcement learning framework.
        :rtype: azureml.contrib.train.rl.RLFramework
        """
        return self._rl_framework

    @property
    def head_configuration(self):
        """Return the head node configuration for the estimator.

        :return: The head node configuration.
        :rtype: azureml.contrib.train.rl.HeadConfiguration
        """
        return self._head_configuration

    @head_configuration.setter
    def head_configuration(self, head_configuration):
        if isinstance(head_configuration, HeadConfiguration):
            self._head_configuration = head_configuration
            self.rl_config.head = self._head_configuration

    @property
    def worker_configuration(self):
        """Return the worker node configuration for the estimator.

        :return: The worker node configuration.
        :rtype: azureml.contrib.train.rl.WorkerConfiguration
        """
        return self._worker_configuration

    @worker_configuration.setter
    def worker_configuration(self, worker_configuration):
        if isinstance(worker_configuration, WorkerConfiguration):
            self._worker_configuration = worker_configuration
            if not self._worker_configuration._is_environment_initialized():
                if self._user_provided_environment:
                    self._worker_configuration._initialize_custom_env(self._original_user_env, self.source_directory)
                else:
                    self._worker_configuration._initialize_env_for_framework(self.framework, self.source_directory)
            self.rl_config.workers = self._worker_configuration

    def _get_head_configuration(self):
        data_reference_inputs, dataset_inputs = _get_data_inputs(self._script_params)
        dataset_outputs = _get_outputs(self._script_params)
        data_references, data = _get_data_configuration(self._inputs, data_reference_inputs, dataset_inputs, None)

        return HeadConfiguration(script=self._entry_script,
                                 arguments=_get_arguments(self._script_params),
                                 compute_target=self._compute_target,
                                 environment=self._environment,
                                 shm_size=self._shm_size,
                                 data_references=data_references,
                                 data=data,
                                 output_data=dataset_outputs)

    def _init_rl_config(self):

        # TODO add list of supported framework versions and validate accordingly

        return ReinforcementLearningConfiguration(framework=self.framework,
                                                  head_configuration=None,
                                                  worker_configuration=None,
                                                  max_run_duration_seconds=self._max_run_duration_seconds,
                                                  cluster_coordination_timeout_seconds=self._coordination_timeout,
                                                  source_directory=self.source_directory)

    def _submit(self, workspace, experiment_name):

        telemetry_values = self._get_telemetry_values(self._submit)
        with TelemetryLogger.log_activity(self._logger,
                                          "train.rl.estimator.submit",
                                          custom_dimensions=telemetry_values) as activity_logger:
            try:
                self._init_head_snapshot(workspace, experiment_name)

                activity_logger.info("Submitting RL experiment through estimator...")
                experiment = Experiment(workspace, experiment_name)
                # TODO check if it's notebook and modify the runconfig appropriately
                self.rl_config._telemetry_values = telemetry_values
                experiment_run = experiment.submit(self.rl_config)
                activity_logger.info("Experiment was submitted. RunId=%s", experiment_run.id)
                return experiment_run
            except AzureMLException as e:
                raise e from None

    def _init_head_snapshot(self, workspace, experiment_name):
        snapshots_client = SnapshotsClient(workspace.service_context)
        thread_pool = Pool(1)
        snapshot_async = thread_pool.apply_async(
            snapshots_client.create_snapshot,
            (os.path.abspath(self._source_directory),))
        snapshot_id = snapshot_async.get()

        self.rl_config.head._snapshot_id = snapshot_id

    def _get_telemetry_values(self, func):
        telemetry_values = {}
        try:
            _azureml_supported_framework_packages = ("tensorflow", "ray")
            # client common...
            telemetry_values['amlClientType'] = 'azureml-sdk-train-rl'
            telemetry_values['amlClientFunction'] = func.__name__
            telemetry_values['amlClientModule'] = self.__class__.__module__
            telemetry_values['amlClientClass'] = self.__class__.__name__
            telemetry_values['amlClientRequestId'] = str(uuid.uuid4())
            telemetry_values['amlClientSessionId'] = _ClientSessionId
            telemetry_values['frameworkName'] = self.framework.name
            telemetry_values['frameworkVersion'] = self.framework.version

            # estimator related...
            telemetry_values['head-useDocker'] = self.head_configuration.environment.docker.enabled
            telemetry_values['head-useCustomDockerImage'] = not (
                self.head_configuration.environment.docker.base_image.lower()
                .startswith('mcr.microsoft.com/azureml/base') or (
                    self.head_configuration.environment.docker.base_image_registry.address
                    is not None and self.head_configuration.environment.docker.base_image_registry.address
                    .startswith('viennaprivate.azurecr.io')))
            telemetry_values['head-addCondaOrPipPackage'] = \
                self.head_configuration.environment.python.conda_dependencies.serialize_to_string() != \
                CondaDependencies().serialize_to_string()
            telemetry_values['head-IsFrameworkPipPackageAdded'] = True \
                if len([p for p in self.head_configuration.environment.python.conda_dependencies.pip_packages if
                        p.lower().startswith(_azureml_supported_framework_packages)]) else False
            telemetry_values['head-IsFrameworkCondaPackageAdded'] = True \
                if len([p for p in self.head_configuration.environment.python.conda_dependencies.conda_packages if
                        p.lower().startswith(_azureml_supported_framework_packages)]) else False
            telemetry_values['head-incrementalBuild'] = self.head_configuration.environment.python. \
                _base_conda_environment is not None
            # TODO how to get whether customer dependencies were added from the new Environment object

            # TODO add data reference telemetry

            # TODO add workers telemetry
        except Exception:
            pass

        return telemetry_values
