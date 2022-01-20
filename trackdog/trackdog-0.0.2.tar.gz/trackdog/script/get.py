import logging
import os

import click
from trackdog.script.get_render import render
from trackdog.script.get_getter import Getter
from trackdog.store import LocalStore


# TODO(ghaocegege): make run a second arg to support same-name runs
@click.command()
@click.argument("resource", default="run")
@click.argument("name", default="")
@click.option("--verbose", is_flag=True)
@click.option("--output", default="normal")
def get(resource, name, verbose, output):
    """Display one or more resources"""
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    # TODO(gaocegege): Handle name carefully, do not use "" as default value.
    if name == "":
        name = None
    getter = Getter(LocalStore())
    artifacts = getter.get(resource, name)

    render(resource, artifacts, output)
