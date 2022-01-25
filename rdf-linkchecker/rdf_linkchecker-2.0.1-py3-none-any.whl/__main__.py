# type: ignore[attr-defined]
from typing import List, Optional

import sys
from enum import Enum
from pathlib import Path

import typer
from rich import console

from rdf_linkchecker import version
from rdf_linkchecker.checkers.requests_based import Checker
from rdf_linkchecker.graph import get_urls


class Color(str, Enum):
    white = "white"
    red = "red"
    cyan = "cyan"
    magenta = "magenta"
    yellow = "yellow"
    green = "green"


app = typer.Typer(
    name="rdf-linkchecker",
    help="Awesome `rdf-linkchecker` is a Python cli/package created with https://github.com/TezRomacH/python-package-template",
    add_completion=False,
)


def version_callback(print_version: bool) -> None:
    """Print the version of the package."""
    if print_version:
        console.Console().print(
            f"[yellow]rdf-linkchecker[/] version: [bold blue]{version}[/]"
        )
        raise typer.Exit()


@app.command(name="")
def main(
    config_file: Optional[Path] = typer.Option(
        None,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
    ),
    files: List[Path] = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
    ),
    print_version: bool = typer.Option(
        None,
        "-v",
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Prints the version of the rdf-linkchecker package.",
    ),
) -> None:
    """Check URLs in given RDF files"""
    checker = Checker(config_file)
    checker.add_urls(get_urls(files))
    sys.exit(int(checker.check()) - 1)


if __name__ == "__main__":
    app()
