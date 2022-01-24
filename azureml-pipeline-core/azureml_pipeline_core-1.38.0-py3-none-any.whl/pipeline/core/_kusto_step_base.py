# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""To add a step to run a Kusto notebook."""
from azureml.pipeline.core import PipelineStep, PipelineData, OutputPortBinding
from azureml.pipeline.core.graph import ParamDef
from azureml.pipeline.core._module_builder import _ModuleBuilder
import json


class _KustoStepBase(PipelineStep):
    """
    Initialize KustoStep.

    :param name: Name of the step
    :type name: str
    :param compute_target: Name of the Kusto compute
    :type compute_target: str
    :param database_name: Name of the Kusto database to query from
    :type database_name: str
    :param query_directory: Path to directory that contains a single file with Kusto query
    :type query_directory: str
    :param output: Output port definition for outputs produced by this step
    :type output: azureml.pipeline.core.builder.PipelineData or azureml.pipeline.core.graph.OutputPortBinding
    :param parameter_dict: Dictionary that maps the parameter name to parameter value in Kusto query
    :type parameter_dict: dict
    :param allow_reuse: Boolean that indicates whether the step should reuse previous results with same settings/inputs
    :type allow_reuse: bool
    """

    def __init__(self, name, compute_target, database_name, query_directory, output,
                 parameter_dict=None, allow_reuse=False):
        if name is None:
            raise ValueError('name is required')
        if not isinstance(name, str):
            raise ValueError('name must be a string')
        if compute_target is None:
            raise ValueError('compute_target is required')
        if not isinstance(compute_target, str):
            raise ValueError('compute_target must be a string')
        if database_name is None:
            raise ValueError('database_name is required')
        if not isinstance(database_name, str):
            raise ValueError('database_name must be a string')
        if query_directory is None:
            raise ValueError('query_directory is required')
        if not isinstance(query_directory, str):
            raise ValueError('query_directory must be a string')
        if output is None:
            raise ValueError('output is required')
        if not isinstance(output, OutputPortBinding) and not isinstance(output, PipelineData):
            raise ValueError('output must be type PipelineData or OutputPortBinding')
        if parameter_dict is not None:
            if isinstance(parameter_dict, dict):
                self._parameter_dict_string = json.dumps(parameter_dict)
            else:
                raise ValueError('parameter_dict must be a dictionary')
        else:
            self._parameter_dict_string = " "

        self._name = name
        self._compute_target = compute_target
        self._database_name = database_name
        self._query_directory = query_directory
        self._allow_reuse = allow_reuse
        self._output = output

        self._params = dict()
        self._params['compute_name'] = self._compute_target
        self._params['database_name'] = self._database_name
        self._params['parameter_dict'] = self._parameter_dict_string

        super(_KustoStepBase, self).__init__(
            name,
            inputs=[],
            outputs=[self._output])

    def create_node(self, graph, default_datastore, context):
        """
        Create a node from this Kusto step and add to the given graph.

        :param graph: The graph object to add the node to.
        :type graph: azureml.pipeline.core.graph.Graph
        :param default_datastore: default datastore
        :type default_datastore: azureml.core.AbstractAzureStorageDatastore
        :param context: The graph context.
        :type context: azureml.pipeline.core._GraphContext

        :return: The created node.
        :rtype: azureml.pipeline.core.graph.Node
        """

        input_bindings, output_bindings = self.create_input_output_bindings([], [self._output], default_datastore)

        param_defs = list()
        param_defs.append(ParamDef('compute_name', self._compute_target, is_metadata_param=True))
        param_defs.append(ParamDef('database_name', self._database_name, is_metadata_param=True))
        param_defs.append(ParamDef('parameter_dict', self._parameter_dict_string))

        module_def = self.create_module_def(execution_type="kustocloud", input_bindings=input_bindings,
                                            output_bindings=output_bindings, param_defs=param_defs,
                                            allow_reuse=self._allow_reuse)

        module_builder = _ModuleBuilder(
            snapshot_root=self._query_directory,
            context=context,
            module_def=module_def)

        node = graph.add_module_node(name=self._name, input_bindings=input_bindings, output_bindings=output_bindings,
                                     param_bindings=self._params, module_builder=module_builder)

        return node
