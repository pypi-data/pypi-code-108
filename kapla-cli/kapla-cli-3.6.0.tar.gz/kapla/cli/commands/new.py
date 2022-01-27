import typer
from kapla.cli.globals import repo

app = typer.Typer(
    name="new",
    add_completion=False,
    no_args_is_help=True,
    invoke_without_command=False,
    help="Create new libraries, plugins or applications.",
)


@app.command("library")
def new_library(name: str) -> None:
    """Create a new library."""
    repo.new_library(name)


@app.command("plugin")
def new_plugin(name: str) -> None:
    """Create a new plugin."""
    repo.new_plugin(name)


@app.command("app")
def new_app(name: str) -> None:
    """Create a new application."""
    repo.new_app(name)
