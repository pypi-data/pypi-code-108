# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import os
import sys
from contextlib import contextmanager

from azureml._base_sdk_common.common import set_correlation_id, CLICommandOutput
from azureml._base_sdk_common.cli_wrapper._common import get_cli_specific_output, get_workspace_or_default
from azureml.pipeline.core import PublishedPipeline, PipelineRun, Pipeline, Schedule, PipelineDraft
from azureml.core import Experiment


def _setup_and_get_workspace(workspace_name, resource_group_name):
    set_correlation_id()

    workspace_object = get_workspace_or_default(workspace_name=workspace_name, resource_group=resource_group_name)
    return workspace_object


def _add_run_properties(info_dict, run_object):
    """Fill in additional properties for a pipeline run"""
    if hasattr(run_object._client.run_dto, 'start_time_utc')\
            and run_object._client.run_dto.start_time_utc is not None:
        info_dict['StartDate'] = run_object._client.run_dto.start_time_utc.isoformat()

    if hasattr(run_object._client.run_dto, 'end_time_utc')\
            and run_object._client.run_dto.end_time_utc is not None:
        info_dict['EndDate'] = run_object._client.run_dto.end_time_utc.isoformat()

    properties = run_object.get_properties()
    if 'azureml.pipelineid' in properties:
        info_dict['PiplineId'] = properties['azureml.pipelineid']


@contextmanager
def _silence_stdout():
    new_target = open(os.devnull, "w")
    old_target = sys.stdout
    sys.stdout = new_target
    try:
        yield new_target
    finally:
        sys.stdout = old_target


def list_pipelines(workspace_name=None, resource_group_name=None, output_file=None):
    """List the published pipelines and respective schedules in a workspace."""
    with _silence_stdout():
        workspace_object = _setup_and_get_workspace(workspace_name=workspace_name,
                                                    resource_group_name=resource_group_name)

        pipelines = PublishedPipeline.list(workspace_object)

        serialized_pipeline_list = []
        for pipeline in pipelines:
            serialized_pipeline_list.append("Pipeline:")
            serialized_pipeline_list.append(pipeline._to_dict_cli(verbose=False))
            schedules = Schedule.list(workspace_object, pipeline_id=pipeline.id)

            for schedule in schedules:
                serialized_pipeline_list.append("Schedule:")
                serialized_pipeline_list.append(schedule._to_dict_cli(verbose=False))

        if output_file is not None:
            _write_to_file(output_file, json.dumps(serialized_pipeline_list, indent=4))
        command_output = CLICommandOutput("")
        command_output.merge_dict(serialized_pipeline_list)

        return get_cli_specific_output(command_output)


def show_pipeline(pipeline_id, workspace_name=None, resource_group_name=None, output_file=None):
    """Show the details of a published pipeline and respective schedules."""
    with _silence_stdout():
        workspace_object = _setup_and_get_workspace(workspace_name=workspace_name,
                                                    resource_group_name=resource_group_name)

        pipeline = PublishedPipeline.get(workspace_object, pipeline_id)
        serialized_pipeline_dict = dict()
        serialized_pipeline_dict["Pipeline"] = pipeline._to_dict_cli(verbose=True)

        schedules = Schedule.list(workspace_object, pipeline_id=pipeline_id)
        schedule_list = list()

        for schedule in schedules:
            schedule_list.append(schedule._to_dict_cli(verbose=False))

        serialized_pipeline_dict["Schedules"] = schedule_list
        if output_file is not None:
            _write_to_file(output_file, json.dumps(serialized_pipeline_dict, indent=4))
        command_output = CLICommandOutput("")
        command_output.merge_dict(serialized_pipeline_dict)

        return get_cli_specific_output(command_output)


def enable_pipeline(pipeline_id, workspace_name=None, resource_group_name=None, output_file=None):
    """Enable a pipeline for execution."""
    with _silence_stdout():
        workspace_object = _setup_and_get_workspace(workspace_name=workspace_name,
                                                    resource_group_name=resource_group_name)

        pipeline = PublishedPipeline.get(workspace_object, pipeline_id)
        pipeline.enable()

        pipeline_output = "Pipeline '%s' (%s) was enabled successfully." % (pipeline.name, pipeline.id)
        command_output = CLICommandOutput(pipeline_output)
        if output_file is not None:
            _write_to_file(output_file, json.dumps(pipeline_output, indent=4))
        command_output.set_do_not_print_dict()
        return get_cli_specific_output(command_output)


