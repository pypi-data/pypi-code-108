import click

from grid.cli import rich_click
from grid.cli.core.team import Team


@rich_click.command()
@rich_click.argument('team_name', type=str, required=True, help="Team name")
def team(team_name: str):
    """Show information about a TEAM_NAME."""
    for t in Team.get_all():
        if t.name == team_name:
            click.echo(f"{t.name} -  Created on {t.created_at}")
            click.echo(f"  Role: {t.role}")
            click.echo("  Members")
            for m in t.members:
                click.echo(f"    {m['firstName']} {m['lastName']} <{m['username']}>")
            return
    click.echo(f"Team {team_name} not found")
