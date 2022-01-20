import typer
import humanize
import os
import yaml

from datetime import datetime
from rich.console import Console
from typing import List

from continual.rpc.management.v1.management_pb2 import YamlDiffRequest
from continual.python.cli import utils
from continual import Client
from pathlib import Path

app = typer.Typer(help="Manage changes.")


def truncate(data, n=40):
    """Truncate string with elipses."""
    return (data[:n] + "...") if len(data) > n else data


def format_changes_data(changes, project, environment, n, filters, all_projects):
    data = []
    for push in changes:
        success = 0
        fs_count = 0
        fs_success = 0
        model_count = 0
        model_success = 0
        for step in push.plan:
            if step.resource_name.split("/")[2] == "featureSets":
                fs_count += 1
                if step.state == "SUCCEEDED":
                    fs_success += 1
                    success += 1
            else:
                model_count += 1
                if step.state == "SUCCEEDED":
                    model_success += 1
                    success += 1
        total = len(push.plan)
        age = humanize.naturaltime(datetime.now() - push.create_time)
        push_id = push.name.split("/")[-1]
        push_data = [
            push_id,
            f"{fs_success}/{fs_count}",
            f"{model_success}/{model_count}",
            f"{success}/{total}",
            push.state,
            age,
            truncate(push.message),
        ]
        if all_projects:
            push_data.insert(0, push.parent.split("/")[1])
        data.append(push_data)
    headers = [
        "ID",
        "Feature Set Steps",
        "Model Steps",
        "Total Steps",
        "State",
        "Age",
        "Message",
    ]
    filter_snippet = " (n=%s)" % n
    project_snippet = "project %s, environment %s" % (project, environment)
    if all_projects:
        project_snippet = "all accessible projects & environments"
        headers.insert(0, "Project")
    if len(filters) > 0:
        filter_snippet = " with filter %s" % str(filters) + filter_snippet
    typer.secho(
        "\nFound %s changes in %s%s:" % (len(data), project_snippet, filter_snippet),
        fg="blue",
    )
    return (data, headers)


# use callback to run list command if nothing is passed in
@app.callback(invoke_without_command=True)
def default(ctx: typer.Context):
    if ctx.invoked_subcommand is not None:
        return
    else:
        list(
            project=None,
            environment=None,
            n=30,
            filters=[],
            all_projects=False,
            style=None,
        )


@app.command("list")
@utils.exit_on_error
def list(
    project: str = typer.Option(None, help="Project ID."),
    environment: str = typer.Option(None, "--env", help="Environment ID."),
    n: int = typer.Option(30, "--num", "-n", help="Number of records to show."),
    filters: List[str] = typer.Option([], "--filter", "-f", help="List of filters."),
    all_projects: bool = typer.Option(False, "--all", "-a", help="Show all projects."),
    style: utils.ContinualStyle = typer.Option(None, help="Color to use for list."),
):
    """List all changes.

    Filters can include:
        --state (i.e. state:FAILED)
    """
    project, environment = utils.get_project_and_environment(project, environment)
    c = Client(project=utils.get_environment_name(project, environment))

    push_list = c.changes.list(n, filters=filters, all_projects=all_projects)
    pushes = sorted(push_list, key=lambda x: x.create_time, reverse=True)
    (data, headers) = format_changes_data(
        pushes, project, environment, n, filters, all_projects
    )
    utils.print_table(data, headers, style=utils.get_style(style))


@app.command("get")
@utils.exit_on_error
def get(
    push_id: str = typer.Argument(..., help="Change ID."),
    project: str = typer.Option(None, help="Project ID."),
    environment: str = typer.Option(None, "--env", help="Environment ID."),
    show_diffs: bool = typer.Option(
        True,
        "--skip-diffs",
        help="Don't show diffs between changes and previous schema.",
    ),
    json: bool = typer.Option(False, "--json", help="Show full JSON representation"),
):
    """Get change details."""
    project, environment = utils.get_project_and_environment(project, environment)
    c = Client(project=utils.get_environment_name(project, environment))
    try:
        push = c.changes.get(push_id)
    except Exception as e:
        typer.secho(
            "Failed to get change %s in project %s, environment %s. Please double check the chagne id, project id, and environment id: %s"
            % (push_id, project, environment, str(e)),
            fg="red",
        )
        raise typer.Exit(code=1)
    if json:
        console = Console()
        console.print(push.to_dict())
    else:
        utils.print_change_plan(push, project, environment)
    if show_diffs:
        typer.secho(
            "\nAnalyzing schemas in change plan with previous schemas...", fg="blue"
        )
        for step in push.plan:
            if len(step.schema_text) > 0:
                name = step.resource_name.split("/")[-1]
                previous_schema_text = step.previous_schema_text
                # dyff errors if previous schema is null, so provide a trivial element
                if len(previous_schema_text) == 0:
                    previous_schema_text = "type:"
                req = YamlDiffRequest(
                    right=name,
                    left="%s (previous)" % name,
                    right_text=step.schema_text,
                    left_text=previous_schema_text,
                    parent=push.parent,
                )
                resp = c._management.GetYamlDiff(req)
                diff_text = resp.text
                typer.secho(
                    "Diffing \n\tleft = %s with \n\tright = %s"
                    % ("%s (previous)" % name, name),
                    fg="blue",
                )
                if len(diff_text) > 0:
                    typer.secho(diff_text)
                else:
                    typer.secho("No changes found.", fg="blue")


