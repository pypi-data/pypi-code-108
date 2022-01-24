# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""_hdinsight_step_base.py, implementation of HDInsightStepBase (module for adding a HDI script as a node)."""
from azureml.core.compute_target import AbstractComputeTarget
from azureml.pipeline.core import PipelineStep
from azureml.pipeline.core._module_builder import _ModuleBuilder
from azureml.pipeline.core._module_parameter_provider import _ModuleParameterProvider
from azureml.pipeline.core._restclients.aeva.models import CloudSettings, HdiRunConfiguration


class _HDInsightStepBase(PipelineStep):
    """
    Add a step to run code in a Hdi cluster.
    """
    def __init__(self, file, compute_target, class_name=None, args=None, name=None, inputs=None, outputs=None,
                 app_name=None, driver_memory=None, driver_cores=None, executor_memory=None,
                 executor_cores=None, num_executors=None, conf=None, jars=None, py_files=None, files=None,
                 archives=None, source_directory=None, queue="default",
                 allow_reuse=True, version=None):
        if args is None:
            args = []
        if files is None:
            files = []
        if archives is None:
            archives = []
        if jars is None:
            jars = []
        if py_files is None:
            py_files = []
        if name is None:
            name = file
        if file is None:
            raise ValueError("file is required")
        if not isinstance(file, str):
            raise ValueError("file must be a string")
        if compute_target is None:
            raise ValueError("compute_target is required")
        if isinstance(compute_target, str):
            compute_name = compute_target
        elif isinstance(compute_target, AbstractComputeTarget):
            compute_name = compute_target.name
        else:
            raise ValueError("compute_target must be a string or a AbstractComputeTarget")

        # handle args
        PipelineStep._process_pipeline_io(args, inputs, outputs)
        self._pipeline_params_implicit = PipelineStep._get_pipeline_parameters_implicit(arguments=args)

        self._params = dict()
        self._source_directory = source_directory
        self._allow_reuse = allow_reuse
        self._script_file = file

        # module runconfig set
        if class_name is not None:
            if not isinstance(class_name, str):
                raise ValueError("class_name must be a string")

        if not isinstance(files, list):
            raise ValueError("files must be a list")

        if not isinstance(archives, list):
            raise ValueError("archives must be a list")

        if not isinstance(jars, list):
            raise ValueError("jars must be a list")

        if not isinstance(py_files, list):
            raise ValueError("py_files must be a list")

        self._module_hdi_run_config = HdiRunConfiguration(file=file, class_name=class_name,
                                                          files=files, archives=archives,
                                                          jars=jars, py_files=py_files)

        # node runconfig set
        if queue is not None:
            if not isinstance(queue, str):
                raise ValueError("queue must be a string")

        if driver_memory is not None:
            if not isinstance(driver_memory, str):
                raise ValueError("driver_memory must be a string")

        if driver_cores is not None:
            if not isinstance(driver_cores, int):
                raise ValueError("driver_cores must be an int")

        if executor_memory is not None:
            if not isinstance(executor_memory, str):
                raise ValueError("executor_memory must be a str")

        if executor_cores is not None:
            if not isinstance(executor_cores, int):
                raise ValueError("executor_cores must be an int")

        if num_executors is not None:
            if not isinstance(num_executors, int):
                raise ValueError("num_executors must be an int")

        if conf is not None:
            if not isinstance(conf, dict):
                raise ValueError("conf must be a dictionary")

        if app_name is not None:
            if not isinstance(app_name, str):
                raise ValueError("app_name must be a string")

        self._node_hdi_run_config = HdiRunConfiguration(compute_name=compute_name, queue=queue,
                                                        driver_memory=driver_memory, driver_cores=driver_cores,
                                                        executor_memory=executor_memory, executor_cores=executor_cores,
                                                        number_executors=num_executors, conf=conf, name=app_name)

        self._version = version
        self._module_param_provider = _ModuleParameterProvider()

        PipelineStep._process_pipeline_io(args, inputs, outputs)
        super(_HDInsightStepBase, self).__init__(name, inputs, outputs, args)

    def create_node(self, graph, default_datastore, context):
        """
        Create a node for HDInsight script step.

        :param graph: graph object
        :type graph: azureml.pipeline.core.graph.Graph
        :param default_datastore: default datastore
        :type default_datastore: azureml.data.azure_storage_datastore.AbstractAzureStorageDatastore or
            azureml.data.azure_data_lake_datastore.AzureDataLakeDatastore
        :param context: context
        :type context: azureml.pipeline.core._GraphContext

        :return: The created node
        :rtype: azureml.pipeline.core.graph.Node
        """
        source_directory = self.get_source_directory(context, self._source_directory, self._script_file)

        input_bindings, output_bindings = self.create_input_output_bindings(self._inputs, self._outputs,
                                                                            default_datastore)
        (self._resolved_arguments, self._annotated_arguments) = \
            super(_HDInsightStepBase, self).resolve_input_arguments(
                self._arguments, self._inputs, self._outputs, self._params)

        module_def = self.create_module_def(execution_type="hdinsightcloud", input_bindings=input_bindings,
                                            output_bindings=output_bindings,
                                            allow_reuse=self._allow_reuse, version=self._version,
                                            arguments=self._annotated_arguments,
                                            cloud_settings=CloudSettings(self._module_hdi_run_config))

        module_builder = _ModuleBuilder(
            snapshot_root=source_directory,
            context=context,
            module_def=module_def,
            arguments=self._annotated_arguments)

        node = graph.add_module_node(self.name,
                                     input_bindings,
                                     output_bindings,
                                     self._params,
                                     module_builder=module_builder,
                                     cloud_settings=CloudSettings(self._node_hdi_run_config))

        # set pipeline parameters on node and on graph
        PipelineStep.\
            _add_pipeline_parameters(graph, self._pipeline_params_implicit)

        return node
