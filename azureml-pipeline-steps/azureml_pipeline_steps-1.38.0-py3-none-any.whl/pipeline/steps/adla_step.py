# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Contains functionality to create an Azure ML Pipeline step to run a U-SQL script with Azure Data Lake Analytics."""
from azureml.pipeline.core._adla_step_base import _AdlaStepBase


class AdlaStep(_AdlaStepBase):
    """Creates an Azure ML Pipeline step to run a U-SQL script with Azure Data Lake Analytics.

    For an example of using this AdlaStep, see the notebook https://aka.ms/pl-adla.

    .. remarks::

        You can use `@@name@@` syntax in your script to refer to inputs, outputs, and params.

        * if `name` is the name of an input or output port binding, any occurrences of `@@name@@` in the script
          are replaced with the actual data path of a corresponding port binding.
        * if `name` matches any key in `params` dict, any occurrences of `@@name@@` will be replaced with
          corresponding value in dict.

        AdlaStep works only with data stored in the default Data Lake Storage of the Data Lake Analytics
        account. If the data is in a non-default storage, use a
        :class:`azureml.pipeline.steps.data_transfer_step.DataTransferStep` to copy the data to the
        default storage. You can find the default storage by opening your Data Lake Analytics account in
        the Azure portal and then navigating to 'Data sources' item under Settings in the left pane.

        The following example shows how to use AdlaStep in an Azure Machine Learning Pipeline.

        .. code-block:: python

            adla_step = AdlaStep(
                name='extract_employee_names',
                script_name='sample_script.usql',
                source_directory=sample_folder,
                inputs=[sample_input],
                outputs=[sample_output],
                compute_target=adla_compute)

        Full sample is available from
        https://github.com/Azure/MachineLearningNotebooks/blob/master/how-to-use-azureml/machine-learning-pipelines/intro-to-pipelines/aml-pipelines-use-adla-as-compute-target.ipynb


    :param script_name: [Required] The name of a U-SQL script, relative to ``source_directory``.
    :type script_name: str
    :param name: The name of the step.  If unspecified, ``script_name`` is used.
    :type name: str
    :param inputs: A list of input port bindings.
    :type inputs: list[typing.Union[azureml.pipeline.core.graph.InputPortBinding,
                    azureml.data.data_reference.DataReference,
                    azureml.pipeline.core.PortDataReference,
                    azureml.pipeline.core.builder.PipelineData]]
    :param outputs: A list of output port bindings.
    :type outputs: list[typing.Union[azureml.pipeline.core.builder.PipelineData,
                    azureml.pipeline.core.pipeline_output_dataset.PipelineOutputAbstractDataset,
                    azureml.pipeline.core.graph.OutputPortBinding]]
    :param params: A dictionary of name-value pairs.
    :type params: dict
    :param degree_of_parallelism: The degree of parallelism to use for this job. This must be greater than 0.
        If set to less than 0, defaults to 1.
    :type degree_of_parallelism: int
    :param priority: The priority value to use for the current job. Lower numbers have a higher priority.
        By default, a job has a priority of 1000. The value you specify must be greater than 0.
    :type priority: int
    :param runtime_version: The runtime version of the Data Lake Analytics engine.
    :type runtime_version: str
    :param compute_target: [Required] The ADLA compute to use for this job.
    :type compute_target: azureml.core.compute.AdlaCompute, str
    :param source_directory: A folder that contains the script, assemblies etc.
    :type source_directory: str
    :param allow_reuse: Indicates whether the step should reuse previous results when re-run with the same
        settings. Reuse is enabled by default. If the step contents (scripts/dependencies) as well as inputs and
        parameters remain unchanged, the output from the previous run of this step is reused. When reusing
        the step, instead of submitting the job to compute, the results from the previous run are immediately
        made available to any subsequent steps. If you use Azure Machine Learning datasets as inputs, reuse is
        determined by whether the dataset's definition has changed, not by whether the underlying data has
        changed.
    :type allow_reuse: bool
    :param version: Optional version tag to denote a change in functionality for the step.
    :type version: str
    :param hash_paths: DEPRECATED: no longer needed.

        A list of paths to hash when checking for changes to the step contents. If there
        are no changes detected, the pipeline will reuse the step contents from a previous run. By default,
        the contents of ``source_directory`` is hashed except for files listed in .amlignore or .gitignore.
    :type hash_paths: list
    """

    def __init__(self, script_name, name=None, inputs=None, outputs=None, params=None, degree_of_parallelism=None,
                 priority=None, runtime_version=None, compute_target=None, source_directory=None, allow_reuse=True,
                 version=None, hash_paths=None):
        """
        Create an Azure ML Pipeline step to run a U-SQL script with Azure Data Lake Analytics.

        :param script_name: [Required] The name of a U-SQL script, relative to ``source_directory``.
        :type script_name: str
        :param name: The name of the step. If unspecified, ``script_name`` is used.
        :type name: str
        :param inputs: List of input port bindings
        :type inputs: list[typing.Union[azureml.pipeline.core.graph.InputPortBinding,
                      azureml.data.data_reference.DataReference,
                      azureml.pipeline.core.PortDataReference,
                      azureml.pipeline.core.builder.PipelineData]]
        :param outputs: A list of output port bindings.
        :type outputs: list[typing.Union[azureml.pipeline.core.builder.PipelineData,
                        azureml.pipeline.core.pipeline_output_dataset.PipelineAbstractOutputDataset,
                        azureml.pipeline.core.graph.OutputPortBinding]]
        :param params: A dictionary of name-value pairs.
        :type params: dict
        :param degree_of_parallelism: The degree of parallelism to use for this job. This must be greater than 0.
            If set to less than 0, defaults to 1.
        :type degree_of_parallelism: int
        :param priority: The priority value to use for the current job. Lower numbers have a higher priority.
            By default, a job has a priority of 1000. The value you specify must be greater than 0.
        :type priority: int
        :param runtime_version: The runtime version of the Data Lake Analytics engine.
        :type runtime_version: str
        :param compute_target: [Required] The ADLA compute to use for this job.
        :type compute_target: azureml.core.compute.AdlaCompute, str
        :param source_directory: A folder that contains the script, assemblies etc.
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
        super(AdlaStep, self).__init__(
            script_name=script_name, name=name, inputs=inputs, outputs=outputs,
            params=params, degree_of_parallelism=degree_of_parallelism, priority=priority,
            runtime_version=runtime_version, compute_target=compute_target,
            source_directory=source_directory, allow_reuse=allow_reuse, version=version, hash_paths=hash_paths)

    def create_node(self, graph, default_datastore, context):
        """
        Create a node from the AdlaStep step and add it to the specified graph.

        This method is not intended to be used directly. When a pipeline is instantiated with this step,
        Azure ML automatically passes the parameters required through this method so that step can be added to a
        pipeline graph that represents the workflow.

        :param graph: The graph object.
        :type graph: azureml.pipeline.core.graph.Graph
        :param default_datastore: The default datastore.
        :type default_datastore:  typing.Union[azureml.data.azure_storage_datastore.AbstractAzureStorageDatastore,
                                azureml.data.azure_data_lake_datastore.AzureDataLakeDatastore]
        :param context: The graph context.
        :type context: azureml.pipeline.core._GraphContext

        :return: The node object.
        :rtype: azureml.pipeline.core.graph.Node
        """
        return super(AdlaStep, self).create_node(
            graph=graph, default_datastore=default_datastore, context=context)
