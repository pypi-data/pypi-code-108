# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains functionality to add a Azure ML Pipeline step to run an MPI job for Machine Learning model training."""
from azureml.core.compute import AmlCompute, KubernetesCompute
from azureml.pipeline.steps import PythonScriptStep
from azureml.pipeline.core import PipelineStep
from azureml.pipeline.core.graph import PipelineParameter
from azureml.core.compute_target import _BatchAITarget
import logging

module_logger = logging.getLogger(__name__)


class MpiStep(PythonScriptStep):
    r"""Creates an Azure ML pipeline step to run an MPI job.

    For an example of using MpiStep, see the notebook https://aka.ms/pl-style-trans.

    :param name: [Required] The name of the module.
    :type name: str
    :param source_directory: [Required] A folder that contains Python script, conda env, and other
        resources used in the step.
    :type source_directory: str
    :param script_name: [Required] The name of a Python script relative to ``source_directory``.
    :type script_name: str
    :param arguments: [Required] A list of command-line arguments.
    :type arguments: list
    :param compute_target: [Required] A compute target to use.
    :type compute_target: azureml.core.compute.AmlCompute, str
    :param node_count: [Required] The number of nodes in the compute target used for training.
        If greater than 1, an mpi distributed job will be run. Only AmlCompute compute target is
        supported for distributed jobs. PipelineParameter values are supported.
    :type node_count: int
    :param process_count_per_node: [Required] The number of processes per node. If greater than 1, an mpi
             distributed job will be run. Only AmlCompute compute target is supported for distributed jobs.
             PipelineParameter values are supported.
    :type process_count_per_node: int
    :param inputs: A list of input port bindings.
    :type inputs: list[typing.Union[azureml.pipeline.core.graph.InputPortBinding,
                    azureml.data.data_reference.DataReference,
                    azureml.pipeline.core.PortDataReference,
                    azureml.pipeline.core.builder.PipelineData,
                    azureml.pipeline.core.pipeline_output_dataset.PipelineOutputAbstractDataset,
                    azureml.data.dataset_consumption_config.DatasetConsumptionConfig]]
    :param outputs: A list of output port bindings.
    :type outputs: list[typing.Union[azureml.pipeline.core.builder.PipelineData,
                    azureml.pipeline.core.pipeline_output_dataset.PipelineOutputAbstractDataset,
                    azureml.pipeline.core.graph.OutputPortBinding]]
    :param params: A dictionary of name-value pairs registered as environment variables with "AML_PARAMETER\_".
    :type params: dict
    :param allow_reuse: Indicates whether the step should reuse previous results when re-run with the same
        settings. Reuse is enabled by default. If the step contents (scripts/dependencies) as well as inputs and
        parameters remain unchanged, the output from the previous run of this step is reused. When reusing
        the step, instead of submitting the job to compute, the results from the previous run are immediately
        made available to any subsequent steps. If you use Azure Machine Learning datasets as inputs, reuse is
        determined by whether the dataset's definition has changed, not by whether the underlying data has
        changed.
    :type allow_reuse: bool
    :param version: An optional version tag to denote a change in functionality for the module.
    :type version: str
    :param hash_paths: DEPRECATED: no longer needed.

        A list of paths to hash when checking for changes to the step contents. If there
        are no changes detected, the pipeline will reuse the step contents from a previous run. By default,
        the contents of ``source_directory`` is hashed except for files listed in .amlignore or .gitignore.
    :type hash_paths: list
    :param use_gpu: Indicates whether the environment to run the experiment should support GPUs.
        If True, a GPU-based default Docker image will be used in the environment. If False, a CPU-based
        image will be used. Default docker images (CPU or GPU) will be used only if the ``custom_docker_image``
        parameter is not set. This setting is used only in Docker-enabled compute targets.
    :type use_gpu: bool
    :param use_docker: Indicates whether the environment to run the experiment should be Docker-based.
    :type use_docker: bool
    :param custom_docker_image: The name of the Docker image from which the image to use for training
            will be built. If not set, a default CPU-based image will be used as the base image.
    :type custom_docker_image: str
    :param image_registry_details: The details of the Docker image registry.
    :type image_registry_details: azureml.core.container_registry.ContainerRegistry
    :param user_managed: Indicates whether Azure ML reuses an existing Python environment; False means
            that Azure ML will create a Python environment based on the conda dependencies specification.
    :type user_managed: bool
    :param conda_packages: A list of strings representing conda packages to be added to the Python environment.
    :type conda_packages: list
    :param pip_packages: A list of strings representing pip packages to be added to the Python environment.
    :type pip_packages: list
    :param pip_requirements_file_path: The relative path to the pip requirements text file.
        This parameter can be specified in combination with the ``pip_packages`` parameter.
    :type pip_requirements_file_path: str
    :param environment_definition: The EnvironmentDefinition for the experiment. It includes
        PythonSection and DockerSection and environment variables. Any environment option not directly
        exposed through other parameters to the MpiStep construction can be set using environment_definition
        parameter. If this parameter is specified, it will take precedence over other environment related
        parameters like use_gpu, custom_docker_image, conda_packages or pip_packages and errors will be
        reported on these invalid combinations.
    :type environment_definition: azureml.core.runconfig.EnvironmentDefinition
    """

    def __init__(self, name=None, source_directory=None, script_name=None, arguments=None, compute_target=None,
                 node_count=None, process_count_per_node=None, inputs=None, outputs=None,
                 allow_reuse=True, version=None, hash_paths=None, **kwargs):
        """Create an Azure ML pipeline step to run an MPI job.

        DEPRECATED. Use the :class:`azureml.pipeline.steps.CommandStep` instead. For an example see `How to run
        distributed training in pipelines with CommandStep <https://github.com/Azure/MachineLearningNotebooks/blob/
        master/how-to-use-azureml/machine-learning-pipelines/intro-to-pipelines/aml-pipelines-with-commandstep.ipynb>`_.

        :param name: [Required] The name of the module.
        :type name: str
        :param source_directory: [Required] A folder that contains Python script, conda env, and other
            resources used in the step.
        :type source_directory: str
        :param script_name: [Required] The name of a Python script relative to ``source_directory``.
        :type script_name: str
        :param arguments: [Required] A list of command-line arguments.
        :type arguments: list
        :param compute_target: [Required] A compute target to use.
        :type compute_target: azureml.core.compute.AmlComputeCompute, str
        :param node_count: [Required] Number of nodes in the compute target used for training. If greater than 1, mpi
               distributed job will be run. Only AmlCompute compute target is supported for distributed jobs.
               PipelineParameter values are supported.
        :type node_count: int
        :param process_count_per_node: [Required] Number of processes per node. If greater than 1, mpi
                 distributed job will be run. Only AmlCompute compute target is supported for distributed jobs.
                 PipelineParameter values are supported.
        :type process_count_per_node: int
        :param inputs: A list of input port bindings.
        :type inputs: list[typing.Union[azureml.pipeline.core.graph.InputPortBinding,
                        azureml.data.data_reference.DataReference,
                        azureml.pipeline.core.PortDataReference,
                        azureml.pipeline.core.builder.PipelineData,
                        azureml.pipeline.core.pipeline_output_dataset.PipelineOutputAbstractDataset,
                        azureml.data.dataset_consumption_config.DatasetConsumptionConfig]]
        :param outputs: A list of output port bindings.
        :type outputs: list[typing.Union[azureml.pipeline.core.builder.PipelineData,
                        azureml.data.output_dataset_config.OutputDatasetConfig,
                        azureml.pipeline.core.pipeline_output_dataset.PipelineOutputAbstractDataset,
                        azureml.pipeline.core.graph.OutputPortBinding]]
        :param params: A dictionary of name-value pairs registered as environment variables with "AML_PARAMETER_".
        :type params: dict
        :param allow_reuse: Indicates Whether the step should reuse previous results when re-run with the same
            parameters remain unchanged, the output from the previous run of this step is reused. When reusing
            the step, instead of submitting the job to compute, the results from the previous run are immediately
            made available to any subsequent steps. If you use Azure Machine Learning datasets as inputs, reuse is
            determined by whether the dataset's definition has changed, not by whether the underlying data has
            changed.
        :type allow_reuse: bool
        :param version: Optional version tag to denote a change in functionality for the module
        :type version: str
        :param hash_paths: DEPRECATED: no longer needed.

            A list of paths to hash when checking for changes to the step contents. If there
            are no changes detected, the pipeline will reuse the step contents from a previous run. By default,
            the contents of ``source_directory`` is hashed except for files listed in .amlignore or .gitignore.
        :type hash_paths: list
        :param use_gpu: Indicates whether the environment to run the experiment should support GPUs.
            If True, a GPU-based default Docker image will be used in the environment. If False, a CPU-based
            image will be used. Default docker images (CPU or GPU) will be used only if the ``custom_docker_image``
            parameter is not set. This setting is used only in Docker-enabled compute targets.
        :type use_gpu: bool
        :param use_docker: Indicates whether the environment to run the experiment should be Docker-based.
            custom_docker_image (str): The name of the docker image from which the image to use for mpi job
            will be built. If not set, a default CPU based image will be used as the base image.
        :type use_docker: bool
        :param custom_docker_image: The name of the Docker image from which the image to use for training
            will be built. If not set, a default CPU-based image will be used as the base image.
        :type custom_docker_image: str
        :param image_registry_details: The details of the Docker image registry.
        :type image_registry_details: azureml.core.container_registry.ContainerRegistry
        :param user_managed: Indicates whether Azure ML reuses an existing Python environment; False means
            that Azure ML will create a Python environment based on the conda dependencies specification.
        :type user_managed: bool
        :param conda_packages: A list of strings representing conda packages to be added to the Python environment.
        :type conda_packages: list
        :param pip_packages: A list of strings representing pip packages to be added to the Python environment.
        :type pip_packages: list
        :param pip_requirements_file_path: The relative path to the pip requirements text file.
            This parameter can be specified in combination with the ``pip_packages`` parameter.
        :type pip_requirements_file_path: str
        :param environment_definition: The EnvironmentDefinition for the experiment. It includes
            PythonSection and DockerSection and environment variables. Any environment option not directly
            exposed through other parameters to the MpiStep construction can be set using environment_definition
            parameter. If this parameter is specified, it will take precedence over other environment related
            parameters like use_gpu, custom_docker_image, conda_packages or pip_packages and errors will be
            reported on these invalid combinations.
        :type environment_definition: azureml.core.runconfig.EnvironmentDefinition
        """
        module_logger.warning("'MpiStep' is deprecated. Please use 'CommandStep' from "
                              "'azureml.pipeline.steps.CommandStep' instead. For an example see "
                              "https://github.com/Azure/MachineLearningNotebooks/blob/master/how-to-use-azureml/"
                              "machine-learning-pipelines/intro-to-pipelines/aml-pipelines-with-commandstep.ipynb.")
        environment_variables = kwargs.get("environment_variables", None)
        use_gpu = kwargs.get("use_gpu", False)
        use_docker = kwargs.get("use_docker", True)
        custom_docker_image = kwargs.get("custom_docker_image", None)
        image_registry_details = kwargs.get("image_registry_details", None)
        user_managed = kwargs.get("user_managed", False)
        conda_packages = kwargs.get("conda_packages", None)
        pip_packages = kwargs.get("pip_packages", None)
        pip_requirements_file_path = kwargs.get("pip_requirements_file_path", None)
        environment_definition = kwargs.get("environment_definition", None)

        if None in [name, source_directory, script_name, arguments, compute_target, node_count,
                    process_count_per_node]:
            raise ValueError('One of the requirement parameters (name, source_directory, script_name, '
                             'arguments, compute_target, node_count, process_count_per_node) is not set')

        PipelineStep._process_pipeline_io(arguments, inputs, outputs)

        runconfig_pipeline_params = {}
        if isinstance(node_count, PipelineParameter):
            runconfig_pipeline_params['NodeCount'] = node_count
            node_count = node_count.default_value

        if isinstance(process_count_per_node, PipelineParameter):
            runconfig_pipeline_params['MpiProcessCountPerNode'] = process_count_per_node
            process_count_per_node = process_count_per_node.default_value

        # use Estimator to construct run config for mpi job
        # not setting script_params because arguments passed to PythonScriptStep will override what is in runconfig
        from azureml.train.estimator import Estimator
        mpi_estimator = Estimator(source_directory=source_directory, compute_target=compute_target,
                                  entry_script=script_name,
                                  script_params={}, node_count=node_count,
                                  distributed_backend='mpi', process_count_per_node=process_count_per_node,
                                  use_gpu=use_gpu, use_docker=use_docker,
                                  custom_docker_image=custom_docker_image,
                                  image_registry_details=image_registry_details,
                                  user_managed=user_managed,
                                  conda_packages=conda_packages, pip_packages=pip_packages,
                                  pip_requirements_file_path=pip_requirements_file_path,
                                  environment_definition=environment_definition)
        mpi_run_config = mpi_estimator.run_config
        if not (compute_target.type.lower() == _BatchAITarget._BATCH_AI_TYPE.lower()
                or compute_target.type.lower() == AmlCompute._compute_type.lower()
                or compute_target.type.lower() == KubernetesCompute._compute_type.lower()):
            raise Exception("Compute compute_target {0} is not supported in MpiStep. "
                            "AmlCompute and KubernetesCompute are the only supported compute_targets."
                            .format(compute_target, ))

        super(self.__class__, self).__init__(name=name, source_directory=source_directory, script_name=script_name,
                                             arguments=arguments, runconfig=mpi_run_config,
                                             runconfig_pipeline_params=runconfig_pipeline_params,
                                             params=environment_variables,
                                             compute_target=compute_target, inputs=inputs, outputs=outputs,
                                             allow_reuse=allow_reuse, version=version, hash_paths=hash_paths)
