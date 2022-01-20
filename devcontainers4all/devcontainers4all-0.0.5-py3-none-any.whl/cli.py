"""Docker technology"""
import sys

# pylint: disable=import-error
import click  # type: ignore
import click_pathlib  # type: ignore

from .factories import Controller
from .interfaces import Configuration


@click.group()
@click.pass_context
def cli(ctx):
    """Main entrypoint for the subcommands"""
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below)
    ctx.ensure_object(dict)


@cli.command()
@click.option(
    "--repository",
    default=".",
    type=click_pathlib.Path(exists=True),
    help="The repository checkout to mount in the devcontainer",
)
@click.option(
    "--location",
    default="./.devcontainer",
    type=click_pathlib.Path(exists=True),
    help="The location of the devcontainer definition",
)
def shell(repository, location):
    """Manage the devcontainer"""
    config = Configuration(location=location, repository=repository)
    controller = Controller(config)
    sys.exit(controller.shell())


@cli.command()
@click.option(
    "--repository",
    default=".",
    type=click_pathlib.Path(exists=True),
    help="The repository checkout to mount in the devcontainer",
)
@click.option(
    "--location",
    default="./.devcontainer",
    type=click_pathlib.Path(exists=True),
    help="The location of the devcontainer definition",
)
def create(repository, location):
    """Manage the devcontainer"""
    config = Configuration(location=location, repository=repository)
    controller = Controller(config)
    controller.create()


if __name__ == "__main__":
    shell()  # pylint: disable=no-value-for-parameter
