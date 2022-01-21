import subprocess
from pathlib import Path
from typing import Optional

import click

from grid.sdk import Session, env
from grid.cli import rich_click
from grid.cli.cli.grid_run import _check_run_name_is_valid, _get_instance_types, _resolve_instance_type_nickname
from grid.cli.cli.utilities import validate_disk_size_callback
from grid.cli.client import Grid
from grid.cli.types import ObservableType
from grid.sdk.datastores import fetch_datastore
from grid.sdk.utils.name_generator import unique_name
import yaspin

WARNING_STR = click.style('WARNING', fg='yellow')
SUCCESS_MARK = click.style("✔", fg='green')
FAIL_MARK = click.style('✘', fg='red')


@rich_click.group(invoke_without_command=True)
@click.pass_context
@click.option(
    '--global',
    'is_global',
    type=bool,
    is_flag=True,
    help='Fetch sessions from everyone in the team when flag is passed'
)
def session(ctx, is_global: bool) -> None:
    """
    Contains a grouping of commands to manage sessions workflows.

    Executing the `grid session` command without any further arguments
    or commands renders a list of all sessions registered to your Grid
    user account.
    """
    client = Grid()
    if ctx.invoked_subcommand is None:
        # Get the status of the interactive observables.
        kind = ObservableType.INTERACTIVE
        client.status(kind=kind, follow=False, is_global=is_global)
    elif is_global:
        click.echo(f"{WARNING_STR}: --global flag doesn't have any effect when invoked with a subcommand")


@session.command()
@click.option('--cluster', 'cluster', type=str, required=False, default=env.CONTEXT, help='Cluster to run on')
@click.option(
    '--instance_type',
    'instance_type',
    type=str,
    default='t2.medium',
    callback=_resolve_instance_type_nickname,
    help='Instance type to start session in.',
    autocompletion=_get_instance_types
)
@click.option(
    '--use_spot',
    'use_spot',
    is_flag=True,
    required=False,
    default=False,
    help='Use spot instance. The spot instances, or preemptive instance can be shut down at will'
)
@click.option(
    '--disk_size',
    'disk_size',
    type=int,
    required=False,
    default=200,
    callback=validate_disk_size_callback,
    help='The disk size in GB to allocate to the session.'
)
@click.option(
    '--datastore_name',
    'datastore_name',
    type=str,
    required=False,
    default=None,
    help='Datastore name to be mounted in the session.'
)
@click.option(
    '--datastore_version',
    'datastore_version',
    type=int,
    required=False,
    default=None,
    help='Datastore version to be mounted in the session.'
)
@click.option(
    '--datastore_mount_dir',
    'datastore_mount_dir',
    type=str,
    required=False,
    default=None,
    help='Absolute path to mount Datastore in the session (defaults to /datastores/<datastore-name>).'
)
@click.option('--config', 'config', type=Path, required=False, default=None, help='Path to Grid config YML')
@click.option(
    '--name', 'name', type=str, required=False, help='Name for this session', callback=_check_run_name_is_valid
)
def create(
    name: Optional[str], cluster: Optional[str], instance_type: str, datastore_name: Optional[str],
    datastore_version: Optional[int], datastore_mount_dir: Optional[str], disk_size: int, use_spot: bool,
    config: Optional[Path]
) -> None:
    """Creates a new interactive session with NAME.

    Interactive sessions are optimized for development activites (before executing
    hyperparemeter sweeps in a Run). Once created, sessions can be accessed via
    VSCode, Jupyter-lab, or SSH interfaces.

    Grid manages the installation of any/all core libraries, drivers, and interfaces
    to the outside world. Sessions can be run on anything from a small 2 CPU core +
    4GB memory instance to a monster machine with 96 CPU cores + 824 GB memory + eight
    V100 GPUs + 40 GBPS network bandwidth (no, those values aren't typos!); or really
    anything in between.
    """
    # make a fun random name when user does not pass in a name
    if name is None:
        name = unique_name()
    spinner = yaspin.yaspin(text=f"Submitting Session {name} ...", color="yellow")
    try:
        spinner.start()
        # process datastore specification args
        dstore = None
        if datastore_name:
            dstore = fetch_datastore(datastore_name, datastore_version, cluster)

        sess = Session(
            name=name,
            instance_type=instance_type,
            disk_size_gb=disk_size,
            use_spot=use_spot,
            cluster_id=cluster,
            datastore=dstore,
            datastore_mount_dir=datastore_mount_dir,
            config_file=config,
        )
        if sess.exists is True:
            raise click.ClickException(f"A session with the name: {name} already exists. Please specify a unique name.")

        click.echo("Creating Interactive session ...", color="yellow")
        sess.start()
        click.echo(
            f"""
        {SUCCESS_MARK} Interactive session created!

        `grid status` to list all runs and interactive sessions.
        `grid status {name}` to see the status for this interactive session.

        ----------------------
        Submission summary
        ----------------------
        name:                    {name}
        instance_type:           {sess.instance_type}
        cluster_id:              {sess.cluster_id}
        datastore_name:          {datastore_name}
        datastore_version:       {datastore_version}
        datastore_mount_dir:     {sess.datastore_mount_dir}
        use_spot:                {sess.use_spot}
        """
        )
        click.echo(f"Interactive session {name} is spinning up.")
    except Exception as e:
        click.echo(f'{FAIL_MARK} {e}')
        raise click.ClickException(str(e))
    finally:
        spinner.stop()


