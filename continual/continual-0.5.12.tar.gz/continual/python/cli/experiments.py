import typer
import json

from continual.python.cli import utils
from continual import Client

from rich.console import Console
from typing import List

app = typer.Typer(help="Manage experiments.")


def format_experiments_data(e, zipped=False, all_projects=False):
    framework = json.loads(e.training_config).get("framework")
    name_parts = e.name.split("/")
    model = name_parts[3]
    model_version = name_parts[5]
    end_time = e.finish_time
    start_time = e.start_time
    if start_time:
        start_time = start_time.replace(microsecond=0)
    if end_time:
        end_time = end_time.replace(microsecond=0)
        duration = (end_time - start_time).seconds
    else:
        end_time = "N/A"
        duration = "N/A"
    if zipped:
        data = [
            e.id,
            e.name,
            e.state.value,
            framework,
            e.type,
            start_time,
            end_time,
            duration,
            e.performance_metric,
            e.performance_metric_val,
        ]
        headers = [
            "ID",
            "Name",
            "State",
            "Framework",
            "Algorithm",
            "Start Time",
            "End Time",
            "Duration (s)",
            "Metric",
            "Metric Value",
        ]
        return tuple(
            [x[0], x[1]] for x in (zip(headers, data))
        )  # for some reason list(zip) causes issues, so ...
    else:
        data = [
            e.id,
            e.state.value,
            model,
            model_version,
            # framework,
            e.type.split("/")[-1],
            # start_time,
            # end_time,
            duration,
            e.performance_metric,
            e.performance_metric_val,
        ]
        headers = [
            "ID",
            "State",
            "Model",
            "Model Version",
            # "Framework",
            "Algorithm",
            # "Start Time",
            # "End Time",
            "Duration (s)",
            "Metric",
            "Metric Value",
        ]
        if all_projects:
            data.insert(0, e.parent.split("/")[1])
            headers.insert(0, "Project")
        return (data, headers)


# use callback to run list command if nothing is passed in
@app.callback(invoke_without_command=True)
def default(ctx: typer.Context):
    if ctx.invoked_subcommand is not None:
        return
    else:
        list(
            model_version=None,
            model=None,
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
    model_version: str = typer.Option(None, help="Model Version ID."),
    model: str = typer.Option(None, help="Model ID."),
    project: str = typer.Option(None, help="Project ID."),
    environment: str = typer.Option(None, "--env", help="Environment ID."),
    n: int = typer.Option(
        30, "--num", "-n", help="Number of records to show.", show_default=False
    ),
    filters: List[str] = typer.Option([], "--filter", "-f", help="List of filters."),
    all_projects: bool = typer.Option(False, "--all", "-a", help="Show all projects."),
    style: utils.ContinualStyle = typer.Option(None, help="Color to use for list."),
):
    """List experiments.

    filters can include:
        - state  (i.e. state:FAILED)
    """
    project, environment = utils.get_project_and_environment(project, environment)
    c = Client(project=utils.get_environment_name(project, environment))

    model_snippet = ""
    filter_snippet = " (n=%s)" % n
    project_snippet = "project %s, environment %s" % (project, environment)
    if model_version is not None:
        c = c.model_versions.get(model_version)
        model_snippet = "for model version %s of model %s " % (
            model_version,
            c.parent.split("/")[-1],
        )
    elif model is not None:
        m = c.models.get(model)
        c = m.model_versions.get(m.latest_model_version)
        model_snippet = "for latest model experiment in model %s " % (model)
    if len(filters) > 0:
        filter_snippet = " with filter %s" % str(filters) + filter_snippet
    if all_projects:
        project_snippet = "all accessible projects"
    data = []
    headers = []
    for e in c.experiments.list(n, filters=filters, all_projects=all_projects):
        (e_data, headers) = format_experiments_data(e, all_projects=all_projects)
        data.append(e_data)
    typer.secho(
        "\nFound %s experiments %sin %s%s: "
        % (len(data), model_snippet, project_snippet, filter_snippet),
        fg="blue",
    )
    utils.print_table(data, headers, style=utils.get_style(style))


@app.command("get")
@utils.exit_on_error
def get(
    experiment: str = typer.Argument(..., help="Experiment ID."),
    project: str = typer.Option(None, help="Project ID."),
    environment: str = typer.Option(None, "--env", help="Environment ID."),
    json: bool = typer.Option(False, "--json", help="Show full JSON representation."),
):
    """Get experiment details."""
    project, environment = utils.get_project_and_environment(project, environment)
    c = Client(project=utils.get_environment_name(project, environment))

    e = c.experiments.get(experiment)
    if json:
        console = Console()
        console.print(e.to_dict())
    else:
        data = format_experiments_data(e, zipped=True)
        typer.secho("\nRetrieving experiment %s: \n" % (experiment), fg="blue")
        utils.print_info(data, headers="")
