#!/usr/bin/env python
import sys
from pathlib import Path

import click

from puddl.cli.base import root
from .app import GitApp
from .repo2rows import Repo
from .utils import list_repo_paths


@root.command()
@click.argument('path', type=str)
def csv(path: str):
    repo = Repo(Path(path).expanduser().absolute())
    print(repo.as_csv(sys.stdout))


# noinspection PyShadowingNames
@root.command()
@click.argument('path', type=str, nargs=-1)
@click.option('-r', '--recursive', is_flag=True, help="Find repos recursively (by looking for .git) and index them")
@click.option('--truncate', is_flag=True, help="Truncate the table 'raw' before loading?")
@click.option('--author', help="Filter by author. See `git log --help`.")
@click.option('--since-commit', help="Only index in the given <revision range>. Check 'git help log'")
def index(path: str, recursive: bool, truncate: bool, author, since_commit):
    """
    Example call:

    puddl-felix-git -linfo index --truncate -r --since-commit HEAD ~
    """
    root_dirs = [Path(d).expanduser().absolute() for d in path]
    app = GitApp()
    if truncate:
        app.truncate()
    if recursive:
        paths = []
        for root_dir in root_dirs:
            paths.extend(list_repo_paths(root_dir))
    else:
        paths = root_dirs
    app.load(paths, author, since_commit)


@root.command()
def truncate():
    app = GitApp()
    app.truncate()


@root.command()
def ls():
    app = GitApp()
    import pandas as pd

    q = "SELECT DISTINCT repo_path || '/' || file_path FROM raw"
    df = pd.read_sql_query(q, app.engine)
    print(df.to_csv(index=False))


def main():
    root(auto_envvar_prefix='PUDDL_FELIX_GIT')


if __name__ == '__main__':
    main()
