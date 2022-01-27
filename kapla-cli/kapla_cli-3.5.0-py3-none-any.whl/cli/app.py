from typing import Optional

import pkg_resources
import typer
from kapla.cli.console import console

from .commands.base import app
from .commands.buildx import app as k_buildx_commands
from .commands.deps import app as k_dep_commands
from .commands.new import app as k_new_commands
from .commands.profile import app as k_profile_commands
from .commands.release import app as k_release_commands


def get_version(package_name: str) -> str:
    return pkg_resources.get_distribution(package_name).version


app.add_typer(k_release_commands)
app.add_typer(k_new_commands)
app.add_typer(k_profile_commands)
app.add_typer(k_buildx_commands)
app.add_typer(k_dep_commands)


def _callback(value: bool) -> None:
    if value:
        version = get_version("kapla-cli-core")
        console.print(version)
        raise typer.Exit(0)


@app.callback()  # type: ignore
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        help="Print the version and exit.",
        callback=_callback,
        is_eager=True,
    ),
) -> None:
    """
    K Command Line Application
    """
    if version:
        raise typer.Exit(0)
