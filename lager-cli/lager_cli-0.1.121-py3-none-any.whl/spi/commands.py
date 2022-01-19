"""
    lager.spi.commands

"""
import time
import threading
from enum import Enum
import click
import trio
import pigpio
from ..gdbserver.tunnel import serve_tunnel
from ..context import get_default_gateway, ensure_debugger_running

_DATATYPE_CHOICES = click.Choice(('HEX', 'STRING', 'BYTE'), case_sensitive=False)
_GPIO_CHOICES = click.IntRange(-1, 14)

LAGER_TO_BROADCOM = [26, 1, 2, 10, 9, 25, 7, 8, 11, 27, 17, 15, 14, 4, 16]

SPI_MODES = ["CPOL=0, CPHA=0", "CPOL=0, CPHA=1", "CPOL=1, CPHA=0", "CPOL=1, CPHA=1"]

DEFAULT_SPEED = 1000000 # 1 MHz
DEFAULT_CS = -1 # No chip select
DEFAULT_MODE = 0

class LagerConnectionError(Exception):
    pass

def run_pigpio_tunnel(debug, ctx, gateway):
    host = 'localhost'
    port = 8888
    connection_params = ctx.obj.websocket_connection_params(socktype='pigpio-tunnel', gateway_id=gateway)
    try:
        trio.run(serve_tunnel, host, port, connection_params, 'lager-gpio', debug)
    except PermissionError as exc:
        if port < 1024:
            click.secho(f'Permission denied for port {port}. Using a port number less than '
                        '1024 typically requires root privileges.', fg='red', err=True)
        else:
            click.secho(str(exc), fg='red', err=True)
        if ctx.obj.debug:
            raise
    except OSError as exc:
        click.secho(f'Could not start gpio tunnel on port {port}: {exc}', fg='red', err=True)
        if ctx.obj.debug:
            raise

def _get_pi():
    pi = pigpio.pi('127.0.0.1', 8888, show_errors=False)
    if not pi.connected:
        raise LagerConnectionError
    return pi

def _get_spi(pi, mode, cs, speed):
    flags = mode
    cs_pin = None
    channel = 0

    # TODO support for active high
    # Use hardware CS
    if cs == 6: # Broadcom pin 7
        pi.set_mode(7, pigpio.ALT0)
        flags |= 0xA0
        channel = 1
    elif cs == 7: # Broadcom pin 8
        pi.set_mode(8, pigpio.ALT0)
        flags |= 0xC0
        channel = 0
   
    elif cs in range(0, 14):
        # Use software CS
        cs_pin = LAGER_TO_BROADCOM[cs]
        pi.set_mode(cs_pin, pigpio.OUTPUT)
        if mode == 0 or mode == 1:
            pi.write(cs_pin, pigpio.LOW)
        else:
            pi.write(cs_pin, pigpio.HIGH)
        flags |= 0xE0

    spi = pi.spi_open(channel, speed, flags)
    return spi, cs_pin

def _parse_input(_type, data):
    if _type == 'HEX':
        return [int(d, base=16) for d in data]
    elif _type == 'STRING':
        return ' '.join([s for s in data])
    elif _type == 'BYTE':
        return [int(b, base=2) for b in data]
    elif _type == 'INT':
        return [int(i) for i in data]

def _parse_output(_type, data):
    if _type == 'HEX':
        return ''.join('0x{:02x} '.format(x) for x in data)
    elif _type == 'STRING':
        try:
            output_data = data.decode("ascii")
        except UnicodeDecodeError:
            click.echo("Unable to decode received bytes to ascii")
            return _parse_output('HEX', data)
    elif _type == 'BYTE':
        bitstring = ''.join(format(byte, '08b') for byte in data)
        output_data = ''
        for i in range(0, len(bitstring), 8):
            output_data += bitstring[i:i+8]
            output_data += " "
        return output_data
    elif _type == 'INT':
        return ' '.join([str(i) for i in data])

def _enable_cs(pi, cs_pin, mode):
    if not cs_pin:
        return
    if mode == 0 or mode == 1:
        pi.write(cs_pin, pigpio.LOW)
    else:
        pi.write(cs_pin, pigpio.HIGH)

