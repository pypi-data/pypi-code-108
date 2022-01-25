# type: ignore
"""
This file contains internal APIs extracted from opensource ray.
"""
from pathlib import Path
from typing import Callable, List, Optional

from pathspec import PathSpec


"""
The following functions are extracted from: ray._private.runtime_env
"""


def _get_gitignore(path: Path) -> Optional[Callable]:
    path = path.absolute()
    ignore_file = path / ".gitignore"
    if ignore_file.is_file():
        with ignore_file.open("r") as f:
            pathspec = PathSpec.from_lines("gitwildmatch", f.readlines())

        def match(p: Path):
            path_str = str(p.absolute().relative_to(path))
            if p.is_dir():
                path_str += "/"
            return pathspec.match_file(path_str)

        return match
    else:
        return None


def _dir_travel(
    path: Path, excludes: List[Callable], handler: Callable,
):
    e = _get_gitignore(path)
    if e is not None:
        excludes.append(e)
    skip = any(e(path) for e in excludes)
    if not skip:
        handler(path)
        if path.is_dir():
            for sub_path in path.iterdir():
                _dir_travel(sub_path, excludes, handler)
    if e is not None:
        excludes.pop()


def _get_excludes(path: Path, excludes: List[str]) -> Callable:
    path = path.absolute()
    pathspec = PathSpec.from_lines("gitwildmatch", excludes)

    def match(p: Path):
        path_str = str(p.absolute().relative_to(path))
        path_str += "/"
        return pathspec.match_file(path_str)

    return match
