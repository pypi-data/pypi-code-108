"""
    lager.wifi.commands

    Commands for controlling the wifi network
"""

import click
from texttable import Texttable

from ..context import get_default_gateway

@click.group(name='wifi')
def _wifi():
    """
        Lager wifi commands
    """
    pass


@_wifi.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway')
def status(ctx, gateway):
    """
        Get the current WiFi Status of the gateway
    """
    if gateway is None:
        gateway = get_default_gateway(ctx)

    session = ctx.obj.session
    resp = session.get_wifi_state(gateway)
    resp.raise_for_status()
    wifis = resp.json()
    for key in wifis:
        click.echo(f"Interface: {key}")
        click.echo(f'\tSSID:  {wifis[key]["ssid"]}')
        click.echo(f'\tState: {wifis[key]["state"]}')

@_wifi.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway')
@click.option('--interface', required=False, help='Wireless interface to use')
def access_points(ctx, gateway, interface=None):
    """
        Get WiFi access points visible to the gateway
    """
    # TODO implement table for ext wifi

    if gateway is None:
        gateway = get_default_gateway(ctx)

    session = ctx.obj.session
    resp = session.get_wifi_access_points(gateway, interface)
    resp.raise_for_status()
    seen = set()

    table = Texttable()
    table.set_deco(Texttable.HEADER)
    table.set_cols_dtype(['t', 't', 'i'])
    table.set_cols_align(['l', 'l', 'r'])
    table.header(['ssid', 'security', 'strength'])
    for ap in resp.json().get('access_points', []):
        if ap['ssid'] not in seen:
            table.add_row([ap['ssid'], ap['security'], ap['strength']])
        seen.add(ap['ssid'])

    click.echo(table.draw())


@_wifi.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway')
@click.option('--ssid', required=True, help='SSID of the network to connect to')
@click.option('--interface', help='Wireless interface to use', default='wlan0', show_default=True)
@click.option('--password', required=False, help='Password of the network to connect to', default='')
def connect(ctx, gateway, ssid, interface, password=''):
    """
        Connect the gateway to a new network
    """
    if gateway is None:
        gateway = get_default_gateway(ctx)

    session = ctx.obj.session
    resp = session.connect_wifi(gateway, ssid, password, interface)
    resp.raise_for_status()
    if resp.json().get('acknowledged'):
        click.secho(f'{interface} connected', fg='green')


@_wifi.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway')
@click.confirmation_option(prompt='An ethernet connection will be required to bring the gateway back online. Proceed?')
@click.argument('SSID', required=True)
def delete_connection(ctx, gateway, ssid):
    """
        Delete the specified network from the gateway
    """
    if gateway is None:
        gateway = get_default_gateway(ctx)

    session = ctx.obj.session
    resp = session.delete_wifi_connection(gateway, ssid)
    resp.raise_for_status()
    if resp.json().get('acknowledged'):
        click.secho(f'{ssid} disconnected', fg='green')