def _disable_cs(pi, cs_pin, mode):
    if not cs_pin:
        return
    if mode == 0 or mode == 1:
        pi.write(cs_pin, pigpio.HIGH)
    else:
        pi.write(cs_pin, pigpio.LOW)
           
@click.group()
def spi():
    """
        Lager spi commands
    """
    pass

@spi.command()
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected')
@click.option('--speed', required=False, help='Speed of the SPI communication in bits per second (default 1 MHz)')
@click.option('--cs', type=_GPIO_CHOICES, required=False, help='GPIO number to use as a Chip Select line')
@click.option('--mode', type=click.Choice(('0', '1', '2', '3')), required=False, help='SPI Mode number (default mode 0)')
@click.option('--type', '_type', type=click.Choice(('HEX', 'STRING', 'BYTE', 'INT'), case_sensitive=False), required=False, default='HEX', show_default=True, help='The datatype of the provided SPI data')
@click.option('--verbose', is_flag=True, help='Display additional transaction information')
@click.argument('length', type=int)
@click.pass_context
def read(ctx, gateway, speed, cs, mode, _type, verbose, length):
    """
    Read <length> data over SPI
    """
    if gateway is None:
        gateway = get_default_gateway(ctx)

    thread = threading.Thread(target=run_pigpio_tunnel, args=(verbose, ctx, gateway), daemon=True)
    thread.start()
    time.sleep(0.01) # Why does this work

    if speed is None:
        speed = ctx.obj.defaults.get('spi_speed', DEFAULT_SPEED)

    if cs is None:
        cs = ctx.obj.defaults.get('spi_cs', DEFAULT_CS)

    if mode is None:
        mode = ctx.obj.defaults.get('spi_mode', DEFAULT_MODE)
    
    if verbose:
        click.echo("Lager SPI read:")
        click.echo(f"\tGateway: <{gateway}>")
        click.echo(f"\tSpeed: {speed} bps")
        click.echo(f"\tChip Select: GPIO {cs}")
        click.echo(f"\tHardware CS: {cs == 6 or cs == 7}")
        click.echo(f"\tMode: {mode} ({SPI_MODES[int(mode)]})")
        click.echo(f"\tType: {_type}")
        click.echo(f"\tData: {data}")

    pi = spi = cs_pin = None

    try:
        pi = _get_pi()
        spi, cs_pin = _get_spi(pi, int(mode), int(cs), speed)

        _enable_cs(pi, cs_pin, int(mode))
        (b, ret_data) = pi.spi_read(spi, length)
        _disable_cs(pi, cs_pin, int(mode))

        output_data = _parse_output(_type, ret_data)

        if verbose:
            click.echo(f"Lager SPI Received {b} bytes: {ret_data}")
            click.echo(f"Formatted output: {output_data}")
        else:
            click.echo(output_data)
    except LagerConnectionError:
        click.secho("Error establishing an SPI connection on gateway", fg='red', err=True)
    finally:
        if spi:
            pi.spi_close(spi)
        if pi:
            pi.stop()

