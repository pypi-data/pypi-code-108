import sys
from pathlib import Path
from typing import Optional

from kapla.cli.console import confirm
from kapla.cli.errors import PyprojectNotFoundError
from kapla.cli.projects import Monorepo
from kapla.cli.utils import run


def create_repo() -> Monorepo:
    if not confirm("Do you want to create a new project ?"):
        sys.exit(0)
    run("poetry init")
    repo = Monorepo(Path.cwd())
    repo.set_include_packages([])

    return repo


def get_repo(path: Optional[Path] = None) -> Monorepo:
    path = path or Path.cwd()
    try:
        return Monorepo(Path.cwd())
    except PyprojectNotFoundError:
        return create_repo()
