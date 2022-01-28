"""
This module cleans up files which are ignored by git
"""
import argparse
import os
import shutil
from collections import deque
from glob import iglob
from pipes import quote
from itertools import chain
from typing import (
    Dict,
    Tuple,
    Iterable,
    Sequence,
    Set,
    FrozenSet,
    List,
)
from .utilities import run

ROOT_DIRECTORY: str = "."
DEFAULT_EXCLUDE: Tuple[str, ...] = (
    ".idea",  # Jetbrains' IDE project settings (Pycharm, Intellij IDEA)
    ".vscode",  # Microsoft Visual Studio Code project settings
    ".git",  # Git history
    "venv",  # Commonly used location for virtual environments
)


def _get_directory_globs_files(
    directory: str, patterns: Iterable[str], *, recursive: bool = False
) -> FrozenSet[str]:
    """
    Return a `frozenset` of file names matching the glob `pattern` within
    `directory`, or in a directory matching the glob pattern.

    Parameters:

    - directory (str)
    - patterns ([str])
    - recursive (bool) = False
    """
    if isinstance(patterns, str):
        patterns = (patterns,)
    file_relative_paths: Set[str]
    relative_paths: FrozenSet[str]
    current_directory: str = os.path.curdir
    os.chdir(directory)
    try:
        relative_paths = frozenset()

        def add_glob(pattern: str) -> None:
            nonlocal relative_paths
            relative_paths |= frozenset(iglob(pattern, recursive=recursive))

        deque(map(add_glob, patterns), maxlen=0)
        file_relative_paths = set()
        relative_path: str
        for relative_path in relative_paths:
            if os.path.isdir(relative_path):
                sub_directory: str
                _: Iterable[str]
                files: Iterable[str]
                for sub_directory, _, files in os.walk(relative_path):
                    sub_directory = sub_directory.replace("\\", "/")
                    file: str
                    for file in files:
                        file_relative_paths.add(f"{sub_directory}/{file}")
            else:
                file_relative_paths.add(relative_path.replace("\\", "/"))
    finally:
        os.chdir(current_directory)
    return frozenset(file_relative_paths)


def _get_directory_globs(
    directory: str, patterns: Iterable[str], *, recursive: bool = False
) -> FrozenSet[str]:
    """
    Return a `frozenset` of directory paths matching the glob `pattern` within
    `directory`, or in a directory matching the glob pattern.

    Parameters:

    - directory (str)
    - patterns ([str])
    - recursive (bool) = False
    """
    if isinstance(patterns, str):
        patterns = (patterns,)
    relative_paths: FrozenSet[str]
    current_directory: str = os.path.curdir
    os.chdir(directory)
    try:
        relative_paths = frozenset()

        def add_glob(pattern: str) -> None:
            nonlocal relative_paths
            relative_paths |= frozenset(iglob(pattern, recursive=recursive))

        deque(map(add_glob, patterns), maxlen=0)
    finally:
        os.chdir(current_directory)
    return relative_paths


def get_ignored_files(
    directory: str = ".",
    exclude: FrozenSet[str] = frozenset(),
) -> Set[str]:
    """
    Get a `set` containing the relative paths of all ignored files
    in `directory` excluding those matching any of the glob patterns
    in `exclude`.

    Parameters:

    - directory (str): The root project directory.
    - exclude ({str}) = frozenset(): A `frozenset` of glob patterns for
      files and sub-directories to exclude.
    """
    quoted_directory: str = quote(os.path.abspath(directory))
    return (
        set(
            run(
                (
                    f"git add {quoted_directory} && "
                    f"git ls-files -o {quoted_directory}"
                ),
                echo=False,
            ).split("\n")
        )
        - _get_directory_globs_files(directory, exclude, recursive=True)
    )


def _is_sub_directory_excluded(
    sub_directory: str, directory: str, exclude: FrozenSet[str]
) -> bool:
    relative_sub_directory: str = os.path.relpath(
        os.path.abspath(sub_directory), directory
    )
    if relative_sub_directory.startswith("./"):
        relative_sub_directory = relative_sub_directory[2:]
    relative_sub_directory_list: List[str] = relative_sub_directory.split("/")
    index: int
    for index in range(1, len(relative_sub_directory_list)):
        ancestor: str = "/".join(relative_sub_directory_list[:index])
        if ancestor in exclude:
            return True
    return False


