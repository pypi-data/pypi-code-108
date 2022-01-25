# coding by stackoverflow :>
# https://stackoverflow.com/a/53503693/241240
import os
from pathlib import Path

DOT_GIT = '.git'


def list_repo_paths(root: Path) -> [Path]:
    """
    Given a root directory, find all of its subdirectories that contain a `.git` file.
    Here `.git` can be a directory (for "normal" repos) or a file (for submodules).
    """
    for path, dirs, files in os.walk(root):
        if DOT_GIT in dirs + files:
            yield Path(path)
