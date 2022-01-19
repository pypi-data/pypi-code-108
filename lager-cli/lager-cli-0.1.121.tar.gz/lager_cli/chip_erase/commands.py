"""
    lager.chip_erase.commands

    Commands for chip erase
"""
import click
from .. import SUPPORTED_DEVICES, SUPPORTED_INTERFACES
from ..context import get_default_gateway

@click.command(name='chip-erase')
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected')
@click.option('--device', help='Target device type', type=click.Choice(SUPPORTED_DEVICES), required=True)
@click.option('--interface', help='Target interface', type=click.Choice(SUPPORTED_INTERFACES), default='ftdi', show_default=True)
@click.option('--transport', help='Target transport', type=click.Choice(['swd', 'jtag', 'hla_swd', 'dapdirect_swd']), default='swd', show_default=True)
@click.option('--speed', help='Target interface speed in kHz', required=False, default='adaptive', show_default=True)
def chip_erase(ctx, gateway, device, interface, transport, speed):
    if gateway is None:
        gateway = get_default_gateway(ctx)

    session = ctx.obj.session
    resp = session.chip_erase(gateway, device, interface, transport, speed).json()
    if resp['ok']:
        click.secho('Chip erase successful', fg='green')
