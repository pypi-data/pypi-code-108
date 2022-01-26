# -*- coding: utf-8 -*-
"""Command-line interface and logging configuration."""
# standard-library imports
from importlib import metadata
from typing import Optional

import typer

from .common import APP
from .common import NAME
from .common import STATE
from .find import find
from .query import query
from .query import rcsb_attributes_to_py

# global constants
unused_cli_funcs = (
    find,
    query,
    rcsb_attributes_to_py,
)  # noqa: F841
VERSION: str = metadata.version(NAME)
click_object = typer.main.get_command(APP)  # noqa: F841


def version_callback(value: bool) -> None:
    """Print version info."""
    if value:
        typer.echo(f"{APP.info.name} version {VERSION}")
        raise typer.Exit()


VERSION_OPTION = typer.Option(
    None,
    "--version",
    callback=version_callback,
    help="Print version string.",
)


@APP.callback()
def set_global_state(
    verbose: bool = False,
    quiet: bool = False,
    version: Optional[bool] = VERSION_OPTION,
) -> None:
    """Set global-state variables."""
    if verbose:
        STATE["verbose"] = True
        STATE["log_level"] = "DEBUG"
    elif quiet:
        STATE["log_level"] = "ERROR"
    unused_state_str = f"{version}"  # noqa: F841


def main() -> None:
    """Run the app."""
    APP()
