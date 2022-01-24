# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains an estimator for training with Scikit-Learn."""

import logging

from azureml.core._experiment_method import experiment_method

from .estimator._estimator import _estimator_submit_method
from .estimator._framework_base_estimator import _FrameworkBaseEstimator


module_logger = logging.getLogger(__name__)


class SKLearn(_FrameworkBaseEstimator):
    """Creates an estimator for training in Scikit-learn experiments.

    DEPRECATED. Use the :class:`azureml.core.script_run_config.ScriptRunConfig` object with your own
    defined environment or the AzureML-Tutorial curated environment. For an introduction to configuring SKLearn
    experiment runs with ScriptRunConfig, see `Train scikit-learn models at scale with Azure Machine Learning
    <https://docs.microsoft.com/azure/machine-learning/how-to-train-scikit-learn?view=azure-ml-py>`_.

    This estimator only supports single-node CPU training.

    Supported versions: 0.20.3

    .. remarks::

            When submitting a training job, Azure ML runs your script in a conda environment within
            a Docker container. SKLearn containers have the following dependencies installed.

            | Dependencies | Scikit-learn 0.20.3 |
            | ---------------------- | ----------------- |
            | Python                 | 3.6.2             |
            | azureml-defaults       | Latest            |
            | IntelMpi               | 2018.3.222        |
            | scikit-learn           | 0.20.3            |
            | numpy                  | 1.16.2            |
            | miniconda              | 4.5.11            |
            | scipy                  | 1.2.1             |
            | joblib                 | 0.13.2            |
            | git                    | 2.7.4             |


            The Docker images extend Ubuntu 16.04.

            If you need to install additional dependencies, you can either use the ``pip_packages`` or
            ``conda_packages`` parameters, or you can provide your ``pip_requirements_file`` or
            ``conda_dependencies_file`` file. Alternatively, you can build your own image and pass the
            ``custom_docker_image`` parameter to the estimator constructor.

    :param source_directory: A local directory containing experiment configuration files.
    :type source_directory: str
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

        This takes effect only when the ``vm_size param`` is specified in the input.
    :type vm_priority: str
    :param entry_script: A string representing the relative path to the file used to start training.
    :type entry_script: str
    :param script_params: A dictionary of command-line arguments to pass to your training script specified in
        ``entry_script``.
    :type script_params: dict
    :param custom_docker_image: The name of the Docker image from which the image to use for training
        will be built. If not set, a default CPU based image will be used as the base image.
    :type custom_docker_image: str
    :param image_registry_details: The details of the Docker image registry.
    :type image_registry_details: azureml.core.container_registry.ContainerRegistry
    :param user_managed: Specifies whether Azure ML reuses an existing Python environment. False means
        that AzureML will create a Python environment based on the conda dependencies specification.
    :type user_managed: bool
    :param conda_packages: A list of strings representing conda packages to be added to the Python environment
        for the experiment.
    :type conda_packages: list
    :param pip_packages: A list of strings representing pip packages to be added to the Python environment
        for the experiment.
    :type pip_packages: list
    :param conda_dependencies_file_path: A string representing the relative path to the conda dependencies yaml file.
        If specified, Azure ML will not install any framework related packages.
        This can be provided in combination with the ``conda_packages`` parameter.
        DEPRECATED. Use the ``conda_dependencies_file`` parameter.
    :type conda_dependencies_file_path: str
    :param pip_requirements_file_path: A string representing the relative path to the pip requirements text file.
        This can be provided in combination with the ``pip_packages`` parameter.
        DEPRECATED. Use the ``pip_requirements_file`` parameter.
    :type pip_requirements_file_path: str
    :param conda_dependencies_file: A string representing the relative path to the conda dependencies yaml file.
        If specified, Azure ML will not install any framework related packages.
        This can be provided in combination with the ``conda_packages`` parameter.
    :type conda_dependencies_file: str
    :param pip_requirements_file: A string representing the relative path to the pip requirements text file.
        This can be provided in combination with the ``pip_packages`` parameter.
    :type pip_requirements_file: str
    :param environment_variables: A dictionary of environment variables names and values.
        These environment variables are set on the process where user script is being executed.
    :type environment_variables: dict
    :param environment_definition: The environment definition for an experiment includes
        PythonSection, DockerSection, and environment variables. Any environment option not directly
        exposed through other parameters to the Estimator construction can be set using ``environment_definition``
        parameter. If this parameter is specified, it will take precedence over other environment related
        parameters like ``use_gpu``, ``custom_docker_image``, ``conda_packages``, or ``pip_packages``.
        Errors will be reported invalid combinations.
    :type environment_definition: azureml.core.Environment
    :param inputs: A list of :class:`azureml.data.data_reference.DataReference` or
        :class:`azureml.data.dataset_consumption_config.DatasetConsumptionConfig` objects to use as input.
    :type inputs: list
    :param shm_size: The size of the Docker container's shared memory block. If not set, the default
        azureml.core.environment._DEFAULT_SHM_SIZE is used.
    :type shm_size: str
    :param resume_from: The data path containing the checkpoint or model files from which to resume the experiment.
    :type resume_from: azureml.data.datapath.DataPath
    :param max_run_duration_seconds: The maximum allowed time for the run. Azure ML will attempt to automatically
        cancel the run if it takes longer than this value.
    :type max_run_duration_seconds: int
    :param framework_version: The Scikit-learn version to be used for executing training code.
        ``SKLearn.get_supported_versions()`` returns a list of the versions supported by the current SDK.
    :type framework_version: str
    """

    FRAMEWORK_NAME = "SKLearn"
    DEFAULT_VERSION = '0.20.3'

    @experiment_method(submit_function=_estimator_submit_method)
    def __init__(self,
                 source_directory,
                 *,
                 compute_target=None,
                 vm_size=None,
                 vm_priority=None,
                 entry_script=None,
                 script_params=None,
                 use_docker=True,
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
                 shm_size=None,
                 resume_from=None,
                 max_run_duration_seconds=None,
                 framework_version=None,
                 _enable_optimized_mode=False,
                 _disable_validation=True,
                 _show_lint_warnings=False,
                 _show_package_warnings=False):
        """Initialize a Scikit-learn estimator.

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
        :param entry_script: A string representing the relative path to the file used to start training.
        :type entry_script: str
        :param script_params: A dictionary of command-line arguments to pass to your training script specified in
           ``entry_script``.
        :type script_params: dict
        :param use_docker: A bool value indicating if the environment to run the experiment should be Docker-based.
        :type use_docker: bool
        :param custom_docker_image: The name of the Docker image from which the image to use for training
            will be built. If not set, a default CPU-based image will be used as the base image.
        :type custom_docker_image: str
        :param image_registry_details: The details of the Docker image registry.
        :type image_registry_details: azureml.core.container_registry.ContainerRegistry
        :param user_managed: Specifies whether Azure ML reuses an existing Python environment. False means
            that AzureML will create a Python environment based on the conda dependencies specification.
        :type user_managed: bool
        :param conda_packages: A list of strings representing conda packages to be added to the Python environment
            for the experiment.
        :type conda_packages: list
        :param pip_packages: A list of strings representing pip packages to be added to the Python environment
            for the experiment.
        :type pip_packages: list
        :param conda_dependencies_file_path: A string representing the relative path to the conda dependencies
            yaml file. If specified, Azure ML will not install any framework related packages.
            This can be provided in combination with the ``conda_packages`` parameter.
            DEPRECATED. Use the ``conda_dependencies_file`` parameter.
        :type conda_dependencies_file_path: str
        :param pip_requirements_file_path: A string representing the relative path to the pip requirements text file.
            This can be provided in combination with the ``pip_packages`` parameter.
            DEPRECATED. Use the ``pip_requirements_file`` parameter.
        :type pip_requirements_file_path: str
        :param conda_dependencies_file: A string representing the relative path to the conda dependencies
            yaml file. If specified, Azure ML will not install any framework related packages.
            This can be provided in combination with the ``conda_packages`` parameter.
        :type conda_dependencies_file: str
        :param pip_requirements_file: A string representing the relative path to the pip requirements text file.
            This can be provided in combination with the ``pip_packages`` parameter.
        :type pip_requirements_file: str
        :param environment_variables: A dictionary of environment variables names and values.
            These environment variables are set on the process where user script is being executed.
        :type environment_variables: dict
        :param environment_definition: The environment definition for an experiment includes
            PythonSection, DockerSection, and environment variables. Any environment option not directly exposed
            through other parameters to the Estimator construction can be set using ``environment_definition``
            parameter. If this parameter is specified, it will take precedence over other environment related
            parameters like ``use_gpu``, ``custom_docker_image``, ``conda_packages``, or ``pip_packages``.
            Errors will be reported invalid combinations.
        :type environment_definition: azureml.core.Environment
        :param inputs: A list of azureml.data.data_reference.DataReference objects to use as input.
        :type inputs: list
        :param shm_size: The size of the Docker container's shared memory block. If not set, the default
            azureml.core.environment._DEFAULT_SHM_SIZE is used.
        :type shm_size: str
        :param resume_from: The data path containing the checkpoint or model files from which to resume the experiment.
        :type resume_from: azureml.data.datapath.DataPath
        :param max_run_duration_seconds: The maximum allowed time for the run. Azure ML will attempt to automatically
            cancel the run if it takes longer than this value.
        :type max_run_duration_seconds: int
        :param framework_version: The Scikit-learn version to be used for executing training code.
            ``SKLearn.get_supported_versions()`` returns a list of the versions supported by the current SDK.
        :type framework_version: str
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
        module_logger.warning("'SKLearn' estimator is deprecated. Please use 'ScriptRunConfig' from "
                              "'azureml.core.script_run_config' with your own "
                              "defined environment or the AzureML-Tutorial curated environment.")

        super().__init__(source_directory, compute_target=compute_target, vm_size=vm_size,
                         vm_priority=vm_priority, entry_script=entry_script,
                         script_params=script_params, node_count=1,
                         process_count_per_node=1,
                         distributed_backend=None, distributed_training=None,
                         use_gpu=False, use_docker=use_docker, custom_docker_image=custom_docker_image,
                         image_registry_details=image_registry_details,
                         user_managed=user_managed, conda_packages=conda_packages,
                         pip_packages=pip_packages,
                         conda_dependencies_file_path=conda_dependencies_file_path,
                         pip_requirements_file_path=pip_requirements_file_path,
                         conda_dependencies_file=conda_dependencies_file,
                         pip_requirements_file=pip_requirements_file,
                         environment_variables=environment_variables,
                         environment_definition=environment_definition, inputs=inputs,
                         source_directory_data_store=None,
                         shm_size=shm_size, resume_from=resume_from,
                         max_run_duration_seconds=max_run_duration_seconds,
                         framework_name=self.FRAMEWORK_NAME,
                         framework_version=framework_version,
                         _enable_optimized_mode=_enable_optimized_mode,
                         _disable_validation=_disable_validation,
                         _show_lint_warnings=_show_lint_warnings,
                         _show_package_warnings=_show_package_warnings)
