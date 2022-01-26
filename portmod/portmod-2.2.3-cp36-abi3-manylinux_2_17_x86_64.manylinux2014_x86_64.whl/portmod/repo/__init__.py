# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import os
from types import SimpleNamespace
from typing import AbstractSet, Dict, Optional, Union

from portmod.functools import system_cache
from portmodlib.l10n import l10n

from ..globals import env


class BaseRepo(SimpleNamespace):
    def __init__(
        self,
        name: str,
        sync_type: Optional[str],
        sync_uri: Optional[str],
        priority: int,
    ):
        self.name = name
        self.sync_type = sync_type
        self.sync_uri = sync_uri
        self.priority = priority


class Repo(BaseRepo):
    def __init__(
        self,
        # Default is empty string so that pickling works.
        # Normally the name and location is required
        name: str = "",
        location: str = "",
        auto_sync: bool = False,
        sync_type: Optional[str] = None,
        sync_uri: Optional[str] = None,
        priority: int = 0,
    ):
        super().__init__(name, sync_type, sync_uri, priority)
        self.location = location
        self.auto_sync = auto_sync

    def to_dict(self) -> Dict[str, Union[str, int, bool]]:
        result = {}
        for attr in [
            "location",
            "auto_sync",
            "sync_type",
            "sync_uri",
            "priority",
        ]:
            if getattr(self, attr):
                result[attr] = getattr(self, attr)
        return result


class RemoteRepo(BaseRepo):
    def __init__(
        self,
        # Default is empty string so that pickling works.
        # Normally the name is required
        name: str = "",
        sync_type: Optional[str] = None,
        sync_uri: Optional[str] = None,
        priority: int = 0,
        description: str = "",
        quality: str = "unspecified",
        arch: AbstractSet[str] = frozenset(),
    ):
        super().__init__(name, sync_type, sync_uri, priority)
        self.description = description
        self.quality = quality
        self.arch = set(arch)


@system_cache
def get_repo_name(path: str) -> str:
    """
    Given a path within a repo, returns the repo's name

    If path is not within a repo, returns None
    """
    root = get_repo_root(path)
    if root is not None:
        path = os.path.join(root, "profiles", "repo_name")
        if os.path.exists(path):
            with open(path, mode="r") as name_file:
                return name_file.read().strip()

    raise FileNotFoundError(
        f"Repo at path {path} does not contain the profiles/repo_name file"
    )


@system_cache
def get_repo_root(path: str) -> Optional[str]:
    """
    Returns the root given a path within a repository

    If the path is not in a repository, returns None
    """
    path = os.path.abspath(path)
    # Recursively look for metadata/repo_name to identify root
    if os.path.exists(os.path.join(path, "profiles", "repo_name")):
        return path
    if os.path.dirname(path) == path:
        # We've reached the root of the FS there is no repo
        return None

    return get_repo_root(os.path.dirname(path))


def has_repo(name: str) -> bool:
    """Returns true iff the repo exists"""
    if env.PREFIX_NAME:
        for repo in env.prefix().REPOS:
            if repo.name == name:
                return True
    else:
        for repo in env.REPOS:
            if repo.name == name:
                return True
    return False


def get_repo(name: str) -> Repo:
    """Returns repo of the given name"""
    if env.PREFIX_NAME:
        repos = env.prefix().REPOS
    else:
        repos = env.REPOS
    for repo in repos:
        if repo.name == name:
            return repo
    raise Exception(l10n("repo-does-not-exist", name=name))