def disable_pipeline(pipeline_id, workspace_name=None, resource_group_name=None, output_file=None):
    """Disable a pipeline from running."""
    with _silence_stdout():
        workspace_object = _setup_and_get_workspace(workspace_name=workspace_name,
                                                    resource_group_name=resource_group_name)

        pipeline = PublishedPipeline.get(workspace_object, pipeline_id)
        pipeline.disable()

        pipeline_output = "Pipeline '%s' (%s) was disabled successfully." % (pipeline.name, pipeline.id)

        command_output = CLICommandOutput(pipeline_output)
        if output_file is not None:
            _write_to_file(output_file, json.dumps(pipeline_output, indent=4))
        command_output.set_do_not_print_dict()
        return get_cli_specific_output(command_output)


def list_pipeline_steps(run_id, workspace_name=None, resource_group_name=None, output_file=None):
    """List child steps for a pipeline run."""
    with _silence_stdout():
        workspace_object = _setup_and_get_workspace(workspace_name=workspace_name,
                                                    resource_group_name=resource_group_name)

        pipeline_run = PipelineRun.get(workspace=workspace_object, run_id=run_id)
        aeva_graph = pipeline_run.get_graph()

        step_runs = pipeline_run.get_steps()
        serialized_run_list = []
        for step_run in step_runs:
            info_dict = step_run._get_base_info_dict()
            _add_run_properties(info_dict, step_run)

            # Get the step name from the Aeva graph
            if step_run._is_reused:
                node_id = step_run._current_node_id
            else:
                node_id = step_run._node_id
            info_dict['Name'] = aeva_graph.get_node(node_id).name
            serialized_run_list.append(info_dict)

        if output_file is not None:
            _write_to_file(output_file, json.dumps(serialized_run_list, indent=4))
        command_output = CLICommandOutput("")
        command_output.merge_dict(serialized_run_list)

        return get_cli_specific_output(command_output)


def create_schedule(name, pipeline_id, experiment_name, schedule_yaml=None, workspace_name=None,
                    resource_group_name=None):
    """Create a schedule."""
    workspace_object = _setup_and_get_workspace(workspace_name=workspace_name, resource_group_name=resource_group_name)

    schedule_info = {}
    if schedule_yaml is not None:
        schedule_info = Schedule.load_yaml(workspace=workspace_object, filename=schedule_yaml)

    schedule = Schedule.create(workspace_object, pipeline_id=pipeline_id, name=name,
                               experiment_name=experiment_name,
                               recurrence=schedule_info.get("recurrence"),
                               description=schedule_info.get("description"),
                               pipeline_parameters=schedule_info.get("pipeline_parameters"),
                               wait_for_provisioning=schedule_info.get("wait_for_provisioning"),
                               wait_timeout=schedule_info.get("wait_timeout"),
                               datastore=schedule_info.get("datastore_name"),
                               polling_interval=schedule_info.get("polling_interval"),
                               data_path_parameter_name=schedule_info.get("data_path_parameter_name"),
                               continue_on_step_failure=schedule_info.get("continue_on_step_failure"),
                               path_on_datastore=schedule_info.get("path_on_datastore"))
    output_dict = schedule._to_dict_cli(verbose=True)

    command_output = CLICommandOutput("")
    command_output.merge_dict(output_dict)

    return get_cli_specific_output(command_output)


def update_schedule(schedule_id, name=None, status=None, schedule_yaml=None,
                    workspace_name=None, resource_group_name=None):
    """Update a schedule."""
    workspace_object = _setup_and_get_workspace(workspace_name=workspace_name, resource_group_name=resource_group_name)

    schedule = Schedule.get(workspace_object, schedule_id)

    schedule_info = {}
    if schedule_yaml is not None:
        schedule_info = Schedule.load_yaml(workspace=workspace_object, filename=schedule_yaml)

    schedule.update(name=name, description=schedule_info.get("description"),
                    recurrence=schedule_info.get("recurrence"),
                    pipeline_parameters=schedule_info.get("pipeline_parameters"), status=status,
                    wait_for_provisioning=schedule_info.get("wait_for_provisioning"),
                    wait_timeout=schedule_info.get("wait_timeout"),
                    datastore=schedule_info.get("datastore_name"),
                    polling_interval=schedule_info.get("polling_interval"),
                    data_path_parameter_name=schedule_info.get("data_path_parameter_name"),
                    continue_on_step_failure=schedule_info.get("continue_on_step_failure"),
                    path_on_datastore=schedule_info.get("path_on_datastore"))

    command_output = CLICommandOutput("Schedule '%s' (%s) was updated successfully." % (schedule.name,
                                      schedule.id))
    command_output.set_do_not_print_dict()
    return get_cli_specific_output(command_output)


