from logging import getLogger
from pathlib import Path
from shutil import rmtree

from typer import Option

from deckz.cli import app
from deckz.paths import GlobalPaths, Paths


@app.command()
def clean_all(
    workdir: Path = Option(
        Path("."), help="Path to move into before running the command"
    )
) -> None:
    """Wipe all build directories."""
    logger = getLogger(__name__)
    paths = GlobalPaths.from_defaults(workdir)
    for deck_path in (p.parent for p in paths.git_dir.glob("**/targets.yml")):
        deck_paths = Paths.from_defaults(deck_path)
        if not deck_paths.build_dir.exists():
            logger.info(f"Nothing to do: {deck_paths.build_dir} doesn't exist")
        else:
            logger.info(f"Deleting {deck_paths.build_dir}")
            rmtree(deck_paths.build_dir)
