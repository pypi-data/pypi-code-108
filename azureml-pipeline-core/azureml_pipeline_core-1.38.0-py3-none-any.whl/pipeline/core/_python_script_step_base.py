# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""_python_script_step_base.py, implementation of PythonScriptStep (module for adding a Python script as a node)."""
from azureml.core.compute import RemoteCompute, AmlCompute, ComputeInstance
from azureml.core.runconfig import RunConfiguration
from azureml.pipeline.core import PipelineStep
from azureml.pipeline.core.graph import ParamDef
from azureml.pipeline.core._module_builder import _ModuleBuilder
from azureml.pipeline.core._module_parameter_provider import _ModuleParameterProvider

import logging


class _HTSStepConstants:
    HTS_TRAINING_DATASET_PARTITION = "hts-training-dataset-partition"
    HTS_HIERARCHY_BUILDER = "hts-hierarchy-builder"
    HTS_DATA_AGGREGATION = "hts-data-aggregation"
    HTS_AUTOML_TRAINING = "hts-automl-training"
    HTS_PROPORTIONS = "hts-proportions-calculation"
    HTS_INFERENCE_DATASET_PARTITION = "hts-inference-dataset-partition"
    HTS_FORECAST = "hts-forecast-parallel"
    HTS_ALLOCATION = "hts-forecast-allocation"
    HTS_EXPLAIN_ALLOCATION = "hts-explanation-allocation"

    HTS_TRAINING_STEPS = {
        HTS_TRAINING_DATASET_PARTITION, HTS_HIERARCHY_BUILDER,
        HTS_DATA_AGGREGATION, HTS_AUTOML_TRAINING, HTS_PROPORTIONS}
    HTS_INFERENCING_STEPS = {HTS_INFERENCE_DATASET_PARTITION, HTS_FORECAST, HTS_ALLOCATION}


