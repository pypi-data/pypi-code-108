"""
Defines and implements `anyscale list {resource}` commands.
Supported resources: clouds, projects, sessions, ips
"""

from typing import Any, Optional

import click

from anyscale.cli_logger import BlockLogger
from anyscale.controllers.list_controller import ListController


log = BlockLogger()


@click.group(
    "list", hidden=True, help="List resources (projects, clusters) within Anyscale."
)
def list_cli() -> None:
    pass


@list_cli.command(
    name="clouds",
    help="[DEPRECATED] List the clouds currently available in your account.",
    hidden=True,
)
@click.option("--json", "show_json", help="Return the results in json", is_flag=True)
def list_clouds(show_json: bool) -> None:
    log.warning(
        "`anyscale list clouds` has been deprecated. Please use `anyscale cloud list` instead."
    )
    list_controller = ListController()
    output = list_controller.list_clouds(json_format=show_json)
    print(output)


@list_cli.command(
    name="projects", help="[DEPRECATED] List all accessible projects.", hidden=True
)
@click.option("--json", "show_json", help="Return the results in json", is_flag=True)
@click.pass_context
def project_list(ctx: Any, show_json: bool) -> None:
    log.warning(
        "`anyscale list projects` has been deprecated. Please use `anyscale project list` instead."
    )
    list_controller = ListController()
    output = list_controller.list_projects(json_format=show_json)
    print(output)


@list_cli.command(
    name="sessions",
    help="[DEPRECATED] List all clusters within the current project.",
    hidden=True,
)
@click.option(
    "--name",
    help="Name of the cluster. If provided, this prints the snapshots that "
    "were applied and commands that ran for all clusters that match "
    "this name.",
    default=None,
)
@click.option("--all", help="List all clusters, including inactive ones.", is_flag=True)
@click.option("--json", "show_json", help="Return the results in json", is_flag=True)
def session_list(name: Optional[str], all: bool, show_json: bool) -> None:
    log.warning(
        "`anyscale list sessions` has been deprecated. Please use `anyscale cluster list` instead."
    )
    list_controller = ListController()
    output = list_controller.list_sessions(
        name=name, show_all=all, json_format=show_json
    )
    print(output)


@list_cli.command(name="ips", help="List IP addresses of head and worker nodes.")
@click.argument("cluster-name", required=False, type=str)
@click.option("--json", "show_json", help="Return the results in json", is_flag=True)
@click.option(
    "--all", "all_sessions", help="List IPs of all active clusters.", is_flag=True
)
def list_ips(cluster_name: Optional[str], show_json: bool, all_sessions: bool) -> None:
    """List IP addresses of head and worker nodes."""
    list_controller = ListController()
    output = list_controller.list_ips(
        session_name=cluster_name, json_format=show_json, all_sessions=all_sessions
    )
    print(output)
