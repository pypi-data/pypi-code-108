from logging import INFO, basicConfig

from rich.logging import RichHandler
from typer import Typer

from deckz.utils import import_module_and_submodules

app = Typer(
    help="Tool to handle a large number of beamer decks, "
    "used by several persons, with shared slides amongst the decks.",
    chain=True,
)


def main() -> None:
    basicConfig(
        level=INFO,
        format="%(message)s",
        datefmt="%H:%M:%S",
        handlers=[RichHandler(rich_tracebacks=True)],
    )
    import_module_and_submodules(__name__)
    app()