def list_pipeline_runs(schedule_id, workspace_name=None, resource_group_name=None, output_file=None):
    """List pipeline runs generated from a schedule."""
    with _silence_stdout():
        workspace_object = _setup_and_get_workspace(workspace_name=workspace_name,
                                                    resource_group_name=resource_group_name)

        schedule = Schedule.get(workspace_object, schedule_id)
        pipeline_runs = schedule.get_pipeline_runs()
        serialized_run_list = []
        for pipeline_run in pipeline_runs:
            serialized_run_list.append(pipeline_run._to_dict_cli(verbose=False))

        if output_file is not None:
            _write_to_file(output_file, json.dumps(serialized_run_list, indent=4))

        command_output = CLICommandOutput("")
        command_output.merge_dict(serialized_run_list)

        return get_cli_specific_output(command_output)


def show_last_pipeline_run(schedule_id, workspace_name=None, resource_group_name=None, output_file=None):
    """Show last pipeline run for a schedule"""
    with _silence_stdout():
        workspace_object = _setup_and_get_workspace(workspace_name=workspace_name,
                                                    resource_group_name=resource_group_name)

        schedule = Schedule.get(workspace_object, schedule_id)
        pipeline_run = schedule.get_last_pipeline_run()

        output_dict = pipeline_run._get_base_info_dict()

        if output_file is not None:
            _write_to_file(output_file, json.dumps(output_dict, indent=4))

        command_output = CLICommandOutput("")
        command_output.merge_dict(output_dict)

        return get_cli_specific_output(command_output)


def _write_to_file(output_file, output):
    if os.path.exists(output_file) and os.path.isdir(output_file):
        raise ValueError("Cannot write to directory path {}. Please specify a file path instead.".format(output_file))
    else:
        with open(output_file, "w+") as f:
            f.write(output)


def _create_pipeline(pipeline_yaml, name, description=None, version=None, continue_on_step_failure=None,
                     output_file=None, workspace_name=None, resource_group_name=None):
    workspace_object = _setup_and_get_workspace(workspace_name=workspace_name, resource_group_name=resource_group_name)

    pipeline = Pipeline.load_yaml(workspace_object, pipeline_yaml)
    published_pipeline = pipeline.publish(name=name, description=description, version=version,
                                          continue_on_step_failure=continue_on_step_failure)

    output_dict = published_pipeline._to_dict_cli(verbose=True)
    if output_file is not None:
        _write_to_file(output_file, json.dumps(output_dict, indent=4))

    command_output = CLICommandOutput("")
    command_output.merge_dict(output_dict)
    return command_output


def create_pipeline(pipeline_yaml, name, description=None, version=None, continue_on_step_failure=None,
                    output_file=None, workspace_name=None, resource_group_name=None):
    """Create a pipeline from a yaml file."""
    with _silence_stdout():
        cli_output = _create_pipeline(pipeline_yaml, name, description, version, continue_on_step_failure,
                                      output_file, workspace_name, resource_group_name)

        return get_cli_specific_output(cli_output)


def clone_pipeline_run(pipeline_run_id, path=None, workspace_name=None, resource_group_name=None, output_file=None):
    """Save the yml for the pipeline run to the given path."""
    with _silence_stdout():
        workspace_object = _setup_and_get_workspace(workspace_name=workspace_name,
                                                    resource_group_name=resource_group_name)

        pipeline_run = PipelineRun.get(workspace=workspace_object, run_id=pipeline_run_id)

        pipeline_run.save(path=path)

        pipeline_output = "Pipeline yml was saved successfully."
        command_output = CLICommandOutput(pipeline_output)
        if output_file is not None:
            _write_to_file(output_file, json.dumps(pipeline_output, indent=4))
        command_output.set_do_not_print_dict()
        return get_cli_specific_output(command_output)


