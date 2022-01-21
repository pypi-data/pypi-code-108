from logging import getLogger
from pathlib import Path

from typer import Option

from deckz.cli import app
from deckz.paths import Paths
from deckz.uploading import Uploader

_logger = getLogger(__name__)


@app.command()
def upload(
    workdir: Path = Option(
        Path("."), help="Path to move into before running the command"
    )
) -> None:
    """Upload pdfs to Google Drive."""
    paths = Paths.from_defaults(workdir)
    Uploader(paths)
