# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains functionality to create an Azure ML Synapse step that runs Python script."""
from azureml._base_sdk_common._docstring_wrapper import experimental
from azureml.pipeline.core._synapse_spark_step_base import _SynapseSparkStepBase


@experimental
class SynapseSparkStep(_SynapseSparkStepBase):
    """
    Creates an Azure ML Synapse step that submit and execute Python script.

    .. remarks::

        A SynapseSparkStep is a basic, built-in step to run a Python Spark job on a synapse spark pools. It takes
        a main file name and other optional parameters like arguments for the script, compute target, inputs
        and outputs.

        The best practice for working with SynapseSparkStep is to use a separate folder for scripts and any dependent
        files associated with the step, and specify that folder with the ``source_directory`` parameter.
        Following this best practice has two benefits. First, it helps reduce the size of the snapshot
        created for the step because only what is needed for the step is snapshotted. Second, the step's output
        from a previous run can be reused if there are no changes to the ``source_directory`` that would trigger
        a re-upload of the snapshot.

        .. code-block:: python

            from azureml.core import Dataset
            from azureml.pipeline.steps import SynapseSparkStep
            from azureml.data import HDFSOutputDatasetConfig

            # get input dataset
            input_ds = Dataset.get_by_name(workspace, "weather_ds").as_named_input("weather_ds")

            # register pipeline output as dataset
            output_ds = HDFSOutputDatasetConfig("synapse_step_output",
                                                destination=(ws.datastores['datastore'],"dir")
                                                ).register_on_complete(name="registered_dataset")

            step_1 = SynapseSparkStep(
                name = "synapse_step",
                file = "pyspark_job.py",
                source_directory="./script",
                inputs=[input_ds],
                outputs=[output_ds],
                compute_target = "synapse",
                driver_memory = "7g",
                driver_cores = 4,
                executor_memory = "7g",
                executor_cores = 2,
                num_executors = 1,
                conf = {})

        SynapseSparkStep only supports DatasetConsumptionConfig as input and HDFSOutputDatasetConfig as output.

    :param file: The name of a synapse script relative to source_directory.
    :type file: str
    :param source_directory: A folder that contains Python script, conda env, and other resources used in the step.
    :type source_directory: str
    :param compute_target: The compute target to use.
    :type compute_target: azureml.core.compute.SynapseCompute or str
    :param driver_memory: Amount of memory to use for the driver process.
    :type driver_memory: str
    :param driver_cores: Number of cores to use for the driver process.
    :type driver_cores: int
    :param executor_memory: Amount of memory to use per executor process.
    :type executor_memory: str
    :param executor_cores: Number of cores to use for each executor.
    :type executor_cores: int
    :param num_executors: Number of executors to launch for this session.
    :type num_executors: int
    :param name: The name of the step.  If unspecified, ``file`` is used.
    :type name: str
    :param app_name: The App name used to submit the spark job.
    :type app_name: str
    :param environment: AML environment will be supported in later release.
    :type environment: azureml.core.Environment
    :param arguments: Command line arguments for the Synapse script file.
    :type arguments: list
    :param inputs: A list of inputs.
    :type inputs: list[azureml.data.dataset_consumption_config.DatasetConsumptionConfig]
    :param outputs: A list of outputs.
    :type outputs: list[azureml.data.output_dataset_config.HDFSOutputDatasetConfig]
    :param conf: Spark configuration properties.
    :type conf: dict
    :param py_files: Python files to be used in this session, parameter of livy API.
    :type py_files: list
    :param files: Files to be used in this session, parameter of livy API.
    :type files: list
    :param allow_reuse: Indicates if the step should reuse previous results when re-run with the same settings.
    :type allow_reuse: bool
    :param version: An optional version tag to denote a change in functionality for the step.
    :type version: str
    """

    def __init__(self, file, source_directory, compute_target,
                 driver_memory, driver_cores,
                 executor_memory, executor_cores, num_executors,
                 name=None, app_name=None, environment=None,
                 arguments=None, inputs=None, outputs=None,
                 conf=None, py_files=None, jars=None, files=None,
                 allow_reuse=True, version=None):
        """
        Create an Azure ML Pipeline step that runs spark job on synapse spark pool.

        :param file: The name of a Synapse script relative to ``source_directory``.
        :type file: str
        :param source_directory: A folder that contains Python script, conda env, and other resources used in
                the step.
        :type source_directory: str
        :param compute_target: The compute target to use.
        :type compute_target: azureml.core.compute.SynapseCompute or str
        :param driver_memory: Amount of memory to use for the driver process.
        :type driver_memory: str
        :param driver_cores: Number of cores to use for the driver process.
        :type driver_cores: int
        :param executor_memory: Amount of memory to use per executor process.
        :type executor_memory: str
        :param executor_cores: Number of cores to use for each executor.
        :type executor_cores: int
        :param num_executors: Number of executors to launch for this session.
        :type num_executors: int
        :param name: The name of the step.  If unspecified, ``file`` is used.
        :type name: str
        :param app_name: The App name used to submit the Apache Spark job.
        :type app_name: str
        :param environment: AML environment that will be leveraged in this SynapseSparkStep.
        :type environment: azureml.core.Environment
        :param arguments: Command line arguments for the Synapse script file.
        :type arguments: list
        :param inputs: A list of inputs.
        :type inputs: list[azureml.data.dataset_consumption_config.DatasetConsumptionConfig]
        :param outputs: A list of outputs.
        :type outputs: list[azureml.data.output_dataset_config.HDFSOutputDatasetConfig]
        :param conf: Spark configuration properties.
        :type conf: dict
        :param py_files: Python files to be used in this session, parameter of livy API.
        :type py_files: list
        :param jars: Jar files to be used in this session, parameter of livy API.
        :type jars: list
        :param files: Files to be used in this session, parameter of livy API.
        :type files: list
        :param allow_reuse: Indicates if the step should reuse previous results when re-run with the same settings.
        :type allow_reuse: bool
        :param version: An optional version tag to denote a change in functionality for the step.
        :type version: str
        """
        super(SynapseSparkStep, self).__init__(
            name=name, file=file, source_directory=source_directory,
            arguments=arguments, inputs=inputs, outputs=outputs,
            compute_target=compute_target, environment=environment, app_name=app_name,
            driver_memory=driver_memory, driver_cores=driver_cores, executor_memory=executor_memory,
            executor_cores=executor_cores, num_executors=num_executors, conf=conf, py_files=py_files,
            jars=jars, files=files, allow_reuse=allow_reuse, version=version)

    def create_node(self, graph, default_datastore, context):
        """
        Create a node for Synapse script step.

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
        return super(SynapseSparkStep, self).create_node(
            graph=graph, default_datastore=default_datastore, context=context)
