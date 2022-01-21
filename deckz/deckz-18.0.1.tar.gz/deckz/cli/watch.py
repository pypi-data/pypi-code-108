from logging import getLogger
from pathlib import Path
from typing import List, Optional

from typer import Argument, Option

from deckz.cli import app
from deckz.paths import Paths
from deckz.watching import watch as watching_watch

_logger = getLogger(__name__)


@app.command()
def watch(
    targets: Optional[List[str]] = Argument(None, help="Targets to watch"),
    handout: bool = Option(False, help="Produce PDFs without animations"),
    presentation: bool = Option(True, help="Produce PDFs with animations"),
    print: bool = Option(False, help="Produce a printable PDF"),
    minimum_delay: int = Option(5, help="Minimum number of seconds before recompiling"),
    workdir: Path = Option(
        Path("."), help="Path to move into before running the command"
    ),
) -> None:
    """Compile on change."""
    _logger.info("Watching current and shared directories")
    watching_watch(
        minimum_delay=minimum_delay,
        paths=Paths.from_defaults(workdir),
        build_handout=handout,
        build_presentation=presentation,
        build_print=print,
        target_whitelist=targets,
    )
