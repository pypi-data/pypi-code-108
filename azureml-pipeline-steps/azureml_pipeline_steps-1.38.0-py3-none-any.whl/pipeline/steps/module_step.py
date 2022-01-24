# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains functionality to add an Azure Machine Learning Pipeline step using an existing version of a Module."""
from azureml.pipeline.core.module_step_base import ModuleStepBase


class ModuleStep(ModuleStepBase):
    """Creates an Azure Machine Learning pipeline step to run a specific version of a Module.

    :class:`azureml.pipeline.core.Module` objects define reusable computations, such as scripts or executables,
    that can be used in different machine learning scenarios and by different users. To use a specific
    version of a Module in a pipeline create a ModuleStep. A ModuleStep is a step in pipeline that uses an existing
    :class:`azureml.pipeline.core.module.ModuleVersion`.

    For an example of using ModuleStep, see the notebook https://aka.ms/pl-modulestep.

    .. remarks::

        A :class:`azureml.pipeline.core.module.Module` is used to create and manage a resusable computational
        unit of an Azure Machine Learning pipeline. ModuleStep is the built-in step in Azure Machine Learning
        used to consume a module. You can either define specifically which ModuleVersion to use or let
        Azure Machine Learning resolve which ModuleVersion to use following the resolution process
        defined in the remarks section of the :class:`azureml.pipeline.core.module.Module` class.
        To define which ModuleVersion is used in a submitted pipeline, define one of the following when
        creating a ModuleStep:

        * A :class:`azureml.pipeline.core.module.ModuleVersion` object.
        * A :class:`azureml.pipeline.core.module.Module` object and a version value.
        * A :class:`azureml.pipeline.core.module.Module` object without a version value. In this case,
          version resolution may vary across submissions.

        You must define the mapping between the ModuleStep's inputs and outputs to the ModuleVersion's inputs
        and outputs.

        The following example shows how to create a ModuleStep as a part of pipeline with multiple ModuleStep
        objects:

        .. code-block:: python

            middle_step = ModuleStep(module=module,
                                     inputs_map= middle_step_input_wiring,
                                     outputs_map= middle_step_output_wiring,
                                     runconfig=RunConfiguration(), compute_target=aml_compute,
                                     arguments = ["--file_num1", first_sum, "--file_num2", first_prod,
                                                  "--output_sum", middle_sum, "--output_product", middle_prod])

        Full sample is available from
        https://github.com/Azure/MachineLearningNotebooks/blob/master/how-to-use-azureml/machine-learning-pipelines/intro-to-pipelines/aml-pipelines-how-to-use-modulestep.ipynb


    :param module: The module used in the step.
        Provide either the ``module`` or the ``module_version`` parameter but not both.
    :type module: azureml.pipeline.core.Module
    :param version: The version of the module used in the step.
    :type version: str
    :param module_version: A ModuleVersion of the module used in the step.
        Provide either the ``module`` or the ``module_version`` parameter but not both.
    :type module_version: azureml.pipeline.core.ModuleVersion
    :param inputs_map: A dictionary that maps the names of port definitions of the ModuleVersion to
                        the step's inputs.
    :type inputs_map: dict[str, typing.Union[azureml.pipeline.core.graph.InputPortBinding,
                    azureml.data.data_reference.DataReference,
                    azureml.pipeline.core.PortDataReference,
                    azureml.pipeline.core.builder.PipelineData,
                    azureml.pipeline.core.pipeline_output_dataset.PipelineOutputAbstractDataset,
                    azureml.data.dataset_consumption_config.DatasetConsumptionConfig]]
    :param outputs_map: A dictionary that maps the names of port definitions of the ModuleVersion to
                        the step's outputs.
    :type outputs_map: dict[str, typing.Union[azureml.pipeline.core.graph.OutputPortBinding,
                    azureml.data.data_reference.DataReference,
                    azureml.pipeline.core.PortDataReference,
                    azureml.pipeline.core.builder.PipelineData,
                    azureml.pipeline.core.pipeline_output_dataset.PipelineOutputAbstractDataset]]
    :param compute_target: The compute target to use. If unspecified, the target from the runconfig will be used.
        May be a compute target object or the string name of a compute target on the workspace.
        Optionally, if the compute target is not available at pipeline creation time, you may specify a tuple of
        ('compute target name', 'compute target type') to avoid fetching the compute target object (AmlCompute
        type is 'AmlCompute' and RemoteCompute type is 'VirtualMachine').
    :type compute_target: typing.Union[azureml.core.compute.DsvmCompute,
                        azureml.core.compute.AmlCompute,
                        azureml.core.compute.RemoteCompute,
                        azureml.core.compute.HDInsightCompute,
                        str,
                        tuple]
    :param runconfig: An optional RunConfiguration to use. A RunConfiguration can be used to specify additional
                    requirements for the run, such as conda dependencies and a Docker image.
    :type runconfig: azureml.core.runconfig.RunConfiguration
    :param runconfig_pipeline_params: An override of runconfig properties at runtime using key-value pairs
                        each with name of the runconfig property and PipelineParameter for that property.

        Supported values: 'NodeCount', 'MpiProcessCountPerNode', 'TensorflowWorkerCount',
        'TensorflowParameterServerCount'

    :type runconfig_pipeline_params: dict[str, azureml.pipeline.core.graph.PipelineParameter]
    :param arguments: A list of command line arguments for the Python script file. The arguments will be delivered
                      to the compute target via arguments in RunConfiguration.
                      For more details how to handle arguments such as special symbols, see the
                      arguments in :class:`azureml.core.RunConfiguration`
    :type arguments: list[str]
    :param params: A dictionary of name-value pairs.
    :type params: dict[str, str]
    :param name: The name of the step.
    :type name: str
    :param _workflow_provider: (Internal use only.) The workflow provider.
    :type _workflow_provider: azureml.pipeline.core._aeva_provider._AevaWorkflowProvider
    """

    def __init__(self, module=None, version=None, module_version=None,
                 inputs_map=None, outputs_map=None,
                 compute_target=None, runconfig=None,
                 runconfig_pipeline_params=None, arguments=None, params=None, name=None,
                 _workflow_provider=None):
        """
        Create an Azure ML pipeline step to run a specific version of a Module.

        :param module: The module used in the step.
            Provide either the ``module`` or the ``module_version`` parameter but not both.
        :type module: azureml.pipeline.core.Module
        :param version: The version of the module used in the step.
        :type version: str
        :param module_version: The ModuleVersion of the module used in the step.
            Provide either the ``module`` or the ``module_version`` parameter but not both.
        :type module_version: azureml.pipeline.core.ModuleVersion
        :param inputs_map: A dictionary that maps the names of port definitions of the ModuleVersion to
                        the step's inputs.
        :type inputs_map: dict[str, typing.Union[azureml.pipeline.core.graph.InputPortBinding,
                        azureml.data.data_reference.DataReference,
                        azureml.pipeline.core.PortDataReference,
                        azureml.pipeline.core.builder.PipelineData,
                        azureml.pipeline.core.pipeline_output_dataset.PipelineOutputDataset,
                        azureml.data.dataset_consumption_config.DatasetConsumptionConfig]]
        :param outputs_map: A dictionary that maps the names of port definitions of the ModuleVersion to
                        the step's outputs.
        :type outputs_map: dict[str, typing.Union[azureml.pipeline.core.graph.InputPortBinding,
                        azureml.data.data_reference.DataReference,
                        azureml.pipeline.core.PortDataReference,
                        azureml.pipeline.core.builder.PipelineData,
                        azureml.pipeline.core.pipeline_output_dataset.PipelineOutputDataset]]
        :param compute_target: The compute target to use. If unspecified, the target from the runconfig will be used.
            May be a compute target object or the string name of a compute target on the workspace.
            Optionally, if the compute target is not available at pipeline creation time, you may specify a tuple of
            ('compute target name', 'compute target type') to avoid fetching the compute target object (AmlCompute
            type is 'AmlCompute' and RemoteCompute type is 'VirtualMachine').
        :type compute_target: typing.Union[azureml.core.compute.DsvmCompute,
                            azureml.core.compute.AmlCompute,
                            azureml.core.compute.RemoteCompute,
                            azureml.core.compute.HDInsightCompute,
                            str,
                            tuple]
        :param runconfig: An optional RunConfiguration to use. A RunConfiguration can be used to specify additional
                      requirements for the run, such as conda dependencies and a Docker image.
        :type runconfig: azureml.core.runconfig.RunConfiguration
        :param runconfig_pipeline_params: An override of runconfig properties at runtime using key-value pairs
                        each with name of the runconfig property and PipelineParameter for that property.

            Supported values: 'NodeCount', 'MpiProcessCountPerNode', 'TensorflowWorkerCount',
                          'TensorflowParameterServerCount'

        :type runconfig_pipeline_params: dict[str, azureml.pipeline.core.graph.PipelineParameter]
        :param arguments: A list of command line arguments for the Python script file. The arguments will be delivered
                        to the compute target via arguments in RunConfiguration.
                        For more details how to handle arguments such as special symbols, see the
                        arguments in :class:`azureml.core.RunConfiguration`
        :type arguments: list[str]
        :param params: A dictionary of name-value pairs.
        :type params: dict[str, str]
        :param name: The name of the step.
        :type name: str
        :param _wokflow_provider: (Internal use only.) The workflow provider.
        :type _workflow_provider: azureml.pipeline.core._aeva_provider._AevaWorkflowProvider
        """
        super(ModuleStep, self).__init__(module=module, version=version, module_version=module_version,
                                         inputs_map=inputs_map, outputs_map=outputs_map,
                                         compute_target=compute_target, runconfig=runconfig,
                                         runconfig_pipeline_params=runconfig_pipeline_params, arguments=arguments,
                                         params=params, name=name, _workflow_provider=_workflow_provider)

    def create_node(self, graph, default_datastore, context):
        """
        Create a node from the ModuleStep step and add it to the specified graph.

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

        :return: The node object.
        :rtype: azureml.pipeline.core.graph.Node
        """
        return super(ModuleStep, self).create_node(
            graph=graph, default_datastore=default_datastore, context=context)
