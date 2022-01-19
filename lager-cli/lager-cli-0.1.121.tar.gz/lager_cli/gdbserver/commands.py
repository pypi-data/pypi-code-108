"""
    lager.gdbserver.commands

    GDB Server tunnel commands
"""

import click
import trio
from .tunnel import serve_tunnel, serve_local_tunnel
from ..context import get_default_gateway, ensure_debugger_running

def _run_gdbserver_cloud(ctx, host, port, gateway, socktype):
    connection_params = ctx.obj.websocket_connection_params(socktype=socktype, gateway_id=gateway)
    try:
        trio.run(serve_tunnel, host, port, connection_params, 'GDB')
    except PermissionError as exc:
        if port < 1024:
            click.secho(f'Permission denied for port {port}. Using a port number less than '
                        '1024 typically requires root privileges.', fg='red', err=True)
        else:
            click.secho(str(exc), fg='red', err=True)
        if ctx.obj.debug:
            raise
    except OSError as exc:
        click.secho(f'Could not start gdbserver on port {port}: {exc}', fg='red', err=True)
        if ctx.obj.debug:
            raise

def _run_gdbserver_local(ctx, host, port, gateway):
    try:
        trio.run(serve_local_tunnel, ctx.obj.session, gateway, host, port, True)
    except PermissionError as exc:
        if port < 1024:
            click.secho(f'Permission denied for port {port}. Using a port number less than '
                        '1024 typically requires root privileges.', fg='red', err=True)
        else:
            click.secho(str(exc), fg='red', err=True)
        if ctx.obj.debug:
            raise
    except OSError as exc:
        click.secho(f'Could not start gdbserver on port {port}: {exc}', fg='red', err=True)
        if ctx.obj.debug:
            raise

@click.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected')
@click.option('--host', default='localhost', help='interface for gdbserver to bind. '
              'Use --host \'*\' to bind to all interfaces.', show_default=True)
@click.option('--port', default=3333, help='Port for gdbserver', show_default=True)
@click.option('--local', is_flag=True, default=False, help='Connect to gateway via local network', show_default=True)
def gdbserver(ctx, gateway, host, port, local):
    """
        Establish a proxy to GDB server on gateway. By default binds to localhost, meaning gdb
        client connections must originate from the machine running `lager gdbserver`. If you would
        like to bind to all interfaces, use --host '*'

        The --local flag can be used if you are on the same network as your gateway, and will cause
        `lager gdbserver` to directly connect to your gateway on the local network for reduced latency.
        This command should only be used if you are on the same, trusted network as your gateway.
    """
    if gateway is None:
        gateway = get_default_gateway(ctx)

    status = ensure_debugger_running(gateway, ctx)
    if 'Listening on port 3333' in status['logfile']:
        socktype = 'gdb-tunnel'
    elif 'Logging started @' in status['logfile']:
        socktype = 'jl-tunnel'
    else:
        raise RuntimeError('Unknown tunnel type')

    if local:
        _run_gdbserver_local(ctx, host, port, gateway)
    else:
        _run_gdbserver_cloud(ctx, host, port, gateway, socktype)
