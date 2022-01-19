"""
    lager.serial_ports.commands

    Listing serial ports
"""
import click
from ..context import get_default_gateway

@click.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected')
def serial_ports(ctx, gateway):
    """
        List the serial ports attached to a gateway

        Example output:

        ➜ lager serial-ports

        \b
        /dev/ttyS0 - Lager Gateway serial port
        /dev/ttyACM0 - Atmel Corp. Xplained Pro board debugger and programmer; serial number ATML2637010000000000
        /dev/ttyACM1 - SEGGER VL805 USB 3.0 Host Controller; serial number 683836793
        /dev/ttyUSB1 - Future Technology Devices International, Ltd FT2232C/D/H Dual UART/FIFO IC; serial number FT4LS2MN
    """
    if gateway is None:
        gateway = get_default_gateway(ctx)

    session = ctx.obj.session
    resp = session.serial_ports(gateway)
    style = ctx.obj.style
    for port in resp.json()['serial_ports']:
        click.echo('{} - {}'.format(style(port['device'], fg='green'), port['description']))
