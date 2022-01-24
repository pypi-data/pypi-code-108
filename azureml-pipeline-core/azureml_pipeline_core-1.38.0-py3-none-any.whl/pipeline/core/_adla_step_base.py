# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""_adla_step_base.py, implementation of AdlaStep (module for adding a adla step as a node)."""
from azureml.pipeline.core import PipelineStep
from azureml.pipeline.core.graph import ParamDef
from azureml.pipeline.core._module_builder import _ModuleBuilder

import logging


class _AdlaStepBase(PipelineStep):
    """Adds a step to run U-SQL script using Azure Data Lake Analytics.

    See example of using this step in notebook https://aka.ms/pl-adla

    .. remarks::

        You can use `@@name@@` syntax in your script to refer to inputs, outputs, and params.

        * if `name` is the name of an input or output port binding, any occurrences of `@@name@@` in the script
          are replaced with actual data path of corresponding port binding.
        * if `name` matches any key in `params` dict, any occurrences of `@@name@@` will be replaced with
          corresponding value in dict.

    :param script_name: name of usql script (relative to source_directory)
    :type script_name: str
    :param name: Name of the step.  If unspecified, script_name will be used
    :type name: str
    :param inputs: List of input port bindings
    :type inputs: list[azureml.pipeline.core.graph.InputPortBinding, azureml.data.data_reference.DataReference,
                  azureml.pipeline.core.PortDataReference, azureml.pipeline.core.builder.PipelineData,
                  azureml.core.Dataset, azureml.data.dataset_definition.DatasetDefinition,
                  azureml.pipeline.core.PipelineDataset]
    :param outputs: List of output port bindings
    :type outputs: list[azureml.pipeline.core.builder.PipelineData, azureml.pipeline.core.graph.OutputPortBinding]
    :param params: Dictionary of name-value pairs
    :type params: dict
    :param degree_of_parallelism: the degree of parallelism to use for this job
    :type degree_of_parallelism: int
    :param priority: the priority value to use for the current job
    :type priority: int
    :param runtime_version: the runtime version of the Data Lake Analytics engine
    :type runtime_version: str
    :param compute_target: the ADLA compute to use for this job
    :type compute_target: azureml.core.compute.AdlaCompute, str
    :param source_directory: folder that contains the script, assemblies etc.
    :type source_directory: str
    :param allow_reuse: Whether the step should reuse previous results when re-run with the same settings.
        Reuse is enabled by default. If the step contents (scripts/dependencies) as well as inputs and
        parameters remain unchanged, the output from the previous run of this step is reused. When reusing
        the step, instead of submitting the job to compute, the results from the previous run are immediately
        made available to any subsequent steps.
    :type allow_reuse: bool
    :param version: Optional version tag to denote a change in functionality for the step
    :type version: str
    :param hash_paths: List of paths to hash when checking for changes to the step contents.  If there
            are no changes detected, the pipeline will reuse the step contents from a previous run.  By default
            contents of the source_directory is hashed (except files listed in .amlignore or .gitignore).
            (DEPRECATED), no longer needed.
    :type hash_paths: list
    """

    def __init__(self, script_name, name=None,
                 inputs=None, outputs=None, params=None, degree_of_parallelism=None,
                 priority=None, runtime_version=None, compute_target=None, source_directory=None,
                 allow_reuse=True, version=None, hash_paths=None):
        """
        Initialize AdlaStep.

        :param script_name: name of usql script (relative to source_directory)
        :type script_name: str
        :param name: Name of the step.  If unspecified, script_name will be used
        :type name: str
        :param inputs: List of input port bindings
        :type inputs: list[azureml.pipeline.core.graph.InputPortBinding, azureml.data.data_reference.DataReference,
                      azureml.pipeline.core.PortDataReference, azureml.pipeline.core.builder.PipelineData,
                      azureml.core.Dataset, azureml.data.dataset_definition.DatasetDefinition,
                      azureml.pipeline.core.PipelineDataset]
        :param outputs: List of output port bindings
        :type outputs: list[azureml.pipeline.core.builder.PipelineData, azureml.pipeline.core.graph.OutputPortBinding]
        :param params: Dictionary of name-value pairs
        :type params: dict
        :param degree_of_parallelism: the degree of parallelism to use for this job
        :type degree_of_parallelism: int
        :param priority: the priority value to use for the current job
        :type priority: int
        :param runtime_version: the runtime version of the Data Lake Analytics engine
        :type runtime_version: str
        :param compute_target: the ADLA compute to use for this job
        :type compute_target: azureml.core.compute.AdlaCompute, str
        :param source_directory: folder that contains the script, assemblies etc.
        :type source_directory: str
        :param allow_reuse: Whether the step should reuse previous results when re-run with the same settings.
            Reuse is enabled by default. If the step contents (scripts/dependencies) as well as inputs and
            parameters remain unchanged, the output from the previous run of this step is reused. When reusing
            the step, instead of submitting the job to compute, the results from the previous run are immediately
            made available to any subsequent steps.
        :type allow_reuse: bool
        :param version: Optional version tag to denote a change in functionality for the step
        :type version: str
        :param hash_paths: List of paths to hash when checking for changes to the step contents.  If there
            are no changes detected, the pipeline will reuse the step contents from a previous run.  By default
            contents of the source_directory is hashed (except files listed in .amlignore or .gitignore).
            (DEPRECATED), no longer needed.
        :type hash_paths: list
        """
        if name is None:
            name = script_name
        if script_name is None:
            raise ValueError("script_name is required")
        if not isinstance(script_name, str):
            raise ValueError("script_name must be a string")
        if compute_target is None:
            raise ValueError('compute_target is required')

        self._script_name = script_name
        self._source_directory = source_directory
        self._compute_target = compute_target
        self._params = params or {}
        self._allow_reuse = allow_reuse
        self._version = version
        self._pipeline_params_in_step_params = PipelineStep._get_pipeline_parameters_step_params(params)

        if hash_paths:
            logging.warning("Parameter 'hash_paths' is deprecated, will be removed. "
                            + "All files under source_directory is hashed "
                            + "except files listed in .amlignore or .gitignore.")

        self._degree_of_parallelism = degree_of_parallelism
        self._priority = priority
        self._runtime_version = runtime_version

        PipelineStep._process_pipeline_io(None, inputs, outputs)
        super(_AdlaStepBase, self).__init__(name, inputs, outputs)

    def create_node(self, graph, default_datastore, context):
        """
        Create a node.

        :param graph: graph object
        :type graph: azureml.pipeline.core.graph.Graph
        :param default_datastore: default datastore
        :type default_datastore: typing.Union[azureml.core.AbstractAzureStorageDatastore,
            azureml.core.AzureDataLakeDatastore]
        :param context: context
        :type context: azureml.pipeline.core._GraphContext

        :return: The node object.
        :rtype: azureml.pipeline.core.graph.Node
        """
        source_directory = self.get_source_directory(context, self._source_directory, self._script_name)

        input_bindings, output_bindings = self.create_input_output_bindings(self._inputs, self._outputs,
                                                                            default_datastore)
        from azureml.pipeline.core import Module
        metadata_params = Module._create_adla_metadata_params(self._script_name, context._workspace,
                                                              self._compute_target, self._degree_of_parallelism,
                                                              self._priority, self._runtime_version)

        param_defs = [ParamDef(param) for param in self._params]
        param_defs += [ParamDef(param, is_metadata_param=True) for param in metadata_params]

        module_def = self.create_module_def(execution_type="adlcloud", input_bindings=input_bindings,
                                            output_bindings=output_bindings, param_defs=param_defs,
                                            allow_reuse=self._allow_reuse, version=self._version)

        module_builder = _ModuleBuilder(
            snapshot_root=source_directory,
            context=context,
            module_def=module_def)

        param_values = self._params.copy()
        param_values.update(metadata_params)

        node = graph.add_module_node(self.name, input_bindings, output_bindings, param_values,
                                     module_builder=module_builder)
        PipelineStep.\
            _configure_pipeline_parameters(graph,
                                           node,
                                           pipeline_params_in_step_params=self._pipeline_params_in_step_params)

        return node