def get_pipeline(pipeline_id, pipeline_draft_id=None, path=None, workspace_name=None, resource_group_name=None):
    """Save the yml for the pipeline run to the given path."""
    workspace_object = _setup_and_get_workspace(workspace_name=workspace_name, resource_group_name=resource_group_name)

    if pipeline_id is not None:
        published_pipeline = PublishedPipeline.get(workspace=workspace_object, id=pipeline_id)
        published_pipeline.save(path=path)
    else:
        pipeline_draft = PipelineDraft.get(workspace=workspace_object, id=pipeline_draft_id)
        pipeline_draft.save(path=path)

    command_output = CLICommandOutput("Pipeline yml was saved successfully.")
    command_output.set_do_not_print_dict()
    return get_cli_specific_output(command_output)


def show_schedule(schedule_id, workspace_name=None, resource_group_name=None):
    """Show the details of a schedule."""
    workspace_object = _setup_and_get_workspace(workspace_name=workspace_name, resource_group_name=resource_group_name)

    schedule = Schedule.get(workspace_object, schedule_id)
    output_dict = schedule._to_dict_cli(verbose=True)

    command_output = CLICommandOutput("")
    command_output.merge_dict(output_dict)

    return get_cli_specific_output(command_output)


def enable_schedule(schedule_id, workspace_name=None, resource_group_name=None):
    """Enable a schedule for execution."""
    workspace_object = _setup_and_get_workspace(workspace_name=workspace_name, resource_group_name=resource_group_name)

    schedule = Schedule.get(workspace_object, schedule_id)
    schedule.enable()

    command_output = CLICommandOutput("Schedule '%s' (%s) was enabled successfully." % (schedule.name, schedule.id))
    command_output.set_do_not_print_dict()
    return get_cli_specific_output(command_output)


def disable_schedule(schedule_id, workspace_name=None, resource_group_name=None):
    """Disable a schedule from running."""
    workspace_object = _setup_and_get_workspace(workspace_name=workspace_name, resource_group_name=resource_group_name)

    schedule = Schedule.get(workspace_object, schedule_id)
    schedule.disable()

    command_output = CLICommandOutput("Schedule '%s' (%s) was disabled successfully." % (schedule.name, schedule.id))
    command_output.set_do_not_print_dict()
    return get_cli_specific_output(command_output)


def show_pipeline_draft(pipeline_draft_id, workspace_name=None, resource_group_name=None):
    """Show the details of a Pipeline Draft."""
    workspace_object = _setup_and_get_workspace(workspace_name=workspace_name, resource_group_name=resource_group_name)

    pipeline_draft = PipelineDraft.get(workspace_object, pipeline_draft_id)
    output_dict = pipeline_draft._to_dict_cli(verbose=True)

    command_output = CLICommandOutput("")
    command_output.merge_dict(output_dict)

    return get_cli_specific_output(command_output)


def list_pipeline_drafts(tags=None, workspace_name=None, resource_group_name=None):
    """List the pipeline drafts in a workspace."""
    workspace_object = _setup_and_get_workspace(workspace_name=workspace_name, resource_group_name=resource_group_name)

    pipelines = PipelineDraft.list(workspace_object, tags=get_dict_from_argument(tags))

    serialized_pipeline_list = []
    for pipeline in pipelines:
        serialized_pipeline_list.append("PipelineDraft:")
        serialized_pipeline_list.append(pipeline._to_dict_cli(verbose=False))

    command_output = CLICommandOutput("")
    command_output.merge_dict(serialized_pipeline_list)

    return get_cli_specific_output(command_output)


def delete_pipeline_draft(pipeline_draft_id, workspace_name=None, resource_group_name=None):
    """Delete the Pipeline Draft."""
    workspace_object = _setup_and_get_workspace(workspace_name=workspace_name, resource_group_name=resource_group_name)

    pipeline_draft = PipelineDraft.get(workspace_object, pipeline_draft_id)
    pipeline_draft.delete()

    command_output = CLICommandOutput("PipelineDraft '%s' (%s) was deleted successfully." %
                                      (pipeline_draft.name, pipeline_draft.id))
    command_output.set_do_not_print_dict()
    return get_cli_specific_output(command_output)


def submit_pipeline_draft(pipeline_draft_id, workspace_name=None, resource_group_name=None):
    """Delete the Pipeline Draft."""
    workspace_object = _setup_and_get_workspace(workspace_name=workspace_name, resource_group_name=resource_group_name)

    pipeline_draft = PipelineDraft.get(workspace_object, pipeline_draft_id)
    pipeline_run = pipeline_draft.submit_run()

    output_dict = pipeline_run._get_base_info_dict()

    command_output = CLICommandOutput("Submitted PipelineRun %s from PipelineDraft %s." %
                                      (pipeline_run.id, pipeline_draft.id))
    command_output.merge_dict(output_dict)

    return get_cli_specific_output(command_output)


