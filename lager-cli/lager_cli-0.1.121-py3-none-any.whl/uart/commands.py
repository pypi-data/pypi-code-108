"""
    lager.uart.commands

    Commands for DUT UART interaction
"""
import sys
import math
import click
from ..context import get_default_gateway
from ..status import run_job_output
from ..config import read_config_file

def do_uart(ctx, gateway, serial_device, baudrate, bytesize, parity, stopbits, xonxoff, rtscts, dsrdtr, test_runner):
    if serial_device is None:
        config = read_config_file()
        if 'LAGER' in config and 'serial_device' in config['LAGER']:
            serial_device = config.get('LAGER', 'serial_device')

    if not serial_device:
        raise click.UsageError(
            '--serial-port required',
            ctx=ctx,
        )

    if xonxoff and rtscts:
        raise click.UsageError(
            'Cannot use xonxoff and rtscts simultaneously',
            ctx=ctx,
        )
    if gateway is None:
        gateway = get_default_gateway(ctx)

    session = ctx.obj.session
    serial_options = {
        'device': serial_device,
        'baudrate': baudrate,
        'bytesize': bytesize,
        'parity': parity,
        'stopbits': stopbits,
        'xonxoff': xonxoff,
        'rtscts': rtscts,
        'dsrdtr': dsrdtr,
    }
    return session.uart_gateway(gateway, serial_options, test_runner)


@click.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected')
@click.option('--serial-device', '--serial-port', help='Gateway serial port device path', metavar='path')
@click.option('--baudrate', help='Serial baud rate', type=int, default=None)
@click.option('--bytesize', help='Number of data bits', type=click.Choice(['5', '6', '7', '8']), default=None)
@click.option('--parity', help='Parity check', type=click.Choice(['none', 'even', 'odd', 'mark', 'space']), default=None)
@click.option('--stopbits', help='Number of stop bits', type=click.Choice(['1', '1.5', '2']), default=None)
@click.option('--xonxoff/--no-xonxoff', default=None, help='Enable/disable software XON/XOFF flow control')
@click.option('--rtscts/--no-rtscts', default=None, help='Enable/disable hardware RTS/CTS flow control')
@click.option('--dsrdtr/--no-dsrdtr', default=None, help='Enable/disable hardware DSR/DTR flow control')
@click.option('--test-runner', help='End the UART session when end-of-test is detected', type=click.Choice(['none', 'unity', 'fixture', 'ptty']), default='none')
@click.option('-i', '--interactive', is_flag=True, help='Run as an interactive TTY session', default=False)
@click.option('--message-timeout', default=math.inf, type=click.FLOAT,
              help='Max time in seconds to wait between messages from API.')
@click.option('--overall-timeout', default=math.inf, type=click.FLOAT,
              help='Cumulative time in seconds to wait for session output.')
@click.option('--eof-timeout', default=None, type=click.FLOAT,
              help='Time in seconds to wait before closing connection after input EOF received')
@click.option('--display-job-id', default=False, is_flag=True)
@click.option('--line-ending', help='Line ending for input - determines the bytes sent to the Device Under Test when you press `Enter` or `Return`', type=click.Choice(['CRLF', 'LF']), default='LF')
@click.option('--opost/--no-opost', help=r'Enable implementation-defined output processing for your local output terminal. Typically this will convert \n to \r\n on output', is_flag=True, default=False, show_default=True)
@click.option('--serial-channel', help=r'Select a specific UART channel (for use with Test Fixture)', type=int, default=0)
@click.option('--fake-tty', help=r'Create a fake serial port (linux ptty)', is_flag=True, default=False, show_default=True)
def uart(ctx, gateway, serial_device, baudrate, bytesize, parity, stopbits, xonxoff, rtscts, dsrdtr,
         test_runner, interactive, message_timeout, overall_timeout, eof_timeout, display_job_id, line_ending, opost, serial_channel, fake_tty):
    """
        Connect to UART on a DUT.
    """
    if interactive:
        if not sys.stdin.isatty():
            click.echo('stdin is not a tty!', err=True)
            ctx.exit(1)
        if not sys.stdout.isatty():
            click.echo('stdout is not a tty!', err=True)
            ctx.exit(1)

    interactive = "raw" if interactive else False
    if gateway is None:
        gateway = get_default_gateway(ctx)

    resp = do_uart(
        ctx, gateway, serial_device, baudrate, bytesize, parity,
        stopbits, xonxoff, rtscts, dsrdtr, test_runner,
    )
    test_run = resp.json()
    job_id = test_run['test_run']['id']
    if display_job_id:
        click.echo('Job id: {}'.format(job_id), err=True)

    region = ctx.obj.session.region(gateway)

    connection_params = ctx.obj.websocket_connection_params(socktype='job', job_id=job_id, region=region)
    run_job_output(connection_params, test_runner, interactive, line_ending, message_timeout, overall_timeout,
        eof_timeout, ctx.obj.debug, opost=opost, serial_channel=serial_channel, ptty=fake_tty)
