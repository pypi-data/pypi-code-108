# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains functionality to create an Azure ML Pipeline step that runs a Windows executable in Azure Batch."""
from azureml.pipeline.core._azurebatch_step_base import _AzureBatchStepBase


class AzureBatchStep(_AzureBatchStepBase):
    r"""
    Creates an Azure ML Pipeline step for submitting jobs to Azure Batch.

    Note: This step does not support upload/download of directories and their contents.

    For an example of using AzureBatchStep, see the notebook https://aka.ms/pl-azbatch.

    .. remarks::

        The following example shows how to use AzureBatchStep in an Azure Machine Learning Pipeline.

        .. code-block:: python

            step = AzureBatchStep(
                        name="Azure Batch Job",
                        pool_id="MyPoolName", # Replace this with the pool name of your choice
                        inputs=[testdata],
                        outputs=[outputdata],
                        executable="azurebatch.cmd",
                        arguments=[testdata, outputdata],
                        compute_target=batch_compute,
                        source_directory=binaries_folder,
            )

        Full sample is available from
        https://github.com/Azure/MachineLearningNotebooks/blob/master/how-to-use-azureml/machine-learning-pipelines/intro-to-pipelines/aml-pipelines-how-to-use-azurebatch-to-run-a-windows-executable.ipynb


    :param name: [Required] The name of the step.
    :type name: str
    :param create_pool: Indicates whether to create the pool before running the jobs.
    :type create_pool: bool
    :param pool_id: [Required] The ID of the pool where the job runs.
        The ID can be an existing pool, or one that will be created when the job is submitted.
    :type pool_id: str
    :param delete_batch_job_after_finish: Indicates whether to delete the job from
                                        Batch account after it's finished.
    :type delete_batch_job_after_finish: bool
    :param delete_batch_pool_after_finish: Indicates whether to delete the pool after
                                        the job finishes.
    :type delete_batch_pool_after_finish: bool
    :param is_positive_exit_code_failure: Indicates whether the job fails if the task exists
                                        with a positive code.
    :type is_positive_exit_code_failure: bool
    :param vm_image_urn: If ``create_pool`` is True and VM uses VirtualMachineConfiguration.
                         Value format: ``urn:publisher:offer:sku``.
                         Example: ``urn:MicrosoftWindowsServer:WindowsServer:2012-R2-Datacenter``.
    :type vm_image_urn: str
    :param run_task_as_admin: Indicates whether the task should run with admin privileges.
    :type run_task_as_admin: bool
    :param target_compute_nodes: If ``create_pool`` is True, indicates how many compute nodes will be added
                                to the pool.
    :type target_compute_nodes: int
    :param vm_size: If ``create_pool`` is True, indicates the virtual machine size of the compute nodes.
    :type vm_size: str
    :param source_directory: A local folder that contains the module binaries, executable, assemblies, etc.
    :type source_directory: str
    :param executable: [Required] The name of the command/executable that will be executed as part of the job.
    :type executable: str
    :param arguments: Arguments for the command/executable.
    :type arguments: str
    :param inputs: A list of input port bindings.
        Before the job runs, a folder is created for each input. The files for each input will be copied
        from the storage to the respective folder on the compute node.
        For example, if the input name is *input1*, and the relative path on storage is
        *some/relative/path/that/can/be/really/long/inputfile.txt*, then the file path on the compute
        will be:  *./input1/inputfile.txt*.
        When the input name is longer than 32 characters, it will be truncated and appended with a unique
        suffix so the folder name can be created successfully on the compute target.
    :type inputs: list[typing.Union[azureml.pipeline.core.graph.InputPortBinding,
                    azureml.data.data_reference.DataReference,
                    azureml.pipeline.core.PortDataReference,
                    azureml.pipeline.core.builder.PipelineData]]
    :param outputs: A list of output port bindings.
        Similar to inputs, before the job runs, a folder is created for each output. The folder name will be
        the same as the output name. The assumption is that the job will put the output into that folder.
    :type outputs: list[typing.Union[azureml.pipeline.core.builder.PipelineData,
                    azureml.pipeline.core.pipeline_output_dataset.PipelineOutputAbstractDataset,
                    azureml.pipeline.core.graph.OutputPortBinding]]
    :param allow_reuse: Indicates whether the step should reuse previous results when re-run with the same
        settings. Reuse is enabled by default. If the step contents (scripts/dependencies) as well as inputs and
        parameters remain unchanged, the output from the previous run of this step is reused. When reusing
        the step, instead of submitting the job to compute, the results from the previous run are immediately
        made available to any subsequent steps. If you use Azure Machine Learning datasets as inputs, reuse is
        determined by whether the dataset's definition has changed, not by whether the underlying data has
        changed.
    :type allow_reuse: bool
    :param compute_target: [Required] A BatchCompute compute where the job runs.
    :type compute_target: azureml.core.compute.BatchCompute, str
    :param version: An optional version tag to denote a change in functionality for the module.
    :type version: str

    """

    def __init__(self,
                 name,
                 create_pool=False,
                 pool_id=None,
                 delete_batch_job_after_finish=True,
                 delete_batch_pool_after_finish=False,
                 is_positive_exit_code_failure=True,
                 vm_image_urn="urn:MicrosoftWindowsServer:WindowsServer:2012-R2-Datacenter",
                 run_task_as_admin=False,
                 target_compute_nodes=1,
                 vm_size="standard_d1_v2",
                 source_directory=None,
                 executable=None,
                 arguments=None,
                 inputs=None,
                 outputs=None,
                 allow_reuse=True,
                 compute_target=None,
                 version=None):
        r"""
        Create an Azure ML Pipeline step for submitting jobs to Azure Batch.

        :param name: [Required] The name of the step.
        :type name: str
        :param create_pool: Indicates whether to create the pool before running the jobs.
        :type create_pool: bool
        :param pool_id: [Required] The ID of the pool where the job runs.
            The ID can be an existing pool, or one that will be created when the job is submitted.
        :type pool_id: str
        :param delete_batch_job_after_finish: Indicates whether to delete the job from
                                        Batch account after it's finished.
        :type delete_batch_job_after_finish: bool
        :param delete_batch_pool_after_finish: Indicates whether to delete the pool after
                                        the job finishes.
        :type delete_batch_pool_after_finish: bool
        :param is_positive_exit_code_failure: Indicates whether the job fails if the task exists
                                        with a positive code.
        :type is_positive_exit_code_failure: bool
        :param vm_image_urn: If ``create_pool`` is True and VM uses VirtualMachineConfiguration.
                         Value format: ``urn:publisher:offer:sku``.
                         Example: ``urn:MicrosoftWindowsServer:WindowsServer:2012-R2-Datacenter``.
        :type vm_image_urn: str
        :param run_task_as_admin: Indicates whether the task should run with admin privileges.
        :type run_task_as_admin: bool
        :param target_compute_nodes: If ``create_pool`` is True, indicates how many compute nodes will be added
                                to the pool.
        :type target_compute_nodes: int
        :param vm_size: If ``create_pool`` is True, indicates the Virtual machine size of the compute nodes.
        :type vm_size: str
        :param source_directory: A local folder that contains the module binaries, executable, assemblies etc.
        :type source_directory: str
        :param executable: [Required] The name of the command/executable that will be executed as part of the job.
        :type executable: str
        :param arguments: Arguments for the command/executable.
        :type arguments: list
        :param inputs: A list of input port bindings.
            Before the job runs, a folder is created for each input. The files for each input will be copied
            from the storage to the respective folder on the compute node.
            For example, if the input name is *input1*, and the relative path on storage is
            *some/relative/path/that/can/be/really/long/inputfile.txt*, then the file path on the compute
            will be:  *./input1/inputfile.txt*.
            In case the input name is longer than 32 characters, it will be truncated and appended with a unique
            suffix, so the folder name could be created successfully on the compute.
        :type inputs: list[typing.Union[azureml.pipeline.core.graph.InputPortBinding,
                        azureml.data.data_reference.DataReference,
                        azureml.pipeline.core.PortDataReference,
                        azureml.pipeline.core.builder.PipelineData]]
        :param outputs: A list of output port bindings.
            Similar to inputs, before the job runs, a folder is created for each output. The folder name will be
            the same as the output name. The assumption is that the job will have the output into that folder.
        :type outputs: list[typing.Union[azureml.pipeline.core.builder.PipelineData,
                        azureml.pipeline.core.pipeline_output_dataset.PipelineOutputAbstractDataset,
                        azureml.pipeline.core.graph.OutputPortBinding]]
        :param allow_reuse: Indicates whether the step should reuse previous results when re-run with the same
            settings. Reuse is enabled by default. If the step contents (scripts/dependencies) as well as inputs and
            parameters remain unchanged, the output from the previous run of this step is reused. When reusing
            the step, instead of submitting the job to compute, the results from the previous run are immediately
            made available to any subsequent steps. If you use Azure Machine Learning datasets as inputs, reuse is
            determined by whether the dataset's definition has changed, not by whether the underlying data has
            changed.
        :type allow_reuse: bool
        :param compute_target: [Required] A BatchCompute compute where the job runs.
        :type compute_target: azureml.core.compute.BatchCompute, str
        :param version: An optional version tag to denote a change in functionality for the module.
        :type version: str

        """
        super(AzureBatchStep, self).__init__(
            name=name, create_pool=create_pool, pool_id=pool_id,
            delete_batch_job_after_finish=delete_batch_job_after_finish,
            delete_batch_pool_after_finish=delete_batch_pool_after_finish,
            is_positive_exit_code_failure=is_positive_exit_code_failure,
            vm_image_urn=vm_image_urn,
            run_task_as_admin=run_task_as_admin,
            target_compute_nodes=target_compute_nodes,
            vm_size=vm_size,
            source_directory=source_directory,
            executable=executable,
            arguments=arguments,
            inputs=inputs,
            outputs=outputs,
            allow_reuse=allow_reuse,
            compute_target=compute_target,
            version=version)

    def create_node(self, graph, default_datastore, context):
        """
        Create a node from the AzureBatch step and add it to the specified graph.

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
        return super(AzureBatchStep, self).create_node(graph=graph, default_datastore=default_datastore,
                                                       context=context)
