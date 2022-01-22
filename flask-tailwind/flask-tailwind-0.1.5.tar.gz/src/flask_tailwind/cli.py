"""Console script for flask_tailwind."""
import shutil
import sys
from pathlib import Path

import click
from flask.cli import with_appcontext

from .npm import NPM


@click.group()
def tailwind():
    """Perform Tailwind operations."""
    pass


@tailwind.command()
@with_appcontext
def init():
    """Init the tailwind/ directory (if it doesn't exist)"""
    source_dir = Path(__file__).parent / "cruft"
    dest_dir = Path("tailwind")
    if dest_dir.exists():
        click.secho(f"Target directory '{dest_dir}' exists, aborting.", fg="red")
        sys.exit(1)

    shutil.copytree(source_dir, dest_dir)
    click.secho(f"Tailwind source and cruft installed in '{dest_dir}'.", fg="green")


@tailwind.command()
@with_appcontext
def install():
    """Install the dependencies using npm."""
    npm_run("install")


@tailwind.command()
@with_appcontext
def build():
    """Build the CSS assets."""
    npm_run("run", "build")


@tailwind.command()
@with_appcontext
def start():
    """Start watching CSS changes for dev."""
    npm_run("run", "start")


@tailwind.command()
@with_appcontext
def check_updates():
    """Check outdated Tailwind dependencies."""
    npm_run("outdated")


@tailwind.command()
@with_appcontext
def update():
    """Update Tailwind and its dependencies, if needed."""
    npm_run("update")


# @tailwind.command()
# @with_appcontext
# def npm(*args):
#     """Call directly npm with given args."""
#     npm_run(*args)


def npm_run(*args):
    cwd = "tailwind"
    npm = NPM(cwd=cwd)
    npm.run(*args)
