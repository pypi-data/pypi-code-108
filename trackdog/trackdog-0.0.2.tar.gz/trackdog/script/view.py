import logging

import click
from trackdog.script.get_getter import Getter
from trackdog.script.get_render import render
from trackdog.store import LocalStore


# TODO(ghaocegege): make run a second arg to support same-name runs
@click.command()
@click.argument("project", default="")
@click.argument("run", default="")
@click.argument("metric", default="")
@click.option("--verbose", is_flag=True)
@click.option("--output", default="chart")
def view(project, run, metric, verbose, output):
    """Open the metrics tracking dashboard and view results."""
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    # metric is only supported now.
    resource = "metric"
    getter = Getter(LocalStore())
    artifacts = getter.get(resource, project, run, metric)
    render(resource, artifacts, output)
