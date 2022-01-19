"""
    lager.grafana.commands

    grafana tunnel commands
"""

import click
import trio
from ..gdbserver.tunnel import serve_tunnel
from ..context import get_default_gateway, ensure_debugger_running

def run_grafana_tunnel(ctx, host, port, gateway):
    connection_params = ctx.obj.websocket_connection_params(socktype='grafana-tunnel', gateway_id=gateway)
    try:
        trio.run(serve_tunnel, host, port, connection_params, 'grafana')
    except PermissionError as exc:
        if port < 1024:
            click.secho(f'Permission denied for port {port}. Using a port number less than '
                        '1024 typically requires root privileges.', fg='red', err=True)
        else:
            click.secho(str(exc), fg='red', err=True)
        if ctx.obj.debug:
            raise
    except OSError as exc:
        click.secho(f'Could not start grafana on port {port}: {exc}', fg='red', err=True)
        if ctx.obj.debug:
            raise

@click.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway')
@click.option('--host', default='localhost', help='interface for grafana to bind. '
              'Use --host \'*\' to bind to all interfaces.', show_default=True)
@click.option('--port', default=3000, help='Port for grafana', show_default=True)
def grafana(ctx, gateway, host, port):
    """

    """
    if gateway is None:
        gateway = get_default_gateway(ctx)

    run_grafana_tunnel(ctx, host, port, gateway)
