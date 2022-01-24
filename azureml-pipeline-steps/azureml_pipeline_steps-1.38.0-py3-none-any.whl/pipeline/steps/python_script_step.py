# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains functionality to create an Azure ML Pipeline step that runs Python script."""
from azureml.pipeline.core._python_script_step_base import _PythonScriptStepBase


class PythonScriptStep(_PythonScriptStepBase):
    r"""Creates an Azure ML Pipeline step that runs Python script.

    For an example of using PythonScriptStep, see the notebook https://aka.ms/pl-get-started.

    .. remarks::

        A PythonScriptStep is a basic, built-in step to run a Python Script on a compute target. It takes
        a script name and other optional parameters like arguments for the script, compute target, inputs
        and outputs. If no compute target is specified, the default compute target for the workspace is
        used. You can also use a :class:`azureml.core.RunConfiguration` to specify requirements for the
        PythonScriptStep, such as conda dependencies and docker image.

        The best practice for working with PythonScriptStep is to use a separate folder for scripts and any dependent
        files associated with the step, and specify that folder with the ``source_directory`` parameter.
        Following this best practice has two benefits. First, it helps reduce the size of the snapshot
        created for the step because only what is needed for the step is snapshotted. Second, the step's output
        from a previous run can be reused if there are  no changes to the ``source_directory`` that would trigger
        a re-upload of the snapshot.

        The following code example shows using a PythonScriptStep in a machine learning training scenario. For more
        details on this example, see https://aka.ms/pl-first-pipeline.

        .. code-block:: python

            from azureml.pipeline.steps import PythonScriptStep

            trainStep = PythonScriptStep(
                script_name="train.py",
                arguments=["--input", blob_input_data, "--output", output_data1],
                inputs=[blob_input_data],
                outputs=[output_data1],
                compute_target=compute_target,
                source_directory=project_folder
            )

        PythonScriptSteps support a number of input and output types. These include
        :class:`azureml.data.dataset_consumption_config.DatasetConsumptionConfig` for inputs and
        :class:`azureml.data.output_dataset_config.OutputDatasetConfig`,
        :class:`azureml.pipeline.core.pipeline_output_dataset.PipelineOutputAbstractDataset`,
        and :class:`azureml.pipeline.core.builder.PipelineData` for inputs and outputs.

        Below is an example of using :class:`azureml.core.Dataset` as a step input and output:

        .. code-block:: python

            from azureml.core import Dataset
            from azureml.pipeline.steps import PythonScriptStep
            from azureml.pipeline.core import Pipeline, PipelineData

            # get input dataset
            input_ds = Dataset.get_by_name(workspace, 'weather_ds')

            # register pipeline output as dataset
            output_ds = PipelineData('prepared_weather_ds', datastore=datastore).as_dataset()
            output_ds = output_ds.register(name='prepared_weather_ds', create_new_version=True)

            # configure pipeline step to use dataset as the input and output
            prep_step = PythonScriptStep(script_name="prepare.py",
                                         inputs=[input_ds.as_named_input('weather_ds')],
                                         outputs=[output_ds],
                                         compute_target=compute_target,
                                         source_directory=project_folder)

        Please reference the corresponding documentation pages for examples of using other input/output types.

    :param script_name: [Required] The name of a Python script relative to ``source_directory``.
    :type script_name: str
    :param name: The name of the step. If unspecified, ``script_name`` is used.
    :type name: str
    :param arguments: Command line arguments for the Python script file. The arguments will be passed
                      to compute via the ``arguments`` parameter in RunConfiguration.
                      For more details how to handle arguments such as special symbols, see
                      the :class:`azureml.core.RunConfiguration`.
    :type arguments: list
    :param compute_target: [Required] The compute target to use. If unspecified, the target from
        the runconfig will be used. This parameter may be specified as
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
    :param runconfig: The optional RunConfiguration to use. A RunConfiguration can be used to specify additional
                    requirements for the run, such as conda dependencies and a docker image. If unspecified, a
                    default runconfig will be created.
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
                        azureml.pipeline.core.pipeline_output_dataset.PipelineOutputFileDataset,
                        azureml.pipeline.core.pipeline_output_dataset.PipelineOutputTabularDataset,
                        azureml.pipeline.core.graph.OutputPortBinding]]
    :param params: A dictionary of name-value pairs registered as environment variables with "AML_PARAMETER\_".
    :type params: dict
    :param source_directory: A folder that contains Python script, conda env, and other resources used in
        the step.
    :type source_directory: str
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
    :param hash_paths: DEPRECATED: no longer needed.

        A list of paths to hash when checking for changes to the step contents. If there
        are no changes detected, the pipeline will reuse the step contents from a previous run. By default,
        the contents of ``source_directory`` is hashed except for files listed in .amlignore or .gitignore.
    :type hash_paths: list
    """

    def __init__(self, script_name, name=None, arguments=None, compute_target=None, runconfig=None,
                 runconfig_pipeline_params=None, inputs=None, outputs=None, params=None, source_directory=None,
                 allow_reuse=True, version=None, hash_paths=None):
        """
        Create an Azure ML Pipeline step that runs Python script.

        :param script_name: [Required] The name of a Python script relative to ``source_directory``.
        :type script_name: str
        :param name: The name of the step.  If unspecified, ``script_name`` is used.
        :type name: str
        :param arguments: Command line arguments for the Python script file. The arguments will be passed
                        to compute via the ``arguments`` parameter in RunConfiguration.
                        For more details how to handle arguments such as special symbols, see
                        the :class:`azureml.core.RunConfiguration`.
        :type arguments: [str]
        :param compute_target: [Required] The compute target to use. If unspecified, the target from
            the runconfig will be used. This parameter may be specified as
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
        :param runconfig: The optional RunConfiguration to use. RunConfiguration can be used to specify additional
                        requirements for the run, such as conda dependencies and a docker image. If unspecified, a
                        default runconfig will be created.
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
                            azureml.pipeline.core.pipeline_output_dataset.PipelineOutputFileDataset,
                            azureml.pipeline.core.pipeline_output_dataset.PipelineOutputTabularDataset,
                            azureml.pipeline.core.graph.OutputPortBinding]]
        :param params: A dictionary of name-value pairs. Registered as environment variables with "AML_PARAMETER_".
        :type params: {str: str}
        :param source_directory: A folder that contains Python script, conda env, and other resources used in
            the step.
        :type source_directory: str
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
        :param hash_paths: DEPRECATED: no longer needed.

            A list of paths to hash when checking for changes to the step contents. If there
            are no changes detected, the pipeline will reuse the step contents from a previous run. By default,
            the contents of ``source_directory`` is hashed except for files listed in .amlignore or .gitignore.
        :type hash_paths: list
        """
        super(PythonScriptStep, self).__init__(
            script_name=script_name, name=name, arguments=arguments, compute_target=compute_target,
            runconfig=runconfig, runconfig_pipeline_params=runconfig_pipeline_params, inputs=inputs, outputs=outputs,
            params=params, source_directory=source_directory, allow_reuse=allow_reuse, version=version,
            hash_paths=hash_paths)

    def create_node(self, graph, default_datastore, context):
        """
        Create a node for PythonScriptStep and add it to the specified graph.

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
        return super(PythonScriptStep, self).create_node(
            graph=graph, default_datastore=default_datastore, context=context)

    def _set_amlcompute_params(self, native_shared_directory=None):
        """
        Set AmlCompute native shared directory param.

        :param native_shared_directory: The native shared directory.
        :type native_shared_directory: str
        """
        super(PythonScriptStep, self)._set_amlcompute_params(native_shared_directory=native_shared_directory)