def publish_pipeline_draft(pipeline_draft_id, workspace_name=None, resource_group_name=None):
    """Delete the Pipeline Draft."""
    workspace_object = _setup_and_get_workspace(workspace_name=workspace_name, resource_group_name=resource_group_name)

    pipeline_draft = PipelineDraft.get(workspace_object, pipeline_draft_id)
    pipeline = pipeline_draft.publish()

    output_dict = pipeline._to_dict_cli()

    command_output = CLICommandOutput("Created PublishedPipeline %s from PipelineDraft %s." %
                                      (pipeline.name, pipeline_draft.id))
    command_output.merge_dict(output_dict)

    return get_cli_specific_output(command_output)


def create_pipeline_draft(pipeline_yml, name, description, experiment_name, pipeline_parameters,
                          continue_on_step_failure, tags, properties, workspace_name=None, resource_group_name=None):
    """Create a Pipeline Draft from yml definition."""
    workspace_object = _setup_and_get_workspace(workspace_name=workspace_name, resource_group_name=resource_group_name)

    pipeline = Pipeline.load_yaml(workspace_object, pipeline_yml)
    pipeline_draft = PipelineDraft.create(workspace=workspace_object,
                                          pipeline=pipeline,
                                          name=name,
                                          description=description,
                                          experiment_name=experiment_name,
                                          pipeline_parameters=get_dict_from_argument(pipeline_parameters),
                                          continue_on_step_failure=continue_on_step_failure,
                                          tags=get_dict_from_argument(tags),
                                          properties=get_dict_from_argument(properties))

    output_dict = pipeline_draft._to_dict_cli()

    command_output = CLICommandOutput("")
    command_output.merge_dict(output_dict)

    return get_cli_specific_output(command_output)


def clone_pipeline_draft(pipeline_draft_id, pipeline_run_id, pipeline_id, experiment_name, workspace_name=None,
                         resource_group_name=None):
    """Create a Pipeline Draft."""
    workspace_object = _setup_and_get_workspace(workspace_name=workspace_name, resource_group_name=resource_group_name)

    if pipeline_draft_id is not None:
        pipeline_draft_to_clone = PipelineDraft.get(workspace_object, pipeline_draft_id)
        pipeline_draft = PipelineDraft.create(workspace_object, pipeline_draft_to_clone)
    elif pipeline_run_id is not None:
        pipeline_run = PipelineRun(Experiment(workspace_object, experiment_name), pipeline_run_id)
        pipeline_draft = PipelineDraft.create(workspace_object, pipeline_run)
    else:
        pipeline = PublishedPipeline.get(workspace_object, pipeline_id)
        pipeline_draft = PipelineDraft.create(workspace_object, pipeline)

    output_dict = pipeline_draft._to_dict_cli()

    command_output = CLICommandOutput("")
    command_output.merge_dict(output_dict)

    return get_cli_specific_output(command_output)


def update_pipeline_draft(pipeline_draft_id, pipeline_yml, name, description, experiment_name, tags,
                          pipeline_parameters, continue_on_step_failure, workspace_name=None,
                          resource_group_name=None):
    """Update a Pipeline Draft."""
    workspace_object = _setup_and_get_workspace(workspace_name=workspace_name, resource_group_name=resource_group_name)
    pipeline_draft = PipelineDraft.get(workspace_object, pipeline_draft_id)

    pipeline = None
    if pipeline_yml is not None:
        pipeline = Pipeline.load_yaml(workspace_object, pipeline_yml)

    pipeline_draft.update(pipeline=pipeline,
                          name=name,
                          description=description,
                          experiment_name=experiment_name,
                          tags=get_dict_from_argument(tags),
                          pipeline_parameters=get_dict_from_argument(pipeline_parameters),
                          continue_on_step_failure=continue_on_step_failure)

    output_dict = pipeline_draft._to_dict_cli()

    command_output = CLICommandOutput("")
    command_output.merge_dict(output_dict)

    return get_cli_specific_output(command_output)


def get_dict_from_argument(arguments_dictionary):
    argument_dict = dict()
    if arguments_dictionary is not None:
        for arg in arguments_dictionary:
            key, value = arg.split("=", 1)
            argument_dict[key] = value
    return argument_dict