def delete_empty_directories(
    directory: str = ".",
    exclude: FrozenSet[str] = frozenset(),
    dry_run: bool = False,
    _recurrence: bool = False,
) -> int:
    """
    Deletes empty directories under the current directory.

    Parameters:

    - exclude ({str}) = frozenset():
      A set of top-level directory names to exclude
    """
    number_of_deleted_directories: int = 0
    sub_directory: str
    sub_directories: Sequence[str]
    files: Sequence[str]
    exclude = _get_directory_globs(directory, exclude)
    for sub_directory, sub_directories, files in os.walk(
        directory, topdown=False
    ):
        if not (
            _is_sub_directory_excluded(sub_directory, directory, exclude)
            or any(
                filter(
                    lambda name: name != ".DS_Store",
                    chain(sub_directories, files),
                )
            )
        ):
            if dry_run:
                print(f"rm -R {sub_directory}")
            else:
                shutil.rmtree(sub_directory)
            number_of_deleted_directories += 1
    if number_of_deleted_directories and not dry_run:
        number_of_deleted_directories += delete_empty_directories(
            directory,
            exclude=exclude,
            dry_run=dry_run,
            _recurrence=True,
        )
    if (not _recurrence) and number_of_deleted_directories:
        if not dry_run:
            print(f"Deleted {number_of_deleted_directories} empty directories")
    return number_of_deleted_directories


def delete_ignored(
    directory: str = ".",
    exclude: FrozenSet[str] = frozenset(),
    dry_run: bool = False,
) -> None:
    """
    Delete files which are ignored by Git.

    Parameters:

    - root_directory (str): The root project directory.
    - exclude ({{str}}) = {EXCLUDE_DIRECTORIES}: A `frozenset` of
      directories to leave untouched.
    """
    sub_directory_name: str
    directories_files: Dict[str, Set[str]] = {}
    paths: Set[str]
    path: str
    for path in get_ignored_files(directory=directory, exclude=exclude):
        sub_directory_name = ""
        if "/" in path:
            sub_directory_name = path.split("/")[0]
        if sub_directory_name not in directories_files:
            directories_files[sub_directory_name] = set()
        directories_files[sub_directory_name].add(
            os.path.join(directory, path)
        )
    for sub_directory_name, paths in directories_files.items():
        number_of_files: int = len(paths)
        if not dry_run:
            print(
                f"Deleting {number_of_files} ignored "
                f'file{"s" if number_of_files > 1 else ""} in '
                f"{sub_directory_name}"
            )
        for path in paths:
            if dry_run:
                print(f"rm {path}")
            else:
                os.remove(path)


delete_ignored.__doc__ = delete_ignored.__doc__.format(  # type: ignore
    EXCLUDE_DIRECTORIES=repr(frozenset(DEFAULT_EXCLUDE))
)


def clean(
    directory: str = ".",
    exclude: FrozenSet[str] = frozenset(DEFAULT_EXCLUDE),
    dry_run: bool = False,
) -> None:
    """
    Cleanup (delete) files which are ignored by Git and subsequently delete all
    empty directories.

    Parameters:

    - root_directory (str) = ".": The project's root directory.
    - exclude ({{str}}) = {EXCLUDE_DIRECTORIES}: A `frozenset` of
      directories to leave untouched.
    """
    delete_ignored(directory, exclude=exclude, dry_run=dry_run)
    delete_empty_directories(directory, exclude=exclude, dry_run=dry_run)


clean.__doc__ = clean.__doc__.format(  # type: ignore
    EXCLUDE_DIRECTORIES=repr(frozenset(DEFAULT_EXCLUDE))
)


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="daves-dev-tool clean",
        description=(
            "This command removes all files from your project directory which "
            "are ignored by git, unless matching one of the EXCLUDE glob "
            "patterns."
        ),
    )
    exclude: str
    default_exclude_parameters: str = " ".join(
        f"-e {exclude}" for exclude in DEFAULT_EXCLUDE
    )
    parser.add_argument(
        "-e",
        "--exclude",
        type=str,
        action="append",
        help=(
            "One or more glob patterns indicating files/directories to "
            "exclude from cleanup. The default values are: `"
            f"{default_exclude_parameters}`."
        ),
    )
    parser.add_argument(
        "-dr",
        "--dry-run",
        default=False,
        action="store_const",
        const=True,
        help=(
            "Instead of executing the cleanup, just print the shell "
            "commands (a list of `rm FILE` commands)."
        ),
    )
    parser.add_argument(
        "directory",
        type=str,
        default=".",
        nargs="?",
        help="The root directory for the project.",
    )
    arguments: argparse.Namespace = parser.parse_args()
    clean(
        directory=arguments.directory,
        exclude=frozenset(
            arguments.exclude if arguments.exclude else DEFAULT_EXCLUDE
        ),
        dry_run=arguments.dry_run,
    )


if __name__ == "__main__":
    main()
