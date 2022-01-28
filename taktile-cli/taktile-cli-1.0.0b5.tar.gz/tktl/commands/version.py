import click

from tktl.commands import login as login_commands


@click.command("version", help="Show the version and exit")
@click.option(
    "--check/--no-check", default=True, help="Check if new version is available"
)
def get_version(check: bool = True):
    command = login_commands.ShowVersionCommand()
    command.execute(check=check)
