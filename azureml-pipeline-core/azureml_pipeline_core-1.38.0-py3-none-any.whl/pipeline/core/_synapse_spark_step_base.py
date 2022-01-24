# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains functionality to create an Azure ML Synapse step that runs Python script."""

from azureml.core.compute import SynapseCompute
from azureml.core.runconfig import RunConfiguration
from azureml.core.environment import Environment
from azureml.data.constants import DIRECT_MODE, HDFS_MODE
from azureml.data.dataset_consumption_config import DatasetConsumptionConfig
from azureml.data.output_dataset_config import HDFSOutputDatasetConfig
from azureml.pipeline.core import PipelineStep
from azureml.pipeline.core.graph import ParamDef
from azureml.pipeline.core._module_builder import _ModuleBuilder
from azureml.pipeline.core._module_parameter_provider import _ModuleParameterProvider


class _SynapseSparkStepBase(PipelineStep):

    def __init__(self, file, source_directory, compute_target,
                 driver_memory, driver_cores,
                 executor_memory, executor_cores, num_executors,
                 name=None, app_name=None, environment=None,
                 arguments=None, inputs=None, outputs=None,
                 conf=None, py_files=None, jars=None, files=None,
                 allow_reuse=True, version=None):

        PipelineStep._process_pipeline_io(arguments, inputs, outputs)

        if inputs:
            if not isinstance(inputs, list):
                raise ValueError(
                    "inputs should be an array of DatasetConsumptionConfig.")
            for input in inputs:
                if not isinstance(input, DatasetConsumptionConfig):
                    raise ValueError(
                        "inputs should be an array of DatasetConsumptionConfig.")
                if input.mode != DIRECT_MODE and input.mode != HDFS_MODE:
                    raise ValueError(
                        "Currently only DIRECT_MODE or HDFS_MODE of DatasetConsumptionConfig "
                        "is supported for SynapseSparkStep.")

        if outputs:
            if not isinstance(outputs, list):
                raise ValueError(
                    "outputs should be an array of HDFSOutputDatasetConfig")
            for output in outputs:
                if not isinstance(output, HDFSOutputDatasetConfig):
                    raise ValueError(
                        "outputs should be an array of HDFSOutputDatasetConfig")

        if file is None:
            raise ValueError("file is required")
        if not isinstance(file, str):
            raise ValueError("file must be a string")
        self._file = file

        if name is None:
            name = file

        if app_name is None:
            app_name = name

        self._params = {}

        if source_directory is None:
            raise ValueError("source_directory is required")
        if not isinstance(source_directory, str):
            raise ValueError("source_directory must be a string")
        self._source_directory = source_directory

        if compute_target is None:
            raise ValueError("compute_target is required")
        if not isinstance(compute_target, str) and not isinstance(compute_target, SynapseCompute):
            raise ValueError("compute_target must be a str or SynapseCompute")
        if compute_target == 'local':
            raise ValueError("SynapseSparkStep doesn't support local compute")
        self._compute_target = compute_target

        # set up runconfig
        self._runconfig = RunConfiguration()
        self._runconfig.framework = 'pyspark'
        self._runconfig.spark.configuration["spark.app.name"] = app_name

        if driver_memory is None:
            raise ValueError("driver_memory is required")
        if not isinstance(driver_memory, str):
            raise ValueError("driver_memory must be a string")
        self._runconfig.spark.configuration["spark.driver.memory"] = driver_memory

        if driver_cores is None:
            raise ValueError("driver_cores is required")
        if not isinstance(driver_cores, int):
            raise ValueError("driver_cores must be a integer")
        self._runconfig.spark.configuration["spark.driver.cores"] = driver_cores

        if executor_memory is None:
            raise ValueError("executor_memory is required")
        if not isinstance(executor_memory, str):
            raise ValueError("executor_memory must be a string")
        self._runconfig.spark.configuration["spark.executor.memory"] = executor_memory

        if executor_cores is None:
            raise ValueError("executor_cores is required")
        if not isinstance(executor_cores, int):
            raise ValueError("executor_cores must be a integer")
        self._runconfig.spark.configuration["spark.executor.cores"] = executor_cores

        if num_executors is None:
            raise ValueError("num_executors is required")
        if not isinstance(num_executors, int):
            raise ValueError("num_executors must be a integer")
        self._runconfig.spark.configuration["spark.executor.instances"] = num_executors

        if py_files:
            if isinstance(py_files, str):
                py_files = [py_files]
            elif isinstance(py_files, list):
                pass
            else:
                raise ValueError("py_files should be str of [str]")
            self._runconfig.spark.configuration["spark.submit.pyFiles"] = ','.join(
                py_files)

        if jars:
            if isinstance(jars, str):
                jars = [jars]
            elif isinstance(jars, list):
                pass
            else:
                raise ValueError("jars should be str of [str]")
            self._runconfig.spark.configuration["spark.yarn.dist.jars"] = ','.join(
                jars)

        if files:
            if isinstance(files, str):
                files = [files]
            elif isinstance(files, list):
                pass
            else:
                raise ValueError("files should be str of [str]")
            self._runconfig.spark.configuration["spark.files"] = ','.join(
                files)

        if environment:
            if not isinstance(environment, Environment):
                raise ValueError("environment should be a valid object of Environment")
            print("only conda_dependencies specified in environment will be used in Synapse Spark run.")
            self._runconfig.environment = environment

        if conf:
            if not isinstance(conf, dict):
                raise ValueError("conf should be dict")
            for key in conf:
                current_value = self._runconfig.spark.configuration.get(
                    key, None)
                if current_value is None:
                    self._runconfig.spark.configuration[key] = conf[key]
                elif current_value != conf[key]:
                    if key == 'spark.submit.pyFiles' or key == 'spark.files':
                        self._runconfig.spark.configuration[key] = current_value + \
                            ',' + conf[key]
                    elif key == 'spark.yarn.dist.jars':
                        self._runconfig.spark.configuration[key] = current_value + \
                            ',' + conf[key]
                    else:
                        raise ValueError(
                            "The values of the paramater {} have conflict".format(key))

        # these pipeline params automatically added to param def
        self._pipeline_params_implicit = PipelineStep._get_pipeline_parameters_implicit(
            arguments=arguments)
        self._update_param_bindings()

        self._module_param_provider = _ModuleParameterProvider()
        self._allow_reuse = allow_reuse
        self._version = version

        super(_SynapseSparkStepBase, self).__init__(name, inputs,
                                                    outputs, arguments, fix_port_name_collisions=True)

    def create_node(self, graph, default_datastore, context):
        """
        Create a node for Synapse script step.

        :param graph: graph object
        :type graph: azureml.pipeline.core.graph.Graph
        :param default_datastore: default datastore
        :type default_datastore: azureml.data.azure_storage_datastore.AbstractAzureStorageDatastore
        :param context: context
        :type context: azureml.pipeline.core._GraphContext

        :return: The created node
        :rtype: azureml.pipeline.core.graph.Node
        """

        input_bindings, output_bindings = self.create_input_output_bindings(
            self._inputs, self._outputs, default_datastore)

        param_def_dict = {}

        # initialize all the parameters for the module
        for module_provider_param in self._module_param_provider.get_params_list():
            param_def_dict[module_provider_param.name] = module_provider_param

        # user-provided params will override module-provider's params
        # this is needed to set run config params based on user specified value
        for param_name in self._params:
            param_def_dict[param_name] = ParamDef(name=param_name, set_env_var=True,
                                                  default_value=self._params[param_name],
                                                  env_var_override=ParamDef._param_name_to_env_variable(param_name))

        param_defs = param_def_dict.values()

        (self._resolved_arguments, self._annotated_arguments) = \
            super(_SynapseSparkStepBase, self).resolve_input_arguments(
                self._arguments, self._inputs, self._outputs, {})

        module_def = self.create_module_def(execution_type="synapse", input_bindings=input_bindings,
                                            output_bindings=output_bindings, param_defs=list(
                                                param_defs),
                                            allow_reuse=self._allow_reuse, version=self._version,
                                            arguments=self._annotated_arguments)

        module_builder = _ModuleBuilder(
            snapshot_root=self._source_directory,
            context=context,
            module_def=module_def,
            arguments=self._annotated_arguments)

        # workaround to let the backend use the structured argument list in place
        # of the module parameter for arguments
        self._resolved_arguments = ["USE_STRUCTURED_ARGUMENTS"]

        node = graph.add_module_node(self.name, input_bindings, output_bindings, None,
                                     module_builder=module_builder, runconfig=repr(self._runconfig))

        # module parameters not set in self._params are set on the node
        self._set_compute_params_to_node(node, context)

        # set pipeline parameters on node and on graph
        PipelineStep. \
            _configure_pipeline_parameters(graph,
                                           node,
                                           pipeline_params_implicit=self._pipeline_params_implicit,
                                           pipeline_params_runconfig={})

        return node

    def _update_param_bindings(self):
        for pipeline_param in self._pipeline_params_implicit.values():
            self._params[pipeline_param.name] = pipeline_param

    @staticmethod
    def _extract_compute_target_params(context, compute_target):
        """Compute params.

        :param compute_target: Compute target from runconfig .  only Synapse Compute is accepted.
        compute_target may be a compute target object or the string name of a compute target on the workspace.
        Optionally if the compute target is not available at pipeline creation time, you may specify a tuple of
        ('compute target name', 'compute target type').
        :type compute_target: str, tuple
        :param context: context
        :type context: azureml.pipeline.core._GraphContext

        :return: compute target type object
        :rtype: str, str, ComputeTarget
        """
        """ For the compute target parameter, the user may pass in one of:
                  1. Compute target name
                  2. Compute target object
                  3. Tuple of (target name, target type)
        """

        if compute_target is None:
            raise ValueError("compute target is required")

        compute_target_object = None
        if isinstance(compute_target, str):
            compute_target_name = compute_target
            compute_target_object = context.get_target(compute_target_name)
            if compute_target_object.type != SynapseCompute._compute_type:
                raise ValueError(
                    'Compute target tuple only supported for Synapse computes')
            compute_target_type = compute_target_object.type
        elif isinstance(compute_target, tuple):
            if not len(compute_target) == 2:
                raise ValueError(
                    'Compute target tuple must have 2 elements (compute name, compute type)')
            if not isinstance(compute_target[0], str) or not isinstance(compute_target[1], str):
                raise ValueError(
                    'Compute target tuple must consist of 2 strings (compute name, compute type)')
            if compute_target[1] != SynapseCompute._compute_type:
                raise ValueError(
                    'Compute target tuple only supported for Synapse computes')
            compute_target_name = compute_target[0]
            compute_target_type = compute_target[1]
        else:
            compute_target_object = compute_target
            if compute_target_object.type != SynapseCompute._compute_type:
                raise ValueError(
                    'Compute target tuple only supported for Synapse computes')
            compute_target_name = compute_target_object.name
            compute_target_type = compute_target_object.type
        return compute_target_name, compute_target_type, compute_target_object

    def _set_compute_params_to_node(self, node, context):
        """Compute params.
        :param node: node object
        :type node: Node
        :param context: context
        :type context: azureml.pipeline.core._GraphContext
        """
        compute_target_name, compute_target_type, compute_target_object = _SynapseSparkStepBase.\
            _extract_compute_target_params(context, self._compute_target)

        self._module_param_provider.set_params_to_node(
            node=node, target_name=compute_target_name, target_type=compute_target_type,
            target_object=compute_target_object, script_name=self._file, arguments=self._resolved_arguments,
            runconfig_params={}, batchai_params=None)
