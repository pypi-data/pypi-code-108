"""
    lager.openocd.commands

    Openocd telnet server tunnel commands
"""

import click
import trio
from ..gdbserver.tunnel import serve_tunnel
from ..context import get_default_gateway, ensure_debugger_running

def run_openocd_tunnel(ctx, host, port, gateway, rtt):
    connection_params = ctx.obj.websocket_connection_params(socktype='openocd-tunnel', gateway_id=gateway)
    rtt_params = None
    if rtt:
        rtt_params = ctx.obj.websocket_connection_params(socktype='rtt', gateway_id=gateway)
    try:
        trio.run(serve_tunnel, host, port, connection_params, 'telnet', True, rtt_params)
    except PermissionError as exc:
        if port < 1024:
            click.secho(f'Permission denied for port {port}. Using a port number less than '
                        '1024 typically requires root privileges.', fg='red', err=True)
        else:
            click.secho(str(exc), fg='red', err=True)
        if ctx.obj.debug:
            raise
    except OSError as exc:
        click.secho(f'Could not start telnet on port {port}: {exc}', fg='red', err=True)
        if ctx.obj.debug:
            raise

@click.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected')
@click.option('--host', default='localhost', help='interface for telnet to bind. '
              'Use --host \'*\' to bind to all interfaces.', show_default=True)
@click.option('--port', default=4444, help='Port for telnet', show_default=True)
@click.option('--rtt', is_flag=True, default=False, help='Enable RTT Tunnel', show_default=True)
def openocd(ctx, gateway, host, port, rtt):
    """
        Establish a telnet proxy to openocd server on gateway. By default binds to localhost, meaning telnet
        client connections must originate from the machine running `lager openocd`. If you would
        like to bind to all interfaces, use --host '*'
    """
    if gateway is None:
        gateway = get_default_gateway(ctx)

    ensure_debugger_running(gateway, ctx)

    run_openocd_tunnel(ctx, host, port, gateway, rtt)
