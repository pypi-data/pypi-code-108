import click
from click import Context, Group
from importlib_metadata import version

from magic.shared.display import EMOJI_SPARKLE

NAME = "Magic"
VERSION = version("tatuarvela-magic")
YEAR = 2021
AUTHOR = "Tatu Arvela"
VERSION_TEXT = (
    f"{EMOJI_SPARKLE} {click.style(NAME, fg='blue')} v{VERSION} © {YEAR} {AUTHOR}"
)
DESCRIPTION = "A tool for simplifying repeated command line tasks"


def get_help(self, ctx: Context):
    click_help = Group.get_help(self, ctx)
    return f"{VERSION_TEXT}\n" f"{DESCRIPTION}\n" f"\n" f"{click_help}"
