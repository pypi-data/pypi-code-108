# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains functionality to add a step to a pipeline using a version of a :class:`azureml.pipeline.core.Module`."""
from azureml.pipeline.core import PipelineStep, PipelineData
from azureml.data.data_reference import DataReference
from azureml.pipeline.core._python_script_step_base import _PythonScriptStepBase
from azureml.pipeline.core.graph import Module as GraphModule, InputPortBinding, PortDataReference, PipelineDataset
from azureml.pipeline.core._module_parameter_provider import _ModuleParameterProvider
import copy


class ModuleStepBase(PipelineStep):
    """Adds a step to a pipeline that uses a specific module.

    A :class:`azureml.pipeline.steps.ModuleStep` derives from ModuleStepBase and is a node in a pipeline that uses
    an existing :class:`azureml.pipeline.core.Module`, and
    specifically, one of its versions. In order to define which ModuleVersion would eventually be used in the
    submitted pipeline, you can define one of the following when creating the ModuleStep:
    -   :class:`azureml.pipeline.core.ModuleVersion` object
    -   :class:`azureml.pipeline.core.Module` object and a version value
    -   Only Module without a version value; in this case, the version resolution used may vary across submissions.

    You also need to define the mapping between the step's inputs and outputs to the
    :class:`azureml.pipeline.core.ModuleVersion` object's inputs and outputs.

    :param module: The Module of the step.
    :type module: azureml.pipeline.core.Module
    :param version: The version of the Module.
    :type version: str
    :param module_version: The ModuleVersion of the step. Either Module of ModuleVersion must be provided.
    :type module_version: azureml.pipeline.core.ModuleVersion
    :param inputs_map: A dictionary where keys are names of inputs on the ``module_version`` and values are input
                port bindings.
    :type inputs_map: typing.Dict[str, typing.Union[azureml.pipeline.core.graph.InputPortBinding,
                  azureml.data.data_reference.DataReference,
                  azureml.pipeline.core.PortDataReference,
                  azureml.pipeline.core.builder.PipelineData,
                  azureml.core.Dataset,
                  azureml.data.dataset_definition.DatasetDefinition,
                  azureml.pipeline.core.graph.PipelineDataset]]
    :param outputs_map: A dictionary where keys are names of inputs on the ``module_version`` and values are output
                port bindings.
    :type outputs_map: typing.Dict[str, typing.Union[azureml.pipeline.core.graph.OutputPortBinding,
                    azureml.data.data_reference.DataReference,
                    azureml.pipeline.core.PortDataReference,
                    azureml.pipeline.core.builder.PipelineData,
                    azureml.core.Dataset,
                    azureml.data.dataset_definition.DatasetDefinition,
                    azureml.pipeline.core.graph.PipelineDataset]]
    :param runconfig_pipeline_params: Override runconfig properties at runtime using key-value pairs each with
                                    name of the runconfig property and PipelineParameter for that property.

        Supported values: 'NodeCount', 'MpiProcessCountPerNode', 'TensorflowWorkerCount',
        'TensorflowParameterServerCount'

    :type runconfig_pipeline_params: typing.Dict[str, azureml.pipeline.core.graph.PipelineParameter]
    :param arguments: Command line arguments for the script file. The arguments will be delivered
                      to compute via arguments in RunConfiguration.
                      For more details on how to handle arguments such as special symbols, please refer
                      arguments in :class:`azureml.core.RunConfiguration`.
    :type arguments: [str]
    :param params: A dictionary of name-value parameter pairs.
    :type params: typing.Dict[str, str]
    :param _workflow_provider: (Internal use only.) The workflow provider.
    :type _workflow_provider: azureml.pipeline.core._aeva_provider._AevaWorkflowProvider
    """

    def __init__(self, module=None, version=None, module_version=None,
                 inputs_map=None, outputs_map=None,
                 compute_target=None, runconfig=None,
                 runconfig_pipeline_params=None, arguments=None, params=None, name=None,
                 _workflow_provider=None):
        """
        Initialize ModuleStepBase.

        :param module: The Module of the step
        :type module: azureml.pipeline.core.Module
        :param version: The version of the Module
        :type version: str
        :param module_version: The ModuleVersion of the step. Either Module of ModuleVersion must be provided
        :type module_version: azureml.pipeline.core.ModuleVersion
        :param inputs_map: A dictionary where keys are names of inputs on the ``module_version`` and values are input
                port bindings.
        :type inputs_map: typing.Dict[str, typing.Union[azureml.pipeline.core.graph.InputPortBinding,
                  azureml.data.data_reference.DataReference,
                  azureml.pipeline.core.PortDataReference,
                  azureml.pipeline.core.builder.PipelineData,
                  azureml.core.Dataset,
                  azureml.data.dataset_definition.DatasetDefinition,
                  azureml.pipeline.core.graph.PipelineDataset]]
        :param outputs_map: A dictionary where keys are names of inputs on the ``module_version`` and values are output
                port bindings.
        :type outputs_map: typing.Dict[str, typing.Union[azureml.pipeline.core.graph.OutputPortBinding,
                    azureml.data.data_reference.DataReference,
                    azureml.pipeline.core.PortDataReference,
                    azureml.pipeline.core.builder.PipelineData,
                    azureml.core.Dataset,
                    azureml.data.dataset_definition.DatasetDefinition,
                    azureml.pipeline.core.graph.PipelineDataset]]
        :param compute_target: Compute target to use. If unspecified, the target from the runconfig will be used.
            compute_target may be a compute target object or the string name of a compute target on the workspace.
            Optionally if the compute target is not available at pipeline creation time, you may specify a tuple of
            ('compute target name', 'compute target type') to avoid fetching the compute target object (AmlCompute
            type is 'AmlCompute' and RemoteTarget type is 'VirtualMachine')
        :type compute_target: DsvmCompute, AmlCompute, ComputeInstance, RemoteTarget, HDIClusterTarget, str, tuple
        :param runconfig: The RunConfiguration to use, optional. A RunConfiguration can be used to specify additional
                      requirements for the run, such as conda dependencies and a docker image.
        :type runconfig: azureml.core.runconfig.RunConfiguration
        :param runconfig_pipeline_params: Override runconfig properties at runtime using key-value pairs each with
                                        name of the runconfig property and PipelineParameter for that property.

            Supported values: 'NodeCount', 'MpiProcessCountPerNode', 'TensorflowWorkerCount',
                          'TensorflowParameterServerCount'

        :type runconfig_pipeline_params: typing.Dict[str, azureml.pipeline.core.graph.PipelineParameter]
        :param arguments: Command line arguments for the script file. The arguments will be delivered
                          to compute via arguments in RunConfiguration.
                          For more details how to handle arguments such as special symbols, please refer
                          arguments in :class:`azureml.core.RunConfiguration`
        :type arguments: [str]
        :param params: A dictionary of name-value pairs.
        :type params: typing.Dict[str, str]
        :param _workflow_provider: (Internal use only.) The workflow provider.
        :type _workflow_provider: azureml.pipeline.core._aeva_provider._AevaWorkflowProvider
        """
        _workflow_provider = _workflow_provider
        if outputs_map is None:
            outputs_map = {}
        if inputs_map is None:
            inputs_map = {}
        if params is None:
            params = {}
        if arguments is None:
            arguments = []
        if module is None and module_version is None:
            raise ValueError('Exactly one of module or module_version is required but both are missing')
        if module is not None and module_version is not None:
            raise ValueError('Exactly one of module or module_version is required but both are provided')

        self._params = params
        self._runconfig_pipeline_params = runconfig_pipeline_params

        if compute_target is None and runconfig is not None:
            self._compute_target = runconfig.target
        else:
            self._compute_target = compute_target
        self._runconfig = runconfig
        self._pipeline_params_implicit = PipelineStep._get_pipeline_parameters_implicit(arguments=arguments)
        self._pipeline_params_in_step_params = PipelineStep._get_pipeline_parameters_step_params(params)
        PipelineStep._validate_params(self._params, self._runconfig_pipeline_params)
        self._pipeline_params_runconfig = PipelineStep._get_pipeline_parameters_runconfig(runconfig_pipeline_params)

        self._update_param_bindings()

        name = name
        if module_version is not None:
            if name is None:
                name = module_version.module(_workflow_provider=_workflow_provider).name
            self._module_version = module_version
            self._version = module_version.version
        else:
            if name is None:
                name = module.name
            self._module = module
            self._version = version
            self._module_version = None
        self._module_wiring = {"inputs": inputs_map, "outputs": outputs_map}
        keys = inputs_map.keys()
        io_refs = {}
        for key in keys:
            if isinstance(inputs_map[key], tuple):
                inputs_map[key] = PipelineStep._tuple_to_ioref(inputs_map[key], io_refs,
                                                               lambda e: self._update_mapped_inputs(e, key))
            else:
                preprocessed_obj = inputs_map[key]
                inputs_map[key] = self._update_mapped_inputs(inputs_map[key], key)
                io_refs[preprocessed_obj] = inputs_map[key]
        keys = outputs_map.keys()
        for key in keys:
            if isinstance(outputs_map[key], tuple):
                outputs_map[key] = PipelineStep._tuple_to_ioref(outputs_map[key], io_refs,
                                                                lambda e: self._update_mapped_outputs(e, key))
            else:
                preprocessed_obj = outputs_map[key]
                outputs_map[key] = self._update_mapped_outputs(outputs_map[key], key)
                outputs_map[key]._output_name = key
                io_refs[preprocessed_obj] = outputs_map[key]
        PipelineStep._replace_ioref(arguments, io_refs)
        for index in range(0, len(arguments)):
            if arguments[index] in io_refs:
                arguments[index] = io_refs[arguments[index]]

        inputs = list(inputs_map.values())
        outputs = list(outputs_map.values())
        super(ModuleStepBase, self).__init__(name, inputs, outputs, arguments=arguments)

    @staticmethod
    def _update_mapped_inputs(entity, name):
        return ModuleStepBase._update_mapped_names(entity, name, is_output=False)

    @staticmethod
    def _update_mapped_outputs(entity, name):
        return ModuleStepBase._update_mapped_names(entity, name, is_output=True)

    @staticmethod
    def _update_mapped_names(entity, name, is_output):
        cloned_entity = copy.copy(entity)
        cloned_entity._name = name
        if is_output:
            # The cloned version of this output will be used when building the graph
            entity._cloned_source = cloned_entity
        return cloned_entity

    # automatically add pipeline params to param binding
    def _update_param_bindings(self):
        for pipeline_param in self._pipeline_params_implicit.values():
            if pipeline_param.name not in self._params:
                self._params[pipeline_param.name] = pipeline_param
            else:
                # example: if the user specifies a non-pipeline param and a pipeline param with same name
                raise Exception('Parameter name {0} is already in use'.format(pipeline_param.name))

    def create_node(self, graph, default_datastore, context):
        """
        Create a pipeline graph node.

        :param graph: The graph to add the node to.
        :type graph: azureml.pipeline.core.graph.Graph
        :param default_datastore: The default datastore to use for this step.
        :type default_datastore: azureml.data.azure_storage_datastore.AbstractAzureStorageDatastore or
            azureml.data.azure_data_lake_datastore.AzureDataLakeDatastore
        :param context: (Internal use only.) The graph context object.
        :type context: azureml.pipeline.core._GraphContext

        :return: The node object.
        :rtype: azureml.pipeline.core.graph.Node
        """
        if self._module_version is None:
            self._module_version = self._module.resolve(self._version)

        input_bindings, output_bindings = self.create_input_output_bindings(self._inputs, self._outputs,
                                                                            default_datastore)

        # repopulating the wiring with the processed bindings
        output_bindings_dict = {}
        for ob in output_bindings:
            output_bindings_dict[ob.name] = ob

        input_bindings_dict = {}
        for ib in input_bindings:
            input_bindings_dict[ib.name] = ib

        output_wiring = {}
        for wiring_target in self._module_wiring["outputs"].keys():
            output_name = self._name_of(self._module_wiring["outputs"][wiring_target])
            processed_output = output_bindings_dict[output_name]
            output_wiring[wiring_target] = processed_output

        input_wiring = {}
        for wiring_target in self._module_wiring["inputs"].keys():
            input_name = self._name_of(self._module_wiring["inputs"][wiring_target])
            processed_input = input_bindings_dict[input_name]
            input_wiring[wiring_target] = processed_input
            wired_input = self._module_wiring["inputs"][wiring_target]
            path_on_compute = ""
            if isinstance(wired_input, InputPortBinding):
                path_on_compute = wired_input.path_on_compute
            if isinstance(wired_input, DataReference):
                path_on_compute = wired_input.path_on_compute
            if isinstance(wired_input, PortDataReference):
                path_on_compute = wired_input._data_reference.path_on_compute
            if isinstance(wired_input, PipelineData):
                path_on_compute = wired_input._output_path_on_compute
            if isinstance(wired_input, PipelineDataset):
                path_on_compute = wired_input.path_on_compute
            if path_on_compute != "" and path_on_compute is not None:
                processed_input.path_on_compute = path_on_compute
                processed_input.bind_mode = "download"

        self._module_wiring["inputs"] = input_wiring
        self._module_wiring["outputs"] = output_wiring

        graph_module = GraphModule(module_id=self._module_version.module_version_id,
                                   module_version=self._module_version, default_version=self._version)

        compute_target_name, compute_target_type, compute_target_object = None, None, None
        if self._compute_target is not None:
            compute_target_name, compute_target_type, compute_target_object = _PythonScriptStepBase. \
                _extract_compute_target_params(context, self._compute_target)

        runconfig_str = None
        if self._runconfig is None:
            if self._module_version.runconfig is None:
                runconfig_str = repr(_PythonScriptStepBase._generate_default_runconfig(compute_target_type))
        else:
            runconfig_str = repr(self._runconfig)

        node = graph.add_module_node(self.name, input_bindings, output_bindings, self._params,
                                     module=graph_module, module_wiring=self._module_wiring,
                                     runconfig=runconfig_str)

        PipelineStep.\
            _configure_pipeline_parameters(graph,
                                           node,
                                           pipeline_params_implicit=self._pipeline_params_implicit,
                                           pipeline_params_in_step_params=self._pipeline_params_in_step_params,
                                           pipeline_params_runconfig=self._pipeline_params_runconfig)

        self._set_compute_params_to_node(node,
                                         graph_module.module_version.interface.parameters,
                                         compute_target_name,
                                         compute_target_type,
                                         compute_target_object)

        return node

    @staticmethod
    def _name_of(object):
        if isinstance(object, DataReference):
            return object.data_reference_name
        return object.name

    def _set_compute_params_to_node(self,
                                    node,
                                    parameters,
                                    compute_target_name,
                                    compute_target_type,
                                    compute_target_object):
        """Compute params.

        :param node: node object
        :type node: Node
        :param parameters: Interface Parameters
        :param parameters: StructuredInterfaceParameters
        :param compute_target_name: Compute Target name
        :type compute_target_name: str
        :param compute_target_type: Compute Target type
        :type compute_target_type: str
        :param compute_target_object: Compute Target object
        :type compute_target_object: ComputeTarget
        """
        script_param = next((p for p in parameters if p.name == 'Script'), None)
        script_name = script_param.default_value if script_param is not None else None

        (resolved_arguments, annotated_arguments) = super(ModuleStepBase, self).resolve_input_arguments(
            self._arguments, self._inputs, self._outputs, self._params)
        _ModuleParameterProvider().set_params_to_node(
            node=node, target_name=compute_target_name, target_type=compute_target_type,
            target_object=compute_target_object, script_name=script_name, arguments=resolved_arguments,
            runconfig_params={}, batchai_params={})
