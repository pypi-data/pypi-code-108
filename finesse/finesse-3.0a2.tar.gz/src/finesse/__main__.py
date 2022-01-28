"""Finesse command line interface."""

import click

# https://github.com/pallets/click/issues/430
from click_default_group import DefaultGroup

from . import __version__, PROGRAM, DESCRIPTION
from .cli import (
    run,
    info,
    syntax,
    config,
    convert,
    print_banner,
)


@click.group(cls=DefaultGroup, default="run", help=DESCRIPTION)
@click.option(
    "--banner",
    is_flag=True,
    default=False,
    callback=print_banner,
    expose_value=False,
    is_eager=True,
    help=print_banner.__doc__,
)
@click.version_option(version=__version__, prog_name=PROGRAM)
@click.pass_context
def cli(ctx):
    pass


cli.add_command(run)
cli.add_command(info)
cli.add_command(syntax)
cli.add_command(config)
cli.add_command(convert)
