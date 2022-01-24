# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains functionality to create an Azure ML Pipeline step that runs R script."""
from azureml._base_sdk_common._docstring_wrapper import experimental
from azureml.pipeline.core._python_script_step_base import _PythonScriptStepBase
from azureml.core.environment import DEFAULT_CPU_IMAGE
import logging

R_DEFAULT_IMAGE_FOR_GPU = 'mcr.microsoft.com/azureml/base-gpu:openmpi3.1.2-cuda10.0-cudnn7-ubuntu16.04'
R_DEFAULT_IMAGE_FOR_CPU = 'mcr.microsoft.com/azureml/base:openmpi3.1.2-ubuntu16.04'
module_logger = logging.getLogger(__name__)


@experimental
class RScriptStep(_PythonScriptStepBase):
    r"""Creates an Azure ML Pipeline step that runs R script.

    .. remarks::

        An RScriptStep is a basic, built-in step to run R script on a compute target. It takes
        a script name and other optional parameters like arguments for the script, compute target, inputs
        and outputs. You should use a :class:`azureml.core.RunConfiguration` to specify requirements for the
        RScriptStep, such as custom docker image, required cran/github packages.

        The best practice for working with RScriptStep is to use a separate folder for scripts and any dependent
        files associated with the step, and specify that folder with the ``source_directory`` parameter.
        Following this best practice has two benefits. First, it helps reduce the size of the snapshot
        created for the step because only what is needed for the step is snapshotted. Second, the step's output
        from a previous run can be reused if there are  no changes to the ``source_directory`` that would trigger
        a re-upload of the snapshot.

        The following code example shows how to use a RScriptStep in a machine learning training scenario.

        .. code-block:: python

            from azureml.core.runconfig import RunConfiguration
            from azureml.core.environment import Environment, RSection, RCranPackage
            from azureml.pipeline.steps import RScriptStep

            rc = RunConfiguration()
            rc.framework='R'
            rc.environment.r = RSection()                            # R details with required packages
            rc.environment.docker.enabled = True                     # to enable docker image
            rc.environment.docker.base_image = '<custom user image>' # to use custom image

            cran_package1 = RCranPackage()
            cran_package1.name = "ggplot2"
            cran_package1.repository = "www.customurl.com"
            cran_package1.version = "2.1"
            rc.environment.r.cran_packages = [cran_package1]

            trainStep = RScriptStep(script_name="train.R",
                                    arguments=["--input", blob_input_data, "--output", output_data1],
                                    inputs=[blob_input_data],
                                    outputs=[output_data1],
                                    compute_target=compute_target,
                                    use_gpu=False,
                                    runconfig=rc,
                                    source_directory=project_folder)

        See https://aka.ms/pl-first-pipeline
        for more details on creating pipelines in general.
        See https://docs.microsoft.com/en-us/python/api/azureml-core/azureml.core.environment.rsection
        for more details on RSection.

    :param script_name: [Required] The name of a R script relative to ``source_directory``.
    :type script_name: str
    :param name: The name of the step. If unspecified, ``script_name`` is used.
    :type name: str
    :param arguments: Command line arguments for the R script file. The arguments will be passed
                      to compute via the ``arguments`` parameter in RunConfiguration.
                      For more details how to handle arguments such as special symbols, see
                      the :class:`azureml.core.RunConfiguration`.
    :type arguments: list
    :param compute_target: [Required] The compute target to use. If unspecified, the target from
        the ``runconfig`` is used. This parameter may be specified as
        a compute target object or the string name of a compute target on the workspace.
        Optionally if the compute target is not available at pipeline creation time, you may specify a tuple of
        ('compute target name', 'compute target type') to avoid fetching the compute target object (AmlCompute
        type is 'AmlCompute' and RemoteCompute type is 'VirtualMachine').
    :type compute_target: typing.Union[azureml.core.compute.DsvmCompute,
                        azureml.core.compute.AmlCompute,
                        azureml.core.compute.RemoteCompute,
                        azureml.core.compute.HDInsightCompute,
                        str,
                        tuple]
    :param runconfig: [Required] Run configuration which encapsulates the information necessary to submit
        a training run in an experiment. This is required to define R run configs which can be defined in
        :class:`azureml.core.environment.RSection`. The RSection is required for this step.
    :type runconfig: azureml.core.runconfig.RunConfiguration
    :param runconfig_pipeline_params: Overrides of runconfig properties at runtime using key-value pairs
                    each with name of the runconfig property and PipelineParameter for that property.

        Supported values: 'NodeCount', 'MpiProcessCountPerNode', 'TensorflowWorkerCount',
        'TensorflowParameterServerCount'

    :type runconfig_pipeline_params: dict[str, azureml.pipeline.core.graph.PipelineParameter]
    :param inputs: A list of input port bindings.
    :type inputs: list[typing.Union[azureml.pipeline.core.graph.InputPortBinding,
                    azureml.data.data_reference.DataReference,
                    azureml.pipeline.core.PortDataReference,
                    azureml.pipeline.core.builder.PipelineData,
                    azureml.pipeline.core.pipeline_output_dataset.PipelineOutputFileDataset,
                    azureml.pipeline.core.pipeline_output_dataset.PipelineOutputTabularDataset,
                    azureml.data.dataset_consumption_config.DatasetConsumptionConfig]]
    :param outputs: A list of output port bindings.
    :type outputs: list[typing.Union[azureml.pipeline.core.builder.PipelineData,
                        azureml.data.output_dataset_config.OutputDatasetConfig,
                        azureml.pipeline.core.pipeline_output_dataset.PipelineOutputAbstractDataset,
                        azureml.pipeline.core.graph.OutputPortBinding]]
    :param params: A dictionary of name-value pairs registered as environment variables with "AML_PARAMETER\_".
    :type params: dict
    :param source_directory: A folder that contains R script, conda env, and other resources used in
        the step.
    :type source_directory: str
    :param use_gpu: Indicates whether the environment to run the experiment should support GPUs.
        If True, a GPU-based default Docker image will be used in the environment. If False, a CPU-based
        image will be used. Default docker images (CPU or GPU) will be used only if a user doesn't set
        both ``base_image`` and ``base_dockerfile`` parameters.
        This setting is used only in Docker-enabled compute targets.
        See https://docs.microsoft.com/en-us/python/api/azureml-core/azureml.core.environment.dockersection
        for more details on ``base_image``.
    :type use_gpu: bool
    :param custom_docker_image: The name of the Docker image from which the image to use for training
        will be built. If not set, a default CPU-based image will be used as the base image.
        This has been deprecated and will be removed in a future release.
        Please use base_image in the DockerSection instead.
    :type custom_docker_image: str
    :param cran_packages: CRAN packages to be installed.
        This has been deprecated and will be removed in a future release.
        Please use RSection.cran_packages instead.
    :type cran_packages: list
    :param github_packages: GitHub packages to be installed.
        This has been deprecated and will be removed in a future release.
        Please use RSection.github_packages instead.
    :type github_packages: list
    :param custom_url_packages: Packages to be installed from local, directory or custom URL.
        This has been deprecated and will be removed in a future release.
        Please use RSection.custom_url_packages instead.
    :type custom_url_packages: list
    :param allow_reuse: Indicates whether the step should reuse previous results when re-run with the same
        settings. Reuse is enabled by default. If the step contents (scripts/dependencies) as well as inputs and
        parameters remain unchanged, the output from the previous run of this step is reused. When reusing
        the step, instead of submitting the job to compute, the results from the previous run are immediately
        made available to any subsequent steps. If you use Azure Machine Learning datasets as inputs, reuse is
        determined by whether the dataset's definition has changed, not by whether the underlying data has
        changed.
    :type allow_reuse: bool
    :param version: An optional version tag to denote a change in functionality for the step.
    :type version: str
    """

    def __init__(self, script_name, name=None, arguments=None, compute_target=None, runconfig=None,
                 runconfig_pipeline_params=None, inputs=None, outputs=None, params=None, source_directory=None,
                 use_gpu=False, custom_docker_image=None, cran_packages=None, github_packages=None,
                 custom_url_packages=None, allow_reuse=True, version=None):
        r"""Create an Azure ML Pipeline step that runs R script.

        DEPRECATED. Use the :class:`azureml.pipeline.steps.CommandStep` instead. For an example see
        `How to run R scripts in pipelines with CommandStep
        <https://github.com/Azure/MachineLearningNotebooks/blob/master/how-to-use-azureml/machine-learning-pipelines/
        intro-to-pipelines/aml-pipelines-with-commandstep-r.ipynb>`_.

        :param script_name: [Required] The name of a R script relative to ``source_directory``.
        :type script_name: str
        :param name: The name of the step. If unspecified, ``script_name`` is used.
        :type name: str
        :param arguments: Command line arguments for the R script file. The arguments will be passed
                          to compute via the ``arguments`` parameter in RunConfiguration.
                          For more details how to handle arguments such as special symbols, see
                          the :class:`azureml.core.RunConfiguration`.
        :type arguments: list
        :param compute_target: [Required] The compute target to use. If unspecified, the target from
            the ``runconfig`` will be used. This parameter may be specified as
            a compute target object or the string name of a compute target on the workspace.
            Optionally if the compute target is not available at pipeline creation time, you may specify a tuple of
            ('compute target name', 'compute target type') to avoid fetching the compute target object (AmlCompute
            type is 'AmlCompute' and RemoteCompute type is 'VirtualMachine').
        :type compute_target: typing.Union[azureml.core.compute.DsvmCompute,
                            azureml.core.compute.AmlCompute,
                            azureml.core.compute.RemoteCompute,
                            azureml.core.compute.HDInsightCompute,
                            str,
                            tuple]
        :param runconfig: [Required] Run configuration which encapsulates the information necessary to submit
            a training run in an experiment. This is required to define R run configs which can be defined in
            :class:`azureml.core.environment.RSection`. The RSection is required for this step.
        :type runconfig: azureml.core.runconfig.RunConfiguration
        :param runconfig_pipeline_params: Overrides of runconfig properties at runtime using key-value pairs
                        each with name of the runconfig property and PipelineParameter for that property.

            Supported values: 'NodeCount', 'MpiProcessCountPerNode', 'TensorflowWorkerCount',
                              'TensorflowParameterServerCount'

        :type runconfig_pipeline_params: dict[str, azureml.pipeline.core.graph.PipelineParameter]
        :param inputs: A list of input port bindings.
        :type inputs: list[typing.Union[azureml.pipeline.core.graph.InputPortBinding,
                        azureml.data.data_reference.DataReference,
                        azureml.pipeline.core.PortDataReference,
                        azureml.pipeline.core.builder.PipelineData,
                        azureml.pipeline.core.pipeline_output_dataset.PipelineOutputFileDataset,
                        azureml.pipeline.core.pipeline_output_dataset.PipelineOutputTabularDataset,
                        azureml.data.dataset_consumption_config.DatasetConsumptionConfig]]
        :param outputs: A list of output port bindings.
        :type outputs: list[typing.Union[azureml.pipeline.core.builder.PipelineData,
                            azureml.pipeline.core.pipeline_output_dataset.PipelineOutputAbstractDataset,
                            azureml.pipeline.core.graph.OutputPortBinding]]
        :param params: A dictionary of name-value pairs registered as environment variables with "AML_PARAMETER\_".
        :type params: dict
        :param source_directory: A folder that contains R script, conda env, and other resources used in
            the step.
        :type source_directory: str
        :param use_gpu: Indicates whether the environment to run the experiment should support GPUs.
            If True, a GPU-based default Docker image will be used in the environment. If False, a CPU-based
            image will be used. Default docker images (CPU or GPU) will be used only if a user doesn't set
            both ``base_image`` and ``base_dockerfile`` parameters.
            This setting is used only in Docker-enabled compute targets.
            See https://docs.microsoft.com/en-us/python/api/azureml-core/azureml.core.environment.dockersection
            for more details on ``base_image``.
        :type use_gpu: bool
        :param custom_docker_image: The name of the Docker image from which the image to use for training
            will be built. If not set, a default CPU-based image will be used as the base image.
            This has been deprecated and will be removed in a future release.
            Please use base_image in the DockerSection instead.
        :type custom_docker_image: str
        :param cran_packages: CRAN packages to be installed.
            This has been deprecated and will be removed in a future release.
            Please use RSection.cran_packages instead.
        :type cran_packages: list
        :param github_packages: GitHub packages to be installed.
            This has been deprecated and will be removed in a future release.
            Please use RSection.github_packages instead.
        :type github_packages: list
        :param custom_url_packages: Packages to be installed from local, directory or custom URL.
            This has been deprecated and will be removed in a future release.
            Please use RSection.custom_url_packages instead.
        :type custom_url_packages: list
        :param allow_reuse: Indicates whether the step should reuse previous results when re-run with the same
            settings. Reuse is enabled by default. If the step contents (scripts/dependencies) as well as inputs and
            parameters remain unchanged, the output from the previous run of this step is reused. When reusing
            the step, instead of submitting the job to compute, the results from the previous run are immediately
            made available to any subsequent steps. If you use Azure Machine Learning datasets as inputs, reuse is
            determined by whether the dataset's definition has changed, not by whether the underlying data has
            changed.
        :type allow_reuse: bool
        :param version: An optional version tag to denote a change in functionality for the step.
        :type version: str
        """
        module_logger.warning("'RScriptStep' is deprecated. Please use 'CommandStep' from "
                              "'azureml.pipeline.steps.CommandStep' instead. For an example see "
                              "https://github.com/Azure/MachineLearningNotebooks/blob/master/how-to-use-azureml/"
                              "machine-learning-pipelines/intro-to-pipelines/aml-pipelines-with-commandstep-r.ipynb.")

        if custom_docker_image is not None:
            logging.warning("'custom_docker_image' parameter is deprecated. Please use 'base_image' "
                            "from 'azureml.core.environment.DockerSection' instead.")

        if cran_packages is not None:
            logging.warning("'cran_packages' parameter is deprecated. Please use 'cran_packages' "
                            "from 'azureml.core.environment.RSection' instead.")

        if github_packages is not None:
            logging.warning("'github_packages' parameter is deprecated. Please use 'github_packages' "
                            "from 'azureml.core.environment.RSection' instead.")

        if custom_url_packages is not None:
            logging.warning("'custom_url_packages' parameter is deprecated. Please use 'custom_url_packages' "
                            "from 'azureml.core.environment.RSection' instead.")

        self._validate_and_process_config(runconfig, use_gpu)

        runconfig.script = script_name
        runconfig.target = compute_target

        super(RScriptStep, self).__init__(
            script_name=script_name, name=name, arguments=arguments, compute_target=compute_target,
            runconfig=runconfig, runconfig_pipeline_params=runconfig_pipeline_params, inputs=inputs, outputs=outputs,
            params=params, source_directory=source_directory, allow_reuse=allow_reuse, version=version)

    @staticmethod
    def _validate_and_process_config(runconfig, use_gpu):
        if runconfig.environment.r is None:
            raise ValueError("RunConfiguration.Environment.RSection is required for r script.")

        if not runconfig.environment.docker.enabled:
            raise ValueError("Environment.DockerSection.enabled needs to be set True for r script.")

        base_image = runconfig.environment.docker.base_image
        base_dockerfile = runconfig.environment.docker.base_dockerfile
        if (not base_image and not base_dockerfile) or \
                base_image in [DEFAULT_CPU_IMAGE, R_DEFAULT_IMAGE_FOR_CPU, R_DEFAULT_IMAGE_FOR_GPU]:
            if use_gpu:
                runconfig.environment.docker.base_image = R_DEFAULT_IMAGE_FOR_GPU
            else:
                runconfig.environment.docker.base_image = R_DEFAULT_IMAGE_FOR_CPU
            print('Default docker image will be used:', runconfig.environment.docker.base_image)
        else:
            if not runconfig.environment.r.user_managed:
                raise ValueError("RSection.user_managed should be true when custom image is used.")
            if not runconfig.environment.python.user_managed_dependencies:
                runconfig.environment.python.user_managed_dependencies = True

    def create_node(self, graph, default_datastore, context):
        """Create a node for RScriptStep and add it to the specified graph.

        DEPRECATED. Use the :class:`azureml.pipeline.steps.CommandStep` instead. For an example see
        `How to run R scripts in pipelines with CommandStep
        <https://github.com/Azure/MachineLearningNotebooks/blob/master/how-to-use-azureml/machine-learning-pipelines/
        intro-to-pipelines/aml-pipelines-with-commandstep-r.ipynb>`_.

        This method is not intended to be used directly. When a pipeline is instantiated with this step,
        Azure ML automatically passes the parameters required through this method so that step can be added to a
        pipeline graph that represents the workflow.

        :param graph: The graph object to add the node to.
        :type graph: azureml.pipeline.core.graph.Graph
        :param default_datastore: The default datastore.
        :type default_datastore:  typing.Union[azureml.data.azure_storage_datastore.AbstractAzureStorageDatastore,
                                azureml.data.azure_data_lake_datastore.AzureDataLakeDatastore]
        :param context: The graph context.
        :type context: azureml.pipeline.core._GraphContext

        :return: The created node.
        :rtype: azureml.pipeline.core.graph.Node
        """
        module_logger.warning("'RScriptStep' is deprecated. Please use 'CommandStep' from "
                              "'azureml.pipeline.steps.CommandStep' instead. For an example see "
                              "https://github.com/Azure/MachineLearningNotebooks/blob/master/how-to-use-azureml/"
                              "machine-learning-pipelines/intro-to-pipelines/aml-pipelines-with-commandstep-r.ipynb.")

        return super(RScriptStep, self).create_node(
            graph=graph, default_datastore=default_datastore, context=context)