@session.command()
@rich_click.argument('session_name', type=str, nargs=1)
def pause(session_name: str) -> None:
    """Pauses a session identified by the SESSION_NAME.

    Pausing a session stops the running instance (and any computations being
    performed on it - be sure to save your work!) and and billing of your account
    for the machine. The session can be resumed at a later point with all your
    persisted files and saved work unchanged.
    """
    click.echo("Pausing Interactive session ...", color="yellow")

    try:
        sess = Session(name=session_name)
        if not sess.exists:
            raise RuntimeError(
                f"Session {session_name} does not exist in {env.CONTEXT}. "
                f"If you are pausing a session in another cluster, set "
                f"the default cluster first using "
                f"`grid user set-default-cluster <cluster_name>`."
            )
        sess.pause()
        click.echo(SUCCESS_MARK)
        click.echo(f'Interactive session {session_name} has been paused successfully.')
    except Exception as e:
        click.echo("✘", color="red")
        raise click.ClickException(f"Failed to pause interactive session: '{session_name}': {e}")


@session.command()
@rich_click.argument('session_name', type=str, nargs=1)
def resume(session_name: str) -> None:
    """Resumes a session identified by SESSION_NAME.
    """
    click.echo("Resuming Interactive session ...", color="yellow")

    try:
        sess = Session(name=session_name)
        if not sess.exists:
            raise RuntimeError(
                f"Session {session_name} does not exist in {env.CONTEXT}. "
                f"If you are pausing a session in another cluster, set "
                f"the default cluster first using "
                f"`grid user set-default-cluster <cluster_name>`."
            )
        sess.start()
        click.echo(f'{SUCCESS_MARK} Interactive session: {session_name} successfully began resuming.')
        click.echo('Note: Depending on instance-type selected, it may take up to 10 minutes to become available.')
    except Exception as e:
        click.echo(f"{FAIL_MARK} {e}")
        raise click.ClickException(f"Failed to resume interactive session: '{session_name}'")


@session.command()
@rich_click.argument('session_name', type=str, nargs=1)
def delete(session_name: str) -> None:
    """Deletes a session identified by SESSION_NAME.

    Deleting a session will stop the running instance (and any computations being
    performed on it) and billing of your account. All work done on the machine
    is permenantly removed, including all/any saved files, code, or downloaded
    data (assuming the source of the data was not a grid datastore - datastore
    data is not deleted).
    """
    click.echo("Deleting Interactive node ...", color="yellow")

    try:
        sess = Session(name=session_name)
        if not sess.exists:
            raise RuntimeError(
                f"Session {session_name} does not exist in {env.CONTEXT}. "
                f"If you are pausing a session in another cluster, set "
                f"the default cluster first using "
                f"`grid user set-default-cluster <cluster_name>`."
            )
        sess.delete()
        click.echo(f'{SUCCESS_MARK} Interactive node {session_name} has been deleted successfully.')
    except Exception as e:
        click.echo(f'{FAIL_MARK} {e}')
        raise click.ClickException(f"Failed to delete interactive session '{session_name}'")


@session.command()
@rich_click.argument('session_name', type=str, nargs=1, help='Name of the session to change')
@rich_click.argument('instance_type', type=str, nargs=1, help='Instance type to change to')
@click.option(
    '--spot',
    type=bool,
    is_flag=True,
    default=None,
    show_default=True,
    help='Use a spot instance to launch the session'
)
@click.option(
    '--on_demand',
    '--on-demand',
    'on_demand',
    type=bool,
    is_flag=True,
    default=None,
    show_default=True,
    help='Use an on-demand instance to launch the session'
)
def change_instance_type(
    session_name: str, instance_type: str, spot: Optional[bool], on_demand: Optional[bool]
) -> None:
    """
    Change the instance type of a session; this allows you to upgrade
    or downgrade the compute capability of the session nodes while keeping
    all of your work in progress untouched.

    The session must be PAUSED in order for this command to succeed

    Specifying --spot allows you to change the instance to an interuptable
    spot instances (which come at a steap discount, but which can be
    interrupted and shut down at any point in time depending on cloud
    provider instance type demand).

    specifying --on_demand changes the instance to an on-demand type,
    which cannot be inturrupted but is more expensive.
    """
    click.echo("Changing Session Instance Type ...", color="yellow")

    if (spot is True) and (on_demand is True):
        raise click.ClickException('cannot pass both --spot and --on_demand flags to this command.')

    use_spot = True if spot else False if on_demand else None

    try:

        sess = Session(name=session_name)
        if not sess.exists:
            raise RuntimeError(
                f"Session {session_name} does not exist in {env.CONTEXT}. "
                f"If you are pausing a session in another cluster, set "
                f"the default cluster first using "
                f"`grid user set-default-cluster <cluster_name>`."
            )
        sess.change_instance_type(instance_type=instance_type, use_spot=use_spot)
        click.echo(f'{SUCCESS_MARK} Interactive session {session_name} instance type changed successfully.')
    except Exception as e:
        click.echo(f'{FAIL_MARK} {e}')
        raise click.ClickException(f"Failed to change session instance type '{session_name}'")


