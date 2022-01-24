# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from azureml.core.runconfig import TensorflowConfiguration, MpiConfiguration, RunConfiguration
from azureml.core.conda_dependencies import CondaDependencies
from azureml.core.experiment import Experiment
from azureml.core.script_run_config import ScriptRunConfig
from azureml.exceptions import TrainingException, AzureMLException
from azureml._base_sdk_common.utils import merge_dict, convert_list_to_dict
from azureml._base_sdk_common import _ClientSessionId
from azureml.train._telemetry_logger import _TelemetryLogger
from azureml.train._estimator_helper import _init_run_config, \
    _get_arguments, _get_data_inputs, _get_data_configuration, _is_notebook_run
from azureml.train._distributed_training import _DistributedTraining
from azureml.train._script_validation import _validate

import uuid
from abc import ABC

module_logger = logging.getLogger(__name__)


class MMLBaseEstimator(ABC):
    """Abstract base class for all estimators.

    DEPRECATED. Use the :class:`azureml.core.script_run_config.ScriptRunConfig` object with your own
    defined environment or an Azure ML curated environment.

    :param source_directory: The directory containing code or configuration for the estimator.
    :type source_directory: str
    :param compute_target: The compute target where training will happen. This can either be an object or the
        string "local".
    :type compute_target: azureml.core.compute_target.AbstractComputeTarget or str
    :param estimator_config: The run-time configuration used by the estimator.
    :type estimator_config: azureml.core.runconfig.RunConfiguration
    :param script_params: A dictionary containing parameters to the entry_script.
    :type script_params: dict
    :param inputs: Data references or Datasets as input.
    :type inputs: list
    :param source_directory_data_store: The backing data store for the project share.
    :type source_directory_data_store: azureml.core.datastore.Datastore
    """

    # these instance variables are added here to enable the use of mock objects in testing
    run_config = None
    _compute_target = None
    _estimator_config = None
    _original_config = None
    _script_params = None
    _inputs = None
    _source_directory_data_store = None

    def __init__(self, source_directory, *, compute_target, estimator_config=None):
        """Initialize properties common to all estimators.

        :param source_directory: The directory containing code or configuration for the estimator.
        :type source_directory: str
        :param compute_target: The compute target where training will happen. This can either be an object or the
            string "local".
        :type compute_target: azureml.core.compute_target.AbstractComputeTarget or str
        :param estimator_config: The run-time configuration used by the estimator.
        :type estimator_config: azureml.core.runconfig.RunConfiguration
        """
        self._source_directory = source_directory if source_directory else "."
        self._compute_target = compute_target
        self._estimator_config = estimator_config
        self._logger = _TelemetryLogger.get_telemetry_logger(__name__)

    @property
    def source_directory(self):
        """Return the path to the source directory.

        :return: The source directory path.
        :rtype: str
        """
        return self._source_directory

    @property
    def run_config(self):
        """Return a RunConfiguration object for this estimator.

        :return: The run configuration.
        :rtype: azureml.core.runconfig.RunConfiguration
        """
        return self._estimator_config

    @property
    def conda_dependencies(self):
        """Return the conda dependencies object for this estimator.

        :return: The conda dependencies.
        :rtype: azureml.core.conda_dependencies.CondaDependencies
        """
        return self.run_config.environment.python.conda_dependencies

    def _get_script_run_config(self, activity_logger=None, telemetry_values=None):
        script = self.run_config.script
        if _is_notebook_run(script):
            if activity_logger is not None:
                activity_logger.info("Training script is a notebook")
            # Since notebook runs are in preview, the dependencies are in contrib package
            # If a user is using notebook run, check if the required contrib package is installed.
            # This is a temp check. Once it is moved out of contrib, no need for this check.
            try:
                from azureml.contrib.notebook import NotebookRunConfig
            except ImportError:
                raise TrainingException("To use a jupyter notebook for training script install notebook"
                                        "dependencies from azureml-contrib-notebook. PyPi information "
                                        "for this package can be found at "
                                        "https://pypi.org/project/azureml-contrib-notebook/")
            return NotebookRunConfig(source_directory=self.source_directory,
                                     notebook=self.run_config.script,
                                     parameters=convert_list_to_dict(self.run_config.arguments),
                                     run_config=self.run_config,
                                     output_notebook="./outputs/{}.output.ipynb".format(script.split(".ipynb")[0]),
                                     _telemetry_values=telemetry_values)
        else:
            return ScriptRunConfig(source_directory=self.source_directory,
                                   script=self.run_config.script, arguments=self.run_config.arguments,
                                   run_config=self.run_config, _telemetry_values=telemetry_values)

    def _submit(self, workspace, experiment_name, telemetry_values):
        # For flag based script arguments with store_action attr,
        # the expected input to estimator script_params is {"--v": ""}
        # The script_params gets translated into list as ["--v", ""].
        # Remove the empty entry from the list before submitting the experiment.

        try:
            telemetry_values['validationDisabled'] = self._disable_validation
            if not self._disable_validation:
                validation_telemetry = _validate(self.source_directory, self.run_config,
                                                 self._show_lint_warnings, self._show_package_warnings)
                telemetry_values.update(validation_telemetry)
        except Exception as e:
            module_logger.warning("Validation throws exception " + e.message)
            raise TrainingException(e.message, inner_exception=e) from None

        with _TelemetryLogger.log_activity(self._logger,
                                           "train.estimator.submit",
                                           custom_dimensions=telemetry_values) as activity_logger:
            try:
                activity_logger.info("Submitting experiment through estimator...")
                experiment = Experiment(workspace, experiment_name, _create_in_cloud=False)
                config = self._get_script_run_config(activity_logger, telemetry_values)
                experiment_run = experiment.submit(config)
                activity_logger.info("Experiment was submitted. RunId=%s", experiment_run.id)

                return experiment_run
            except AzureMLException as e:
                raise TrainingException(e.message, inner_exception=e) from None

    def _fit(self, workspace, experiment_name):
        telemetry_values = self._get_telemetry_values(self._fit)
        self._last_submitted_runconfig = self.run_config

        return self._submit(workspace, experiment_name, telemetry_values)

    def _override_params(self, script_params=None, inputs=None, source_directory_data_store=None):
        data_reference_inputs = None
        dataset_inputs = None
        if script_params:
            merged_script_params = merge_dict(convert_list_to_dict(self._estimator_config.arguments), script_params)
            self._estimator_config.arguments = _get_arguments(merged_script_params)
            data_reference_inputs, dataset_inputs = _get_data_inputs(script_params)

        data_references, data = \
            _get_data_configuration(inputs,
                                    data_reference_inputs,
                                    dataset_inputs,
                                    source_directory_data_store)
        self._estimator_config.data_references = \
            merge_dict(self._estimator_config.data_references, data_references)
        self._estimator_config.data = \
            merge_dict(self._estimator_config.data, data)
        if source_directory_data_store:
            self._estimator_config.source_directory_data_store = source_directory_data_store.name

    def _get_telemetry_values(self, func):
        telemetry_values = {}

        try:
            _azureml_supported_framework_packages = ("tensorflow", "torch", "chainer", "scikit-learn")

            # client common...
            telemetry_values['amlClientType'] = 'azureml-sdk-train'
            telemetry_values['amlClientFunction'] = func.__name__
            telemetry_values['amlClientModule'] = self.__class__.__module__
            telemetry_values['amlClientClass'] = self.__class__.__name__
            telemetry_values['amlClientRequestId'] = str(uuid.uuid4())
            telemetry_values['amlClientSessionId'] = _ClientSessionId

            # estimator related...
            telemetry_values['useDocker'] = self.run_config.environment.docker.enabled
            telemetry_values['useDockerFile'] = True \
                if self.run_config.environment.docker.base_dockerfile is not None else False
            if self.run_config.environment.docker.base_image:
                telemetry_values['useCustomDockerImage'] = not (
                    self.run_config.environment.docker.base_image.lower().
                    startswith('mcr.microsoft.com/azureml')
                    or (self.run_config.environment.docker.base_image_registry.address is not None
                        and self.run_config.environment.docker.base_image_registry.address.startswith
                        ('viennaprivate.azurecr.io')))
            telemetry_values['addCondaOrPipPackage'] = self.conda_dependencies.serialize_to_string() != \
                CondaDependencies().serialize_to_string()
            telemetry_values['IsFrameworkPipPackageAdded'] = True \
                if len([p for p in self.conda_dependencies.pip_packages if
                        p.lower().startswith(_azureml_supported_framework_packages)]) else False
            telemetry_values['IsFrameworkCondaPackageAdded'] = True \
                if len([p for p in self.conda_dependencies.conda_packages if
                        p.lower().startswith(_azureml_supported_framework_packages)]) else False

            # data references and data configurations related...
            data_references = self.run_config.data_references
            data = self.run_config.data

            telemetry_values['amlDataReferencesEnabled'] = len(data_references) > 0
            telemetry_values['amlDatasEnabled'] = len(data) > 0

            # distributed training related...
            telemetry_values['nodeCount'] = self._estimator_config.node_count
            telemetry_values['processCountPerNode'] = self.run_config.mpi.process_count_per_node

            telemetry_values['manualRestart'] = self._manual_restart_used

            if self._distributed_backend:
                if isinstance(self._distributed_backend, str):
                    telemetry_values['distributed_backend'] = self._distributed_backend
                elif isinstance(self._distributed_backend, TensorflowConfiguration):
                    telemetry_values['distributed_backend'] = "ps"
                elif isinstance(self._distributed_backend, MpiConfiguration):
                    telemetry_values['distributed_backend'] = "mpi"
                elif isinstance(self._distributed_backend, _DistributedTraining):
                    telemetry_values['distributed_backend'] = self._distributed_backend.__str__()

            telemetry_values['computeTarget'] = self._compute_target if isinstance(self._compute_target, str) else \
                self._compute_target.type if self._compute_target else "amlcompute"
            telemetry_values['vmSize'] = self.run_config.amlcompute.vm_size if self.run_config.amlcompute \
                else None
            telemetry_values['shmSize'] = self.run_config.environment.docker.shm_size

            return telemetry_values

        # Exception in collecting telemetry shouldn't fail user runs.
        except Exception:
            pass

    @classmethod
    def _get_supported_backends(cls):
        """
        Return the distributed training backend(s) supported by the estimator class.

        :return: The supported backend(s).
        :rtype: list
        """
        return cls._SUPPORTED_BACKENDS


