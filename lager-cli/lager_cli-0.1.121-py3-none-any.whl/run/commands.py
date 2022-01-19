"""
    lager.run.commands

    Commands for running a an image on a DUT
"""
import click
from ..context import get_default_gateway

@click.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected')
def run(ctx, gateway):
    """
        Run a DUT connected to a gateway
    """
    if gateway is None:
        gateway = get_default_gateway(ctx)

    session = ctx.obj.session
    resp = session.run_dut(gateway)
    for chunk in resp.iter_content(chunk_size=1):
        click.echo(chunk, nl=False)
