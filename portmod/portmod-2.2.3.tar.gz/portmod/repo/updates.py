# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""A module for parsing package updates"""

import os
from typing import Any, Dict, Optional

from portmod.globals import env
from portmod.repos import Repo

_UPDATES: Optional[Dict[str, Dict[str, Any]]] = None


def get_moved(repo: Repo) -> Dict[str, str]:
    global _UPDATES
    if _UPDATES is None:
        _UPDATES = {}
        for repo in env.REPOS:
            parse_updates(repo)

    assert _UPDATES is not None
    return _UPDATES.get(repo.name, {}).get("move", {})


def parse_updates(repo: Repo):
    global _UPDATES
    path = os.path.join(repo.location, "profiles", "updates")
    repo_updates: Dict[str, Any] = {}

    def update_gt(update_filename: str, other: str):
        if not other:
            return True

        if not update_filename:
            return False

        update_parts = reversed(update_filename.split("-"))
        other_parts = reversed(other.split("-"))
        for component1, component2 in zip(update_parts, other_parts):
            if component1 > component2:
                return True
        return False

    def parse_file(filename: str):
        result = {}
        with open(filename, "r") as file:
            for line in file.readlines():
                command, _, arguments = line.partition(" ")
                if command == "move":
                    source, target = arguments.split(" ")
                    source = source.strip()
                    target = target.strip()
                    if "move" not in result:
                        result["move"] = {source: target}
                    else:
                        result["move"][source] = target
        return result

    newest = repo_updates.get("newest", "")
    if os.path.exists(path):
        for filename in os.listdir(path):
            if update_gt(filename, repo_updates.get("newest", "")):
                if update_gt(filename, newest):
                    newest = filename
                repo_updates.update(parse_file(os.path.join(path, filename)))

    assert _UPDATES is not None
    _UPDATES[repo.name] = repo_updates
