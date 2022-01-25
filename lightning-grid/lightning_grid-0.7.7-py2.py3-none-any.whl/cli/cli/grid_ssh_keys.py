from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from grid.cli import rich_click
from grid.cli.client import Grid


@rich_click.group()
def ssh_keys() -> None:
    """Manage SSH keys."""


@ssh_keys.command()
@rich_click.argument('name', type=str, nargs=1, required=True)
@rich_click.argument('key', type=click.Path(exists=True), nargs=1, required=True)
def add(name: str, key: str):
    """Register a new SSH public key by providing a path to the KEY file
    and a NAME for it in Grid.
    """
    key = Path(key).read_text('utf-8').strip()
    result = Grid().add_ssh_public_key(key=key, name=name)

    if result['addSSHPublicKey'].get('success'):
        click.echo(f"Added key {name} with id: {result['addSSHPublicKey']['id']}")

    else:
        raise click.ClickException(f"Failed to add key: {key}")


@ssh_keys.command(name="list")
@click.option('--limit', 'limit', type=int, required=False, default=100, help='maximum number of public keys to fetch')
def ls(limit: int):
    """"list currently registered SSH public keys"""
    table = Table(show_header=True, header_style="bold green")
    table.add_column('id', style='dim')
    table.add_column('name', style='dim')
    table.add_column('public_key', style='dim')

    client = Grid()
    for row in client.list_public_ssh_keys(limit):
        table.add_row(row['id'], row['name'], row['publicKey'])
    Console().print(table)


@ssh_keys.command(name="authorized_keys", hidden=True)
@click.option('--limit', 'limit', type=int, required=False, default=100, help='maximum number of public keys to fetch')
def authorized_keys(limit: int):
    """list all registered SSH public keys in authorized_keys format"""
    for row in Grid().list_public_ssh_keys(limit):
        click.echo(f"#ID {row['id'].strip()}")
        click.echo(f"#Name {row['name'].strip()}")
        click.echo(row['publicKey'].strip())


# This command is used within ssh server AuthorizedKeysCommand section
# and it is not intended to be used by the end consumer, thus it's hidden
@ssh_keys.command(help="remote registered SSH public key")
@rich_click.argument('key_id', type=str, nargs=1)
def rm(key_id: str):
    Grid().delete_ssh_public_key(key_id=key_id)
