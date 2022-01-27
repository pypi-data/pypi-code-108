import os
import pathlib
import shutil
from contextlib import contextmanager
from shlex import quote
from typing import Iterator

import typer
from kapla.cli.console import console, style_str
from kapla.cli.utils import run

RC_BRANCH_NAME = os.environ.get("RC_BRANCH_NAME", "next")
STABLE_BRANCH_NAME = os.environ.get("STABLE_BRANCH_NAME", "stable")


@contextmanager
def ensure_config() -> Iterator[pathlib.Path]:
    """A context manager to make sure a semantic release config is present in the directory."""
    # The configuration must be located in the root directory of the project
    config = pathlib.Path.cwd() / "release.config.js"
    is_default = False
    # If it does not exist we copy the default config
    if not config.exists():
        is_default = True
        shutil.copy2(
            pathlib.Path(__file__).parent.parent / "defaults" / "release.config.js",
            config,
        )
    # We print the config as debug
    try:
        console.print("Using config: ", config.read_text())
        # Yield the config so that it is returned by the context manager
        yield config
    finally:
        # Only remove the file is the default
        if is_default:
            config.unlink(missing_ok=True)


app = typer.Typer(
    name="release",
    add_completion=False,
    no_args_is_help=True,
    invoke_without_command=False,
    help="Python monorepo release toolkit",
)

BRANCH = typer.Option(..., help="git branch from which release should be performed")
VERSION = typer.Option(..., help="version number to bump to")


@app.command("prepare")
def prepare_release(
    version: str = VERSION,
    branch: str = BRANCH,
) -> None:
    """Prepare the release."""
    # Make sure to start from given branch
    run(f"git checkout {branch}")
    # Update version using command defined above
    run(f"k bump {version}")
    # At this point semantic release already performed a commit
    run("git add .")
    # Commit changes to the current branch
    run(f"git commit -m 'chore(release): bumped to version {version}'")


@app.command("publish")
def publish_release(branch: str = BRANCH) -> None:
    """Perform the release."""
    # Checkout target branch
    run(f"git checkout {branch}")
    # Push changes into target branch
    run(f"git push origin {branch}")


@app.command("success")
def on_success(branch: str = BRANCH) -> None:
    """Merge changes back into next on success on stable releases only."""
    if branch == STABLE_BRANCH_NAME:
        # Checkout release candidate branch ("next" by default)
        run(
            f"git switch -c {RC_BRANCH_NAME} 2>/dev/null || git checkout {RC_BRANCH_NAME}"
        )
        # Merge changes from stable branch
        run(
            f"git merge --no-ff origin/{branch} -m 'chore(release): merge from stable branch [skip ci]'"
        )
        # Push changes into release candidate branch ("next" by default)
        run(f"git push origin {RC_BRANCH_NAME}")


@app.command("dry-run")
def dry_run() -> None:
    """Perform a release dry-run."""
    with ensure_config():
        run("semantic-release --dry-run --debug")


@app.command("do")
def do_release() -> None:
    """Perform a release."""
    with ensure_config():
        run("semantic-release --debug")


@app.command("install")
def install_deps(
    become: bool = typer.Option(
        False, "-b", "--become", help="perform installation as root user using sudo"
    )
) -> None:
    """Install release dependencies"""
    deps = [
        "semantic-release",
        "@semantic-release/commit-analyzer",
        "@semantic-release/changelog",
        "@semantic-release/exec",
        "conventional-changelog-conventionalcommits",
    ]
    cmd = "npm i -g " + " ".join(deps)
    if become:
        cmd = "sudo " + cmd
    console.print(f"Running command: {quote(style_str(cmd, 'bold'))}")
    run(cmd)
