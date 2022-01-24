# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""The Reinforcement Learning estimator class."""

from azureml.core._experiment_method import experiment_method

from azureml.contrib.train.rl._rl_base_estimator import _RLBaseEstimator, _rl_estimator_submit_method
from azureml.contrib.train.rl._rl_framework import Ray
from azureml.train._estimator_helper import _create_conda_dependencies


class ReinforcementLearningEstimator(_RLBaseEstimator):
    """ Represents an estimator for training Reinforcement Learning experiments.

    .. remarks::

            When submitting a training job, Azure ML runs your script in a conda environment within
            a Docker container. The Reinforcement Learning containers have the following dependencies
            installed.

            | Dependencies | Ray 0.8.0 | Ray 0.8.3 |
            | --------------------------------------| ----------------- | ----------------- |
            | Python                                | 3.6.2             | 3.6.2             |
            | CUDA  (GPU image only)                | 10.0              | 10.0              |
            | cuDNN (GPU image only)                | 7.5               | 7.5               |
            | NCCL  (GPU image only)                | 2.4.2             | 2.4.2             |
            | azureml-defaults                      | Latest            | Latest            |
            | azureml-contrib-reinforcementlearning | Latest            | Latest            |
            | ray[rllib,dashboard]                  | 0.8.0             | 0.8.3             |
            | tensorflow                            | 1.14.0            | 1.14.0            |
            | psutil                                | Latest            | Latest            |
            | setproctitle                          | Latest            | Latest            |
            | gym[atari]                            | Latest            | Latest            |


            The Docker images extend Ubuntu 16.04.

            To install additional dependencies in the head docker container, you can either use
            the ``pip_packages`` or ``conda_packages``. Alternatively, you can build your own image, and pass
            it in the environment parameter as part of an Environment object.

            The Reinforcement Learning estimator supports distributed training across CPU and GPU clusters using
            `Ray <https://github.com/ray-project/ray>`_, an open-source framework for handling distributed training.

    :param source_directory: A local directory containing experiment configuration files.
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
        compute target name. AmlWindowsCompute supports only Azure Files as mounted storage and does not support
        environment definition.
    :type compute_target: azureml.core.compute_target.AbstractComputeTarget or str
    :param use_gpu: Specifies whether the environment should support GPUs.
        If true, a GPU-based default Docker image will be used in the environment. If false, a CPU-based
        image will be used. Default docker images (CPU or GPU) will be used only if the ``environment``
        parameter is not set.
    :type use_gpu: bool
    :param conda_packages: A list of strings representing conda packages to be added to the head's Python
        environment for the experiment.
    :type conda_packages: list
    :param pip_packages: A list of strings representing pip packages to be added to the head's Python environment
        for the experiment.
    :type pip_packages: list
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
    :param pip_requirements_file: The relative path to the head's pip requirements text file.
        This can be provided in combination with the ``pip_packages`` parameter.
    :type pip_requirements_file: str
    :param conda_dependencies_file: The relative path to the head's conda dependencies
        yaml file.
    :type conda_dependencies_file: str
    :param environment_variables: A dictionary of environment variables names and values.
        These environment variables are set on the head process, where the ``entry_script`` being executed.
    :type environment_variables: dict
    :param shm_size: The size of the Docker container's shared memory block. If not set, the default
        azureml.core.environment._DEFAULT_SHM_SIZE is used. For more information, see
        `Docker run reference <https://docs.docker.com/engine/reference/run/>`_.
    :type shm_size: str
    :param inputs: A list of :class:`azureml.data.data_reference.DataReference` or
        :class:`azureml.data.dataset_consumption_config.DatasetConsumptionConfig` objects to use as input.
    :type inputs: list
    """
    DEFAULT_FRAMEWORK = Ray()

    @experiment_method(submit_function=_rl_estimator_submit_method)
    def __init__(self,
                 source_directory,
                 *,
                 environment=None,
                 entry_script=None,
                 script_params=None,
                 compute_target=None,
                 use_gpu=None,
                 pip_packages=None,
                 conda_packages=None,
                 environment_variables=None,
                 rl_framework=DEFAULT_FRAMEWORK,
                 cluster_coordination_timeout_seconds=None,
                 max_run_duration_seconds=None,
                 worker_configuration=None,
                 conda_dependencies_file=None,
                 pip_requirements_file=None,
                 shm_size=None,
                 inputs=None):
        conda_dependencies = None
        if pip_packages or pip_requirements_file \
                or conda_packages or conda_dependencies_file:
            conda_dependencies = _create_conda_dependencies(source_directory=source_directory,
                                                            pip_packages=pip_packages,
                                                            pip_requirements_file=pip_requirements_file,
                                                            conda_packages=conda_packages,
                                                            conda_dependencies_file=conda_dependencies_file)

        super().__init__(source_directory, environment=environment, use_gpu=use_gpu,
                         entry_script=entry_script, script_params=script_params,
                         conda_dependencies=conda_dependencies,
                         compute_target=compute_target, rl_framework=rl_framework,
                         worker_configuration=worker_configuration,
                         max_run_duration_seconds=max_run_duration_seconds,
                         cluster_coordination_timeout_seconds=cluster_coordination_timeout_seconds,
                         environment_variables=environment_variables, shm_size=shm_size, inputs=inputs)

    def _get_telemetry_values(self, func):
        telemetry_values = super()._get_telemetry_values(func)
        # TODO define telemetry to be logged
        return telemetry_values
