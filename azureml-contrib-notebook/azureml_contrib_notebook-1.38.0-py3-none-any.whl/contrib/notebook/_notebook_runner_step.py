# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains functionality to create a pipeline step that runs a local notebook as a step in
   Azure Machine Learning Pipelines."""
import json
import ast

from azureml.pipeline.core._python_script_step_base import _PythonScriptStepBase
from azureml.data.data_reference import DataReference
from azureml.pipeline.core import PipelineData, PipelineParameter, OutputPortBinding
from azureml.pipeline.core import InputPortBinding, PortDataReference
from azureml.data.dataset_consumption_config import DatasetConsumptionConfig
from azureml.pipeline.core.pipeline_output_dataset import PipelineOutputFileDataset


class NotebookRunnerStep(_PythonScriptStepBase):
    """Creates a step to run a local notebook as a pipeline step in an Azure Machine Learning.

    :param name: The name of the step.
    :type name: str
    :param notebook_run_config: The associated notebook run config object for this step.
    :type notebook_run_config: azureml.contrib.notebook.NotebookRunConfig
    :param runconfig_pipeline_params: An override of runconfig properties at runtime using key-value pairs,
                            each with name of the runconfig property and PipelineParameter for that property.
    :type runconfig_pipeline_params: dict[str, azureml.pipeline.core.PipelineParameter]
    :param compute_target: [Required] The compute target to use.
    :type compute_target: typing.Union[azureml.core.compute.DsvmCompute,
                        azureml.core.compute.AmlCompute,
                        azureml.core.compute.RemoteCompute,
                        str]
    :param params: A dictionary of name-value pairs to be accessible in notebook.
        This is additional to `parameters` in azureml.contrib.notebook.NotebookRunConfig
        azureml.pipeline.core.PipelineParameters can be provided here.
    :type params: dict
    :param inputs: A list of input port bindings.
    :type inputs: list[typing.Union[azureml.pipeline.core.graph.InputPortBinding,
                    azureml.data.data_reference.DataReference,
                    azureml.pipeline.core.PortDataReference,
                    azureml.pipeline.core.builder.PipelineData,
                    azureml.data.dataset_consumption_config.DatasetConsumptionConfig,
                    azureml.pipeline.core.pipeline_output_dataset.PipelineOutputFileDataset]]
    :param outputs: A list of output port bindings.
    :type outputs: list[typing.Union[azureml.pipeline.core.builder.PipelineData,
                        azureml.pipeline.core.graph.OutputPortBinding,
                        azureml.pipeline.core.pipeline_output_dataset.PipelineOutputFileDataset]]
    :param allow_reuse: Indicates whether the step should reuse previous results when re-run with the same
        settings. Reuse is enabled by default. If the step contents (scripts/dependencies) as well as inputs and
        parameters remain unchanged, the output from the previous run of this step is reused. When reusing
        the step, instead of submitting the job to compute, the results from the previous run are immediately
        made available to any subsequent steps.
    :type allow_reuse: bool
    :param version: An optional version tag to denote a change in functionality for the module.
    :type version: str
    :param output_notebook_pipeline_data_name: The name of the intermediate pipeline data containing
        the output notebook (with output of each cell) of the run. Specifying this would produce an output notebook
        as one of the outputs of the step which can be further passed along in the pipeline.
    :type output_notebook_pipeline_data_name: str
    """

    def __init__(self, name=None, notebook_run_config=None, runconfig_pipeline_params=None, compute_target=None,
                 params=None, inputs=None, outputs=None, allow_reuse=True, version=None,
                 output_notebook_pipeline_data_name=None):
        """Create an Azure ML Pipeline step to run a local notebook as a step in azure machine learning pipeline.

        :param name: The name of the step.
        :type name: str
        :param notebook_run_config: The associated notebook run config object for this step.
        :type notebook_run_config: azureml.contrib.notebook.NotebookRunConfig
        :param runconfig_pipeline_params: An override of runconfig properties at runtime using key-value pairs,
                                each with name of the runconfig property and PipelineParameter for that property.
        :type runconfig_pipeline_params: dict[str, (azureml.pipeline.core.PipelineParameter]
        :param compute_target: [Required] The compute target to use.
        :type compute_target: typing.Union[azureml.core.compute.DsvmCompute,
                            azureml.core.compute.AmlCompute,
                            azureml.core.compute.RemoteCompute,
                            str]
        :param params: A dictionary of name-value pairs to be accessible in notebook.
            This is additional to `parameters` in azureml.contrib.notebook.NotebookRunConfig
            azureml.pipeline.core.PipelineParameters can be provided here.
        :type params: dict
        :param inputs: A list of input port bindings.
        :type inputs: list[typing.Union[azureml.pipeline.core.graph.InputPortBinding,
                        azureml.data.data_reference.DataReference,
                        azureml.pipeline.core.PortDataReference,
                        azureml.pipeline.core.builder.PipelineData,
                        azureml.data.dataset_consumption_config.DatasetConsumptionConfig,
                        azureml.pipeline.core.pipeline_output_dataset.PipelineOutputFileDataset]]
        :param outputs: A list of output port bindings.
        :type outputs: list[typing.Union[azureml.pipeline.core.builder.PipelineData,
                        azureml.pipeline.core.graph.OutputPortBinding,
                        azureml.pipeline.core.pipeline_output_dataset.PipelineOutputFileDataset]]
        :param allow_reuse: Indicates whether the step should reuse previous results when re-run with the same
            settings. Reuse is enabled by default. If the step contents (scripts/dependencies) as well as inputs and
            parameters remain unchanged, the output from the previous run of this step is reused. When reusing
            the step, instead of submitting the job to compute, the results from the previous run are immediately
            made available to any subsequent steps.
        :type allow_reuse: bool
        :param version: An optional version tag to denote a change in functionality for the module.
        :type version: str
        :param output_notebook_pipeline_data_name: Name of the intermediate pipeline data containing
            output notebook (with output of each cell) of the run. Specifying this would produce output notebook
            as one of the output of the step which can be further passed along in the pipeline.
        :type allow_reuse: str
        """
        # the following args are required
        if None in [name, notebook_run_config, compute_target]:
            raise ValueError("name, notebook_run_config, compute_target parameters are required")

        # resetting compute_target, arguments as it will not be used in NotebookRunnerStep
        notebook_run_config.run_config._target = None

        run_config = notebook_run_config.run_config
        source_directory = notebook_run_config.source_directory
        script_name = notebook_run_config.script
        self._output_notebook_pipeline_data_name = output_notebook_pipeline_data_name

        super(NotebookRunnerStep, self).__init__(name=name, script_name=script_name,
                                                 arguments=notebook_run_config.arguments,
                                                 compute_target=compute_target,
                                                 runconfig=run_config,
                                                 runconfig_pipeline_params=runconfig_pipeline_params,
                                                 params=params, inputs=inputs, outputs=outputs,
                                                 source_directory=source_directory, allow_reuse=allow_reuse,
                                                 version=version)

    def create_node(self, graph, default_datastore, context):
        """
        Create a node for a Python script step.

        :param graph: The graph object.
        :type graph: azureml.pipeline.core.graph.Graph
        :param default_datastore: The default datastore.
        :type default_datastore: azureml.data.azure_storage_datastore.AbstractAzureStorageDatastore or
            azureml.data.azure_data_lake_datastore.AzureDataLakeDatastore
        :param context: The graph context.
        :type context: azureml.pipeline.core._GraphContext

        :return: The created node.
        :rtype: azureml.pipeline.core.graph.Node
        """
        # Enable output notebook as pipeline data if user chose to
        # allow output notebook as pipeline data by providing the
        # output notebook pipeline data name
        if (self._output_notebook_pipeline_data_name):
            output_notebook_name = self._output_notebook_pipeline_data_name
            output_notebook = PipelineData(name=output_notebook_name,
                                           datastore=default_datastore,
                                           pipeline_output_name=output_notebook_name)
            output_notebook._set_producer(self)
            self._outputs.append(output_notebook)

        self._resolve_notebook_parameters()
        return super(NotebookRunnerStep, self).create_node(graph, default_datastore, context)

    def _resolve_notebook_parameters(self):
        new_params = {}

        for input_data_ref in self._inputs:
            name = NotebookRunnerStep._get_io_name_by_type(input_data_ref)
            new_params[name] = NotebookRunnerStep._prefix_data_reference(name)

        for output_data_ref in self._outputs:
            name = NotebookRunnerStep._get_io_name_by_type(output_data_ref)
            # Replace the -o arg as the pipeline data name if user chose to
            # allow output notebook as pipeline data
            if (self._output_notebook_pipeline_data_name and name == self._output_notebook_pipeline_data_name):
                pipeline_output_notebook = "/".join([NotebookRunnerStep._prefix_data_reference(name),
                                                     self._get_or_modify_arg_by_prefix("-o")])
                self._get_or_modify_arg_by_prefix("-o", pipeline_output_notebook)
            else:
                new_params[name] = NotebookRunnerStep._prefix_data_reference(name)

        for key, value in self._params.items():
            if (isinstance(value, PipelineParameter)):
                new_params[key] = NotebookRunnerStep._prefix_param(key)
            else:
                new_params[key] = value

        self._add_to_notebook_parameters(new_params)

    def _add_to_notebook_parameters(self, params):
        notebook_params = ast.literal_eval(self._get_or_modify_arg_by_prefix("-n"))
        notebook_params.update(params)
        self._get_or_modify_arg_by_prefix("-n", json.dumps(notebook_params))

    def _get_or_modify_arg_by_prefix(self, prefix, new_value=None):
        last_arg = None
        arg_value = None

        for i in range(len(self._arguments)):
            if (last_arg and last_arg == prefix):
                if new_value:
                    self._arguments[i] = new_value
                arg_value = self._arguments[i]
                break

            last_arg = self._arguments[i]

        return arg_value

    @staticmethod
    def _get_io_name_by_type(io_object):
        if (isinstance(io_object, PipelineData) or isinstance(io_object, OutputPortBinding)
                or isinstance(io_object, InputPortBinding) or isinstance(io_object, DatasetConsumptionConfig)
                or isinstance(io_object, PipelineOutputFileDataset)):
            return io_object.name
        elif (isinstance(io_object, DataReference) or isinstance(io_object, PortDataReference)):
            return io_object.data_reference_name
        else:
            raise TypeError(
                "Type: " + str(type(io_object)) + " not supported. " + "Input or output should be of one of \
                these types: " + "PipelineData, OutputPortBinding, InputPortBinding, " + "DataReference,\
                 PortDataReference, DatasetConsumptionConfig, " + "PipelineOutputFileDataset.")

    @staticmethod
    def _prefix_data_reference(data_reference_name):
        """Get data reference name with prefix.

        :param data_reference_name: data reference name
        :type data_reference_name: str

        :return: data reference name with prefix
        :rtype: str
        """
        return "$AZUREML_DATAREFERENCE_{0}".format(data_reference_name)

    @staticmethod
    def _prefix_param(param_name):
        """Get parameter with prefix.

        :param param_name: param name
        :type param_name: str

        :return: parameter with prefix
        :rtype: str
        """
        return "$AML_PARAMETER_{0}".format(param_name)
