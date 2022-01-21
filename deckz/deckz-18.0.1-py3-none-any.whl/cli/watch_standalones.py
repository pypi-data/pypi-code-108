from logging import getLogger
from pathlib import Path

from typer import Option

from deckz.cli import app
from deckz.paths import GlobalPaths
from deckz.watching import watch_standalones as watching_watch_standalones

_logger = getLogger(__name__)


@app.command()
def watch_standalones(
    minimum_delay: int = Option(5, help="Minimum number of seconds before recompiling"),
    workdir: Path = Option(
        Path("."), help="Path to move into before running the command"
    ),
) -> None:
    """Compile standalones on change."""
    watching_watch_standalones(
        minimum_delay, workdir, GlobalPaths.from_defaults(workdir)
    )
