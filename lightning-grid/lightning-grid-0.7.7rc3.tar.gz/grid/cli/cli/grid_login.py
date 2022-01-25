from typing import Optional

import click

from grid.cli import rich_click
import grid.sdk.env as env
from grid.sdk.login import login as grid_login
from grid.sdk.rest.exceptions import GridException


@click.option('--username', type=str, help='Username used in Grid')
@click.option('--key', type=str, help='API Key from Grid')
@rich_click.command()
def login(username: Optional[str] = None, key: Optional[str] = None) -> None:
    """Authorize the CLI to access Grid AI resources for a particular user.

    If no username or key is provided, the CLI will prompt for them. After
    providing your username, a web browser will open to your account settings
    page where your API key can be found.
    """
    # Prompt the user for username and API Key.
    # We ask for the username first because that's
    # the same as their Github usernames.
    if not username:
        username = click.prompt('Please provide your Grid or GitHub username')
    if not key:
        settings_url = env.GRID_URL + "#/settings?tabId=apikey"
        click.launch(settings_url)
        key = click.prompt('Please provide your Grid API key')

    try:
        status = grid_login(username=username, api_key=key)
    except ConnectionRefusedError:  # only relevant until we have gQL
        raise click.ClickException('Invalid username or API key')
    except GridException as e:
        raise click.ClickException(str(e))
    if status:
        click.echo('Login successful. Welcome to Grid.')
