import click

from spell.cli.utils import tabulate_rows, with_emoji, prettify_time, truncate_string, fetch_project
from spell.cli.exceptions import api_client_exception_handler, ExitException
from spell.cli.log import logger
from spell.cli.commands.ps import ps


@click.group(
    name="project",
    short_help="Manage Spell Projects",
    help="Create, List, Archive and manage Projects on Spell",
)
@click.pass_context
def project(ctx):
    pass


@project.command(name="create", short_help="Create a new Project")
@click.option("-n", "--name", "name", prompt="Enter a name for the project", help="Name of the project")
@click.option("-d", "--description", "description", help="Optional description of the project")
@click.option(
    "-r",
    "--run-id",
    "run_ids",
    multiple=True,
    type=int,
    help="RunIDs to add to created project (multiple allowed)",
)
@click.pass_context
def create(ctx, name, description, run_ids):
    proj_req = {
        "name": name,
        "description": description,
        "run_ids": run_ids,
    }
    client = ctx.obj["client"]
    with api_client_exception_handler():
        client.create_project(proj_req)
    click.echo(with_emoji("💫", f"Created project '{name}'", ctx.obj["utf8"]))


@project.command(name="list", short_help="List all Projects")
@click.option(
    "--archived",
    "show_archived",
    is_flag=True,
    help="Flag to list archived projects. Default lists only unarchived projects.",
)
@click.pass_context
def list_projects(ctx, show_archived):
    client = ctx.obj["client"]
    with api_client_exception_handler():
        projects = client.list_projects(show_archived)
    display_project_list(ctx, projects, show_archived)


def display_project_list(ctx, projects, show_archived=False, show_id=False):
    def create_row(proj):
        tup = (
            proj.name,
            truncate_string(proj.description, 35, utf8=ctx.obj["utf8"]),
            proj.creator.user_name,
            proj.total_run_count,
            prettify_time(proj.created_at),
        )
        if show_id:
            tup = (proj.id, *tup)
        if show_archived:
            tup = (*tup, prettify_time(proj.archived_at))
        return tup

    headers = ["NAME", "DESCRIPTION", "CREATOR", "TOTAL RUNS", "CREATED AT"]
    if show_id:
        headers = ["ID", *headers]
    if show_archived:
        headers = [*headers, "ARCHIVED AT"]
    tabulate_rows(
        [create_row(proj) for proj in projects],
        headers=headers,
    )


@project.command(name="get", short_help="Get a Project by Name")
@click.argument("name")
@click.pass_context
def get(ctx, name):
    client = ctx.obj["client"]
    proj = fetch_project(client, name)

    tabulate_rows(
        [
            ("Name", proj.name),
            ("Description", proj.description),
            ("Creator", proj.creator.user_name),
            ("Created At", prettify_time(proj.created_at)),
        ],
    )

    click.echo("")
    click.echo(f"Current {proj.name} Runs:")
    ctx.invoke(ps, project=proj.name)


@project.command(name="archive", short_help="Archive a project by name")
@click.argument("project_name")
@click.pass_context
def archive(ctx, project_name):
    """
    Archive a project given the name
    """
    client = ctx.obj["client"]
    proj = fetch_project(client, project_name)

    with api_client_exception_handler():
        logger.info(f"Archiving project {project_name}")
        client.archive_project(proj.id)
    click.echo(with_emoji("💫", f"Successfully archived project {project_name}", ctx.obj["utf8"]))


@project.command(name="unarchive", short_help="Unarchive a project by name")
@click.argument("project_name")
@click.pass_context
def unarchive(ctx, project_name):
    """
    Unarchive a project given the name
    """
    client = ctx.obj["client"]
    with api_client_exception_handler():
        all_projects = client.list_projects(show_archived=True)
    matching = [proj for proj in all_projects if proj.name.lower() == project_name.lower()]
    if len(matching) == 0:
        raise ExitException(
            f"Unknown project `{project_name}`. "
            "Run `spell project list --archived` to see all currently archived projects"
        )
    if len(matching) > 1:
        click.echo(
            f'Found {len(matching)} archived projects with name "{project_name}". '
            "Please select which one from the list below"
        )
        display_project_list(ctx, matching, show_archived=True, show_id=True)
        proj_id = click.prompt(
            "What is the ID of the project you would like to unarchive?",
            type=click.Choice([str(p.id) for p in matching]),
        )
        proj = [p for p in matching if p.id == int(proj_id)][0]
    else:
        proj = matching[0]

    with api_client_exception_handler():
        logger.info(f"Unarchiving project {project_name}")
        client.unarchive_project(proj.id)
    click.echo(with_emoji("💫", f"Successfully unarchived project {project_name}", ctx.obj["utf8"]))


@project.command(name="edit", short_help="Edit a project by name")
@click.argument("project_name")
@click.option("-n", "--name", "name", help="Name of the project", default=None)
@click.option("-d", "--description", "description", help="Edit the description of the project", default=None)
@click.pass_context
def edit(ctx, project_name, name, description):
    """
    Edit the name or desciption of a project
    """
    client = ctx.obj["client"]
    proj = fetch_project(client, project_name)

    if name is None and description is None:
        raise ExitException("Please provide either a name or a description to change.")
    with api_client_exception_handler():
        client.edit_project(proj.id, name, description)
        click.echo(with_emoji("💫", "Successfully edited project", ctx.obj["utf8"]))


@project.command(name="add-runs", short_help="Add runs to a project")
@click.argument("project-name")
@click.argument("run-ids", type=int, nargs=-1)
@click.pass_context
def addRuns(ctx, project_name, run_ids):
    client = ctx.obj["client"]
    proj = fetch_project(client, project_name)
    with api_client_exception_handler():
        client.add_runs(proj.id, run_ids)
    run_str = ", ".join([str(r) for r in run_ids])
    click.echo(f"Successfully added runs {run_str} to project '{project_name}'!")


@project.command(name="remove-runs", short_help="Move runs from this project back to uncategorized")
@click.argument("project-name")
@click.argument("run-ids", type=int, nargs=-1)
@click.pass_context
def removeRuns(ctx, project_name, run_ids):
    client = ctx.obj["client"]
    proj = fetch_project(client, project_name)
    with api_client_exception_handler():
        client.remove_runs(proj.id, run_ids)
    run_str = ", ".join([str(r) for r in run_ids])
    click.echo(f"Successfully removed runs {run_str} from project '{project_name}'!")
