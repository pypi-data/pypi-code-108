import logging
import os

import click

from datafold_sdk.cli import dbt, alerts
from datafold_sdk.cli import context
from datafold_sdk.cli.context import CliContext
from datafold_sdk.cli.context import DATAFOLD_HOST, DATAFOLD_APIKEY
from datafold_sdk.version import __version__


FORMAT = '%(asctime)-15s:%(levelname)s:%(module)s: %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)

logger = logging.getLogger(__file__)


@click.group()
@click.option('--host',
              default="https://app.datafold.com",
              help="The host where the datafold app is located, e.g. 'https://app.datafold.com'")
@click.pass_context
def manager(ctx, host: str, **kwargs):
    """Management script for Datafold CLI"""
    api_key = os.environ.get(DATAFOLD_APIKEY)
    if not api_key:
        raise ValueError(f"The {DATAFOLD_APIKEY} environment variable is not set")

    override_host = os.environ.get(DATAFOLD_HOST)
    if override_host is not None:
        logger.info(f"Overriding host {host} to {override_host}")
        host = override_host

    ctx.obj = CliContext(host=host, api_key=api_key)


@manager.command()
@click.pass_context
def version(ctx):
    """Displays Datafold CLI version."""
    print(__version__)


manager.add_command(dbt.manager, "dbt")
manager.add_command(alerts.manager, "queries")
