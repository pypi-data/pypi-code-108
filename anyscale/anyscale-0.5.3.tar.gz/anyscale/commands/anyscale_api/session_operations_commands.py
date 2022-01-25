"""
Commands to interact with the Anyscale Session Operatons API
"""

import click

from anyscale.authenticate import get_auth_api_client
from anyscale.formatters import common_formatter


@click.group(
    "session_operations", help="Commands to interact with the Session Operations API.",
)
def session_operations_commands() -> None:
    pass


@session_operations_commands.command(
    name="get", short_help="Retrieves a Session Operation."
)
@click.argument("session_operation_id", required=True)
def get_session_operation(session_operation_id: str,) -> None:
    """Retrieves a Session Operation.
    """

    api_client = get_auth_api_client().anyscale_api_client
    response = api_client.get_session_operation(session_operation_id)
    print(common_formatter.prettify_json(response.to_dict()))
