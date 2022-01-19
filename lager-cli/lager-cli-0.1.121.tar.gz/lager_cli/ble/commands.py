"""
    lager.ble.commands

    Commands for BLE
"""
import re
import click
from texttable import Texttable
from ..context import get_default_gateway

@click.group(name='ble')
def ble():
    """
        Lager BLE commands
    """
    pass

ADDRESS_NAME_RE = re.compile(r'\A([0-9A-F]{2}-){5}[0-9A-F]{2}\Z')

def check_name(device):
    return 0 if ADDRESS_NAME_RE.search(device['name']) else 1

def normalize_device(device):
    (address, data) = device
    item = {'address': address}
    manufacturer_data = data['manufacturer_data']
    for (k, v) in manufacturer_data.items():
        manufacturer_data[k] = bytes(v)
    item.update(data)
    return item

@ble.command('scan')
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected')
@click.option('--timeout', required=False, help='Total time gateway will spend scanning for devices', default=5.0, type=click.FLOAT, show_default=True)
@click.option('--name-contains', required=False, help='Filter devices to those whose name contains this string')
@click.option('--name-exact', required=False, help='Filter devices to those whose name matches this string')
@click.option('--verbose', required=False, is_flag=True, default=False, help='Verbose output (includes UUIDs)')
def scan(ctx, gateway, timeout, name_contains, name_exact, verbose):
    """
        Scan for BLE devices
    """
    if gateway is None:
        gateway = get_default_gateway(ctx)

    session = ctx.obj.session
    resp = session.ble_scan(gateway, timeout)

    table = Texttable(max_width=100)
    table.set_deco(Texttable.HEADER)
    coltypes = ['t', 'i', 'i']
    colaligns = ['l', 'r', 'r']
    header = ['Name', 'Address', 'rssi']
    if verbose:
        coltypes.extend(['t'])
        colaligns.extend(['r'])
        header.extend(['UUIDs'])

    table.set_cols_dtype(coltypes)
    table.set_cols_align(colaligns)
    table.add_row(header)

    devices = (normalize_device(device) for device in resp.json().items())
    devices = sorted(devices, key=check_name, reverse=True)

    devices = [device for device in devices if name_exact is None or name_exact == device['name']]
    devices = [device for device in devices if name_contains is None or name_contains.lower() in device['name'].lower()]

    if not devices:
        click.secho('No devices found!', fg='red', err=True)
    else:
        for device in devices:
            row = [device['name'], device['address'], device['rssi']]
            if verbose:
                row.extend(['\n'.join(device['uuids'])])
            table.add_row(row)
        click.echo(table.draw())
