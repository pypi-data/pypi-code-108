import typer

from continual.python.cli import utils
from continual import Client

from rich.console import Console

app = typer.Typer(help="Manage organizations.")


def format_organization_data(o, zipped=False):
    create_time = o.create_time.replace(microsecond=0)
    update_time = o.update_time.replace(microsecond=0)
    num_projects = len(o.projects.list(1000))
    data = [o.id, o.display_name, num_projects, create_time, update_time]
    headers = ["ID", "Display Name", "Projects", "Created", "Updated"]

    if zipped:
        return tuple(
            [x[0], x[1]] for x in (zip(headers, data))
        )  # for some reason list(zip) causes issues, so ...
    else:
        return (data, headers)


# use callback to run list command if nothing is passed in
@app.callback(invoke_without_command=True)
def default(ctx: typer.Context):
    if ctx.invoked_subcommand is not None:
        return
    else:
        list(n=30, style=None)


@app.command("list")
@utils.exit_on_error
def list(
    n: int = typer.Option(30, "--num", "-n", help="Number of records to show."),
    style: utils.ContinualStyle = typer.Option(None, help="Color to use for list."),
):
    """List organizations."""
    c = Client()
    data = []
    headers = []
    for org in c.organizations.list(n):
        (o_data, headers) = format_organization_data(org)
        data.append(o_data)
    typer.secho("\nFound %s organizations:" % len(data), fg="blue")
    if style is None:
        style = c.config.style
    style = utils.get_style(style)
    utils.print_table(data, headers, style=style)


@app.command("get")
@utils.exit_on_error
def get(
    organization: str = typer.Argument(..., help="Organization ID."),
    json: bool = typer.Option(False, "--json", help="Print full JSON representation."),
):
    """Get orgaanization details."""
    c = Client()
    try:
        org = c.organizations.get(organization)
    except:
        org = utils.get_org_from_display_name(organization)
    if json:
        console = Console()
        console.print(org.to_dict())
    else:
        data = format_organization_data(org, zipped=True)
        typer.secho("\nRetrieving organization %s: \n" % (org.id), fg="blue")
        utils.print_info(data)


@app.command("create")
@utils.exit_on_error
def create(
    organization: str = typer.Argument(
        ..., help="Organization name.", show_default=False
    ),
):
    """Create organization."""
    org = utils.get_or_create_org(organization)
    typer.secho(
        "Successfully created organization %s with id %s." % (org.display_name, org.id),
        fg="green",
    )


@app.command("delete")
@utils.exit_on_error
def delete(
    organization: str = typer.Argument(..., help="Organization ID."),
):
    """Delete organization."""
    c = Client()
    org = c.organizations.get(organization)
    org.delete()
    typer.secho("Successfully deleted org %s." % organization, fg="green")


@app.command("update")
@utils.exit_on_error
def update(
    organization: str = typer.Argument(..., help="Organization ID"),
    display_name: str = typer.Option(..., help="Display name."),
):
    """Update Org Name."""
    c = Client()
    org = c.organizations.get(organization)
    org.update(display_name)
    typer.secho("Successfully updated organization %s." % organization, fg="green")
