# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""Module for interacting with PORTMOD_CONFIG/repos.cfg"""

import ast
import configparser
import os
from logging import info, warning
from typing import Dict, List, Optional, Set

from portmodlib.l10n import l10n

from .config import get_config
from .globals import env
from .repo import RemoteRepo, Repo, get_repo_name
from .repo.metadata import get_archs, get_master_names


def _iterate_repos_cfg(path: str):
    """Parses contents of repos.cfg"""

    repo_config = configparser.ConfigParser()
    repo_config.read(path)

    for name, conf in repo_config.items():
        if name == "DEFAULT":
            # Ignore DEFAULT key, as it is always there. We will not use it
            continue

        yield name, conf


def parse_remote_repos(path: str) -> List[RemoteRepo]:
    repos = []
    for name, conf in _iterate_repos_cfg(path):
        repos.append(
            RemoteRepo(
                name,
                sync_type=conf.get("sync_type"),
                sync_uri=conf.get("sync_uri"),
                priority=int(conf.get("priority", "0")),
                description=conf.get("description"),
                quality=conf.get("quality"),
                arch=set(conf.get("arch", "").split(",")),
            )
        )

    return repos


def parse_repos(path: str) -> List[Repo]:
    repos = []
    for name, conf in _iterate_repos_cfg(path):
        if "location" not in conf:
            warning(l10n("repo-missing-location", repo=name))
            continue
        repo_name = name
        if os.path.exists(conf["location"]):
            name = get_repo_name(conf["location"])

        repos.append(
            Repo(
                name=repo_name,
                location=os.path.expanduser(conf["location"]),
                auto_sync=ast.literal_eval(conf.get("auto_sync", "False")),
                sync_type=conf.get("sync_type"),
                sync_uri=conf.get("sync_uri"),
                priority=int(conf.get("priority", "0")),
            )
        )
    return repos


def get_local_repos() -> Dict[str, Repo]:
    meta_repo = Repo(
        "meta",
        os.path.join(env.REPOS_DIR, "meta"),
        auto_sync=True,
        sync_type="git",
        sync_uri="https://gitlab.com/portmod/meta.git",
        priority=-1000,
    )
    repos = {"meta": meta_repo}
    if os.path.exists(env.REPOS_FILE):
        repos.update({repo.name: repo for repo in parse_repos(env.REPOS_FILE)})
        return repos
    return repos


def get_repos():
    """Returns available repositories"""
    added = {"meta"}
    local = get_local_repos()
    repos = [get_local_repos()["meta"]]

    def add_repos(to_add: Set[str]):
        nonlocal repos
        for repo_name in to_add:
            if repo_name not in local:
                warning(l10n("repo-does-not-exist", name=repo_name))
                continue
            repo = local[repo_name]
            if repo.name not in added:
                repos.append(repo)
                added.add(repo.name)
            add_repos(get_master_names(repo.location))

    add_repos(get_config()["REPOS"])

    # Sort repos by priority such that the highest priority appears first
    repos.sort(key=lambda x: (x.priority, x.name), reverse=True)

    return repos


def add_repo(repo: RemoteRepo) -> Optional[Repo]:
    """
    Adds repository to repos.cfg

    If the repository already exists, None will be returned
    Otherwise, the repo added to the file will be returned
    """
    # comment_prefixes="/" and allow_no_value makes comments be treated as keys and preserved.
    # Unfortunately comments on the line of the section header are not preserved
    repo_config = configparser.ConfigParser(comment_prefixes="/", allow_no_value=True)
    repo_config.read(env.REPOS_FILE)

    new_repo = None
    if repo.name not in repo_config:
        new_repo = Repo(
            repo.name,
            os.path.join(env.REPOS_DIR, repo.name),
            auto_sync=repo.sync_type == "git",
            sync_type=repo.sync_type,
            sync_uri=repo.sync_uri,
            priority=repo.priority or 0,
        )
        repo_config.add_section(repo.name)
        for key, value in new_repo.to_dict().items():
            repo_config.set(repo.name, key, str(value))

        info(l10n("repo-adding", name=repo.name, conf=env.REPOS_FILE))

        os.makedirs(os.path.dirname(env.REPOS_FILE), exist_ok=True)
        with open(env.REPOS_FILE, "w") as file:
            repo_config.write(file)
        env.REPOS.append(new_repo)

    return new_repo


def get_remote_repos(arch: Optional[str] = None) -> Dict[str, RemoteRepo]:
    """
    Returns repositories declared by the repositories currently known
    """
    # Note: This method should not be cached, as new declarations may be
    # added when synchronizing a repository, and may be immediately used by
    # a repository synchronizing afterwards.
    repos = {}
    for repo in env.REPOS:
        conf = os.path.join(repo.location, "metadata", "repos.cfg")
        if os.path.exists(conf):
            repos.update(
                {
                    remote_repo.name: remote_repo
                    for remote_repo in parse_remote_repos(conf)
                    if arch is None or arch in remote_repo.arch
                }
            )
    for repo in env.REPOS:
        if (
            repo.name not in repos
            and repo.name != "meta"
            and arch in get_archs(repo.location)
        ):
            repos[repo.name] = RemoteRepo(
                name=repo.name,
                sync_type=repo.sync_type,
                sync_uri=repo.sync_uri,
                priority=repo.priority,
                description="Local repository in repos.cfg",
                arch=get_archs(repo.location),
            )
    return repos
