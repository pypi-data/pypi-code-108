#!/usr/bin/env python3.7

import imp
import sys

import typer
from typer import echo as print
from typing import TypeVar, Optional, Callable
from pathlib import Path

from demopy.puml import synchro
from demopy.tools import clean_multiline_str
from demopy.constants import DiagramType, DEFAULTS
from demopy.puml import simple as simple_puml

app = typer.Typer()

def _generate_url(label:str, puml: str, base_url, diagram_type):
    content = synchro.compress(puml)
    return f'[{label}]({base_url}/{diagram_type}{content})'


@app.command()
def simple(line:str, base_url:str=DEFAULTS["url"], diagram_type:DiagramType=DEFAULTS["type"]):
    """
    Simple English -> PlantUML Url.
    """
    typer.echo(
        _generate_url(
            "diagram",
            simple_puml.convert_to_puml(line),
            base_url,
            diagram_type
        )
    )


@app.command()
def generate_url(path:Path, base_url:str=DEFAULTS["url"], diagram_type:DiagramType=DEFAULTS["type"]):
    """
    File w/ Puml (or stdin) -> PlantUML Url.
    """
    if path.name != "-" and not path.is_file():
        typer.echo("Path must be a file.")
        raise typer.Abort()
    if path.name == "-":
        content = sys.stdin.read().strip()
    else:
        with open(path, "r") as fh:
            content = fh.read().strip()
    typer.echo(_generate_url(path.name, content, base_url, diagram_type.value))

if __name__ == "__main__":
    app()

# http://codaset.com/repo/python-markdown/tickets/new