"""
Commands to interact with the Anyscale API
"""

import click

from anyscale.commands.anyscale_api.projects_commands import projects
from anyscale.commands.anyscale_api.session_commands_commands import session_commands
from anyscale.commands.anyscale_api.session_operations_commands import (
    session_operations_commands,
)
from anyscale.commands.anyscale_api.sessions_commands import sessions


@click.group(
    "api", hidden=True, help="Various commands to interact with the Anyscale API."
)
def anyscale_api() -> None:
    pass


anyscale_api.add_command(session_commands)
anyscale_api.add_command(projects)
anyscale_api.add_command(sessions)
anyscale_api.add_command(session_operations_commands)