class MMLBaseEstimatorRunConfig(RunConfiguration):
    """
    Abstract base class for all Estimator run configs.

    DEPRECATED. Use the :class:`azureml.core.runconfig.RunConfiguration` class.

    :param compute_target: The compute target where training will happen. This can either be an object or the
        string "local".
    :type compute_target: azureml.core.compute_target.AbstractComputeTarget or str
    :param vm_size: The VM size of the compute target that will be created for the training.

        Supported values: Any `Azure VM size
        <https://docs.microsoft.com/azure/cloud-services/cloud-services-sizes-specs>`_.
    :type vm_size: str
    :param vm_priority: The VM priority of the compute target that will be created for the training. If not
        specified, 'dedicated' is used.

        Supported values: 'dedicated' and 'lowpriority'.

        This takes effect only when the ``vm_size`` parameter is specified in the input.
    :type vm_priority: str
    :param entry_script: The relative path to the file used to start training.
    :type entry_script: str
    :param script_params: A dictionary containing parameters that will be passed as arguments to the ``entry_script``.
    :type script_params: dict
    :param node_count: The number of nodes in the compute target used for training. Only the
        the :class:`azureml.core.compute.AmlCompute` target is supported for distributed training (``node_count`` > 1).
    :type node_count: int
    :param process_count_per_node: When using MPI as an execution backend, the number of processes per node.
    :type process_count_per_node: int
    :param distributed_backend: The communication backend for distributed training.

        Supported values: 'mpi' and 'ps'.

            'mpi': MPI/Horovod
            'ps': parameter server

        This parameter is required when any of ``node_count``, ``process_count_per_node``, ``worker_count``, or
        ``parameter_server_count`` > 1.

        When ``node_count`` == 1 and ``process_count_per_node`` == 1, no backend will be used unless a backend
        is explicitly set. Only the azureml.core.compute.AmlCompute target is supported for distributed training.
    :type distributed_backend: str
    :param use_gpu: Specifies whether the environment to run the experiment should support GPUs.
        If true, a GPU-based default Docker image will be used in the environment. If false, a CPU-based
        image will be used. Default Docker images (CPU or GPU) will be used only if the ``custom_docker_image``
        parameter is not set. This setting is used only in Docker-enabled compute targets.
    :type use_gpu: bool
    :param use_docker: Specifies whether the environment to run the experiment should be Docker-based.
    :type use_docker: bool
    :param custom_docker_base_image: The name of the Docker image from which the image to use for training
        will be built.

        DEPRECATED. Use the ``custom_docker_image`` parameter.

        If not set, a default CPU-based image will be used as the base image.
    :type custom_docker_base_image: str
    :param custom_docker_image: The name of the Docker image from which the image to use for training
        will be built. If not set, a default CPU-based image will be used as the base image.
    :type custom_docker_image: str
    :param image_registry_details: The details of the Docker image registry.
    :type image_registry_details: azureml.core.container_registry.ContainerRegistry
    :param user_managed: Specifies whether Azure ML reuses an existing Python environment. If false,
        a Python environment is created based on the conda dependencies specification.
    :type user_managed: bool
    :param conda_packages: List of strings representing conda packages to be added to the Python environment
        for the experiment.
    :type conda_packages: list
    :param pip_packages: A list of strings representing pip packages to be added to the Python environment
        for the experiment.
    :type pip_packages: list
    :param environment_definition: The environment definition for the experiment. It includes
        PythonSection, DockerSection, and environment variables. Any environment option not directly
        exposed through other parameters to the Estimator construction can be set using this
        parameter. If this parameter is specified, it will take precedence over other environment related
        parameters like ``use_gpu``, ``custom_docker_image``, ``conda_packages``, or ``pip_packages`` and
        errors will be reported on these invalid combinations.
    :type environment_definition: azureml.core.Environment
    :param inputs: A list of :class:`azureml.data.data_reference.DataReference` or
        :class:`azureml.data.dataset_consumption_config.DatasetConsumptionConfig` objects to use as input.
    :type inputs: list
    :param source_directory_data_store: The backing data store for the project share.
    :type source_directory_data_store: str
    :param shm_size: The size of the Docker container's shared memory block. For more information, see
        `Docker run reference <https://docs.docker.com/engine/reference/run/>`_. If not set, the default
        azureml.core.environment._DEFAULT_SHM_SIZE is used.
    :type shm_size: str
    """

    def __init__(self, compute_target, vm_size=None, vm_priority=None,
                 entry_script=None, script_params=None, node_count=None,
                 process_count_per_node=None, distributed_backend=None, use_gpu=None, use_docker=None,
                 custom_docker_base_image=None, custom_docker_image=None, image_registry_details=None,
                 user_managed=False, conda_packages=None, pip_packages=None, environment_definition=None,
                 inputs=None, source_directory_data_store=None, shm_size=None):
        """Initialize the MMLBaseEstimatorRunConfig."""
        module_logger.warning("'MMLBaseEstimatorRunConfig' will be deprecated soon. Please "
                              "use 'azureml.core.runconfig.RunConfiguration'.")

        estimator_config = _init_run_config(
            estimator=None,
            source_directory=None,
            compute_target=compute_target,
            vm_size=vm_size,
            vm_priority=vm_priority,
            entry_script=entry_script,
            script_params=script_params,
            node_count=node_count,
            process_count_per_node=process_count_per_node,
            distributed_backend=distributed_backend,
            use_gpu=use_gpu,
            use_docker=use_docker,
            custom_docker_base_image=custom_docker_base_image,
            custom_docker_image=custom_docker_image,
            image_registry_details=image_registry_details,
            user_managed=user_managed,
            conda_packages=conda_packages,
            pip_packages=pip_packages,
            environment_definition=environment_definition,
            inputs=inputs,
            source_directory_data_store=source_directory_data_store,
            shm_size=shm_size)
        self.__dict__.update(estimator_config.__dict__)
