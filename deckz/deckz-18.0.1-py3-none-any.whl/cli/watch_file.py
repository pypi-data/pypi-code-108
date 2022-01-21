from logging import getLogger
from pathlib import Path
from tempfile import TemporaryDirectory

from typer import Argument, Option, launch

from deckz import app_name
from deckz.cli import app
from deckz.paths import GlobalPaths, Paths
from deckz.watching import watch_file as watching_watch_file

_logger = getLogger(__name__)


@app.command()
def watch_file(
    latex: str = Argument(..., help="File to watch, relative to share/latex"),
    handout: bool = Option(False, help="Produce PDFs without animations"),
    presentation: bool = Option(True, help="Produce PDFs with animations"),
    print: bool = Option(False, help="Produce a printable PDF"),
    minimum_delay: int = Option(5, help="Minimum number of seconds before recompiling"),
    workdir: Path = Option(
        Path("."), help="Path to move into before running the command"
    ),
) -> None:
    """Compile a specific file on change."""
    _logger.info(f"Watching {latex}")
    global_paths = GlobalPaths.from_defaults(workdir)
    with TemporaryDirectory(prefix=f"{app_name}-") as build_dir, TemporaryDirectory(
        prefix=f"{app_name}-"
    ) as pdf_dir:
        _logger.info(
            f"Output directory located at [link=file://{pdf_dir}]{pdf_dir}[/link]",
            extra=dict(markup=True),
        )
        launch(str(pdf_dir))
        watching_watch_file(
            minimum_delay=minimum_delay,
            latex=latex,
            paths=Paths.from_defaults(
                workdir,
                check_depth=False,
                build_dir=Path(build_dir),
                pdf_dir=Path(pdf_dir),
                company_config=global_paths.template_company_config,
                deck_config=global_paths.template_deck_config,
            ),
            build_handout=handout,
            build_presentation=presentation,
            build_print=print,
        )
