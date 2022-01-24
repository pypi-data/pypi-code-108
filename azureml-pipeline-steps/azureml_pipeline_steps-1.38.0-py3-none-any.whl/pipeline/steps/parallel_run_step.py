# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains functionality to add a step to run user script in parallel mode on multiple AmlCompute targets."""
from azureml.pipeline.core._parallel_run_step_base import _ParallelRunStepBase


class ParallelRunStep(_ParallelRunStepBase):
    r"""
    Creates an Azure Machine Learning Pipeline step to process large amounts of data asynchronously and in parallel.

    For an example of using ParallelRunStep, see the notebook https://aka.ms/batch-inference-notebooks.

    For troubleshooting guide, see https://aka.ms/prstsg. You can find more references there.

    .. remarks::

        ParallelRunStep can be used for processing large amounts of data in parallel. Common use cases are training
        an ML model or running offline inference to generate predictions on a batch of observations. ParallelRunStep
        works by breaking up your data into batches that are processed in parallel. The batch size node count,
        and other tunable parameters to speed up your parallel processing can be controlled with the
        :class:`azureml.pipeline.steps.ParallelRunConfig` class. ParallelRunStep can work with either
        :class:`azureml.data.TabularDataset` or :class:`azureml.data.FileDataset` as input.

        To use ParallelRunStep:

        * Create a :class:`azureml.pipeline.steps.ParallelRunConfig` object to specify how batch
          processing is performed, with parameters to control batch size, number of nodes per compute target,
          and a reference to your custom Python script.

        * Create a ParallelRunStep object that uses the ParallelRunConfig object, define inputs and
          outputs for the step.

        * Use the configured ParallelRunStep object in a :class:`azureml.pipeline.core.Pipeline`
          just as you would with other pipeline step types.

        Examples of working with ParallelRunStep and ParallelRunConfig classes for batch inference are discussed in
        the following articles:

        * `Tutorial: Build an Azure Machine Learning pipeline for batch
          scoring <https://docs.microsoft.com/azure/machine-learning/tutorial-pipeline-batch-scoring-classification>`_.
          This article shows how to use these two classes for asynchronous batch scoring in a pipeline and enable a
          REST endpoint to run the pipeline.

        * `Run batch inference on large amounts of data by using Azure Machine
          Learning <https://docs.microsoft.com/azure/machine-learning/how-to-use-parallel-run-step>`_. This article
          shows how to process large amounts of data asynchronously and in parallel with a custom inference script
          and a pre-trained image classification model bases on the MNIST dataset.

        .. code:: python

            from azureml.pipeline.steps import ParallelRunStep, ParallelRunConfig

            parallel_run_config = ParallelRunConfig(
                source_directory=scripts_folder,
                entry_script=script_file,
                mini_batch_size="5",
                error_threshold=10,         # Optional, allowed failed count on mini batch items
                allowed_failed_count=15,    # Optional, allowed failed count on mini batches
                allowed_failed_percent=10,  # Optional, allowed failed percent on mini batches
                output_action="append_row",
                environment=batch_env,
                compute_target=compute_target,
                node_count=2)

            parallelrun_step = ParallelRunStep(
                name="predict-digits-mnist",
                parallel_run_config=parallel_run_config,
                inputs=[ named_mnist_ds ],
                output=output_dir,
                arguments=[ "--extra_arg", "example_value" ],
                allow_reuse=True
            )

        For more information about this example, see the notebook https://aka.ms/batch-inference-notebooks.

    :param name: Name of the step. Must be unique to the workspace, only consist of lowercase letters,
        numbers, or dashes, start with a letter, and be between 3 and 32 characters long.
    :type name: str
    :param parallel_run_config: A ParallelRunConfig object used to determine required run properties.
    :type parallel_run_config: azureml.pipeline.steps.ParallelRunConfig
    :param inputs: List of input datasets. All datasets in the list should be of same type.
        Input data will be partitioned for parallel processing. Each dataset in the list is partitioned
        into mini-batches separately, and each of the mini-batches is treated equally in the parallel processing.
    :type inputs: list[typing.Union[azureml.data.dataset_consumption_config.DatasetConsumptionConfig,
                    azureml.pipeline.core.pipeline_output_dataset.PipelineOutputFileDataset,
                    azureml.pipeline.core.pipeline_output_dataset.PipelineOutputTabularDataset]]
    :param output: Output port binding, may be used by later pipeline steps.
    :type output: typing.Union[azureml.pipeline.core.builder.PipelineData,
        azureml.pipeline.core.graph.OutputPortBinding,
        azureml.data.output_dataset_config.OutputDatasetConfig]
    :param side_inputs: List of side input reference data. Side inputs will not be partitioned as input data.
    :type side_inputs: list[typing.Union[azureml.pipeline.core.graph.InputPortBinding,
                    azureml.data.data_reference.DataReference,
                    azureml.pipeline.core.PortDataReference,
                    azureml.pipeline.core.builder.PipelineData,
                    azureml.pipeline.core.pipeline_output_dataset.PipelineOutputFileDataset,
                    azureml.pipeline.core.pipeline_output_dataset.PipelineOutputTabularDataset,
                    azureml.data.dataset_consumption_config.DatasetConsumptionConfig]]
    :param arguments: List of command-line arguments to pass to the Python entry_script.
    :type arguments: list[str]
    :param allow_reuse: Whether the step should reuse previous results when run with the same settings/inputs.
        If this is false, a new run will always be generated for this step during pipeline execution.
    :type allow_reuse: bool
    """

    def __init__(
        self,
        name,
        parallel_run_config,
        inputs,
        output=None,
        side_inputs=None,
        arguments=None,
        allow_reuse=True,
    ):
        r"""Create an Azure ML Pipeline step to process large amounts of data asynchronously and in parallel.

        For an example of using ParallelRunStep, see the notebook link https://aka.ms/batch-inference-notebooks.

        :param name: Name of the step. Must be unique to the workspace, only consist of lowercase letters,
            numbers, or dashes, start with a letter, and be between 3 and 32 characters long.
        :type name: str
        :param parallel_run_config: A ParallelRunConfig object used to determine required run properties.
        :type parallel_run_config: azureml.pipeline.steps.ParallelRunConfig
        :param inputs: List of input datasets. All datasets in the list should be of same type.
            Input data will be partitioned for parallel processing. Each dataset in the list is partitioned
            into mini-batches separately, and each of the mini-batches is treated equally in the parallel
            processing.
        :type inputs: list[typing.Union[azureml.data.dataset_consumption_config.DatasetConsumptionConfig,
                        azureml.pipeline.core.pipeline_output_dataset.PipelineOutputFileDataset,
                        azureml.pipeline.core.pipeline_output_dataset.PipelineOutputTabularDataset]]
        :param output: Output port binding, may be used by later pipeline steps.
        :type output: azureml.pipeline.core.builder.PipelineData, azureml.pipeline.core.graph.OutputPortBinding
        :param side_inputs: List of side input reference data. Side inputs will not be partitioned as input data.
        :type side_inputs: list[typing.Union[azureml.pipeline.core.graph.InputPortBinding,
                        azureml.data.data_reference.DataReference,
                        azureml.pipeline.core.PortDataReference,
                        azureml.pipeline.core.builder.PipelineData,
                        azureml.pipeline.core.pipeline_output_dataset.PipelineOutputFileDataset,
                        azureml.pipeline.core.pipeline_output_dataset.PipelineOutputTabularDataset,
                        azureml.data.dataset_consumption_config.DatasetConsumptionConfig]]
        :param arguments: List of command-line arguments to pass to the Python entry_script.
        :type arguments: list[str]
        :param allow_reuse: Whether the step should reuse previous results when run with the same settings/inputs.
            If this is false, a new run will always be generated for this step during pipeline execution.
        :type allow_reuse: bool
        """
        super(ParallelRunStep, self).__init__(
            name=name,
            parallel_run_config=parallel_run_config,
            inputs=inputs,
            output=output,
            side_inputs=side_inputs,
            arguments=arguments,
            allow_reuse=allow_reuse,
        )

    def create_node(self, graph, default_datastore, context):
        """
        Create a node for :class:`azureml.pipeline.steps.PythonScriptStep` and add it to the specified graph.

        This method is not intended to be used directly. When a pipeline is instantiated with ParallelRunStep,
        Azure Machine Learning automatically passes the parameters required through this method so that the step
        can be added to a pipeline graph that represents the workflow.

        :param graph: Graph object.
        :type graph: azureml.pipeline.core.graph.Graph
        :param default_datastore: Default datastore.
        :type default_datastore: azureml.data.azure_storage_datastore.AbstractAzureStorageDatastore or
            azureml.data.azure_data_lake_datastore.AzureDataLakeDatastore
        :param context: Context.
        :type context: azureml.pipeline.core._GraphContext

        :return: The created node.
        :rtype: azureml.pipeline.core.graph.Node
        """
        return super(ParallelRunStep, self).create_node(graph, default_datastore, context)

    def create_module_def(
        self,
        execution_type,
        input_bindings,
        output_bindings,
        param_defs=None,
        create_sequencing_ports=True,
        allow_reuse=True,
        version=None,
        arguments=None,
    ):
        """
        Create the module definition object that describes the step.

        This method is not intended to be used directly.

        :param execution_type: The execution type of the module.
        :type execution_type: str
        :param input_bindings: The step input bindings.
        :type input_bindings: list
        :param output_bindings: The step output bindings.
        :type output_bindings: list
        :param param_defs: The step param definitions.
        :type param_defs: list
        :param create_sequencing_ports: If true, sequencing ports will be created for the module.
        :type create_sequencing_ports: bool
        :param allow_reuse: If true, the module will be available to be reused in future Pipelines.
        :type allow_reuse: bool
        :param version: The version of the module.
        :type version: str
        :param arguments: Annotated arguments list to use when calling this module.
        :type arguments: builtin.list

        :return: The module def object.
        :rtype: azureml.pipeline.core.graph.ModuleDef
        """
        return super(ParallelRunStep, self).create_module_def(
            execution_type=execution_type,
            input_bindings=input_bindings,
            output_bindings=output_bindings,
            param_defs=param_defs,
            create_sequencing_ports=create_sequencing_ports,
            allow_reuse=allow_reuse,
            version=version,
            arguments=arguments,
        )
