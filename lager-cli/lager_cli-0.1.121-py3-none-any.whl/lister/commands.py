"""
    lager.lister.commands

    List commands
"""
import click
from texttable import Texttable
from .. import SUPPORTED_DEVICES
from ..config import read_config_file

@click.group(name='list')
def lister():
    """
        Lager list commands
    """
    pass


@lister.command()
@click.pass_context
def gateways(ctx):
    """
        List a user's gateways
    """

    session = ctx.obj.session
    resp = session.list_gateways()
    resp.raise_for_status()

    table = Texttable()
    table.set_deco(Texttable.HEADER)
    table.set_cols_dtype(['t', 'i'])
    table.set_cols_align(["l", "r"])
    table.add_row(['name', 'id'])

    for gateway in resp.json()['gateways']:
        table.add_row([gateway['name'], gateway['id']])
    click.echo(table.draw())

@lister.command()
def supported_devices():
    """
        List supported devices
    """
    for device in SUPPORTED_DEVICES:
        click.echo(device)

@lister.command()
def secret_token():
    """
        Show the secret token, which can be used within a third-party CI system to auth lager-cli
    """
    config = read_config_file()
    click.echo(config['AUTH']['refresh'])
