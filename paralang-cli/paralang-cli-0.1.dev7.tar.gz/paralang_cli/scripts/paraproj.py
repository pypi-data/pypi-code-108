""" The CLI 'paraproj' command - Para Project Configuration Helper """
import time
from typing import NoReturn
import click
import paralang_base
from rich import get_console

from .. import (cli_init_rich_console, cli_print_para_banner, __title__,
                __version__, cli_print_paraproj_banner)
from ..utils import cli_abortable, cli_keep_open_callback, cli_escape_ansi_args


class ParaProjCLI:
    """ CLI for the Para Project Configuration Helper """

    @staticmethod
    @cli_abortable(reraise=True)
    @cli_keep_open_callback
    @cli_escape_ansi_args
    def cli(ctx: click.Context, version, *args, **kwargs):
        """
        Main entry point of the compiler CLI. Either returns version or prints
        the init_banner of the Compiler
        """
        # If the console was not initialised yet, initialise it
        if get_console() is None:
            cli_init_rich_console()

        out = get_console()
        if version:
            out.print(
                ' '.join([
                    "Para Project Configuration Tool", __version__,
                    "\nPara Compiler", paralang_base.__version__
                ])
            )
            return
        else:
            cli_print_paraproj_banner()
            out.print('')

            # Sleeping to prevent that subcommands sending to stderr
            # causing the banner to be displayed at the end of the output
            time.sleep(.100)

        if not ctx.invoked_subcommand:
            out.print(ctx.get_help())


@click.group(invoke_without_command=True)
@click.option("--keep-open", is_flag=True)
@click.option(
    "--version",
    is_flag=True,
    help="Prints the version of the compiler"
)
@click.option(
    "--help",
    is_flag=True,
    help="Show this message and exit."
)
@click.pass_context
@cli_abortable(reraise=True)
def cli_paraproj(*args, **kwargs):
    """
    Console Line Interface for the Para Project Configuration Helper

    \f Cuts off the content after this line

    Entry point for the CLI. This should be called when wanting to start the
    cli. It will utilise the command line args passed to the program as the
    click arguments
    """
    ParaProjCLI.cli(*args, **kwargs)


def cli_run() -> NoReturn:
    """
    Runs the cli and parses the input args.

    This function will **not** return and close the application itself.
    """
    cli_init_rich_console()
    cli_paraproj()
