#!/usr/bin/env python3.7

import json
import sys

import typer

from typing import Optional, List
from pathlib import Path

from demopy.puml import synchro
from demopy.tools import clean_multiline_str
from demopy.constants import DiagramType, DEFAULTS
from demopy.puml import simple as simple_puml

app = typer.Typer()

def _generate_url(label:str, puml: str, base_url, diagram_type):
    content = synchro.compress(puml)
    return f'[{label}]({base_url}/{diagram_type}{content})'


# "https://typer.tiangolo.com/tutorial/multiple-values/multiple-options/"
@app.command()
def simple(
        chain: Optional[List[str]] = typer.Option([]), 
        resource_definitions:Optional[Path]=typer.Option(None), 
        base_url:str=typer.Option(DEFAULTS["url"]), 
        diagram_type:DiagramType=typer.Option(DEFAULTS["type"])
    ):
    """
    Simple English -> PlantUML Url.
    """
    if resource_definitions:
        with open(resource_definitions) as fh:
            custom_resources = json.load(fh)
    else:
        custom_resources = {}
    typer.echo(
        _generate_url(
            "diagram",
            simple_puml.convert_to_puml("\n".join(chain), custom_resources),
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