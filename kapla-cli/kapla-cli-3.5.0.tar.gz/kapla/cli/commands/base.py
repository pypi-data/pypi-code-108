from pathlib import Path
from typing import List, Optional

import typer
from kapla.cli.console import console
from kapla.cli.globals import repo
from kapla.cli.utils import current_directory, run
from rich.table import Table

app = typer.Typer(
    name="k",
    add_completion=False,
    no_args_is_help=True,
    invoke_without_command=False,
    help="Python monorepo toolkit",
)


@app.command("list")
def list(
    filter: Optional[str] = typer.Option(
        None, help="Optional string to use as filter when looking for package names"
    )
) -> None:
    """List packages in the monorepo"""
    projects = Table(title="Projects")
    projects.add_column("Name")
    projects.add_column("Directory")
    projects.add_column("Description")
    for project in repo.get_packages():
        projects.add_row(
            project.pyproject.name,
            str(project.root.relative_to(Path.cwd())),
            project.pyproject.description,
        )
    console.print(projects)


@app.command("build")
def build(
    format: Optional[str] = None,
    package: Optional[List[str]] = typer.Argument(None, help="Packages to build"),
    skip: Optional[List[str]] = typer.Option(
        None, "-s", "--skip", help="Packages to skip"
    ),
) -> None:
    """Build all or some packages using poetry."""
    packages = [pkg for pkg in package if pkg not in (skip or [])] if package else []
    repo.build_packages(packages, format)


@app.command("test")
def test(
    package: Optional[List[str]] = typer.Argument(default=None),
    markers: List[str] = typer.Option(
        [], "--markers", "-m", help="specify markers to run only a subset of tests."
    ),
    exprs: List[str] = typer.Option(
        [],
        "--exprs",
        "-k",
        help="Pytest expression to select tests based on their name.",
    ),
) -> None:
    """Run unit tests using pytest."""
    repo.test_packages(package, markers=markers, exprs=exprs)


@app.command("bump")
def bump(
    version: str = typer.Argument(
        ..., metavar="VERSION", help="New version to bump to."
    )
) -> None:
    """Bump packages to a new version."""
    repo.bump_packages(version)


@app.command("lint")
def lint(
    package: Optional[List[str]] = typer.Argument(default=None),
) -> None:
    """Lint all source code using flake8."""
    if package:
        repo.lint_packages(package)
    else:
        repo.lint_packages()


@app.command("typecheck")
def typecheck(
    package: Optional[List[str]] = typer.Argument(default=None),
) -> None:
    """Run mypy typechecking againt all source code."""
    repo.typecheck_packages(package)


@app.command("format")
def format(
    package: Optional[List[str]] = typer.Argument(default=None),
) -> None:
    """Format all source code using black."""
    repo.format_packages(package)


@app.command("install")
def install(
    package: Optional[List[str]] = typer.Argument(default=None),
    skip: Optional[List[str]] = typer.Option(None, "--skip", "-s"),
) -> None:
    """Install all packages in editable mode and development dependencies."""
    if skip is None:
        skip = []
    repo.install_packages(package, skip=skip)


@app.command("clean")
def clean(
    package: Optional[List[str]] = typer.Argument(default=None), dist: bool = True
) -> None:
    """Clean directories."""
    repo.clean_packages(package, no_dist=not dist)


@app.command("update")
def update(package: Optional[List[str]] = typer.Argument(default=None)) -> None:
    """Update all packages dependencies and generate lock file."""
    repo.update_packages(package)


@app.command("export")
def export(
    package: Optional[List[str]] = typer.Argument(default=None),
) -> None:
    """Export all packages for offline installation."""
    for project in repo.get_packages(package):
        project.export()


@app.command("coverage")
def coverage() -> None:
    """Start HTML server displaying code coverage."""
    with current_directory(repo.root):
        run("python -m http.server --bind 127.0.0.1 --directory coverage-report")


@app.command("commit")
def commit() -> None:
    """Commit changes to git repository."""
    with current_directory(repo.root):
        run("cz commit")


@app.command("config")
def config() -> None:
    """Print config to console."""
    print(repo.config)
