from typing import List, Optional

import typer
from kapla.cli.globals import repo

app = typer.Typer(
    name="dep",
    add_completion=False,
    no_args_is_help=True,
    invoke_without_command=False,
    help="Manage dependencies accross all packages.",
)


@app.command("add")
def add_dep(
    name: str = typer.Argument(..., help="Name of the dependency"),
    dev: bool = typer.Option(False, help="Install as development dependency"),
    package: Optional[List[str]] = typer.Option(
        None, "-p", "--packages", help="Install for those packages only"
    ),
    skip: Optional[List[str]] = typer.Option(
        None, "-s", "--skip", help="Skip those packages"
    ),
) -> None:
    """Install a new dependency for several projects."""
    packages = [pkg for pkg in package if pkg not in (skip or [])] if package else []
    repo.add_dependency(name, packages, dev=dev)
