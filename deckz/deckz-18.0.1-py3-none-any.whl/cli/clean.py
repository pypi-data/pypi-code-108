from logging import getLogger
from pathlib import Path
from shutil import rmtree

from typer import Option

from deckz.cli import app
from deckz.paths import Paths


@app.command()
def clean(
    workdir: Path = Option(
        Path("."), help="Path to move into before running the command"
    )
) -> None:
    """Wipe the build directory."""
    logger = getLogger(__name__)
    paths = Paths.from_defaults(workdir)
    if not paths.build_dir.exists():
        logger.info(f"Nothing to do: {paths.build_dir} doesn't exist")
    else:
        logger.info(f"Deleting {paths.build_dir}")
        rmtree(paths.build_dir)
