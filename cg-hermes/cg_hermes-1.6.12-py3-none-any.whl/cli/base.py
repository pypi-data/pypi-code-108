import logging
from enum import Enum
from typing import Optional

import coloredlogs
import pkg_resources
import typer

from cg_hermes.cli import convert, export, validate

app = typer.Typer()

app.add_typer(convert.app, name="convert")
app.add_typer(validate.app, name="validate")
app.add_typer(export.app, name="export")

__version__ = pkg_resources.get_distribution("cg_hermes").version
LOG = logging.getLogger(__name__)


class LogLevel(str, Enum):
    debug = "DEBUG"
    info = "INFO"
    warning = "WARNING"


def version_callback(value: bool):
    if value:
        typer.echo(f"hermes version: {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    loglevel: LogLevel = typer.Option(LogLevel.info, help="Set the log level"),
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, is_eager=True
    ),
):
    """
    Manage users in the awesome CLI app.
    """
    LOG.info("Running hermes")
    coloredlogs.install(level=loglevel.value)
