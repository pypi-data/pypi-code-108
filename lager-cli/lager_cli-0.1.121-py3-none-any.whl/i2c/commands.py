"""
    lager.i2c.commands

"""
import time
import threading
import click
import trio
import pigpio
from ..gdbserver.tunnel import serve_tunnel
from ..context import get_default_gateway, ensure_debugger_running

_DATATYPE_CHOICES = click.Choice(('HEX', 'STRING', 'BYTE'), case_sensitive=False)

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

def _get_i2c(pi, addr):
    try:
        i2c = pi.i2c_open(1, addr)
        return i2c
    except AttributeError:
        raise LagerConnectionError

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

def _parse_addr(device):
    if isinstance(device, str):
        if '0x' in device:
            return int(device, base=16)
        else:
            return int(device)
    return device

@click.group()
def i2c():
    """
        Lager i2c commands
    """
    pass

@i2c.command()
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected')
@click.option('--reg', required=False, default=None, help='Optional device register to read from')
@click.option('--type', '_type', type=click.Choice(('HEX', 'STRING', 'BYTE', 'INT'), case_sensitive=False), required=False, default='HEX', show_default=True, help='The datatype of the received I2C data')
@click.option('--verbose', is_flag=True, help='Display additional transaction information')
@click.argument('device')
@click.argument('length', type=int)
@click.pass_context
def read(ctx, gateway, reg, _type, verbose, device, length):
    """
    Read X bytes from an i2c device with an optional register
    """
    if gateway is None:
        gateway = get_default_gateway(ctx)

    thread = threading.Thread(target=run_pigpio_tunnel, args=(verbose, ctx, gateway), daemon=True)
    thread.start()
    time.sleep(0.01) # Why does this work

    if verbose:
        click.secho("Running i2c read")
        click.secho(f"\tGateway: <{gateway}>")
        click.secho(f"\tAddress: {device}")
        click.secho(f"\tRegister: {reg}")
        click.secho(f"\tLength: {length}")

    if reg:
        reg = _parse_addr(reg)
    
    pi = i2c = None

    try:
        pi = _get_pi()
        i2c = _get_i2c(pi, _parse_addr(device))

        if reg is None:
            b, ret_data = pi.i2c_read_device(i2c, length)
        else:
            b, ret_data = pi.i2c_read_i2c_block_data(i2c, reg, length)

        if b < 0:
            click.secho("I2C Read Failed", fg='red', err=True)
            click.echo("Check your device address, electrical connections, and pull-up resistors")
            return

        output_data = _parse_output(_type, ret_data)

        if verbose:
            click.echo(f"Lager I2C Received {b} bytes: {output_data}")
        else:
            click.echo(output_data)
    except LagerConnectionError:
        click.secho("Error establishing an I2C connection on gateway", fg='red', err=True)
    finally:
        if i2c:
            pi.i2c_close(i2c)
        if pi:
            pi.stop()

@i2c.command()
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected')
@click.option('--reg', required=False, default=None, help='Optional device register to write to')
@click.option('--type', '_type', type=click.Choice(('HEX', 'STRING', 'BYTE', 'INT'), case_sensitive=False), required=False, default='HEX', show_default=True, help='The datatype of the provided data')
@click.option('--verbose', is_flag=True, help='Display additional transaction information')
@click.argument('device')
@click.argument('data', nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def write(ctx, gateway, reg, _type, verbose, device, data):
    """
    Write X bytes to an i2c deice with an optional register
    """
    if gateway is None:
        gateway = get_default_gateway(ctx)

    thread = threading.Thread(target=run_pigpio_tunnel, args=(verbose, ctx, gateway), daemon=True)
    thread.start()
    time.sleep(0.01) # Why does this work

    data = _parse_input(_type, data)
    device = _parse_addr(device)
    if reg:
        reg = _parse_addr(reg)
    
    if verbose:
        click.secho("Running i2c read")
        click.secho(f"\tGateway: <{gateway}>")
        click.secho(f"\tAddress: {device}")
        click.secho(f"\tRegister: {reg}")
        click.secho(f"\tData: {data} ({type(data)})")

    pi = i2c = None

    try:
        pi = _get_pi()
        i2c = _get_i2c(pi, _parse_addr(device))

        if reg is None:
            pi.i2c_write_device(i2c, data)
        else:
            pi.i2c_write_i2c_block_data(i2c, reg, data)
    except pigpio.error as e:
        click.secho(e.value, fg='red', err=True)
        if e.value == "I2C write failed":
            click.echo("Check your device address, electrical connections, and pull-up resistors")
    except LagerConnectionError:
        click.secho("Error establishing an I2C connection on gateway", fg='red', err=True)
    finally:
        pi.i2c_close(i2c)
        pi.stop()