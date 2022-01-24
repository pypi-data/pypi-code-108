# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains functionality to create an Azure ML Pipeline step that transfers data between storage options."""
from azureml.pipeline.core._data_transfer_step_base import _DataTransferStepBase


class DataTransferStep(_DataTransferStepBase):
    """Creates an Azure ML Pipeline step that transfers data between storage options.

    DataTransferStep supports common storage types such as Azure Blob Storage and Azure Data Lake as sources and
    sinks. For more more information, see the
    `Remarks </python/api/azureml-pipeline-steps/azureml.pipeline.steps.datatransferstep#remarks>`_ section.

     For an example of using DataTransferStep, see the notebook https://aka.ms/pl-data-trans.

    .. remarks::

        This step supports the following storage types as sources and sinks except where noted:

        * Azure Blob Storage
        * Azure Data Lake Storage Gen1 and Gen2
        * Azure SQL Database
        * Azure Database for PostgreSQL
        * Azure Database for MySQL

        For Azure SQL Database, you must use service principal authentication. For more information, see
        `Service Principal Authentication
        <https://docs.microsoft.com/azure/data-factory/connector-azure-sql-database#service-principal-authentication>`_.
        For an example of using service principal authentication for Azure SQL Database, see
        https://aka.ms/pl-data-trans.

        To establish data dependency between steps, use the
        :func:`azureml.pipeline.steps.data_transfer_step.DataTransferStep.get_output` method to get a
        :class:`azureml.pipeline.core.PipelineData` object that represents the output of this data
        transfer step and can be used as input for later steps in the pipeline.

        .. code-block:: python

            data_transfer_step = DataTransferStep(name="copy data", ...)

            # Use output of data_transfer_step as input of another step in pipeline
            # This will make training_step wait for data_transfer_step to complete
            training_input = data_transfer_step.get_output()
            training_step = PythonScriptStep(script_name="train.py",
                                    arguments=["--model", training_input],
                                    inputs=[training_input],
                                    compute_target=aml_compute,
                                    source_directory=source_directory)

        To create an :class:`azureml.pipeline.core.graph.InputPortBinding` with specific name, you can combine
        `get_output()` output with the output of the :func:`azureml.pipeline.core.PipelineData.as_input` or
        :func:`azureml.pipeline.core.PipelineData.as_mount` methods of
        :class:`azureml.pipeline.core.PipelineData`.

        .. code-block:: python

            data_transfer_step = DataTransferStep(name="copy data", ...)
            training_input = data_transfer_step.get_output().as_input("my_input_name")


    :param name: [Required] The name of the step.
    :type name: str
    :param source_data_reference: [Required] An input connection that serves as source of
                the data transfer operation.
    :type source_data_reference: typing.Union[azureml.pipeline.core.graph.InputPortBinding,
                  azureml.data.data_reference.DataReference,
                  azureml.pipeline.core.PortDataReference,
                  azureml.pipeline.core.builder.PipelineData]
    :param destination_data_reference: [Required] An output connection that serves as destination of
                the data transfer operation.
    :type destination_data_reference: typing.Union[azureml.pipeline.core.graph.InputPortBinding,
                                        azureml.pipeline.core.pipeline_output_dataset.PipelineOutputAbstractDataset,
                                        azureml.data.data_reference.DataReference]
    :param compute_target: [Required] An Azure Data Factory to use for transferring data.
    :type compute_target: azureml.core.compute.DataFactoryCompute, str
    :param source_reference_type: An optional string specifying the type of ``source_data_reference``. Possible values
        include: 'file', 'directory'. When not specified, the type of existing path is used.
        Use this parameter to differentiate between a file and directory of the same name.
    :type source_reference_type: str
    :param destination_reference_type: An optional string specifying the type of ``destination_data_reference``.
        Possible values include: 'file', 'directory'. When not specified, Azure ML uses the type of
        existing path, source reference, or 'directory', in that order.
    :type destination_reference_type: str
    :param allow_reuse: Indicates whether the step should reuse previous results when re-run with the same
        settings. Reuse is enabled by default. If step arguments remain unchanged, the output from the previous
        run of this step is reused. When reusing the step, instead of transferring data again, the results from
        the previous run are immediately made available to any subsequent steps. If you use Azure Machine Learning
        datasets as inputs, reuse is determined by whether the dataset's definition has changed, not by whether
        the underlying data has changed.
    :type allow_reuse: bool
    """

    def __init__(self, name, source_data_reference=None, destination_data_reference=None, compute_target=None,
                 source_reference_type=None, destination_reference_type=None, allow_reuse=True):
        """
        Create an Azure ML Pipeline step that transfers data between storage options.

        :param name: [Required] The name of the step.
        :type name: str
        :param source_data_reference: [Required] An input connection that serves as source of
                    the data transfer operation.
        :type source_data_reference: typing.Union[azureml.pipeline.core.graph.InputPortBinding,
                  azureml.data.data_reference.DataReference,
                  azureml.pipeline.core.PortDataReference,
                  azureml.pipeline.core.builder.PipelineData]
        :param destination_data_reference: [Required] An output connection that serves as destination of
                    the data transfer operation.
        :type destination_data_reference: typing.Union[azureml.pipeline.core.graph.InputPortBinding,
                                        azureml.pipeline.core.pipeline_output_dataset.PipelineOutputAbstractDataset,
                                        azureml.data.data_reference.DataReference]
        :param compute_target: [Required] An Azure Data Factory to use for transferring data.
        :type compute_target: azureml.core.compute.DataFactoryCompute, str
        :param source_reference_type: An optional string specifying the type of ``source_data_reference``. Possible
            values include: 'file', 'directory'. When not specified, the type of existing path is used.
            Use this parameter to differentiate between a file and directory of the same name.
        :type source_reference_type: str
        :param destination_reference_type: An optional string specifying the type of ``destination_data_reference``.
            Possible values include: 'file', 'directory'. When not specified, Azure ML uses the type of
            existing path, source reference, or 'directory', in that order.
        :type destination_reference_type: str
        :param allow_reuse: Indicates whether the step should reuse previous results when re-run with the same
            settings. Reuse is enabled by default. If step arguments remain unchanged, the output from the previous
            run of this step is reused. When reusing the step, instead of transferring data again, the results from
            the previous run are immediately made available to any subsequent steps. If you use Azure Machine
            Learning datasets as inputs, reuse is determined by whether the dataset's definition has changed,
            not by whether the underlying data has changed.
        :type allow_reuse: bool
        """
        super(DataTransferStep, self).__init__(
            name=name, source_data_reference=source_data_reference,
            destination_data_reference=destination_data_reference, compute_target=compute_target,
            source_reference_type=source_reference_type, destination_reference_type=destination_reference_type,
            allow_reuse=allow_reuse)

    def create_node(self, graph, default_datastore, context):
        """
        Create a node from the DataTransfer step and add it to the given graph.

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
        return super(DataTransferStep, self).create_node(graph=graph, default_datastore=default_datastore,
                                                         context=context)

    def get_output(self):
        """
        Get the output of the step as PipelineData.

        .. remarks::

            To establish data dependency between steps, use :func:`azureml.pipeline.steps.DataTransferStep.get_output`
            method to get a :class:`azureml.pipeline.core.PipelineData` object that represents the output of this data
            transfer step and can be used as input for later steps in the pipeline.

            .. code-block:: python

                data_transfer_step = DataTransferStep(name="copy data", ...)

                # Use output of data_transfer_step as input of another step in pipeline
                # This will make training_step wait for data_transfer_step to complete
                training_input = data_transfer_step.get_output()
                training_step = PythonScriptStep(script_name="train.py",
                                        arguments=["--model", training_input],
                                        inputs=[training_input],
                                        compute_target=aml_compute,
                                        source_directory=source_directory)

            To create an :class:`azureml.pipeline.core.graph.InputPortBinding` with specific name, you can combine
            `get_output()` call with :func:`azureml.pipeline.core.PipelineData.as_input` or
            :func:`azureml.pipeline.core.PipelineData.as_mount` helper methods.

            .. code-block:: python

                data_transfer_step = DataTransferStep(name="copy data", ...)

                training_input = data_transfer_step.get_output().as_input("my_input_name")

        :return: The output of the step.
        :rtype: azureml.pipeline.core.builder.PipelineData
        """
        return super(DataTransferStep, self).get_output()
