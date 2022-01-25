"""
Commands to interact with the Anyscale Session Commands API
"""

from typing import Optional

import click

from anyscale.authenticate import get_auth_api_client
from anyscale.formatters import common_formatter
from anyscale.sdk.anyscale_client import CreateSessionCommand


@click.group(
    "commands", help="Commands to interact with the Session Commands API.",
)
def session_commands() -> None:
    pass


@session_commands.command(name="list", short_help="Lists Session Commands.")
@click.argument("session-id", required=True)
@click.option(
    "--count", type=int, default=10, help="Number of commands to show. Defaults to 10"
)
@click.option(
    "--paging-token",
    required=False,
    help="Paging token used to fetch subsequent pages of commands.",
)
def list_session_commands(
    session_id: str, count: int, paging_token: Optional[str],
) -> None:
    """Lists commands that have been executed on Session with SESSION_ID"""

    api_client = get_auth_api_client().anyscale_api_client
    response = api_client.list_session_commands(
        session_id, count=count, paging_token=paging_token
    )

    print(common_formatter.prettify_json(response.to_dict()))


@session_commands.command(name="get", short_help="Get details about a Session Command.")
@click.argument("session-command-id", required=True)
def get_session_command(session_command_id: str) -> None:
    """Get details about the Session Command with id SESSION_COMMAND_ID"""

    api_client = get_auth_api_client().anyscale_api_client
    response = api_client.get_session_command(session_command_id)

    print(common_formatter.prettify_json(response.to_dict()))


@session_commands.command(name="kill", short_help="Kills a Session Command.")
@click.argument("session-command-id", required=True)
def kill_session_command(session_command_id: str) -> None:
    """Kills the Session Command with id SESSION_COMMAND_ID"""

    api_client = get_auth_api_client().anyscale_api_client
    response = api_client.kill_session_command(session_command_id)

    print(common_formatter.prettify_json(response.to_dict()))


@session_commands.command(
    name="create", short_help="Creates and executes a Session Command."
)
@click.argument("session-id", required=True)
@click.argument("shell-command", required=True)
def create_session_command(session_id: str, shell_command: str) -> None:
    """Creates and executes SHELL_COMMAND on the session with id SESSION_ID."""

    api_client = get_auth_api_client().anyscale_api_client
    create_data = CreateSessionCommand(
        session_id=session_id, shell_command=shell_command
    )
    response = api_client.create_session_command(create_data)

    print(common_formatter.prettify_json(response.to_dict()))