@spi.command()
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected')
@click.option('--speed', required=False, help='Speed of the SPI communication in bits per second (default 1 MHz)')
@click.option('--cs', type=_GPIO_CHOICES, required=False, help='GPIO number to use as a Chip Select line')
@click.option('--mode', type=click.Choice(('0', '1', '2', '3')), required=False, help='SPI Mode number (default mode 0)')
@click.option('--type', '_type', type=click.Choice(('HEX', 'STRING', 'BYTE', 'INT'), case_sensitive=False), required=False, default='HEX', show_default=True, help='The datatype of the provided SPI data')
@click.option('--verbose', is_flag=True, help='Display additional transaction information')
@click.argument('data', nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def write(ctx, gateway, speed, cs, mode, _type, verbose, data):
    """
    Send data over SPI
    """
    if gateway is None:
        gateway = get_default_gateway(ctx)

    thread = threading.Thread(target=run_pigpio_tunnel, args=(verbose, ctx, gateway), daemon=True)
    thread.start()
    time.sleep(0.01) # Why does this work
    
    data = _parse_input(_type, data)

    if speed is None:
        speed = ctx.obj.defaults.get('spi_speed', DEFAULT_SPEED)

    if cs is None:
        cs = ctx.obj.defaults.get('spi_cs', DEFAULT_CS)

    if mode is None:
        mode = ctx.obj.defaults.get('spi_mode', DEFAULT_MODE)

    if verbose:
        click.secho("Lager SPI write:")
        click.secho(f"\tGateway: <{gateway}>")
        click.secho(f"\tSpeed: {speed} bps")
        click.secho(f"\tChip Select: GPIO{cs}")
        click.secho(f"\tMode: {mode} ({SPI_MODES[int(mode)]})")
        click.secho(f"\tType: {_type}")
        click.secho(f"\tData: {data}")

    pi = spi = cs_pin = None

    try:
        pi = _get_pi()
        if cs is None:
            cs = -1
        spi, cs_pin = _get_spi(pi, int(mode), int(cs), speed)

        _enable_cs(pi, cs_pin, int(mode))
        pi.spi_write(spi, data)
        _disable_cs(pi, cs_pin, int(mode))

        if verbose:
            click.echo("Acknowledged")
    except LagerConnectionError:
        click.secho("Error establishing an SPI connection on gateway", fg='red', err=True)
    finally:
        if spi:
            pi.spi_close(spi)
        if pi:
            pi.stop()

@spi.command()
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected')
@click.option('--speed', required=False, help='Speed of the SPI communication in bits per second (default 1 MHz)')
@click.option('--cs', type=_GPIO_CHOICES, required=False, help='GPIO number to use as a Chip Select line')
@click.option('--mode', type=click.Choice(('0', '1', '2', '3')), required=False, help='SPI Mode number (default mode 0)')
@click.option('--type', '_type', type=click.Choice(('HEX', 'STRING', 'BYTE', 'INT'), case_sensitive=False), required=False, default='HEX', show_default=True, help='The datatype of the provided SPI data')
@click.option('--verbose', is_flag=True, help='Display additional transaction information')
@click.argument('data', nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def transfer(ctx, gateway, speed, cs, mode, _type, verbose, data):
    """
    Transfer data over SPI
    """
    if gateway is None:
        gateway = get_default_gateway(ctx)

    thread = threading.Thread(target=run_pigpio_tunnel, args=(verbose, ctx, gateway), daemon=True)
    thread.start()
    time.sleep(0.01) # Why does this work
    
    data = _parse_input(_type, data)

    if speed is None:
        speed = ctx.obj.defaults.get('spi_speed', DEFAULT_SPEED)

    if cs is None:
        cs = ctx.obj.defaults.get('spi_cs', DEFAULT_CS)

    if mode is None:
        mode = ctx.obj.defaults.get('spi_mode', DEFAULT_MODE)

    if verbose:
        click.secho("Lager SPI transfer:")
        click.secho(f"\tGateway: <{gateway}>")
        click.secho(f"\tSpeed: {speed} bps")
        click.secho(f"\tChip Select: GPIO{cs}")
        click.secho(f"\tMode: {mode} ({SPI_MODES[int(mode)]})")
        click.secho(f"\tType: {_type}")
        click.secho(f"\tData: {data}")

    pi = spi = cs_pin = None

    try:
        pi = _get_pi()
        if cs is None:
            cs = -1
        spi, cs_pin = _get_spi(pi, int(mode), int(cs), speed)

        _enable_cs(pi, cs_pin, int(mode))
        (b, ret_data) = pi.spi_xfer(spi, data)
        _disable_cs(pi, cs_pin, int(mode))

        output_data = _parse_output(_type, ret_data)

        if verbose:
            click.echo(f"Lager SPI Received {b} bytes: {ret_data}")
            click.echo(f"Formatted output: {output_data}")
        else:
            click.echo(output_data)
    except LagerConnectionError:
        click.secho("Error establishing an SPI connection on gateway", fg='red', err=True)
    finally:
        if spi:
            pi.spi_close(spi)
        if pi:
            pi.stop()

