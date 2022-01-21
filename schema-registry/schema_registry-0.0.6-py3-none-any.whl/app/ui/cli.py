import logging
from typing import List
import typer

from rich.console import Console
from rich.logging import RichHandler

from schema_registry.app.ui.registry import app as reg_app

from schema_registry.app.business.cli import get_registry

console = Console()
app = typer.Typer()

FORMAT = "%(message)s"


@app.callback()
def main(
    ctx: typer.Context,
    verbose: List[bool] = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Output more details on what is happening. Use multiple times for more details.",
    ),
    profile: str = typer.Option(
        "default",
        "--profile",
        "-p",
        help="The profile to use for the command that is about to run.",
    ),
    extended: bool = typer.Option(
        False,
        "--extended",
        "-e",
        help="If enabled the output will be extended with explanatory text where available.",
    ),
) -> None:
    level = "WARNING"
    if len(verbose) == 1:
        level = "INFO"
    if len(verbose) >= 2:
        level = "DEBUG"

    logging.basicConfig(
        level=level, format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
    )

    ctx.obj = {"registry": get_registry(profile=profile, extended=extended)}


app.add_typer(reg_app, name="registry")

typer_click_object = typer.main.get_command(app)

if __name__ == "__main__":
    app()
