# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azureml.pipeline.core._hdinsight_step_base import _HDInsightStepBase


class _HDInsightStep(_HDInsightStepBase):
    # TODO[Pepe]: add more comments: example code
    r"""Creates an Azure ML Pipeline step to run HDInsight Spark jobs.
    :param file: [required] File containing the application to execute. It's a relative path to source_directory.
    :type file: str
    :param compute_target: [required] Hdi Compute name that is attached to AML.
    :type compute_target: str or azureml.core.compute_target.AbstractComputeTarget
    :param class_name: Application Java/Spark main class.
    :type class_name: str
    :param args: Command line arguments for the application.
    :type args: list
    :param name: The name of the step. If unspecified, ``file`` is used.
    :type name: str
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
                    azureml.pipeline.core.pipeline_output_dataset.PipelineOutputFileDataset,
                    azureml.pipeline.core.pipeline_output_dataset.PipelineOutputTabularDataset,
                    azureml.pipeline.core.graph.OutputPortBinding]]
    :param app_name: The name of the HDInsight session.
    :type app_name: str
    :param driver_memory: Amount of memory to use for the HDInsight driver process.
                            It's the same format as JVM memory strings. Use lower-case suffixes,
                            e.g. k, m, g, t, and p, for kibi-, mebi-, gibi-, tebi-, and pebibytes, respectively.
    :type driver_memory: str
    :param driver_cores: Number of cores to use for the HDInsight driver process.
    :type driver_cores: int
    :param executor_memory: Amount of memory to use per HDInsight executor process.
                            It's the same format as JVM memory strings. Use lower-case suffixes,
                            e.g. k, m, g, t, and p, for kibi-, mebi-, gibi-, tebi-, and pebibytes, respectively.
    :type executor_memory: str
    :param executor_cores: Number of cores to use for each HDInsight executor.
    :type executor_cores: int
    :param num_executors: Number of executors to launch for HDInsight session.
    :type num_executors: int
    :param conf: Spark configuration properties.
    :type conf: dict
    :param jars: Jars to be used in HDInsight session.
    :type jars: list
    :param py_files: Python files to be used in HDInsight session.
    :type py_files: list
    :param files: Files to be used in HDInsight session.
    :type files: list
    :param archives: Archives to be used in HDInsight session.
    :type archives: list
    :param source_directory: A folder that contains file, files, archives, jars, py_files used in the step.
    :type source_directory: str
    :param queue: The name of the YARN queue to which submitted.
    :type queue: str
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
    def __init__(self, file, compute_target, class_name=None, args=None, name=None, inputs=None, outputs=None,
                 app_name=None, driver_memory=None, driver_cores=None, executor_memory=None, executor_cores=None,
                 num_executors=None, conf=None, jars=None, py_files=None, files=None, archives=None,
                 source_directory=None, queue="default", allow_reuse=True, version=None):

        super(_HDInsightStep, self).__init__(
            file=file, compute_target=compute_target, class_name=class_name,
            args=args, name=name, inputs=inputs, outputs=outputs, app_name=app_name, driver_memory=driver_memory,
            driver_cores=driver_cores, executor_memory=executor_memory, executor_cores=executor_cores,
            num_executors=num_executors, conf=conf, jars=jars, py_files=py_files, files=files, archives=archives,
            source_directory=source_directory, queue=queue, allow_reuse=allow_reuse, version=version)

    def create_node(self, graph, default_datastore, context):
        return super(_HDInsightStep, self).create_node(
            graph=graph, default_datastore=default_datastore, context=context)