@app.command("rerun")
@utils.exit_on_error
def rerun(
    push_id: str = typer.Argument(..., help="Change ID."),
    project: str = typer.Option(None, help="Project ID."),
    environment: str = typer.Option(None, "--env", help="Environment ID."),
    message: str = typer.Option("Re-running from CLI", help="Message for new change"),
):
    """Rerun a previous change."""
    project, environment = utils.get_project_and_environment(project, environment)
    c = Client(project=utils.get_environment_name(project, environment))
    try:
        push = c.changes.rerun(push_id)
        utils.print_change(push, project, environment, message)
    except Exception as e:
        typer.secho(
            "Failed to re-run change %s in project %s, environment %s. Please double check the chagne id, project id, and environment id: %s"
            % (push_id, project, environment, str(e)),
            fg="red",
        )


@app.command("cancel")
@utils.exit_on_error
def cancel(
    push_id: str = typer.Argument(..., help="Change ID."),
    project: str = typer.Option(None, help="Project ID."),
    environment: str = typer.Option(None, "--env", help="Environment ID."),
    force: bool = typer.Option(
        False, "--force", help="Force cancellation. Skips confirmation."
    ),
):
    """Cancel change."""
    project, environment = utils.get_project_and_environment(project, environment)
    c = Client(project=utils.get_environment_name(project, environment))
    try:
        if not force:
            force = typer.confirm(
                "Are you sure you want to cancel the change %s?" % push_id
            )
        if force:
            c.changes.cancel(push_id)
            typer.secho("Change %s successfully cancelled." % push_id, fg="green")
    except Exception as e:
        typer.secho(
            "Failed to cancel change %s in project %s, environment %s. Please double check the chagne id, project id, and environment id: %s"
            % (push_id, project, environment, str(e)),
            fg="red",
        )


@app.command("export")
@utils.exit_on_error
def export(
    push_id: str = typer.Argument(..., help="Change ID."),
    project: str = typer.Option(None, "--project", help="Project ID."),
    environment: str = typer.Option(None, "--env", help="Environment ID."),
    path: Path = typer.Option(
        None,
        help="Directory to save projects resources into. Defaults to ./<project_id> if not provided.",
    ),
    # include_predictions: bool = typer.Option(False, "--predictions", hidden=True, help="Include csv of latest predictions for each model"),
):
    """
    Exports change YAMLs to a directory.
    """
    project, environment = utils.get_project_and_environment(project, environment)
    c = Client(project=utils.get_environment_name(project, environment))

    change = c.changes.get(push_id)
    export_change(path, project, change)


def export_change(path, project, change):

    # use cwd/project_id if no path provided
    if path is None:
        path = os.path.join(os.getcwd(), project)
        if not os.path.exists(path):
            os.mkdir(path)

    fs_dir = os.path.join(path, "feature_sets")
    if not os.path.exists(fs_dir):
        os.mkdir(fs_dir)
    model_dir = os.path.join(path, "models")
    if not os.path.exists(model_dir):
        os.mkdir(model_dir)
    # bpj_dir = os.path.join(path,"predictions")

    try:
        fs_yamls = []
        m_yamls = []
        if len(change.plan) > 0:
            for step in change.plan:
                plan_schema = step.schema_text
                if len(plan_schema) > 0:
                    schema_text = yaml.load(plan_schema, Loader=yaml.FullLoader)
                    schema_yaml = utils.format_yaml(schema_text)
                    parts = step.resource_name.split("/")
                    type = parts[2]
                    if type == "featureSets":
                        m_yamls.append((parts[-1], schema_yaml))
                    if type == "models":
                        fs_yamls.append((parts[-1], schema_yaml))

            if len(fs_yamls) > 0:
                utils.save_yamls(fs_yamls, fs_dir)
            if len(m_yamls) > 0:
                utils.save_yamls(m_yamls, model_dir)
            typer.secho(
                "Successfully saved change yamls to directory: %s \n" % fs_dir,
                fg="green",
            )
        else:
            typer.secho("No steps found in change %s" % change.id, fg="blue")
    except Exception as e:
        typer.secho(
            "Failed to get all save change yamls:%s \n" % (str(e)),
            fg="red",
        )
