import typer

from continual.python.cli import utils
from continual import Client

from rich.console import Console
from typing import List

app = typer.Typer(help="Manage events.")


def format_event_data(ev, zipped=False, all_projects=False):
    start_time = ev.create_time.replace(microsecond=0)
    if zipped:
        data = [
            ev.id,
            ev.name,
            ev.subject,
            ev.severity,
            ev.event,
            ev.resource,
            ev.parent,
            ev.message,
            start_time,
            ev.data,
        ]
        headers = [
            "ID",
            "Name",
            "Subject",
            "Severity",
            "Event",
            "Resource",
            "Parent",
            "Message",
            "Created",
            "Extra Data",
        ]
        return tuple([x[0], x[1]] for x in (zip(headers, data)))
    else:
        data = [
            ev.id,
            ev.severity,
            ev.subject,
            ev.event,
            ev.message,
            start_time,
        ]
        headers = ["ID", "Severity", "Subject", "Event", "Message", "Created"]
        if all_projects:
            data.insert(0, ev.parent.split("/")[1])
            headers.insert(0, "Project")
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
            resource=None,
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
    resource: str = typer.Option(None, help="Filter events by resource name."),
    filters: List[str] = typer.Option(
        [], "--filter", "-f", help="List of event filters."
    ),
    n: int = typer.Option(30, "--num", "-n", help="Number of records to show."),
    all_projects: bool = typer.Option(False, "--all", "-a", help="Show all projects."),
    style: utils.ContinualStyle = typer.Option(None, help="Color to use for list."),
):
    """List events.

    Filters can include:
        -- severity (i.e. severity:ERROR)
        -- subject (i.e. subject:users/system)
        -- event (i.e. event:modelVersion:CREATED)
    """
    project, environment = utils.get_project_and_environment(project, environment)
    c = Client(project=utils.get_environment_name(project, environment))
    rs_snippet = ""
    filter_snippet = " (n=%s)" % n
    project_snippet = "project %s, environment %s" % (project, environment)
    if resource is not None:
        rs_snippet = "for resource %s " % resource
    if len(filters) > 0:
        filter_snippet = " with filter %s" % str(filters) + filter_snippet
    if all_projects:
        project_snippet = "all accessible projects"
    data = []
    headers = []
    for ev in c.events.list(
        filters=filters, page_size=n, parent=resource, all_projects=all_projects
    ):
        (ev_data, headers) = format_event_data(ev, all_projects=all_projects)
        data.append(ev_data)
    typer.secho(
        "\nFound %s events %sin %s%s: "
        % (len(data), rs_snippet, project_snippet, filter_snippet),
        fg="blue",
    )
    utils.print_table(data, headers, style=utils.get_style(style))


@app.command("get")
@utils.exit_on_error
def get(
    event: str = typer.Argument(..., help="Event ID."),
    json: bool = typer.Option(False, "--json", help="Show full JSON representation."),
):
    """Get event details."""
    c = Client()
    if "/" in event:
        ev_slug = event
    else:
        typer.secho(
            "Error: You must provide the full event name, not only the event ID.",
            fg="red",
        )
        raise typer.Exit(code=1)
    ev = c.events.get(ev_slug)
    if json:
        console = Console()
        console.print(ev.to_dict())
    else:
        data = format_event_data(ev, zipped=True)
        typer.secho("\nRetrieving event %s: \n" % (event.split("/")[-1]), fg="blue")
        utils.print_info(data)
