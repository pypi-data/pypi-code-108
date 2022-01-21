import json
from typing import Any, Dict, List, Optional

import click
from dateutil.parser import parse as date_string_parse
from rich.console import Console

from grid.cli import rich_click
from grid.cli.client import Grid
from grid.cli.observables import BaseObservable


@rich_click.group(invoke_without_command=True)
@click.pass_context
@click.option('--set_default', type=str, help='Credential set to make default.')
def credentials(ctx, set_default: Optional[str] = None) -> None:
    """Manages credentials."""
    if ctx.invoked_subcommand is None:
        client = Grid()

        if set_default:
            client.credentials_update(credential_id=set_default, is_default=True)

        result = client.get_credentials()
        print_creds_table(result['getUserCredentials'])


@credentials.command()
@click.option(
    '--provider', type=click.Choice(['aws'], case_sensitive=False), help='Credential provider.', required=True
)
@click.option('--file', type=click.File('r'), help='JSON file to where credentials are', required=True)
@click.option('--alias', type=str, help='Given name for a credential set')
@click.option('--description', type=str, help='Description for a credential set')
def add(
    provider: Optional[str] = None,
    file: Optional[click.File] = None,
    alias: Optional[str] = None,
    description: Optional[str] = None
) -> None:
    """Adds user credentials to access Grid."""
    client = Grid()

    #  Creates new credentials.
    creds = json.load(file)
    client.credentials_add(provider=provider, credentials=creds, alias=alias, description=description)

    #  Print credentials in terminal.
    result = client.get_credentials()
    print_creds_table(result['getUserCredentials'])


def print_creds_table(creds: List[Dict[str, Any]]) -> Console:
    """Prints table with cloud credentials."""
    if not creds:
        message = """
            No credentials available. Add new credentials with:

                grid credentials add --file [CREDENTIALS_JSON_FILE] --provider [PROVIDER]

            """
        raise click.ClickException(message)
    table = BaseObservable.create_table(
        columns=['Credential', 'Provider', 'Alias', 'Created At', 'Last Used At', 'Default']
    )

    for row in creds:
        created_at = date_string_parse(row['createdAt'])
        _created_at = f'{created_at:%Y-%m-%d %H:%M}'
        table.add_row(
            row['credentialId'], row['provider'], row['alias'], _created_at, row['lastUsedAt'],
            str(row['defaultCredential'])
        )

    console = Console()
    console.print(table)

    #  We return the console for testing purposes.
    #  This isn't actually used anywhere else.
    return console
