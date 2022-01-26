# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import os
from typing import Dict

from portmod.repo import Repo, get_repo
from portmod.repo.metadata import get_master_names
from portmod.repos import add_repo, get_local_repos, get_remote_repos
from portmod.sync import sync
from portmodlib.l10n import l10n


def sync_args(args):
    local_repos = get_local_repos()
    remote_repos = get_remote_repos()
    to_sync: Dict[str, Repo] = {}

    meta = get_repo("meta")
    # Always sync meta, in case it needs to inform us
    # of newly added repositories
    if not os.path.exists(meta.location):
        sync([meta])
    else:
        to_sync["meta"] = meta

    def add_repo_and_deps(repo_name):
        if repo_name in to_sync:
            return

        repo = local_repos.get(repo_name) or add_repo(remote_repos[repo_name])

        if repo:
            for dep in get_master_names(repo.location):
                add_repo_and_deps(dep)
            to_sync[repo_name] = repo
        else:
            to_sync[repo_name] = local_repos[repo_name]

    if args.repository:
        for name in args.repository:
            add_repo_and_deps(name)
    else:
        for name in local_repos:
            add_repo_and_deps(name)

    sync(to_sync.values())


def add_sync_parser(subparsers, parents):
    parser = subparsers.add_parser("sync", help=l10n("sync-help"), parents=parents)
    parser.add_argument(
        "repository",
        help=l10n("sync-repositories-help"),
        nargs="*",
    )
    parser.set_defaults(func=sync_args)
