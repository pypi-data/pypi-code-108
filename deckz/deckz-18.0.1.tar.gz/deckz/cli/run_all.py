from pathlib import Path

from typer import Option

from deckz.cli import app
from deckz.running import run_all as running_run_all


@app.command()
def run_all(
    handout: bool = Option(True, help="Produce PDFs without animations"),
    presentation: bool = Option(True, help="Produce PDFs with animations"),
    print: bool = Option(True, help="Produce printable PDFs"),
    workdir: Path = Option(
        Path("."), help="Path to move into before running the command"
    ),
) -> None:
    """Compile all shared slides (all formats by default)."""
    running_run_all(
        directory=workdir,
        build_handout=handout,
        build_presentation=presentation,
        build_print=print,
    )
