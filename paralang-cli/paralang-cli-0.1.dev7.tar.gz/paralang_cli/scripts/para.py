""" The CLI 'para' command - CLI for the Para Compiler """
from typing import NoReturn
import time
import asyncio
import click
import colorama
import logging

import paralang_base
from paralang_base import __version__, __title__
from paralang_base.exceptions import FailedToProcessError
from paralang_base.compiler import CompileResult

from ..__main__ import RUNTIME_COMPILER
from ..logging import (cli_get_rich_console as get_console,
                       cli_print_result_banner, cli_init_rich_console,
                       cli_print_para_banner, cli_create_prompt,
                       cli_format_default)
from ..utils import (cli_run_output_dir_validation, cli_keep_open_callback,
                     cli_abortable, cli_escape_ansi_args)

__all__ = [
    "cli_run_output_dir_validation",
    "ParaCLI",
    "cli_run"
]

colorama.init(autoreset=True)


class ParaCLI:
    """ CLI for the Para Compiler """

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
                    "Para Compiler", paralang_base.__version__
                ])
            )
            return
        else:
            cli_print_para_banner()
            out.print('')

            # Sleeping to prevent that subcommands sending to stderr
            # causing the banner to be displayed at the end of the output
            time.sleep(.100)

        if not ctx.invoked_subcommand:
            out.print(ctx.get_help())

    @staticmethod
    @cli_abortable(reraise=True)
    @cli_keep_open_callback
    @cli_escape_ansi_args
    def para_compile(
            directory: str,
            encoding: str,
            log: str,
            overwrite_build: bool,
            overwrite_dist: bool,
            source: bool,
            executable: bool,
            debug: bool
    ) -> CompileResult:
        """
        CLI interface for the parac_compile command.
        Will create a compilation-process and run it
        """
        raise NotImplementedError("This command has not been implemented yet.")

    @staticmethod
    @cli_abortable(reraise=True)
    @cli_keep_open_callback
    @cli_escape_ansi_args
    def para_run(
            directory: str,
            encoding: str,
            log: str,
            overwrite_build: bool,
            overwrite_dist: bool,
            debug: bool
    ) -> None:
        """ CLI interface for compiling and running a program. """
        raise NotImplementedError("This command has not been implemented yet.")

    @staticmethod
    @cli_abortable(reraise=True)
    @cli_keep_open_callback
    @cli_escape_ansi_args
    def para_syntax_check(
            file: str,
            encoding: str,
            log: str,
            debug: bool
    ):
        """ Runs a syntax check on the specified file (imports excluded) """
        if not RUNTIME_COMPILER.is_cli_logger_ready:
            RUNTIME_COMPILER.init_cli_logging(
                log,
                level=logging.DEBUG if debug else logging.INFO,
                banner_name="Syntax Check"
            )

        # Exception won't be reraised and directly logged to the console
        try:
            asyncio.run(
                RUNTIME_COMPILER.validate_syntax(
                    file, encoding, prefer_logging=True
                )
            )
        # FailedToProcess -> SyntaxError
        except FailedToProcessError:
            ...  # ignoring as the following items will handle the errors

        errors = RUNTIME_COMPILER.stream_handler.errors
        warnings = RUNTIME_COMPILER.stream_handler.warnings
        if errors == 0:
            cli_print_result_banner("Syntax Check")
            get_console().print(
                "[bold bright_cyan]"
                "Syntax check finished successfully"
                "[/bold bright_cyan]"
            )
        else:
            cli_print_result_banner("Syntax Check", success=False)
            get_console().print(
                "[bold yellow]"
                "Syntax check detected "
                f"{'an error' if errors == 1 else 'multiple errors'}"
                "[/bold yellow]"
            )

        get_console().print(
            f"[bold yellow]{warnings} Warnings [/bold yellow]"
            f"[bold red]{errors} Errors[/bold red]"
        )


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
@cli_abortable(reraise=False)
def cli_para(*args, **kwargs):
    """
    Console Line Interface for the Para Compiler

    \f Cuts off the content after this line

    Entry point for the CLI. This should be called when wanting to start the
    cli. It will utilise the command line args passed to the program as the
    click arguments
    """
    ParaCLI.cli(*args, **kwargs)


