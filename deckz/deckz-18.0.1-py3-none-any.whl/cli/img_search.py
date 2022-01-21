from pathlib import Path
from re import compile as re_compile

from rich.console import Console
from typer import Argument, Option

from deckz.cli import app
from deckz.paths import GlobalPaths


@app.command()
def img_search(
    image: str = Argument(
        ..., help="Specific image to track, like img/turing or tikz/variables"
    ),
    workdir: Path = Option(
        Path("."), help="Path to move into before running the command"
    ),
) -> None:
    """Find which latex files use a given image."""
    global_paths = GlobalPaths.from_defaults(workdir)
    console = Console(highlight=False)
    pattern = re_compile(fr'(\\V{{\[?"{image}".*\]? \| image}})')
    current_dir = global_paths.current_dir
    for latex_dir in global_paths.latex_dirs():
        for f in latex_dir.rglob("*.tex"):
            if pattern.search(f.read_text(encoding="utf8")):
                console.print(f"[link=file://{f}]{f.relative_to(current_dir)}[/link]")
