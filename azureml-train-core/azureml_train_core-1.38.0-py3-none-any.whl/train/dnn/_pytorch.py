# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""The PyTorch estimator class."""

import logging

from azureml.core._experiment_method import experiment_method

from ..estimator._framework_base_estimator import _FrameworkBaseEstimator
from .._estimator_helper import _estimator_submit_method


module_logger = logging.getLogger(__name__)


class PyTorch(_FrameworkBaseEstimator):
    """Represents an estimator for training in PyTorch experiments.

    DEPRECATED. Use the :class:`azureml.core.script_run_config.ScriptRunConfig` object with your own
    defined environment or one of the Azure ML PyTorch curated environments. For an introduction to
    configuring PyTorch experiment runs with ScriptRunConfig, see
    `Train PyTorch models at scale with Azure Machine Learning
    <https://docs.microsoft.com/azure/machine-learning/how-to-train-pytorch?view=azure-ml-py>`_.

    Supported versions: 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6

    .. remarks::

            When submitting a training job, Azure ML runs your script in a conda environment within
            a Docker container. The PyTorch containers have the following dependencies installed.

            | Dependencies | PyTorch 1.0/1.1/1.2/1.3/    | PyTorch 1.4/1.5/1.6 |
            | ---------------------- | ----------------- | -------------   |
            | Python                 | 3.6.2             | 3.6.2           |
            | CUDA  (GPU image only) | 10.0              | 10.1            |
            | cuDNN (GPU image only) | 7.6.3             | 7.6.3           |
            | NCCL  (GPU image only) | 2.4.8             | 2.4.8           |
            | azureml-defaults       | Latest            | Latest          |
            | OpenMpi                | 3.1.2             | 3.1.2           |
            | horovod                | 0.18.1            | 0.18.1/0.19.1/0.19.5  |
            | miniconda              | 4.5.11            | 4.5.11          |
            | torch                  | 1.0/1.1/1.2/1.3.1 | 1.4.0/1.5.0/1.6.0     |
            | torchvision            | 0.4.1             | 0.5.0           |
            | git                    | 2.7.4             | 2.7.4           |
            | tensorboard            | 1.14              | 1.14            |
            | future                 | 0.17.1            | 0.17.1          |

            The Docker images extend Ubuntu 16.04.

            To install additional dependencies, you can either use the ``pip_packages`` or ``conda_packages``
            parameter. Or, you can specify the ``pip_requirements_file`` or ``conda_dependencies_file`` parameter.
            Alternatively, you can build your own image, and pass the ``custom_docker_image`` parameter to the
            estimator constructor.

            For more information about Docker containers used in PyTorch training, see
            https://github.com/Azure/AzureML-Containers.

            The PyTorch estimator supports distributed training across CPU and GPU clusters using
            `Horovod <https://github.com/uber/horovod>`_, an open-source, all reduce framework for distributed
            training.  For examples and more information about using PyTorch in distributed training, see the
            tutorial `Train and register PyTorch models at scale with Azure Machine Learning
            <https://docs.microsoft.com/azure/machine-learning/how-to-train-pytorch>`_.

    :param source_directory: A local directory containing experiment configuration files.
    :type source_directory: str
    :param compute_target: The compute target where training will happen. This can either be an object or the
        string "local".
    :type compute_target: azureml.core.compute_target.AbstractComputeTarget or str
    :param vm_size: The VM size of the compute target that will be created for the training. Supported values:
        Any `Azure VM size
        <https://docs.microsoft.com/azure/cloud-services/cloud-services-sizes-specs>`_.
    :type vm_size: str
    :param vm_priority: The VM priority of the compute target that will be created for the training. If not
        specified, 'dedicated' is used.

        Supported values: 'dedicated' and 'lowpriority'.

        This takes effect only when the ``vm_size param`` is specified in the input.
    :type vm_priority: str
    :param entry_script: The relative path to the file containing the training script.
    :type entry_script: str
    :param script_params: A dictionary of command-line arguments to pass to the training script specified in
        ``entry_script``.
    :type script_params: dict
    :param node_count: The number of nodes in the compute target used for training. If greater than 1, an MPI
        distributed job will be run. Only the :class:`azureml.core.compute.AmlCompute` target is supported
        for distributed jobs.
    :type node_count: int
    :param process_count_per_node: The number of processes per node. If greater than 1, an MPI
        distributed job will be run. Only the :class:`azureml.core.compute.AmlCompute` target is supported for
        distributed jobs.
    :type process_count_per_node: int
    :param distributed_backend: The communication backend for distributed training.

        DEPRECATED. Use the ``distributed_training`` parameter.

        Supported values: 'mpi', 'gloo' and 'nccl'.

            'mpi': MPI/Horovod
            'gloo', 'nccl': Native PyTorch Distributed Training

        This parameter is required when ``node_count`` or ``process_count_per_node`` > 1.

        When ``node_count`` == 1 and ``process_count_per_node`` == 1, no backend will be used
        unless the backend is explicitly set. Only the :class:`azureml.core.compute.AmlCompute` target is
        supported for distributed training.
    :type distributed_backend: str
    :param distributed_training: Parameters for running a distributed training job.

        For running a distributed job with MPI backend, use :class:`azureml.train.dnn.Mpi`
        object to specify ``process_count_per_node``.
        For running a distributed job with gloo backend, use :class:`azureml.train.dnn.Gloo`.
        For running a distributed job with nccl backend, use :class:`azureml.train.dnn.Nccl`.
    :type distributed_training: azureml.train.dnn.Mpi or azureml.train.dnn.Gloo or
        azureml.train.dnn.Nccl
    :param use_gpu: Specifies whether the environment to run the experiment should support GPUs.
        If true, a GPU-based default Docker image will be used in the environment. If false, a CPU-based
        image will be used. Default docker images (CPU or GPU) will be used only if the ``custom_docker_image``
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
    :param user_managed: Specifies whether Azure ML reuses an existing python environment. If false,
        Azure ML will create a Python environment based on the conda dependencies specification.
    :type user_managed: bool
    :param conda_packages: A list of strings representing conda packages to be added to the Python environment
        for the experiment.
    :type conda_packages: list
    :param pip_packages: A list of strings representing pip packages to be added to the Python environment
        for the experiment.
    :type pip_packages: list
    :param conda_dependencies_file_path: The relative path to the conda dependencies yaml file.
        If specified, Azure ML will not install any framework related packages.
        DEPRECATED. Use the ``conda_dependencies_file`` parameter.
    :type conda_dependencies_file_path: str
    :param pip_requirements_file_path: The relative path to the pip requirements text file.
        This can be provided in combination with the ``pip_packages`` parameter.
        DEPRECATED. Use the ``pip_requirements_file`` parameter.
    :type pip_requirements_file_path: str
    :param conda_dependencies_file: The relative path to the conda dependencies yaml file.
        If specified, Azure ML will not install any framework related packages.
    :type conda_dependencies_file: str
    :param pip_requirements_file: The relative path to the pip requirements text file.
        This can be provided in combination with the ``pip_packages`` parameter.
    :type pip_requirements_file: str
    :param environment_variables: A dictionary of environment variables names and values.
        These environment variables are set on the process where user script is being executed.
    :type environment_variables: dict
    :param environment_definition: The environment definition for the experiment. It includes
        PythonSection, DockerSection, and environment variables. Any environment option not directly
        exposed through other parameters to the Estimator construction can be set using this
        parameter. If this parameter is specified, it will take precedence over other environment-related
        parameters like ``use_gpu``, ``custom_docker_image``, ``conda_packages``, or ``pip_packages``.
        Errors will be reported on invalid combinations of parameters.
    :type environment_definition: azureml.core.Environment
    :param inputs: A list of :class:`azureml.data.data_reference.DataReference` or
        :class:`azureml.data.dataset_consumption_config.DatasetConsumptionConfig` objects to use as input.
    :type inputs: list
    :param source_directory_data_store: The backing datastore for project share.
    :type source_directory_data_store: azureml.core.Datastore
    :param shm_size: The size of the Docker container's shared memory block. If not set, the default
        azureml.core.environment._DEFAULT_SHM_SIZE is used. For more information, see
        `Docker run reference <https://docs.docker.com/engine/reference/run/>`_.
    :type shm_size: str
    :param resume_from: The data path containing the checkpoint or model files from which to resume the experiment.
    :type resume_from: azureml.data.datapath.DataPath
    :param max_run_duration_seconds: The maximum allowed time for the run. Azure ML will attempt to automatically
        cancel the run if it takes longer than this value.
    :type max_run_duration_seconds: int
    :param framework_version: The PyTorch version to be used for executing training code.
        ``PyTorch.get_supported_versions()`` returns a list of the versions supported by the current SDK.
    :type framework_version: str
    """

    FRAMEWORK_NAME = "PyTorch"
    DEFAULT_VERSION = '1.4'
    _SUPPORTED_BACKENDS = ["mpi", "gloo", "nccl"]

    @experiment_method(submit_function=_estimator_submit_method)
    def __init__(self,
                 source_directory,
                 *,
                 compute_target=None,
                 vm_size=None,
                 vm_priority=None,
                 entry_script=None,
                 script_params=None,
                 node_count=1,
                 process_count_per_node=1,
                 distributed_backend=None,
                 distributed_training=None,
                 use_gpu=False,
                 use_docker=True,
                 custom_docker_base_image=None,
                 custom_docker_image=None,
                 image_registry_details=None,
                 user_managed=False,
                 conda_packages=None,
                 pip_packages=None,
                 conda_dependencies_file_path=None,
                 pip_requirements_file_path=None,
                 conda_dependencies_file=None,
                 pip_requirements_file=None,
                 environment_variables=None,
                 environment_definition=None,
                 inputs=None,
                 source_directory_data_store=None,
                 shm_size=None,
                 resume_from=None,
                 max_run_duration_seconds=None,
                 framework_version=None,
                 _enable_optimized_mode=False,
                 _disable_validation=True,
                 _show_lint_warnings=False,
                 _show_package_warnings=False):
        """Initialize a PyTorch estimator.

        :param source_directory: A local directory containing experiment configuration files.
        :type source_directory: str
        :param compute_target: The compute target where training will happen. This can either be an object or the
            string "local".
        :type compute_target: azureml.core.compute_target.AbstractComputeTarget or str
        :param vm_size: The VM size of the compute target that will be created for the training. Supported values:
            Any `Azure VM size
            <https://docs.microsoft.com/azure/cloud-services/cloud-services-sizes-specs>`_.
        :type vm_size: str
        :param vm_priority: The VM priority of the compute target that will be created for the training. If not
            specified, 'dedicated' is used.

            Supported values: 'dedicated' and 'lowpriority'.

            This takes effect only when the ``vm_size param`` is specified in the input.
        :type vm_priority: str
        :param entry_script: The relative path to the file containing the training script.
        :type entry_script: str
        :param script_params: A dictionary of command-line arguments to pass to the training script specified in
            ``entry_script``.
        :type script_params: dict
        :param node_count: The number of nodes in the compute target used for training. If greater than 1, mpi
            distributed job will be run. Only the azureml.core.compute.AmlCompute target is supported for
            distributed jobs.
        :type node_count: int
        :param process_count_per_node: The number of processes per node. If greater than 1, an MPI
            distributed job will be run. Only the :class:`azureml.core.compute.AmlCompute` target is supported
            for distributed jobs.
        :type process_count_per_node: int
        :param distributed_backend: The communication backend for distributed training.

            DEPRECATED. Use the ``distributed_training`` parameter.

            Supported values: 'mpi', 'gloo' and 'nccl'.

                'mpi': MPI/Horovod
                'gloo', 'nccl': Native PyTorch Distributed Training

            This parameter is required when ``node_count`` or ``process_count_per_node`` > 1.

            When ``node_count`` == 1 and ``process_count_per_node`` == 1, no backend will be used
            unless the backend is explicitly set. Only the :class:`azureml.core.compute.AmlCompute` target is
            supported for distributed training.
        :type distributed_backend: str
        :param distributed_training: Parameters for running a distributed training job.

            For running a distributed job with MPI backend, use :class:`azureml.train.dnn.Mpi`
            object to specify ``process_count_per_node``.
            For running a distributed job with gloo backend, use :class:`azureml.train.dnn.Gloo`.
            For running a distributed job with nccl backend, use :class:`azureml.train.dnn.Nccl`.
        :type distributed_training: azureml.train.dnn.Mpi or azureml.train.dnn.Gloo or
            azureml.train.dnn.Nccl
        :param use_gpu: Specifies whether the environment to run the experiment should support GPUs.
            If true, a GPU-based default Docker image will be used in the environment. If false, a CPU-based
            image will be used. Default docker images (CPU or GPU) will be used only if the ``custom_docker_image``
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
            Azure ML will create a Python environment based on the conda dependencies specification.
        :type user_managed: bool
        :param conda_packages: A list of strings representing conda packages to be added to the Python environment
            for the experiment.
        :type conda_packages: list
        :param pip_packages: A list of strings representing pip packages to be added to the Python environment
            for the experiment.
        :type pip_packages: list
        :param conda_dependencies_file_path: The relative path to the conda dependencies
            yaml file. If specified, Azure ML will not install any framework related packages.
            DEPRECATED. Use the ``conda_dependencies_file`` parameter.
        :type conda_dependencies_file_path: str
        :param pip_requirements_file_path: The relative path to the pip requirements text file.
            This can be provided in combination with the ``pip_packages`` parameter.
            DEPRECATED. Use the ``pip_requirements_file`` parameter.
        :type pip_requirements_file_path: str
        :param conda_dependencies_file: The relative path to the conda dependencies
            yaml file. If specified, Azure ML will not install any framework related packages.
        :type conda_dependencies_file: str
        :param pip_requirements_file: The relative path to the pip requirements text file.
            This can be provided in combination with the ``pip_packages`` parameter.
        :type pip_requirements_file: str
        :param environment_variables: A dictionary of environment variables names and values.
            These environment variables are set on the process where user script is being executed.
        :type environment_variables: dict
        :param environment_definition: The environment definition for the experiment. It includes
            PythonSection, DockerSection, and environment variables. Any environment option not directly
            exposed through other parameters to the Estimator construction can be set using this
            parameter. If this parameter is specified, it will take precedence over other environment-related
            parameters like ``use_gpu``, ``custom_docker_image``, ``conda_packages``, or ``pip_packages``.
            Errors will be reported on invalid combinations.
        :type environment_definition: azureml.core.Environment
        :param inputs: A list of azureml.data.data_reference.DataReference objects to use as input.
        :type inputs: list
        :param source_directory_data_store: The backing datastore for project share.
        :type source_directory_data_store: azureml.core.Datastore
        :param shm_size: The size of the Docker container's shared memory block. If not set, the default
            azureml.core.environment._DEFAULT_SHM_SIZE is used. For more information, see
        `Docker run reference <https://docs.docker.com/engine/reference/run/>`_.
        :type shm_size: str
        :param resume_from: The data path containing the checkpoint or model files from which to resume the experiment.
        :type resume_from: azureml.data.datapath.DataPath
        :param max_run_duration_seconds: The maximum allowed time for the run. Azure ML will attempt to automatically
            cancel the run if it takes longer than this value.
        :type max_run_duration_seconds: int
        :param framework_version: The PyTorch version to be used for executing training code.
            ``PyTorch.get_supported_versions()`` returns a list of the versions supported by the current SDK.
        :type framework_version: str
        :param _enable_optimized_mode: Enable incremental environment build with pre-built framework images for faster
            environment preparation. A pre-built framework image is built on top of Azure ML default CPU/GPU base
            images with framework dependencies pre-installed.
        :type _enable_optimized_mode: bool
        :param _disable_validation: Disable script validation before run submission. The default is True.
        :type _disable_validation: bool
        :param _show_lint_warnings: Show script linting warnings. The default is False.
        :type _show_lint_warnings: bool
        :param _show_package_warnings: Show package validation warnings. The default is False.
        :type _show_package_warnings: bool
        """
        module_logger.warning("'PyTorch' estimator is deprecated. Please use 'ScriptRunConfig' from "
                              "'azureml.core.script_run_config' with your own defined environment or "
                              "one of the Azure ML PyTorch curated environments.")

        super().__init__(source_directory, compute_target=compute_target, vm_size=vm_size,
                         vm_priority=vm_priority, entry_script=entry_script,
                         script_params=script_params, node_count=node_count,
                         process_count_per_node=process_count_per_node,
                         distributed_backend=distributed_backend, distributed_training=distributed_training,
                         use_gpu=use_gpu, use_docker=use_docker, custom_docker_base_image=custom_docker_base_image,
                         custom_docker_image=custom_docker_image,
                         image_registry_details=image_registry_details,
                         user_managed=user_managed, conda_packages=conda_packages,
                         pip_packages=pip_packages,
                         conda_dependencies_file_path=conda_dependencies_file_path,
                         pip_requirements_file_path=pip_requirements_file_path,
                         conda_dependencies_file=conda_dependencies_file,
                         pip_requirements_file=pip_requirements_file,
                         environment_variables=environment_variables,
                         environment_definition=environment_definition, inputs=inputs,
                         source_directory_data_store=source_directory_data_store,
                         shm_size=shm_size, resume_from=resume_from,
                         max_run_duration_seconds=max_run_duration_seconds,
                         framework_name=self.FRAMEWORK_NAME,
                         framework_version=framework_version,
                         _enable_optimized_mode=_enable_optimized_mode,
                         _disable_validation=_disable_validation,
                         _show_lint_warnings=_show_lint_warnings,
                         _show_package_warnings=_show_package_warnings)

        # To resolve horovod hangs due to a known NCCL issue in version 2.4.
        # Can remove it once we upgrade NCCL to 2.5+.
        # https://github.com/horovod/horovod/issues/893
        self._estimator_config.environment.environment_variables['NCCL_TREE_THRESHOLD'] = '0'

        if distributed_backend and distributed_backend.lower() in ["gloo", "nccl"]:
            self._estimator_config.framework = "PyTorch"
            self._estimator_config.communicator = distributed_backend.lower()