def _update_ssh_config_and_check_ixsession_status(ctx, param, value: str) -> int:
    """
    This updates the SSH config for interactive nodes and
    also checks if those nodes can be interacted with SSH
    before attempting an operation. This prevents SSHing into
    nodes that are not un a running state, e.g. paused or pending.

    This manages a section within user's ssh config file
    for all interactive nodes shh config details

    Afterwards you can use systems ssh & related utilities
    (sshfs, rsync, ansible, whatever) with interactive nodes
    directly

    The default file is ~/.ssh/config and  can be changed via
    envvar GRID_SSH_CONFIG

    Returns
    --------
    value: str
        Unmodified value if valid
    """
    client = Grid()
    nodes = client.sync_ssh_config()

    click.echo(f"Sync config for {len(nodes)} interactive nodes")

    target_ixsession = None
    for node in nodes:
        if node["name"] == value:
            target_ixsession = node

    # Check if interactive session exists at all
    if not target_ixsession:
        session_names = [n["name"] for n in nodes]
        raise click.BadArgumentUsage(
            f"Interactive session {value} does not exist. "
            f"Available Interactive Sessions are: {', '.join(session_names)}"
        )

    # Check if the node is in 'running' status
    if target_ixsession["status"] != "running":
        running_ixsessions = [n["name"] for n in nodes if n["status"] == "running"]
        raise click.BadArgumentUsage(
            f"Interactive session {value} is not ready. "
            f"Sessions that are ready to SSH are: {', '.join(running_ixsessions)}"
        )

    return value


@session.command()
@rich_click.argument(
    'node_name',
    type=str,
    callback=_update_ssh_config_and_check_ixsession_status,
    help="The name of the node. This command executes ssh <node name>.",
)
@rich_click.argument('ssh_args', nargs=-1, type=click.UNPROCESSED, help="Arguments to be forwarded to the SSH command.")
def ssh(node_name, ssh_args):
    """SSH into the interactive node identified by NODE_NAME.

    If you'd like the full power of ssh, you can use any ssh client and
    do `ssh <node_name>`. This command is stripped down version of it.

    Example:

        1. Path to custom key:

        grid session ssh satisfied-rabbit-962 -- -i ~/.ssh/my-key

        2. Custom ssh option:

        grid session ssh satisfied-rabbit-962 -- -o "StrictHostKeyChecking accept-new"
    """
    subprocess.check_call(['ssh', node_name, *ssh_args])


@session.command()
@rich_click.argument('interactive_node', type=str, nargs=1, callback=_update_ssh_config_and_check_ixsession_status)
@rich_click.argument('mount_dir', type=str, nargs=1)
def mount(interactive_node, mount_dir):
    r"""Mount session directory to local. The session is identified by
    INTERACTIVE_NODE and MOUNT_DIR is a path to a directory on the local machine.

    To mount a filesystem use:
    ixNode:[dir] mountpoint

    Examples:
        # Mounts the home directory on the interactive node in dir data
        grid interactive mount bluberry-122 ./data

        # mounts ~/data directory on the interactive node to ./data
        grid interactive mount bluberry-122:~/data ./data

    To unmount it:
      fusermount3 -u mountpoint   # Linux
      umount mountpoint           # OS X, FreeBSD

    Under the hood this is just passing data to sshfs after syncing grid's interactive,
    i.e. this command is dumbed down sshfs

    See Also:
        grid sync-ssh-config --help
    """
    if ':' not in interactive_node:
        interactive_node += ":/home/jovyan"

    client = Grid()
    client.sync_ssh_config()

    try:
        subprocess.check_call(['sshfs', interactive_node, mount_dir])
    except FileNotFoundError:
        raise click.ClickException('Unable to mount: sshfs was not found')
    except subprocess.CalledProcessError as e:
        raise click.ClickException(f'Unable to mount: sshfs failed with code {e.returncode}')
