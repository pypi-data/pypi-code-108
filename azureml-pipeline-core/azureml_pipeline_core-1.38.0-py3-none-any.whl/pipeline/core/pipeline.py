# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Defines the class for creating reusable Azure Machine Learning workflows."""
from azureml.pipeline.core._graph_context import _GraphContext
from azureml.pipeline.core._pipeline_yaml_parser import _PipelineYamlParser
from azureml.pipeline.core.builder import _PipelineGraphBuilder
from azureml.core._experiment_method import experiment_method
import logging


def _submit_pipeline(pipeline, workspace, experiment_name, **kwargs):
    """
    Submit a pipeline.

    :param pipeline: pipeline
    :type pipeline: Pipeline
    :param workspace: workspace
    :type workspace: Workspace
    :param experiment_name: experiment name
    :type experiment_name: str
    :param kwargs: kwargs
    :type kwargs: dict

    :return: PipelineRun object
    :rtype: PipelineRun
    """
    continue_on_step_failure = False
    regenerate_outputs = False
    pipeline_params = None
    parent_run_id = None
    enable_email_notification = None
    credential_passthrough = False
    for key, value in kwargs.items():
        if key == 'continue_on_step_failure':
            continue_on_step_failure = value
        elif key == 'regenerate_outputs':
            regenerate_outputs = value
        elif key == 'pipeline_params':
            pipeline_params = value
            logging.warning("The 'pipeline_params' argument is deprecated. Please use 'pipeline_parameters' instead.")
        elif key == 'pipeline_parameters':
            pipeline_params = value
        elif key == 'parent_run_id':
            parent_run_id = value
        elif key == 'enable_email_notification':
            enable_email_notification = value
        elif key == 'credential_passthrough':
            credential_passthrough = value
    return pipeline.submit(experiment_name, pipeline_parameters=pipeline_params,
                           continue_on_step_failure=continue_on_step_failure,
                           regenerate_outputs=regenerate_outputs, parent_run_id=parent_run_id,
                           enable_email_notification=enable_email_notification,
                           credential_passthrough=credential_passthrough)


