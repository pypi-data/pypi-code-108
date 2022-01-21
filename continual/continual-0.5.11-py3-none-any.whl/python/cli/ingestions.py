import typer

from continual.python.cli import utils
from continual import Client

from rich.console import Console
from datetime import datetime
from typing import List

app = typer.Typer(help="Manage Ingestions")


def format_ingestion_data(i, zipped=False, all_projects=False):
    feature_set = i.parent.split("/")[-1]
    end_time = i.finish_time
    start_time = i.start_time.replace(microsecond=0)
    if end_time:
        end_time = end_time.replace(microsecond=0)
        duration = (end_time - start_time).seconds
    else:
        end_time = "N/A"
        if i.state.value == "RUNNING":
            duration = (datetime.utcnow() - start_time).seconds
        else:
            duration = "N/A"
    if zipped:
        data = [
            i.id,
            i.name,
            i.state.value,
            feature_set,
            start_time,
            end_time,
            duration,
            i.ingested_row_count,
        ]
        headers = [
            "ID",
            "Name",
            "State",
            "Feature Set",
            "Started",
            "Finished",
            "Duration",
            "Ingested Rows",
        ]
        return tuple(
            [x[0], x[1]] for x in (zip(headers, data))
        )  # for some reason list(zip) causes issues, so ...
    else:
        data = [
            i.id,
            i.state.value,
            feature_set,
            start_time,
            end_time,
            duration,
            i.ingested_row_count,
        ]
        headers = [
            "ID",
            "State",
            "Feature Set",
            "Started",
            "Finished",
            "Duration (s)",
            "Ingested Rows",
        ]
        if all_projects:
            data.insert(0, i.parent.split("/")[1])
            headers.insert(0, "Project")
        return (data, headers)


@app.command("list")
@utils.exit_on_error
def list(
    feature_set: str = typer.Option(None, help="Feature Set ID"),
    project: str = typer.Option(None, help="Project ID"),
    n: int = typer.Option(30, "--num", "-n", help="Number of records to show"),
    filters: List[str] = typer.Option([], "--filter", "-f", help="List of filters"),
    all_projects: bool = typer.Option(
        False, "--all", "-a", help="Do not filter results by current project"
    ),
    style: utils.ContinualStyle = typer.Option(None, help="Color to use for report"),
):
    """List Ingestions

    filter can be one of the following:
    - state  (i.e. state:FAILED)
    """
    c = Client(project=project)
    if project is None:
        project = utils.get_default_project()
    fs_snippet = ""
    filter_snippet = ""
    project_snippet = "project %s" % project
    if feature_set is not None:
        c = c.feature_sets.get(feature_set)
        fs_snippet = "for feature set %s " % feature_set
    if len(filters) > 0:
        filter_snippet = " with filter %s" % str(filters)
    if all_projects:
        project_snippet = "all accessible projects"
    data = []
    headers = []
    for i in c.ingestions.list(n, filters=filters, all_projects=all_projects):
        (i_data, headers) = format_ingestion_data(i, all_projects=all_projects)
        data.append(i_data)
    typer.secho(
        "\nFound %s Ingestions %sin %s%s: "
        % (len(data), fs_snippet, project_snippet, filter_snippet),
        fg="blue",
    )
    if style is None:
        style = c.config.style
    style = utils.get_style(style)
    utils.print_table(data, headers, style=style)


@app.command("get")
@utils.exit_on_error
def get(
    ingestion: str = typer.Argument(..., help="Ingestion ID"),
    project: str = typer.Option(None, help="Project ID"),
    json: bool = typer.Option(False, "--json", help="Show full json representation?"),
):
    """Get Ingestion information"""
    c = Client(project=project)
    if project is None:
        project = utils.get_default_project()
    i = c.ingestions.get(ingestion)
    if json:
        console = Console()
        console.print(i.to_dict())
    else:
        data = format_ingestion_data(i, zipped=True)
        typer.secho("\nRetrieving ingestion %s: \n" % (ingestion), fg="blue")
        utils.print_info(data)


@app.command("cancel")
@utils.exit_on_error
def cancel(
    ingestion: str = typer.Argument(..., help="Ingestion ID"),
    project: str = typer.Option(None, help="Project ID"),
    feature_set: str = typer.Option(None, help="Feature set ID"),
):
    """Cancel an ingestion that is currently running"""
    c = Client(project=project)
    if project is None:
        project = utils.get_default_project()
    if "/" in ingestion:
        i_slug = ingestion
    else:
        i_slug = "projects/%s/featureSets/%s/ingetions/%s" % (
            project,
            feature_set,
            ingestion,
        )
    i = c.ingestions.get(i_slug)
    i.cancel()
    typer.secho("Successfully cancelled ingestion %s" % (i.name), fg="green")
