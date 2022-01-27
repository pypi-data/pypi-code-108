from __future__ import annotations

import contextlib
import os
import pathlib
import subprocess
import sys
from typing import Dict, Iterable, Iterator


@contextlib.contextmanager
def current_directory(path: pathlib.Path) -> Iterator[pathlib.Path]:
    """Context manager to temporary go into a specific directory."""
    old_dir = os.getcwd()
    try:
        os.chdir(str(path))
        yield path
    finally:
        os.chdir(old_dir)


def run(cmd: str) -> None:
    """Run a command in shell mode and exit on error."""
    try:
        subprocess.check_call(cmd, shell=True)
    except subprocess.CalledProcessError:
        sys.exit(1)


def install_release_dependencies() -> None:
    run(
        "npm i -g "
        "semantic-release "
        "@semantic-release/changelog "
        "@semantic-release/exec "
        "conventional-changelog-conventionalcommits"
    )


def perform_release(debug: bool = True) -> None:
    run("semantic-release" + (" --debug" if debug else ""))


def string_to_dict(string: str) -> Dict[str, str]:
    key, value = string.split("=")
    return {key: value}


def map_string_to_dict(iterable: Iterable[str]) -> Dict[str, str]:
    keyvalues = {}
    if isinstance(iterable, (list, tuple, set)):
        for string in iterable:
            try:
                keyvalues.update(string_to_dict(string))
            except (TypeError, ValueError):
                raise ValueError(f"Cannot parse string as dict: {string}")
    elif isinstance(iterable, str):
        for string in iterable.split(","):
            try:
                keyvalues.update(string_to_dict(string))
            except (TypeError, ValueError):
                raise ValueError(f"Cannot parse string as dict: {string}")
    elif isinstance(iterable, dict):
        keyvalues.update(iterable)
    return keyvalues