class Pipeline(object):
    """
    Represents a collection of steps which can be executed as a reusable Azure Machine Learning workflow.

    Use a Pipeline to create and manage workflows that stitch together various machine learning
    phases. Each machine learning phase, such as data preparation and model training, can consist of one or
    more steps in a Pipeline.

    For an overview of why and when to use Pipelines, see https://aka.ms/pl-concept.

    For an overview on constructing a Pipeline, see https://aka.ms/pl-first-pipeline.

    .. remarks::

        A pipeline is created with a list of steps and a workspace. There are a number of step types which can be
        used in a pipeline. You will select step type based on your machine learning scenario.

        * Azure Machine Learning Pipelines provides built-in steps for common scenarios. Pre-built steps derived
          from PipelineStep are steps that are used in one pipeline. For examples, see the
          :mod:`azureml.pipeline.steps` package and the :class:`azureml.train.automl.runtime.AutoMLStep` class.
        * If your use machine learning workflow calls for creating steps that can be versioned and used across
          different pipelines, then use the functionality in the :class:`azureml.pipeline.core.Module` module.

        Submit a pipeline using :func:`azureml.core.Experiment.submit`. When submit is called,
        a :class:`azureml.pipeline.core.PipelineRun` is created which in turn creates
        :class:`azureml.pipeline.core.StepRun` objects for each step in the workflow. Use these objects to monitor
        the run execution.

        An example to submit a Pipeline is as follows:

        .. code-block:: python

            from azureml.pipeline.core import Pipeline

            pipeline = Pipeline(workspace=ws, steps=steps)
            pipeline_run = experiment.submit(pipeline)

        There are a number of optional settings for a Pipeline which can be specified on submission in the
        :meth:`azureml.pipeline.core.Pipeline.submit`.

        * continue_on_step_failure: Whether to continue pipeline execution if a step fails; the default is False.
          If True, only steps that have no dependency on the output of the failed step will continue execution.
        * regenerate_outputs: Whether to force regeneration of all step outputs and disallow data reuse for
          this run, default is False.
        * pipeline_parameters: Parameters to pipeline execution, dictionary of {name: value}.
          See :class:`azureml.pipeline.core.PipelineParameter` for more details.
        * parent_run_id: You can supply a run id to set the parent run of this pipeline run, which is reflected in
          RunHistory.  The parent run must belong to the same experiment as this pipeline is being submitted to.

        An example to submit a Pipeline using these settings is as follows:

        .. code-block:: python

            from azureml.pipeline.core import Pipeline

            pipeline = Pipeline(workspace=ws, steps=steps)
            pipeline_run = experiment.submit(pipeline,
                                             continue_on_step_failure=True,
                                             regenerate_outputs=True,
                                             pipeline_parameters={"param1": "value1"},
                                             parent_run_id="<run_id>")


    :param workspace: The workspace to submit the Pipeline on.
    :type workspace: azureml.core.workspace.Workspace
    :param steps: The list of steps to execute as part of a Pipeline.
    :type steps: builtin.list
    :param description: The description of the Pipeline.
    :type description: str
    :param default_datastore: The default datastore to use for data connections.
    :type default_datastore: azureml.data.azure_storage_datastore.AbstractAzureStorageDatastore or
            azureml.data.azure_data_lake_datastore.AzureDataLakeDatastore
    :param default_source_directory: The default script directory for steps which execute a script.
    :type default_source_directory: str
    :param resolve_closure: Whether to resolve closure or not (automatically bring in dependent steps).
    :type resolve_closure: bool
    """

    @experiment_method(submit_function=_submit_pipeline)
    def __init__(self, workspace, steps, description=None,
                 default_datastore=None, default_source_directory=None, resolve_closure=True,
                 _workflow_provider=None, _service_endpoint=None, **kwargs):
        """
        Initialize Pipeline.

        :param workspace: The workspace to submit the Pipeline on.
        :type workspace: azureml.core.workspace.Workspace
        :param steps: The list of steps to execute as part of a Pipeline.
        :type steps: builtin.list
        :param description: The description of the Pipeline.
        :type description: str
        :param default_datastore: The default datastore to use for data connections.
        :type default_datastore: azureml.data.azure_storage_datastore.AbstractAzureStorageDatastore or
            azureml.data.azure_data_lake_datastore.AzureDataLakeDatastore
        :param default_source_directory: The default script directory for steps which execute a script.
        :type default_source_directory: str
        :param resolve_closure: Whether resolve closure or not (automatically bring in dependent steps).
        :type resolve_closure: bool
        :param _workflow_provider: The workflow provider, if None one is created.
        :type _workflow_provider: azureml.pipeline.core._aeva_provider._AevaWorkflowProvider
        :param _service_endpoint: The service endpoint, if None it is determined using the workspace.
        :type _service_endpoint: str
        :param kwargs: Custom keyword arguments, reserved for future development
        :type kwargs: dict
        """
        self._name = description

        self._graph_context = _GraphContext("placeholder", workspace=workspace,
                                            default_source_directory=default_source_directory,
                                            workflow_provider=_workflow_provider,
                                            service_endpoint=_service_endpoint)
        self._graph_builder = _PipelineGraphBuilder(resolve_closure=resolve_closure,
                                                    context=self._graph_context,
                                                    default_datastore=default_datastore)
        if 'aether-dev' in self._graph_context.service_endpoint:
            print('Using dev endpoint:', self._graph_context.service_endpoint)
        enable_email_notification = None
        for key, value in kwargs.items():
            if key == 'enable_email_notification':
                enable_email_notification = value
            else:
                raise ValueError('parameter %s is not recognized for Pipeline ' % key)
        self._enable_email_notification = enable_email_notification
        self._graph = self._graph_builder.build(self._name, steps, finalize=False)

    def _set_experiment_name(self, name):
        self._graph_context.experiment_name = name
        if self._graph._name is None:
            self._graph._name = name
        if self._name is None:
            self._name = name

    @property
    def graph(self):
        """
        Get the graph associated with the pipeline. Steps and data inputs appear as nodes in the graph.

        :return: The graph.
        :rtype: azureml.pipeline.core.graph.Graph
        """
        return self._graph

    def service_endpoint(self):
        """
        Get the service endpoint associated with the pipeline.

        :return: The service endpoint.
        :rtype: str
        """
        return self._graph_context.service_endpoint

    def validate(self):
        """
        Validate a pipeline and identify potential errors, such as unconnected inputs.

        .. remarks::

            Examples of validation errors include:

            * missing or unexpected pipeline datasources or step types
            * missing parameters or output definitions for a pipeline datasource or step
            * unconnected inputs
            * pipeline steps that form a loop or cycle

            If validation passes (returns an empty list) and your pipeline doesn't
            work, then see the `Debug and troubleshoot machine learning
            pipelines <https://docs.microsoft.com/azure/machine-learning/how-to-debug-pipelines>`_.

        :return: A list of errors in the pipeline.
        :rtype: builtin.list
        """
        return self.graph.validate()

    def _finalize(self, regenerate_outputs=False):
        """
        Finalize the graph.

        :param regenerate_outputs: Whether to regenerate step outputs.
        :type regenerate_outputs: bool

        :return: Dictionary of {node_id, (resource_id, is_new_resource)}
        :rtype: dict
        """
        return self.graph.finalize(regenerate_outputs=regenerate_outputs)

    def submit(self, experiment_name, pipeline_parameters=None, continue_on_step_failure=False,
               regenerate_outputs=False, parent_run_id=None, credential_passthrough=None, **kwargs):
        """
        Submit a pipeline run. This is equivalent to using :func:`azureml.core.Experiment.submit`.

        Returns the submitted :class:`azureml.pipeline.core.PipelineRun`. Use this object to monitor and
        view details of the run.

        :param experiment_name: The name of the experiment to submit the pipeline on.
        :type experiment_name: str
        :param pipeline_parameters: Parameters to pipeline execution, dictionary of {name: value}.
                                    See :class:`azureml.pipeline.core.PipelineParameter` for more details.
        :type pipeline_parameters: dict
        :param continue_on_step_failure: Indicates whether to continue pipeline execution if a step fails.
            If True, only steps that have no dependency on the output of the failed step will continue execution.
        :type continue_on_step_failure: bool
        :param regenerate_outputs: Indicates whether to force regeneration of all step outputs and disallow data
            reuse for this run. If False, this run may reuse results from previous runs and subsequent runs may reuse
            the results of this run.
        :type regenerate_outputs: bool
        :param parent_run_id: Optional run ID to set for the parent run of this pipeline run, which is reflected in
            RunHistory.  The parent run must belong to same experiment as this pipeline is being submitted to.
        :type parent_run_id: str
        :param credential_passthrough: Optional, if this flag is enabled the remote pipeline job will use the
            credentials of the user that initiated the job. This feature is only available in private preview.
        :return: The submitted pipeline run.
        :rtype: azureml.pipeline.core.run.PipelineRun
        """
        self._set_experiment_name(experiment_name)
        enable_email_notification = None
        for key, value in kwargs.items():
            if key == 'enable_email_notification':
                enable_email_notification = value
            else:
                raise ValueError('parameter %s is not recognized for Pipeline ' % key)

        # overrides submission info notification over pipeline notification
        if enable_email_notification is None:
            enable_email_notification = self._enable_email_notification

        return self.graph.submit(
            pipeline_parameters=pipeline_parameters, continue_on_step_failure=continue_on_step_failure,
            regenerate_outputs=regenerate_outputs, parent_run_id=parent_run_id,
            enable_email_notification=enable_email_notification,
            credential_passthrough=credential_passthrough)

    def publish(self, name=None, description=None, version=None, continue_on_step_failure=None):
        """
        Publish a pipeline and make it available for rerunning.

        Once a Pipeline is published, it can be submitted without the Python code which constructed
        the Pipeline. Returns the created :class:`azureml.pipeline.core.PublishedPipeline`.

        :param name: The name of the published pipeline.
        :type name: str
        :param description: The description of the published pipeline.
        :type description: str
        :param version: The version of the published pipeline.
        :type version: str
        :param continue_on_step_failure: Indicates whether to continue execution of other steps in the PipelineRun
                                         if a step fails; the default is false. If True, only steps that have
                                         no dependency on the output of the failed step will continue execution.
        :type continue_on_step_failure: bool

        :return: Created published pipeline.
        :rtype: azureml.pipeline.core.PublishedPipeline
        """
        return self.graph._save(name=name, description=description, version=version,
                                continue_on_step_failure=continue_on_step_failure,
                                enable_email_notification=self._enable_email_notification)

    @staticmethod
    def load_yaml(workspace, filename, _workflow_provider=None, _service_endpoint=None):
        r"""
        Load a Pipeline from the specified YAML file.

        A YAML file can be used to describe a Pipeline consisting of ModuleSteps.

        .. remarks::
            See below for an example YAML file. The YAML contains a name, default_compute and lists of parameters,
            data references, and steps for the Pipeline. Each step should specify the module, compute and parameter,
            input, and output bindings. Additionally, a step runconfig and arguments can be specified if necessary.

            Sample Yaml file:

            .. code-block:: python

                pipeline:
                    description: SamplePipelineFromYaml
                    parameters:
                        NumIterationsParameter:
                            type: int
                            default: 40
                        DataPathParameter:
                            type: datapath
                            default:
                                datastore: workspaceblobstore
                                path_on_datastore: sample2.txt
                        NodeCountParameter:
                            type: int
                            default: 4
                    data_references:
                        DataReference:
                            datastore: workspaceblobstore
                            path_on_datastore: testfolder/sample.txt
                        Dataset:
                            dataset_name: 'titanic'
                    default_compute: aml-compute
                    steps:
                        PrepareStep:
                            type:  ModuleStep
                            name: "TestModule"
                            compute: aml-compute2
                            runconfig: 'D:\.azureml\default_runconfig.yml'
                            arguments:
                            -'--input1'
                            -input:in1
                            -'--input2'
                            -input:in2
                            -'--input3'
                            -input:in3
                            -'--output'
                            -output:output_data
                            -'--param'
                            -parameter:NUM_ITERATIONS
                            parameters:
                                NUM_ITERATIONS:
                                    source: NumIterationsParameter
                            inputs:
                                in1:
                                    source: Dataset
                                    bind_mode: mount
                                in2:
                                    source: DataReference
                                in3:
                                    source: DataPathParameter
                            outputs:
                                output_data:
                                    destination: Output1
                                    datastore: workspaceblobstore
                                    bind_mode: mount
                        TrainStep:
                            type: ModuleStep
                            name: "TestModule2"
                            version: "2"
                            runconfig: 'D:\.azureml\default_runconfig.yml'
                            arguments:
                            -'--input'
                            -input:train_input
                            -'--output'
                            -output:result
                            -'--param'
                            -parameter:NUM_ITERATIONS
                            parameters:
                                NUM_ITERATIONS: 10
                            runconfig_parameters:
                                NodeCount:
                                    source: NodeCountParameter
                            inputs:
                                train_input:
                                    source: Output1
                                    bind_mode: mount
                            outputs:
                                result:
                                    destination: Output2
                                    datastore: workspaceblobstore
                                    bind_mode: mount


        :param workspace: The workspace to submit the Pipeline on.
        :type workspace: azureml.core.workspace.Workspace
        :param filename: The YAML file which describes the Pipeline.
        :type filename: str
        :param _workflow_provider: The workflow provider.
        :type _workflow_provider: azureml.pipeline.core._aeva_provider._AevaWorkflowProvider
        :param _service_endpoint: The service endpoint, if None, it is determined using the workspace.
        :type _service_endpoint: str
        :return: The constructed Pipeline.
        :rtype: azureml.pipeline.core.Pipeline

        """
        step_objects, description = _PipelineYamlParser.load_yaml(workspace=workspace, filename=filename,
                                                                  _workflow_provider=_workflow_provider,
                                                                  _service_endpoint=_service_endpoint)
        pipeline = Pipeline(workspace=workspace, steps=step_objects, description=description,
                            _workflow_provider=_workflow_provider, _service_endpoint=_service_endpoint)

        return pipeline
