from pathlib import Path
from typing import List, Optional

from typer import Argument, Option

from deckz.cli import app
from deckz.paths import Paths
from deckz.running import run as running_run


@app.command()
def run(
    targets: Optional[List[str]] = Argument(None, help="Targets to compile"),
    handout: bool = Option(True, help="Produce PDFs without animations"),
    presentation: bool = Option(True, help="Produce PDFs with animations"),
    print: bool = Option(True, help="Produce a printable PDF"),
    workdir: Path = Option(
        Path("."), help="Path to move into before running the command"
    ),
) -> None:
    """Compile main targets."""
    paths = Paths.from_defaults(workdir)
    running_run(
        paths=paths,
        build_handout=handout,
        build_presentation=presentation,
        build_print=print,
        target_whitelist=targets,
    )
