from typing import Optional, List

import click
import humanize
from yaspin import yaspin
from rich.console import Console
from grid.cli import rich_click
from grid.cli.client import Grid
from grid.cli.observables import BaseObservable
from grid.sdk import env
from grid.sdk._gql.queries import get_user
from grid.sdk.datastores import parse_name_from_source, Datastore, list_datastores
from grid.sdk.utils.datastore_uploader import clear_cache

WARNING_STR = click.style('WARNING', fg='yellow')


@click.group(invoke_without_command=True)
@click.pass_context
@click.option(
    '--global',
    'is_global',
    type=bool,
    is_flag=True,
    help='Fetch sessions from everyone in the team when flag is passed'
)
def datastore(ctx, is_global: bool = False) -> None:
    """Manages Datastore workflows."""
    if ctx.invoked_subcommand is None:
        spinner = yaspin(text=f"Loading Datastores in {env.CONTEXT}...", color="yellow")
        spinner.start()
        try:
            datastores: List[Datastore] = list_datastores(is_global=is_global)
        except Exception as e:
            spinner.fail("✘")
            raise click.ClickException(e)
        if is_global:
            table_cols = ["Cluster Id", "Name", "Version", "Size", "Created At", "Created By", "Team Name", "Status"]
        else:
            table_cols = ["Cluster Id", "Name", "Version", "Size", "Created", "Created By", "Status"]
        table = BaseObservable.create_table(columns=table_cols)
        sorted_datastores = sorted(datastores, key=lambda k: (k.name, k.version))
        for ds in sorted_datastores:
            created_at = f'{ds.created_at:%Y-%m-%d %H:%M}'
            size = ds.size
            if size or size == 0:
                size = humanize.naturalsize(size * 1.04858 * (1000**2))  # megibyte to megabyte
            status = ds.snapshot_status.title()
            username = ds.user.username
            if is_global:
                team_name = ds.team.name if hasattr(ds.team, 'name') else None
                table.add_row(ds.cluster_id, ds.name, str(ds.version), size, created_at, username, team_name, status)
            else:
                table.add_row(ds.cluster_id, ds.name, str(ds.version), size, created_at, username, status)
        spinner.ok("✔")
        console = Console()
        console.print(table)
    elif is_global:
        click.echo(f"{WARNING_STR}: --global flag doesn't have any effect when invoked with a subcommand")


@datastore.command()
@rich_click.argument('session_name', nargs=1, help="The name of the session.")
@click.pass_context
def resume(ctx, session_name: str):
    """Resume uploading a datastore. SESSION_NAME identifies the datastore upload session to resume.

    The SESSION_NAME argument is displayed which starting (or resuming) an upload.
    """
    client = Grid()
    if session_name == "list":
        client.list_resumable_datastore_sessions()
        return

    client.resume_datastore_session(session_name)


@datastore.command(cls=rich_click.deprecate_grid_options())
@click.option(
    '--source',
    required=True,
    help=(
        "Source to create datastore from. This could either be a local "
        "directory (e.g: /opt/local_folder) or a remote HTTP URL pointing "
        "to a TAR file (e.g: http://some_domain/data.tar.gz)."
    )
)
@click.option('--name', type=str, required=False, help='Name of the datastore')
@click.option(
    '--compression',
    type=bool,
    required=False,
    help='Compresses datastores with GZIP when flag is passed.',
    default=False,
    is_flag=True
)
@click.option(
    '--cluster',
    type=str,
    required=False,
    help='cluster id to create the datastore on. (Bring Your Own Cloud Customers Only).'
)
@click.pass_context
def create(ctx, source: str, name: str, compression: bool = False, cluster: Optional[str] = None) -> None:
    """Creates a datastore and begins the process of uploading files.
    The upload session is referenced by the SESSION_NAME. this SESSION_NAME
    must be used to resume the upload if it is interupted.
    """
    client = Grid()
    user_data = get_user()
    client.check_is_blocked(user_data=user_data)
    if not name:
        name = parse_name_from_source(source)
    client.upload_datastore(source=source, name=name, compression=compression, cluster=cluster)


@datastore.command()
@click.pass_context
def clearcache(ctx) -> None:
    """Clears datastore cache which is saved on the local machine when uploading a datastore to grid.

    This removes all the cached files from the local machine, meaning that resuming an incomplete
    upload is not possible after running this command.
    """
    clear_cache()
    click.echo("Datastore cache cleared")


@datastore.command(cls=rich_click.deprecate_grid_options())
@click.option('--name', type=str, required=True, help='Name of the datastore')
@click.option('--version', type=int, required=True, help='Version of the datastore')
@click.option(
    '--cluster',
    type=str,
    required=False,
    help='cluster id to delete the datastore from. (Bring Your Own Cloud Customers Only).'
)
@click.pass_context
def delete(ctx, name: str, version: int, cluster: Optional[str] = None) -> None:
    """Deletes a datastore with the given name and version tag.

    For bring-your-own-cloud customers, the cluster id of the associated
    resource is required as well.
    """
    client = Grid()
    client.delete_datastore(name=name, version=version, cluster=cluster)
