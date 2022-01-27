"""
This module cleans up files which are ignored by git
"""
import argparse
import functools
import os
import shutil
from pipes import quote
from itertools import chain
from typing import Any, Callable, Dict, FrozenSet, Iterable, Sequence, Set
from .utilities import run

ROOT_DIRECTORY: str = "."
EXCLUDE_DIRECTORIES: FrozenSet[str] = frozenset(
    (
        "./.idea",  # Jetbrains' IDE project settings (Pycharm, Intellij IDEA)
        "./.vscode",  # Microsoft Visual Studio Code project settings
        "./.git",  # Git history
        "./venv",  # Commonly used location for virtual environments
    )
)

lru_cache: Callable[..., Any] = functools.lru_cache


@lru_cache()
def _is_excluded(
    absolute_path: str, exclude_directories: FrozenSet[str] = frozenset()
) -> bool:
    absolute_path = absolute_path.rstrip("/")
    for directory_path in exclude_directories:
        if absolute_path.startswith(f"{directory_path}/"):
            return True
    return False


@lru_cache()
def _absolute_sub_directories(
    root_directory: str, directories: FrozenSet[str]
) -> FrozenSet[str]:
    directory: str
    return frozenset(
        (
            os.path.abspath(os.path.join(root_directory, directory))
            for directory in directories
        )
    )


def get_ignored_files(
    root_directory: str = ".",
    exclude_directories: FrozenSet[str] = frozenset(),
) -> Iterable[str]:
    """
    Yield the absolute path of all ignored files, excluding those in any of the
    `exclude_directories`.

    Parameters:

    - root_directory (str): The root project directory.
    - exclude_directories ({str}) = frozenset(): A `frozenset` of
      sub-directories to exclude.
    """
    path: str
    directory_name: str
    directories_files: Dict[str, Set[str]] = {}
    paths: Set[str]
    root_directory = os.path.abspath(root_directory)
    exclude_directories = _absolute_sub_directories(
        root_directory, exclude_directories
    )
    path_prefix: str = f'{root_directory.rstrip("/")}/'
    path_prefix_length: int = len(path_prefix)
    quoted_root_dir: str = quote(root_directory)
    for path in run(
        f"git add {quoted_root_dir} && git ls-files -o {quoted_root_dir}",
        echo=False,
    ).split("\n"):
        path = os.path.abspath(f"./{path}")
        if not _is_excluded(path, exclude_directories):
            directory_name = ""
            if "/" in path[path_prefix_length:]:
                directory_name = path[path_prefix_length:].split("/")[0]
            if directory_name not in directories_files:
                directories_files[directory_name] = set()
            directories_files[directory_name].add(path)
    for directory_name, paths in directories_files.items():
        number_of_files: int = len(paths)
        print(
            f"Found {number_of_files} ignored "
            f'file{"s" if number_of_files > 1 else ""} in ./'
            f"{directory_name}"
        )
        for path in paths:
            yield path


def delete_empty_directories(
    root_directory: str = ".",
    exclude_directories: FrozenSet[str] = frozenset(),
    _recurrence: bool = True,
) -> int:
    """
    Deletes empty directories under the current directory.

    Parameters:

    - exclude_directories ({str}) = frozenset():
      A set of top-level directory names to exclude
    """
    number_of_deleted_directories: int = 0
    root: str
    directories: Sequence[str]
    files: Sequence[str]
    if not _recurrence:
        root_directory = os.path.abspath(root_directory)
        exclude_directories = _absolute_sub_directories(
            root_directory, exclude_directories
        )
    for root, directories, files in os.walk(root_directory, topdown=False):
        root = os.path.abspath(root)
        if not _is_excluded(root, exclude_directories):
            if not any(
                filter(
                    lambda name: name != ".DS_Store", chain(directories, files)
                )
            ):
                shutil.rmtree(root)
                number_of_deleted_directories += 1
    if number_of_deleted_directories:
        number_of_deleted_directories += delete_empty_directories(
            root_directory,
            exclude_directories=exclude_directories,
            _recurrence=False,
        )
    if _recurrence and number_of_deleted_directories:
        print(f"Deleted {number_of_deleted_directories} empty directories")
    return number_of_deleted_directories


def delete_ignored(
    root_directory: str = ".",
    exclude_directories: FrozenSet[str] = frozenset(),
) -> None:
    """
    Delete files which are ignored by Git.

    Parameters:

    - root_directory (str): The root project directory.
    - exclude_directories ({str}) = frozenset(): A `frozenset` of directories
      which should not be touched.
    """
    for path in get_ignored_files(
        root_directory=root_directory, exclude_directories=exclude_directories
    ):
        os.remove(path)


def clean(
    root_directory: str = ".",
    exclude_directories: FrozenSet[str] = EXCLUDE_DIRECTORIES,
) -> None:
    """
    Cleanup (delete) files which are ignored by Git and subsequently delete all
    empty directories.

    Parameters:

    - root_directory (str) = ".": The project's root directory.
    - exclude_directories ({{str}}) = {EXCLUDE_DIRECTORIES}: A `frozenset` of
      directories to leave untouched.
    """
    delete_ignored(root_directory, exclude_directories=exclude_directories)
    delete_empty_directories(
        root_directory, exclude_directories=exclude_directories
    )


clean.__doc__ = clean.__doc__.format(  # type: ignore
    EXCLUDE_DIRECTORIES=EXCLUDE_DIRECTORIES
)


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="daves-dev-tool clean"
    )
    parser.add_argument(
        "--exclude",
        "-e",
        action="store",
        type=str,
        default=None,
        help=(
            'A path list of sub-directories to exclude (separated by ":" or '
            '";", depending on the operating system).'
        ),
    )
    parser.add_argument(
        "root",
        type=str,
        default=".",
        nargs="?",
        help="The root directory path for the project.",
    )
    arguments: argparse.Namespace = parser.parse_args()
    clean(
        root_directory=arguments.root,
        exclude_directories=(
            frozenset(os.path.split(arguments.exclude))
            if arguments.exclude
            else EXCLUDE_DIRECTORIES
        ),
    )


if __name__ == "__main__":
    main()
