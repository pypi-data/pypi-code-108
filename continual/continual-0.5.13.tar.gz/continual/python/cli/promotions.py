import typer
import humanize

from continual.python.cli import utils
from continual import Client

from rich.console import Console
from datetime import datetime
from typing import List

app = typer.Typer(help="Manage promotions.")


def format_promotion_data(d, zipped=False, all_projects=False):
    end_time = d.demoted_time
    if not d.promoted_time:
        online_time = "N/A"
        end_time = "N/A"
        duration = "N/A"
    elif end_time:
        online_time = d.promoted_time.replace(microsecond=0)
        end_time = end_time.replace(microsecond=0)
        duration = humanize.naturaldelta(end_time - online_time)
    else:
        online_time = d.promoted_time.replace(microsecond=0)
        end_time = "N/A"
        if d.state.value == "SUCCEEDED":
            duration = humanize.naturaldelta(datetime.utcnow() - online_time)
        else:
            duration = "N/A"
    if zipped:
        data = [
            d.id,
            d.name,
            d.state.value,
            d.improvement_metric,
            d.improvement_metric_value,
            online_time,
            end_time,
            duration,
        ]
        headers = [
            "ID",
            "Name",
            "State",
            "Metric",
            "Metric Value",
            "Promoted",
            "Demoted",
            "Time Promoted",
        ]
        return tuple(
            [x[0], x[1]] for x in (zip(headers, data))
        )  # for some reason list(zip) causes issues, so ...
    else:
        data = [
            d.id,
            d.state.value,
            d.name.split("/")[3],
            d.model_version.split("/")[-1],
            d.improvement_metric,
            d.improvement_metric_value,
            online_time,
            end_time,
            duration,
        ]
        headers = [
            "ID",
            "State",
            "Model",
            "Model Version",
            "Metric",
            "Metric Value",
            "Promoted",
            "Demoted",
            "Time Promoted",
        ]
        if all_projects:
            data.insert(0, d.parent.split("/")[1])
            headers.insert(0, "Project")
        return (data, headers)


# use callback to run list command if nothing is passed in
@app.callback(invoke_without_command=True)
def default(ctx: typer.Context):
    if ctx.invoked_subcommand is not None:
        return
    else:
        list(
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
    model: str = typer.Option(None, help="Model ID."),
    project: str = typer.Option(None, help="Project ID."),
    environment: str = typer.Option(None, "--env", help="Environment ID."),
    n: int = typer.Option(30, "--num", "-n", help="Number of records to show."),
    filters: List[str] = typer.Option([], "--filter", "-f", help="List of filters."),
    all_projects: bool = typer.Option(False, "--all", "-a", help="Show all projects."),
    style: utils.ContinualStyle = typer.Option(None, help="Color to use for list."),
):
    """List promotions.

    Filters can include:
        --state (i.e. state:FAILED)
    """
    project, environment = utils.get_project_and_environment(project, environment)
    c = Client(project=utils.get_environment_name(project, environment))

    model_snippet = ""
    filter_snippet = " (n=%s)" % n
    project_snippet = "project %s, environment %s" % (project, environment)
    if model is not None:
        c = c.models.get(model)
        model_snippet = "for model %s " % model
    if len(filters) > 0:
        filter_snippet = " with filters %s" % str(filters) + filter_snippet
    if all_projects:
        project_snippet = "all accessible projects"
    data = []
    headers = []
    for d in c.promotions.list(n, filters=filters, all_projects=all_projects):
        (d_data, headers) = format_promotion_data(d, all_projects=all_projects)
        data.append(d_data)
    typer.secho(
        "\nFound %s promotions %sin %s%s: "
        % (len(data), model_snippet, project_snippet, filter_snippet),
        fg="blue",
    )
    utils.print_table(data, headers, style=utils.get_style(style))


@app.command("get")
@utils.exit_on_error
def get(
    promotion: str = typer.Argument(..., help="Promotion ID."),
    project: str = typer.Option(None, help="Project ID."),
    environment: str = typer.Option(None, "--env", help="Environment ID."),
    json: bool = typer.Option(False, "--json", help="Show full JSON representation."),
):
    """Get promotion details."""
    project, environment = utils.get_project_and_environment(project, environment)
    c = Client(project=utils.get_environment_name(project, environment))

    d = c.promotions.get(promotion)
    if json:
        console = Console()
        console.print(d.to_dict())
    else:
        data = format_promotion_data(d, zipped=True)
        typer.secho("\nRetrieving promotion %s: \n" % (promotion), fg="blue")
        utils.print_info(data)
