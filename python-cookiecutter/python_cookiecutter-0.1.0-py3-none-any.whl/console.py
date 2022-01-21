"""Command-line interface."""
import textwrap

import click

from . import __version__, wikipedia


# Define the start for the commands.
@click.command()
# Define the language option (--language).
@click.option(
    "--language",
    "-l",
    default="en",
    help="Language edition of Wikipedia",
    metavar="LANG",
    show_default=True,
)
# Define the version option (--version).
@click.version_option(version=__version__)
def main(language: str) -> None:
    """The hypermodern Python project."""
    page = wikipedia.random_page(language=language)
    # Print title to console with foreground color.
    click.secho(page.title, fg="green")
    # Print extract, wrapping text so that every line is at most 70 characters long.
    click.echo(textwrap.fill(page.extract))
