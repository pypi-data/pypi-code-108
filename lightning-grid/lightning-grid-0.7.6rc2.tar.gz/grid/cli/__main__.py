#!/usr/bin/env python
# Copyright 2020 Grid AI Inc.
"""Entrypoint for the Grid CLI."""
import sys

import click

from grid.cli import rich_click
import grid.cli.cli as cli
from grid.cli.exceptions import ResourceNotFound
from grid.cli.utilities import introspect_module
from grid.metadata import __logo__, __version__
import grid.sdk.env as env


@rich_click.main_group(cls=rich_click.deprecate_and_alias({"train": "run", "interactive": "session", "cancel": "stop"}))
@click.option(
    '--debug', type=bool, help='Used for logging additional information for debugging purposes.', is_flag=True
)
@click.option(
    '-o',
    '--output',
    'output',
    type=click.Choice(['console', 'json'], case_sensitive=False),
    default="console",
    help='Output format'
)
@click.pass_context
def main(ctx: click.Context, debug: bool, output: str) -> None:
    """Grid CLI"""
    if not ctx.obj:
        ctx.obj = {}
    if debug:
        env.logger.info('Starting gridrunner in DEGUB mode.')
    ctx.obj['output'] = output

    env.DEBUG = debug


@main.command()
def version() -> None:
    """
    Prints CLI version to stdout.
    """
    logo = click.style(__logo__, fg='bright_green')
    click.echo(logo)

    version = f"""
                              Grid CLI ({__version__})
                            https://docs.grid.ai
    """
    click.echo(version)


@main.command()
def docs() -> None:
    """
    Open the CLI docs.
    """
    click.launch('https://docs.grid.ai/products/global-cli-configs')


#  Adds all CLI commands. Commands are introspected
#  from the cli module.
for command in introspect_module(cli):
    command: click.Command
    main: click.Group
    main.add_command(command)

if __name__ == '__main__':
    try:
        main.main(prog_name="grid", standalone_mode=False)
    except click.ClickException as e:
        e.show()
        sys.exit(e.exit_code)
    except ResourceNotFound as e:
        print(e)
        sys.exit(2)
    finally:
        pass
