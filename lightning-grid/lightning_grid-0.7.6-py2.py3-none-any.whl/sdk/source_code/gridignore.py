from copy import copy
from pathlib import Path
from typing import Set


def generate(src: Path) -> Set[str]:
    """
    Generates list of glob strings to ignore. These need to be parsed to identify
    which files are actually ignored.

    Parameters
    ----------
    src: Path
        Path to location where to generate ignore list from.

    Returns
    -------
    Set[str]
        Glob strings to parse
    """
    # fallback files in case we can't find .gridignore
    fallback_ignore_files = {".dockerignore", ".gitignore"}

    # never include these paths in the package
    excluded_paths = {".git"}

    # if it is a file, then just read from it and return lines
    if src.is_file():
        return _read_and_filter_gridignore(src)

    # ignores all paths from excluded paths by default
    ignore_globs = {f"{p}/" for p in excluded_paths}

    # look first for `.gridignore` files
    for path in src.glob('**/*'):
        if path.name in excluded_paths:
            continue
        if path.is_file():
            if path.name == ".gridignore":
                filtered = _read_and_filter_gridignore(path)
                relative_dir = path.relative_to(src).parents[0]
                relative_globs = [str(relative_dir / glob) for glob in filtered]
                ignore_globs.update(relative_globs)

    # if found .gridignore, return it
    if len(ignore_globs) > len(excluded_paths):
        return ignore_globs

    # if not found, look everything else -- combine all fallback_ignore_files into one
    for path in src.glob('**/*'):
        if path.name in excluded_paths:
            continue
        if path.is_file():
            if path.name in fallback_ignore_files:
                filtered = _read_and_filter_gridignore(path)
                relative_dir = path.relative_to(src).parents[0]
                relative_globs = [str(relative_dir / glob) for glob in filtered]
                ignore_globs.update(relative_globs)

    return ignore_globs


def _read_and_filter_gridignore(path: Path) -> Set[str]:
    """
    Reads ignore file and filter and empty lines. This will also remove patterns that start with a `/`.
    That's done to allow `glob` to simulate the behavior done by `git` where it interprets that as a
    root path.

    Parameters
    ----------
    path: Path
        Path to .gridignore file or equivalent.

    Returns
    -------
    Set[str]
        Set of unique lines.
    """
    raw_lines = [ln.strip() for ln in path.open().readlines()]

    # creates a set that removes empty lines and comments
    lines = {ln for ln in raw_lines if ln != "" and ln is not None and not ln.startswith("#")}

    # removes first `/` character
    _lines = copy(lines)
    for pattern in _lines:
        if pattern.startswith("/"):
            lines.remove(pattern)
            lines.add(pattern[1:])

    return lines