@cli_para.command(name="compile")
@click.option("--keep-open", is_flag=True)
@click.option(
    "-f",
    "--files",
    prompt=cli_create_prompt("Specify the files for your Para program"),
    type=str,
    help="The files for your program that should be compiled and linked. You"
         "may specify multiple files with '-f'",
    multiple=True
)
@click.option(
    "--encoding",
    default="utf-8",
    type=str,
    help="The encoding the files should be opened with"
)
@click.option(
    "-l",
    "--log",
    default=cli_format_default("./parac.log"),
    type=str,
    prompt=cli_create_prompt(
        "Specify where the console .log file should be created"
    ),
    help="Path of the output .log file where program messages should be logged"
         ". If set to None it will not use a log file and only use the console"
         " as the output method"
)
@click.option(
    "--overwrite-build",
    is_flag=True,
    type=bool,
    default=False,
    help="If set to True the build folder will always be overwritten "
         "without consideration of pre-existing data"
)
@click.option(
    "--overwrite-dist",
    is_flag=True,
    type=bool,
    default=False,
    help="If flag is set the dist folder will always be overwritten without "
         "consideration of pre-existing data"
)
@click.option(
    "--source/--no-source",
    is_flag=True,
    type=bool,
    default=True,
    help="If flag is set the compiler will compile the code down to native C"
         " (C11). If set with --executable, the executable will be also "
         "generated next the source C code."
)
@click.option(
    "--executable/--no-executable",
    type=bool,
    default=False,
    help="If flag is set the compiler will compile the native C code and "
         "directly generate an executable. If set with --source, the source C"
         "code will be also generated next the executable."
)
@click.option(
    "--debug/--no-debug",
    is_flag=True,
    type=bool,
    default=False,
    help="If set the compiler will add additional debug information"
)
@cli_abortable(reraise=False)
def cli_para_compile(*args, **kwargs):
    """ Compile a Para program to C or executable """
    ParaCLI.para_compile(*args, **kwargs)


@cli_para.command(name="run")
@click.option("--keep-open", is_flag=True)
@click.option(
    "-p",
    "--path",
    prompt=cli_create_prompt("Specify the path to your built"),
    default=cli_format_default("./dist/"),
    type=str,
    help="The path where your finished built is located"
)
@click.option(
    "--encoding",
    default="utf-8",
    type=str,
    help="The encoding the files should be opened with"
)
@click.option(
    "-l",
    "--log",
    type=str,
    default=cli_format_default("./parac.log"),
    prompt=cli_create_prompt(
        "Specify where the console .log file should be created"),
    help="Path of the output .log file where program messages should be logged"
         ". If set to None it will not use a log file and only use the console"
         " as the output method"
)
@click.option(
    "--overwrite-build",
    is_flag=True,
    type=bool,
    default=False,
    help="If set to True the build folder will always be overwritten without "
         "consideration of pre-existing data"
)
@click.option(
    "--overwrite-dist",
    is_flag=True,
    type=bool,
    default=False,
    help="If flag is set the dist folder will always be overwritten without "
         "consideration of pre-existing data"
)
@click.option(
    "--debug/--no-debug",
    is_flag=True,
    type=bool,
    default=False,
    help="If set the compiler will add additional debug information"
)
@cli_abortable(reraise=False)
def para_run(*args, **kwargs):
    """
    Runs a built Para program in './dist/'
    """
    ParaCLI.para_run(*args, **kwargs)


@cli_para.command(name="syntax-check")
@click.option("--keep-open", is_flag=True)
@click.option(
    "-f",
    "--file",
    type=str,
    default=cli_format_default("main.para"),
    prompt=cli_create_prompt("Specify the entry-point of your program"),
    help="The entry-point of the program where the compiler "
         "should start the compilation process."
)
@click.option(
    "--encoding",
    default="utf-8",
    type=str,
    help="The encoding the files should be opened with"
)
@click.option(
    "-l",
    "--log",
    type=str,
    default=cli_format_default("./parac.log"),
    prompt=cli_create_prompt(
        "Specify where the console .log file should be created"),
    help="Path of the output .log file where program messages should be logged"
         ". If set to None it will not use a log file and only use the console"
         " as the output method"
)
@click.option(
    "--debug/--no-debug",
    is_flag=True,
    type=bool,
    default=False,
    help="If set the compiler will add additional debug information"
)
@cli_abortable(reraise=False)
def para_syntax_check(*args, **kwargs):
    """ Validates the syntax of a Para program """
    ParaCLI.para_syntax_check(*args, **kwargs)


def cli_run() -> NoReturn:
    """
    Runs the cli and parses the input args.

    This function will **not** return and close the application itself.
    """
    cli_init_rich_console()
    cli_para()
