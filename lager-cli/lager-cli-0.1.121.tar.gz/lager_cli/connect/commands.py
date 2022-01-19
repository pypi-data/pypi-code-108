"""
    lager.connect.commands

    Commands for connecting to / disconnecting from DUT
"""
import itertools
import time
import click
from .. import SUPPORTED_DEVICES, SUPPORTED_INTERFACES
from ..context import get_default_gateway
from ..exceptions import GatewayTimeoutError
from ..paramtypes import HexParamType, VarAssignmentType

@click.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected')
@click.option(
    '--snr',
    help='Serial number of device to connect. Required if multiple DUTs connected to gateway')
@click.option('--device', help='Target device type', type=click.Choice(SUPPORTED_DEVICES), required=True)
@click.option('--interface', help='Target interface', type=click.Choice(SUPPORTED_INTERFACES), default='ftdi', show_default=True)
@click.option('--transport', help='Target transport', type=click.Choice(['swd', 'jtag', 'hla_swd', 'dapdirect_swd']), default='swd', show_default=True)
@click.option('--speed', help='Target interface speed in kHz', required=False, default='adaptive', show_default=True)
@click.option('--workareasize', help='Set work area size. Useful for STM32 chips.', type=HexParamType(), required=False, default=None)
@click.option('--set', 'set_', multiple=True, type=VarAssignmentType(), help='Set debugger environment variable FOO to BAR')
@click.option('--force', is_flag=True, default=False, help='Disconnect debugger before reconnecting. If not set, connect will fail if debugger is already connected. Cannot be used with --ignore-if-connected', show_default=True)
@click.option('--ignore-if-connected', is_flag=True, default=False, help='If debugger is already connected, skip connection attempt and exit with success. Cannot be used with --force', show_default=True)
def connect(ctx, gateway, snr, device, interface, transport, speed, workareasize, set_, force, ignore_if_connected):
    """
        Connect your gateway to your Device Under Test (DUT).
    """
    if force and ignore_if_connected:
        click.secho('Cannot specify --force and --ignore-if-connected', fg='red')
        ctx.exit(1)

    set_ = list(set_)
    if workareasize:
        set_.append(['WORKAREASIZE', hex(workareasize)])
    if gateway is None:
        gateway = get_default_gateway(ctx)

    # Step one, try to start gdb on gateway
    files = []
    if snr:
        files.append(('snr', snr))
    files.append(('device', device))
    files.append(('interface', interface))
    files.append(('transport', transport))
    files.append(('speed', speed))
    files.append(('force', force))
    files.append(('ignore_if_connected', ignore_if_connected))
    files.extend(
        zip(itertools.repeat('varnames'), [name for (name, _value) in set_])
    )
    files.extend(
        zip(itertools.repeat('varvalues'), [value for (_name, value) in set_])
    )

    session = ctx.obj.session
    tries = 3
    while True:
        try:
            resp = session.start_debugger(gateway, files=files).json()
            break
        except GatewayTimeoutError as exc:
            tries -= 1
            if tries <= 0:
                click.secho(str(exc), fg='red', err=True)
                ctx.exit(1)
            else:
                click.echo('Connection to gateway timed out, retrying...', err=True)
                time.sleep(2)

    if device == 'at91samdxx':
        if 'Error: Failed to read memory' in resp['logfile'] and 'Info : SWD DPIDR' in resp['logfile']:
            click.secho('Failed to read memory; you may need to issue a chip-erase command', fg='red')
            try:
                session.stop_debugger(gateway)
            except Exception:
                pass
            raise SystemExit(1)

    if resp.get('start') == 'ok':
        click.secho('Connected!', fg='green')
    elif resp.get('already_running') == 'ok':
        click.secho('Debugger already connected, ignoring', fg='green')

@click.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected')
def disconnect(ctx, gateway):
    """
        Disconnect your gateway from your Device Under Test (DUT).
    """
    if gateway is None:
        gateway = get_default_gateway(ctx)

    session = ctx.obj.session
    session.stop_debugger(gateway)
    click.secho('Disconnected!', fg='green')
