from logging import getLogger
from pathlib import Path

from typer import Option

from deckz.cli import app
from deckz.config import get_config
from deckz.paths import Paths


@app.command()
def print_config(
    workdir: Path = Option(
        Path("."), help="Path to move into before running the command"
    )
) -> None:
    """Print the resolved configuration."""
    logger = getLogger(__name__)
    paths = Paths.from_defaults(workdir)
    config = get_config(paths)
    logger.info(
        "Resolved config as:\n%s",
        "\n".join((f"  - {k}: {v}") for k, v in config.items()),
    )