class _PythonScriptStepBase(PipelineStep):
    """
    Add a step to run a Python script in a Pipeline.

    _PythonScriptStepBase is the implementation for the public-facing PythonScriptStep.  This exists so the unit
    tests in azureml-pipeline-core can be implemented without referencing the azureml-pipeline-steps package.
    """

    def __init__(self, script_name=None, name=None, arguments=None, compute_target=None, runconfig=None,
                 runconfig_pipeline_params=None, inputs=None, outputs=None, params=None, source_directory=None,
                 allow_reuse=True, version=None, hash_paths=None, command=None):
        if params is None:
            params = {}
        if name is None:
            name = script_name

        # script_name must be specified for non command run
        if not script_name and not command:
            raise ValueError("script_name is required")
        if script_name and not isinstance(script_name, str):
            raise ValueError("script_name must be a string")

        PipelineStep._process_pipeline_io(arguments, inputs, outputs)

        self._source_directory = source_directory

        if hash_paths:
            logging.warning("Parameter 'hash_paths' is deprecated, will be removed. "
                            + "All files under source_directory are hashed "
                            + "except files listed in .amlignore or .gitignore.")

        self._script_name = script_name
        self._command = command
        if compute_target is None and runconfig is not None:
            self._compute_target = runconfig.target
        else:
            self._compute_target = compute_target
        self._params = params
        self._module_param_provider = _ModuleParameterProvider()
        self._runconfig = runconfig
        self._runconfig_pipeline_params = runconfig_pipeline_params
        self._allow_reuse = allow_reuse
        self._version = version
        # these pipeline params automatically added to param def
        self._pipeline_params_implicit = PipelineStep._get_pipeline_parameters_implicit(arguments=arguments)
        # these pipeline params are not added to param def because they are already mapped to step param
        self._pipeline_params_in_step_params = PipelineStep._get_pipeline_parameters_step_params(params)
        PipelineStep._validate_params(self._params, self._runconfig_pipeline_params)
        self._pipeline_params_runconfig = PipelineStep._get_pipeline_parameters_runconfig(runconfig_pipeline_params)

        self._update_param_bindings()
        self._amlcompute_params = {}

        super(_PythonScriptStepBase, self).__init__(name, inputs, outputs, arguments, fix_port_name_collisions=True)

    def create_node(self, graph, default_datastore, context):
        """
        Create a node for python script step.

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
        if not self._command:
            source_directory = self.get_source_directory(context, self._source_directory, self._script_name)
        else:
            source_directory = self._source_directory

        input_bindings, output_bindings = self.create_input_output_bindings(self._inputs, self._outputs,
                                                                            default_datastore)

        param_def_dict = {}
        # initialize all the parameters for the module
        params_list = self._modify_module_param_for_step(
            self._module_param_provider.get_params_list(), self.name)
        for module_provider_param in params_list:
            param_def_dict[module_provider_param.name] = module_provider_param

        # user-provided params will override module-provider's params
        # this is needed to set run config params based on user specified value
        for param_name in self._params:
            param_def_dict[param_name] = ParamDef(name=param_name, set_env_var=True,
                                                  default_value=self._params[param_name],
                                                  env_var_override=ParamDef._param_name_to_env_variable(param_name))

        param_defs = param_def_dict.values()

        PipelineStep._validate_runconfig_pipeline_params(self._runconfig_pipeline_params, param_defs)

        (self._resolved_arguments, self._annotated_arguments) = \
            super(_PythonScriptStepBase, self).resolve_input_arguments(
                self._arguments, self._inputs, self._outputs, self._params)

        module_def = self.create_module_def(execution_type="escloud", input_bindings=input_bindings,
                                            output_bindings=output_bindings, param_defs=list(param_defs),
                                            allow_reuse=self._allow_reuse, version=self._version,
                                            arguments=self._annotated_arguments)

        module_builder = _ModuleBuilder(
            snapshot_root=source_directory,
            context=context,
            module_def=module_def,
            arguments=self._annotated_arguments)

        # workaround to let the backend use the structured argument list in place
        # of the module parameter for arguments
        self._resolved_arguments = ["USE_STRUCTURED_ARGUMENTS"]

        compute_target_name, compute_target_type, compute_target_object = None, None, None
        if self._compute_target is not None:
            compute_target_name, compute_target_type, compute_target_object = _PythonScriptStepBase.\
                _extract_compute_target_params(context, self._compute_target)
        if self._runconfig is None:
            self._runconfig = _PythonScriptStepBase._generate_default_runconfig(compute_target_type)

        node = graph.add_module_node(self.name, input_bindings, output_bindings, self._params,
                                     module_builder=module_builder, runconfig=repr(self._runconfig))

        # module parameters not set in self._params are set on the node
        self._set_compute_params_to_node(node,
                                         compute_target_name,
                                         compute_target_type,
                                         compute_target_object)

        # set pipeline parameters on node and on graph
        PipelineStep.\
            _configure_pipeline_parameters(graph,
                                           node,
                                           pipeline_params_implicit=self._pipeline_params_implicit,
                                           pipeline_params_in_step_params=self._pipeline_params_in_step_params,
                                           pipeline_params_runconfig=self._pipeline_params_runconfig)

        return node

    # automatically add pipeline params to param binding
    def _update_param_bindings(self):
        for pipeline_param in self._pipeline_params_implicit.values():
            if pipeline_param.name not in self._params:
                self._params[pipeline_param.name] = pipeline_param
            else:
                # example: if the user specifies a non-pipeline param and a pipeline param with same name
                raise Exception('Parameter name {0} is already in use'.format(pipeline_param.name))

    @staticmethod
    def _extract_compute_target_params(context, compute_target):
        """Compute params.

        :param compute_target: Compute target to use.  If unspecified, the target from the runconfig will be used.
        compute_target may be a compute target object or the string name of a compute target on the workspace.
        Optionally if the compute target is not available at pipeline creation time, you may specify a tuple of
        ('compute target name', 'compute target type') to avoid fetching the compute target object (AmlCompute
        type is 'AmlCompute' and RemoteTarget type is 'VirtualMachine')
        :type compute_target: DsvmCompute, AmlCompute, ComputeInstance, RemoteTarget, HDIClusterTarget, str, tuple
        :param context: context
        :type context: azureml.pipeline.core._GraphContext

        :return: compute target name, type and object
        :rtype: str, str, ComputeTarget
        """
        if compute_target is None:
            raise ValueError("compute target is required")

        """ For the compute target parameter, the user may pass in one of:
          1. Compute target name
          2. Compute target object
          3. Tuple of (target name, target type)

          In most cases, we just need to extract the name and type (legacy BatchAI and DSVM being exceptions).
          """
        # TODO:  After DSVM and BatchAi compute types are removed, we won't need to track the compute object
        compute_target_object = None

        if isinstance(compute_target, str):
            compute_target_name = compute_target
            compute_target_object = context.get_target(compute_target_name)
            compute_target_type = compute_target_object.type
        elif isinstance(compute_target, tuple):
            if not len(compute_target) == 2:
                raise ValueError('Compute target tuple must have 2 elements (compute name, compute type)')
            compute_target_name = compute_target[0]
            compute_target_type = compute_target[1]
            if not isinstance(compute_target_name, str) or not isinstance(compute_target_type, str):
                raise ValueError('Compute target tuple must consist of 2 strings (compute name, compute type)')
            if compute_target_type == 'batchai':
                raise ValueError('Compute target tuple not supported for legacy BatchAi computes')
        else:
            compute_target_object = compute_target
            compute_target_name = compute_target_object.name
            compute_target_type = compute_target_object.type
        return compute_target_name, compute_target_type, compute_target_object

    def _set_compute_params_to_node(self,
                                    node,
                                    compute_target_name,
                                    compute_target_type,
                                    compute_target_object):
        """Compute params.

        :param node: node object
        :type node: Node
        :param compute_target_name: Compute Target name
        :type compute_target_name: str
        :param compute_target_type: Compute Target type
        :type compute_target_type: str
        :param compute_target_object: Compute Target object
        :type compute_target_object: ComputeTarget
        """

        self._module_param_provider.set_params_to_node(
            node=node, target_name=compute_target_name, target_type=compute_target_type,
            target_object=compute_target_object, script_name=self._script_name, arguments=self._resolved_arguments,
            runconfig_params={}, batchai_params=self._amlcompute_params, command=self._command)

    def _set_amlcompute_params(self, native_shared_directory=None):
        """
        Set AmlCompute native shared directory param.

        :param native_shared_directory: native shared directory
        :type native_shared_directory: str
        """
        self._amlcompute_params = {'NativeSharedDirectory': native_shared_directory}

    @staticmethod
    def _generate_default_runconfig(target_type):
        """Generate default runconfig for python script step.

        :param target_type: Compute target type
        :type target_type: None, str

        :return: runConfig
        :rtype: RunConfig
        """
        # name and target should already be validated as non None since they were passed to this class directly
        runconfig = RunConfiguration()
        if target_type == AmlCompute._compute_type or \
           target_type == ComputeInstance._compute_type or \
           target_type == RemoteCompute._compute_type:
            runconfig.docker.use_docker = True
        return runconfig

    @staticmethod
    def _get_string_from_dictionary(dictionary_items):
        """_Get string from dictionary.

        :param dictionary_items: dictionary items
        :type dictionary_items: list

        :return: string of dictionary items
        :rtype: str
        """
        items_list = []
        for item in dictionary_items:
            items_list.append("{0}={1}".format(item[0], item[1]))
        return ";".join(items_list)

    @staticmethod
    def _modify_module_param_for_step(params_list, step_name):
        if step_name in _HTSStepConstants.HTS_TRAINING_STEPS:
            params_list.append(ParamDef('RunType', "azureml.HTSTraining", is_optional=True))
        elif step_name in _HTSStepConstants.HTS_INFERENCING_STEPS:
            params_list.append(ParamDef('RunType', "azureml.HTSInferencing", is_optional=True))
        params_list = _ModuleParameterProvider._remove_duplicate_params(params_list)
        return params_list
