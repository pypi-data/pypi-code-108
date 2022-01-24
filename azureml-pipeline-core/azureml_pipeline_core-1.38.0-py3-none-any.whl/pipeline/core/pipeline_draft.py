# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Defines classes for managing mutable pipelines."""

from collections import OrderedDict
from azureml.pipeline.core.run import PipelineRun
from azureml.core._experiment_method import experiment_method
from azureml._html.utilities import to_html
import os


def _submit_draft(pipeline_draft, workspace, experiment_name, **kwargs):
    """
    Submit a pipeline draft.

    :param pipeline: pipeline draft
    :type pipeline: PipelineDraft
    :param workspace: workspace
    :type workspace: Workspace
    :param experiment_name: experiment name
    :type experiment_name: str
    :param kwargs: kwargs
    :type kwargs: dict

    :return: PipelineRun object
    :rtype: PipelineRun
    """
    pipeline_draft._experiment_name = experiment_name
    return pipeline_draft.submit_run()


class PipelineDraft(object):
    """
    Represents a mutable pipeline which can be used to submit runs and create Published Pipelines.

    Use PipelineDrafts to iterate on Pipelines. PipelineDrafts can be created from scratch, another PipelineDraft,
    or existing pipelines: :class:`azureml.pipeline.core.Pipeline`, :class:`azureml.pipeline.core.PublishedPipeline`,
    or :class:`azureml.pipeline.core.PipelineRun`.

    .. remarks::

        A PipelineDraft can be created from a :class:`azureml.pipeline.core.Pipeline` by using the
        :meth:`azureml.pipeline.core.PipelineDraft.create` function. An example is below:

        .. code-block:: python

            from azureml.pipeline.core import Pipeline, PipelineDraft
            from azureml.pipeline.steps import PythonScriptStep

            train_step = PythonScriptStep(name="Training_Step",
                                          script_name="train.py",
                                          compute_target=aml_compute_target,
                                          source_directory=".")
            pipeline = Pipeline(workspace=ws, steps=[train_step])
            pipeline_draft = PipelineDraft.create(workspace=ws,
                                                  name="TestPipelineDraft",
                                                  description="draft description",
                                                  experiment_name="helloworld",
                                                  pipeline=pipeline,
                                                  continue_on_step_failure=True,
                                                  tags={'dev': 'true'},
                                                  properties={'train': 'value'})

        PipelineDraft.create()'s pipeline parameter can also be a :class:`azureml.pipeline.core.PublishedPipeline`,
        :class:`azureml.pipeline.core.PipelineRun`, or another :class:`azureml.pipeline.core.PipelineDraft`.

        To submit a run from a PipelineDraft use the :meth:`azureml.pipeline.core.PipelineDraft.submit_run` method:

        .. code-block:: python

            pipeline_run = pipeline_draft.submit_run()

        To update a PipelineDraft use the :meth:`azureml.pipeline.core.PipelineDraft.update` method. The update()
        function of a pipeline draft can be used to update the name, description, experiment name, pipeline parameter
        assignments, continue on step failure setting and Pipeline associated with the PipelineDraft.

        .. code-block:: python

            new_train_step = PythonScriptStep(name="New_Training_Step",
                                              script_name="train.py",
                                              compute_target=aml_compute_target,
                                              source_directory=source_directory)

            new_pipeline = Pipeline(workspace=ws, steps=[new_train_step])

            pipeline_draft.update(name="UpdatedPipelineDraft",
                                  description="has updated train step",
                                  pipeline=new_pipeline)


    :param workspace: The workspace object for this PipelineDraft.
    :type workspace: azureml.core.Workspace
    :param id: The ID of the PipelineDraft.
    :type id: str
    :param name: The name of the PipelineDraft.
    :type name: str
    :param description: The description of the PipelineDraft.
    :type description: str
    :param experiment_name: The experiment name for the PipelineDraft.
    :type experiment_name: str
    :param tags: An optional tags dictionary for the PipelineDraft.
    :type tags: typing.Dict[str, str]
    :param properties: An optional properties dictionary for the PipelineDraft.
    :type properties: typing.Dict[str, str]
    :param graph_draft_id: The ID of the graph draft associated with the PipelineDraft.
    :type graph_draft_id: str
    :param parent_pipeline_id: The ID of the parent PublishedPipeline.
    :type parent_pipeline_id: str
    :param parent_pipeline_run_id: The ID of the parent PipelineRun.
    :type parent_pipeline_run_id: str
    :param parent_step_run_ids: A list of the StepRun ID's of the parent PipelineRun.
    :type parent_step_run_ids: builtin.list
    :param parent_pipeline_draft_id: The ID of the parent PipelineDraft.
    :type parent_pipeline_draft_id: str
    :param last_submitted_pipeline_run_id: The ID of the last submitted PipelineRun.
    :type last_submitted_pipeline_run_id: str
    :param _pipeline_draft_provider: (Internal use only.) The PipelineDraft provider.
    :type _pipeline_draft_provider: azureml.pipeline.core._aeva_provider._AevaPipelineDraftProvider
    """

    @experiment_method(submit_function=_submit_draft)
    def __init__(self, workspace, id, name=None, description=None, experiment_name=None, tags=None, properties=None,
                 graph_draft_id=None, parent_pipeline_id=None, parent_pipeline_run_id=None, parent_step_run_ids=None,
                 parent_pipeline_draft_id=None, last_submitted_pipeline_run_id=None, _pipeline_draft_provider=None):
        """
        Initialize PipelineDraft.

        :param workspace: Workspace object for this PipelineDraft.
        :type workspace: azureml.core.Workspace
        :param id: The id of the PipelineDraft.
        :type id: str
        :param name: The name of the PipelineDraft.
        :type name: str
        :param description: The description of the PipelineDraft.
        :type description: str
        :param experiment_name: The experiment name for the PipelineDraft.
        :type experiment_name: str
        :param tags: Tags dictionary for the PipelineDraft.
        :type tags: typing.Dict[str, str]
        :param properties: Properties dictionary for the PipelineDraft.
        :type properties: typing.Dict[str, str]
        :param graph_draft_id: The id of the graph draft associated with the PipelineDraft.
        :type graph_draft_id: str
        :param parent_pipeline_id: The id of the parent PublishedPipeline.
        :type parent_pipeline_id: str
        :param parent_pipeline_run_id: The id of the parent PipelineRun.
        :type parent_pipeline_run_id: str
        :param parent_step_run_ids: A list of the StepRun id's of the parent PipelineRun.
        :type parent_step_run_ids: builtin.list
        :param parent_pipeline_draft_id: The id of the parent PipelineDraft.
        :type parent_pipeline_draft_id: str
        :param last_submitted_pipeline_run_id: The id of the last submitted PipelineRun.
        :type last_submitted_pipeline_run_id: str
        :param _pipeline_draft_provider: The PipelineDraft provider.
        :type _pipeline_draft_provider: azureml.pipeline.core._aeva_provider._AevaPipelineDraftProvider
        """
        self._workspace = workspace
        self._id = id
        self._name = name
        self._description = description
        self._tags = tags
        self._properties = properties
        self._parent_pipeline_id = parent_pipeline_id
        self._parent_pipeline_run_id = parent_pipeline_run_id
        self._parent_step_run_ids = parent_step_run_ids
        self._parent_pipeline_draft_id = parent_pipeline_draft_id
        self._last_submitted_pipeline_run_id = last_submitted_pipeline_run_id
        self._graph_draft_id = graph_draft_id
        self._experiment_name = experiment_name

        self._workspace = workspace
        self._pipeline_draft_provider = _pipeline_draft_provider

    @property
    def id(self):
        """
        Get the ID of the PipelineDraft.

        :return: The id.
        :rtype: str
        """
        return self._id

    @property
    def name(self):
        """
        Tet the name of the PipelineDraft.

        :return: The name.
        :rtype: str
        """
        return self._name

    @property
    def description(self):
        """
        Get the description of the PipelineDraft.

        :return: The description string.
        :rtype: str
        """
        return self._description

    @property
    def tags(self):
        """
        Get the tags of the PipelineDraft.

        :return: The tags dictionary.
        :rtype: dict
        """
        return self._tags

    @property
    def properties(self):
        """
        Get the properties of the PipelineDraft.

        :return: The properties dictionary.
        :rtype: dict
        """
        return self._properties

    @property
    def parent_pipeline_id(self):
        """
        Get the ID of the parent PublishedPipeline of the PipelineDraft.

        :return: The PublishedPipeline ID.
        :rtype: str
        """
        return self._parent_pipeline_id

    @property
    def parent_pipeline_run_id(self):
        """
        Get the ID of the parent PipelineRun of the PipelineDraft.

        :return: The PipelineRun ID.
        :rtype: str
        """
        return self._parent_pipeline_run_id

    @property
    def parent_step_run_ids(self):
        """
        Get the list of StepRun IDs of the parent PipelineRun of the PipelineDraft.

        :return: A list of StepRun IDs.
        :rtype: builtin.list
        """
        return self._parent_step_run_ids

    @property
    def parent_pipeline_draft_id(self):
        """
        Get the ID of the parent PipelineDraft of the PipelineDraft.

        :return: The PipelineDraft ID.
        :rtype: str
        """
        return self._parent_pipeline_draft_id

    @property
    def last_submitted_pipeline_run_id(self):
        """
        Get the ID of the last submitted PipelineRun of the PipelineDraft.

        :return: The PipelineRun ID.
        :rtype: str
        """
        return self._last_submitted_pipeline_run_id

    @staticmethod
    def get(workspace, id, _workflow_provider=None, _service_endpoint=None):
        """
        Get the PipelineDraft with the given ID.

        :param workspace: The workspace the PipelineDraft was created in.
        :type workspace: azureml.core.Workspace
        :param id: The ID of the PipelineDraft.
        :type id: str
        :param _workflow_provider: (Internal use only.) The workflow provider.
        :type _workflow_provider: azureml.pipeline.core._aeva_provider._AevaWorkflowProvider
        :param _service_endpoint: The service endpoint.
        :type _service_endpoint: str

        :return: PipelineDraft object
        :rtype: azureml.pipeline.core.pipeline_draft.PipelineDraft
        """
        from azureml.pipeline.core._graph_context import _GraphContext
        graph_context = _GraphContext('placeholder', workspace,
                                      workflow_provider=_workflow_provider,
                                      service_endpoint=_service_endpoint)
        pipeline_draft_provider = graph_context.workflow_provider.pipeline_draft_provider
        result = pipeline_draft_provider.get_pipeline_draft(workspace, id)
        return result

    @staticmethod
    def create(workspace, pipeline, name=None, description=None, experiment_name=None, pipeline_parameters=None,
               continue_on_step_failure=None, tags=None, properties=None, _workflow_provider=None,
               _service_endpoint=None):
        """
        Create a PipelineDraft.

        :param workspace: The workspace object this PipelineDraft will belong to.
        :type workspace: azureml.core.Workspace
        :param pipeline: The published pipeline or pipeline.
        :type pipeline: azureml.pipeline.core.graph.PublishedPipeline or
            azureml.pipeline.core.Pipeline or azureml.pipeline.core.PipelineRun or azureml.pipeline.core.PipelineDraft
        :param name: The name of the PipelineDraft; only needed when creating from a
            :class:`azureml.pipeline.core.pipeline.Pipeline`.
        :type name: str
        :param description: The description of the PipelineDraft; only needed when creating from a
            :class:`azureml.pipeline.core.pipeline.Pipeline`.
        :type description: str
        :param experiment_name: The experiment name for the PipelineDraft; only needed when creating from a
            :class:`azureml.pipeline.core.pipeline.Pipeline`.
        :type experiment_name: str
        :param pipeline_parameters: An optional dictionary of pipeline parameter assignments for the PipelineDraft;
            only needed when creating from a :class:`azureml.pipeline.core.pipeline.Pipeline`.
        :type pipeline_parameters: typing.Dict[str, str]
        :param continue_on_step_failure: Indicates whether to continue a PipelineRun when a step run fails setting for
            the PipelineDraft; only needed when creating from a :class:`azureml.pipeline.core.pipeline.Pipeline`.
        :type continue_on_step_failure: bool
        :param tags: An optional tags dictionary for the PipelineDraft, only needed when creating from a
            :class:`azureml.pipeline.core.pipeline.Pipeline`.
        :type tags: typing.Dict[str, str]
        :param properties: Optional properties dictionary for the PipelineDraft, only needed when creating from a
            :class:`azureml.pipeline.core.pipeline.Pipeline`.
        :type properties: typing.Dict[str, str]
        :param _service_endpoint: The service endpoint.
        :type _service_endpoint: str
        :param _workflow_provider: (Internal use only.) The workflow provider.
        :type _workflow_provider: azureml.pipeline.core._aeva_provider._AevaWorkflowProvider
        :return: The created PipelineDraft.
        :rtype: azureml.pipeline.core.PipelineDraft
        """
        from azureml.pipeline.core import Pipeline, PublishedPipeline, PipelineRun
        if type(pipeline) not in [Pipeline, PublishedPipeline, PipelineDraft, PipelineRun]:
            raise ValueError("pipeline should be of type Pipeline, PublishedPipeline, PipelineDraft, or PipelineRun")

        from azureml.pipeline.core._graph_context import _GraphContext
        graph_context = _GraphContext('placeholder', workspace,
                                      workflow_provider=_workflow_provider,
                                      service_endpoint=_service_endpoint)
        pipeline_draft_provider = graph_context.workflow_provider.pipeline_draft_provider
        if type(pipeline) is Pipeline:
            pipeline.graph._validate_and_finalize(pipeline_parameters=pipeline_parameters, regenerate_outputs=False)
            if name is None:
                raise ValueError("name can not be None")
            if experiment_name is None:
                raise ValueError("experiment_name can not be None")
            pipeline_draft = pipeline_draft_provider.create_pipeline_draft(workspace, name,
                                                                           description, experiment_name,
                                                                           pipeline.graph, continue_on_step_failure,
                                                                           pipeline_parameters=pipeline_parameters,
                                                                           tags=tags,
                                                                           properties=properties)
        elif type(pipeline) is PipelineDraft:
            pipeline_draft = pipeline_draft_provider.clone_from_pipeline_draft(workspace, pipeline.id)
        elif type(pipeline) is PipelineRun:
            pipeline_draft = pipeline_draft_provider.clone_from_pipeline_run(workspace, pipeline.id)
        elif type(pipeline) is PublishedPipeline:
            pipeline_draft = pipeline_draft_provider.clone_from_published_pipeline(workspace, pipeline.id)
        else:
            raise ValueError("pipeline parameter must be of type Pipeline, PublishedPipeline, "
                             "PipelineRun or PipelineDraft")

        return pipeline_draft

    def get_graph(self, _workflow_provider=None):
        """
        Get the graph associated with the PipelineDraft.

        :param _workflow_provider: (Internal use only.) The workflow provider.
        :type _workflow_provider: azureml.pipeline.core._aeva_provider._AevaWorkflowProvider
        :return: The Graph object.
        :rtype: azureml.pipeline.core.graph.Graph
        """
        from azureml.pipeline.core._graph_context import _GraphContext
        context = _GraphContext('placeholder', self._workspace, workflow_provider=_workflow_provider)
        return self._pipeline_draft_provider.get_graph_draft(context, self.id, self._graph_draft_id)

    def submit_run(self, _workflow_provider=None):
        """
        Submit a PipelineRun from the PipelineDraft.

        :param _workflow_provider: (Internal use only.) The workflow provider.
        :type _workflow_provider: azureml.pipeline.core._aeva_provider._AevaWorkflowProvider
        :return: The submitted PipelineRun.
        :rtype: azureml.pipeline.core.run.PipelineRun
        """
        from azureml.pipeline.core._graph_context import _GraphContext
        context = _GraphContext(self._experiment_name, self._workspace,
                                workflow_provider=_workflow_provider)

        pipeline_run_id = context.workflow_provider.pipeline_draft_provider.submit_run_from_pipeline_draft(self)

        pipeline_run = PipelineRun(experiment=context._experiment, run_id=pipeline_run_id,
                                   _service_endpoint=context.workflow_provider._service_caller._service_endpoint)

        return pipeline_run

    def publish(self, _workflow_provider=None):
        """
        Publish a PublishedPipeline from the PipelineDraft.

        :param _workflow_provider: (Internal use only.) The workflow provider.
        :type _workflow_provider: azureml.pipeline.core._aeva_provider._AevaWorkflowProvider
        :return: The created PublishedPipeline.
        :rtype: azureml.pipeline.core.graph.PublishedPipeline
        """
        return self._pipeline_draft_provider.create_pipeline_from_pipeline_draft(self)

    def delete(self, _workflow_provider=None):
        """
        Delete the PipelineDraft.

        :param _workflow_provider: (Internal use only.) The workflow provider.
        :type _workflow_provider: azureml.pipeline.core._aeva_provider._AevaWorkflowProvider
        """
        self._pipeline_draft_provider.delete_graph_draft(self._graph_draft_id)
        self._pipeline_draft_provider.delete_pipeline_draft(self.id)

    def update(self, pipeline=None, name=None, description=None, experiment_name=None, tags=None,
               pipeline_parameters=None, continue_on_step_failure=None, _workflow_provider=None):
        """
        Update a PipelineDraft.

        The provided fields will be updated.

        :param pipeline: The updated pipeline for the draft.
        :type pipeline: azureml.pipeline.core.Pipeline
        :param name: The name of the PipelineDraft.
        :type name: str
        :param description: The description of the PipelineDraft.
        :type description: str
        :param experiment_name: The experiment name for the PipelineDraft.
        :type experiment_name: str
        :param tags: A tags dictionary for the PipelineDraft.
        :type tags: typing.Dict[str, str]
        :param pipeline_parameters: The pipeline parameter assignments for the PipelineDraft.
        :type pipeline_parameters: typing.Dict[str, str]
        :param continue_on_step_failure: Whether to continue PipelineRun when a step run fails setting for
            the PipelineDraft.
        :type continue_on_step_failure: bool
        :param _workflow_provider: (Internal use only.) The workflow provider.
        :type _workflow_provider: azureml.pipeline.core._aeva_provider._AevaWorkflowProvider
        """
        graph = None
        if pipeline is not None:
            from azureml.pipeline.core import Pipeline
            if not isinstance(pipeline, Pipeline):
                raise ValueError("pipeline should be of type Pipeline")

            pipeline.graph._validate_and_finalize(pipeline_parameters=pipeline_parameters, regenerate_outputs=False)
            graph = pipeline.graph

        updated = self._pipeline_draft_provider.save_pipeline_draft(self._workspace, pipeline_draft_id=self.id,
                                                                    name=name, description=description,
                                                                    experiment_name=experiment_name, graph=graph,
                                                                    continue_on_step_failure=continue_on_step_failure,
                                                                    pipeline_parameters=pipeline_parameters,
                                                                    tags=tags)

        self._name = updated.name
        self._description = updated.description
        self._tags = updated.tags
        self._properties = updated.properties
        self._experiment_name = updated._experiment_name

    @staticmethod
    def list(workspace, tags=None, _workflow_provider=None):
        """
        Get all pipeline drafts in a workspace.

        :param workspace: The workspace from which to list drafts.
        :type workspace: azureml.core.Workspace
        :param tags:  If specified, returns drafts matching specified {*"tag"*: *"value"*}.
        :type tags: dict
        :param _workflow_provider: (Internal use only.) The workflow provider.
        :type _workflow_provider: azureml.pipeline.core._aeva_provider._AevaWorkflowProvider
        :return: A list of :class:`azureml.pipeline.core.pipeline_draft.PipelineDraft` objects.
        :rtype: builtin.list
        """
        from azureml.pipeline.core._graph_context import _GraphContext
        graph_context = _GraphContext('placeholder', workspace,
                                      workflow_provider=_workflow_provider)
        return graph_context.workflow_provider.pipeline_draft_provider.list_pipeline_drafts(workspace, tags=tags)

    def save(self, path=None, _workflow_provider=None):
        """Save the PipelineDraft YAML to a file.

        :param path: The path to save the YAML to. If the path is a directory, the PipelineDraft YAML file is saved at
                     `path/pipeline_name.yml`. If path is None, the current directory is used.
        :type path: str
        :param _workflow_provider: (Internal use only.) The workflow provider.
        :type _workflow_provider: azureml.pipeline.core._aeva_provider._AevaWorkflowProvider
        :return:
        :rtype: None
        """
        if not path:
            path = os.getcwd()

        if os.path.exists(path) and os.path.isdir(path):
            path = os.path.join(path, self.name + ".yml")

        commented_map_dict = self.get_graph()._serialize_to_dict()

        with open(path, 'w') as outfile:
            import azureml._vendor.ruamel.yaml as ruamelyaml
            ruamelyaml.round_trip_dump(commented_map_dict, outfile)

    def _repr_html_(self):
        info = self._get_base_info_dict()
        return to_html(info)

    def _get_base_info_dict(self):
        return OrderedDict([
            ('Name', self.name),
            ('Id', self.id),
            ('Tags', self.tags),
            ('Properties', self.properties),
            ('Last Submitted Pipeline Run Id', self.last_submitted_pipeline_run_id)
        ])

    def __str__(self):
        """Return the string representation of the PipelineDraft."""
        info = self._get_base_info_dict()
        formatted_info = ',\n'.join(["{}: {}".format(k, v) for k, v in info.items()])
        return "Pipeline({0})".format(formatted_info)

    def __repr__(self):
        """Return the representation of the PipelineDraft."""
        return self.__str__()

    def _to_dict_cli(self, verbose=True):
        """
        Serialize this PipelineDraft into a dictionary for CLI output.

        :param verbose: Whether to include all properties.
        :type verbose: bool
        :return: A dictionary of {str, str} name/value pairs
        :rtype: dict
        """
        result_dict = self._get_base_info_dict()
        if verbose:
            result_dict["Description"] = self.description

        return result_dict
