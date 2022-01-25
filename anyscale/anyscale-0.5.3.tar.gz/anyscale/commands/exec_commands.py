from typing import List, Optional, Tuple

import click

from anyscale.controllers.exec_controller import ExecController


@click.command(
    name="exec",
    hidden=True,
    help="[DEPRECATED] Execute shell commands in interactive cluster.",
)
@click.option(
    "--session-name",
    "-n",
    type=str,
    required=False,
    default=None,
    help="Cluster name: optional if only one running cluster.",
    envvar="SESSION_NAME",
    hidden=True,
)
@click.option(
    "--cluster-name",
    "-n",
    type=str,
    required=False,
    default=None,
    help="Cluster name: optional if only one running cluster.",
    envvar="CLUSTER_NAME",
)
@click.option(
    "--screen", is_flag=True, default=False, help="Run the command in a screen."
)
@click.option("--tmux", is_flag=True, default=False, help="Run the command in tmux.")
@click.option(
    "--port-forward",
    "-p",
    required=False,
    multiple=True,
    type=int,
    help="Port to forward. Use this multiple times to forward multiple ports.",
)
@click.option(
    "--sync",
    is_flag=True,
    default=False,
    help="Rsync all the file mounts before executing the command.",
)
@click.option(
    "--stop",
    help="Stop session after command finishes executing.",
    is_flag=True,
    default=False,
)
@click.option(
    "--terminate",
    help="Terminate session after command finishes executing.",
    is_flag=True,
    default=False,
)
@click.argument("commands", nargs=-1, type=str)
def anyscale_exec(
    session_name: str,
    cluster_name: Optional[str],
    screen: bool,
    tmux: bool,
    port_forward: Tuple[int],
    sync: bool,
    stop: bool,
    terminate: bool,
    commands: List[str],
) -> None:
    exec_controller = ExecController()
    exec_controller.anyscale_exec(
        cluster_name or session_name,
        screen,
        tmux,
        port_forward,
        sync,
        stop,
        terminate,
        commands,
    )
