#!/usr/bin/env python3
import click
import click_creds

from pydragonfly import Dragonfly
from .resources import analysis, profile, rule, access_info
from .config import config
from ._utils import (
    get_logger,
    ClickContext,
    get_version_number,
)


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option("-d", "--debug", is_flag=True, help="Set log level to DEBUG")
@click.version_option(version=get_version_number())
@click_creds.use_netrcstore(
    name="pydragonfly",
    mapping={"login": "certificate", "password": "api_key", "account": "instance_url"},
)
@click.pass_context
def cli(ctx: ClickContext, debug: bool):
    host = click_creds.get_netrc_object_from_ctx(ctx).host.copy()
    api_key, url = host["password"], host["account"]
    if (not api_key or not url) and ctx.invoked_subcommand != "config":
        click.echo("Hint: Use `config set` to set config variables!")
        exit()
    else:
        logger = get_logger("DEBUG" if debug else "INFO")
        ctx.obj = Dragonfly(api_key=api_key)
        ctx.obj._server_url = url
        ctx.obj._logger = logger


# Compile all groups and commands
for c in [
    config,
    analysis,
    profile,
    rule,
    access_info,
]:
    cli.add_command(c)

# Entrypoint/executor
if __name__ == "__main__":
    cli()
