import click
from .model import run
from .util import (
    set_debug,
    input_file_argument,
    plot_option,
    trace_option,
    legacy_option,
    verbose_option,
    quiet_option,
    fancy_error_option,
    debug_option,
    log_display_level_option,
    log_exclude_option,
)


@click.group()
@click.pass_context
def debug(ctx):
    """Debug tools."""
    # The debug flag is implied.
    set_debug(ctx, None, True)


@debug.command(name="run")
@input_file_argument
@plot_option
@trace_option
@legacy_option
@verbose_option
@quiet_option
@fancy_error_option
@debug_option
@log_display_level_option
@log_exclude_option
@click.pass_context
def run_debug(
    ctx,
    input_file,
    plot,
    trace,
    legacy,
):
    """Run a Finesse script with Python fault handler enabled.

    If the file extension is 'py', it is interpreted as Python code; otherwise it is
    parsed assuming it to be kat script.
    """
    import os
    import faulthandler

    click.secho("Enabling Python fault handler", fg="yellow")
    faulthandler.enable()

    root, ext = os.path.splitext(input_file.name)
    if ext.casefold() == ".py":
        exec(input_file.read())
    else:
        # Forward arguments to normal "run" command.
        ctx.forward(run)


if __name__ == "__main__":
    run_debug()
