import argparse
import re
import sys
import os
from itertools import chain
from pkg_resources import Distribution
from pipes import quote
from typing import Iterable, Set, List, Tuple, Pattern
from .requirements.utilities import (
    get_distribution,
    get_installed_distributions,
    get_requirements_required_distribution_names,
    normalize_name,
    get_setup_distribution_name,
    is_installed,
)
from .utilities import iter_parse_delimited_values, run


_SETUP_NAMES: Set[str] = {"setup.cfg", "setup.py"}
EXCLUDE_DIRECTORY_REGULAR_EXPRESSIONS: Tuple[str, ...] = (
    r"^[.~].*$",
    r"^venv$",
    r"^site-packages$",
)


def _get_requirement_string(
    name: str, directory: str, include_extras: bool
) -> str:
    requirement_string: str = os.path.abspath(directory)
    if is_installed(name) and include_extras:
        distribution: Distribution = get_distribution(name)
        if distribution.extras:
            requirement_string = (
                f"{requirement_string}" f"[{','.join(distribution.extras)}]"
            )
    return requirement_string


def _iter_find_distributions(
    distribution_names: Set[str],
    directories: Iterable[str] = ("../"),
    exclude_directory_regular_expressions: Iterable[
        str
    ] = EXCLUDE_DIRECTORY_REGULAR_EXPRESSIONS,
    include_extras: bool = False,
) -> Iterable[str]:
    if isinstance(directories, str):
        directories = (directories,)
    directories = map(os.path.abspath, directories)
    exclude_directory_patterns: Tuple[Pattern, ...] = tuple(
        map(re.compile, exclude_directory_regular_expressions)
    )

    def include_directory(directory: str) -> bool:
        directory_basename: str = os.path.basename(directory)
        for exclude_directory_pattern in exclude_directory_patterns:
            if exclude_directory_pattern.match(directory_basename):
                return False
        return True

    def iter_find_directory_distributions(directory: str) -> Iterable[str]:
        sub_directories: List[str]
        files: List[str]
        sub_directories, files = next(iter(os.walk(directory)))[1:3]

        def get_subdirectory_path(subdirectory: str) -> str:
            return os.path.join(directory, subdirectory)

        sub_directories = list(map(get_subdirectory_path, sub_directories))
        # Check to see if this is a project directory
        if any(map(_SETUP_NAMES.__contains__, map(str.lower, files))):
            name: str = get_setup_distribution_name(directory)
            if name in distribution_names:
                return (
                    _get_requirement_string(name, directory, include_extras),
                )
            else:
                return ()
        else:
            return chain(
                *map(
                    iter_find_directory_distributions,
                    filter(include_directory, sub_directories),
                )
            )

    return chain(*map(iter_find_directory_distributions, directories))


def find_and_install_distributions(
    distribution_names: Set[str],
    directories: Iterable[str] = ("../"),
    exclude_directory_regular_expressions: Iterable[
        str
    ] = EXCLUDE_DIRECTORY_REGULAR_EXPRESSIONS,
    dry_run: bool = False,
    include_extras: bool = False,
) -> None:
    requirements: Tuple[str, ...] = tuple(
        map(
            quote,
            _iter_find_distributions(
                distribution_names=distribution_names,
                directories=directories,
                exclude_directory_regular_expressions=(
                    exclude_directory_regular_expressions
                ),
                include_extras=include_extras,
            ),
        )
    )
    if requirements:
        command = (
            f"{quote(sys.executable)} -m pip install "
            f"-e {' -e '.join(requirements)}"
        )
        if dry_run:
            print(command)
        else:
            run(command)


def install_editable(
    requirements: Iterable[str] = (),
    directories: Iterable[str] = ("../"),
    exclude: Iterable[str] = (),
    exclude_directory_regular_expressions: Iterable[
        str
    ] = EXCLUDE_DIRECTORY_REGULAR_EXPRESSIONS,
    dry_run: bool = False,
    include_extras: bool = False,
) -> None:
    """
    Install, in editable/develop mode, all distributions, except for those
    specified in `exclude`, which are required for the specified
    `requirements`.

    Parameters:
    - requirements ([str]) = ():
      One or more requirement specifiers or configuration file paths to which
      installation should be limited
    - directories ([str]) = ("../",): The directories in which to search
      for distributions to install. By default, the parent of the currently
      directory is used.
    - exclude ([str]): One or more distributions to pass over when searching
      for distributable projects
    - exclude_directory_regular_expressions ([str])
    - dry_run (bool)
    - include_extras ([str])
    """
    required_distribution_names: Set[str] = (
        get_requirements_required_distribution_names(requirements)
        if requirements
        else set(get_installed_distributions().keys())
    )
    find_and_install_distributions(
        distribution_names=(
            required_distribution_names - set(map(normalize_name, exclude))
        ),
        directories=directories,
        exclude_directory_regular_expressions=(
            exclude_directory_regular_expressions
        ),
        dry_run=dry_run,
        include_extras=include_extras,
    )


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="daves-dev-tools install-editable",
        description=(
            "This command will attempt to find and install, in "
            "develop (editable) mode, all packages which are "
            "installed in the current python environment. If one or "
            "more `requirement` file paths or specifiers are provided, "
            "installation will be limited to the dependencies identified "
            "(recursively) by these requirements. Exclusions can be specified "
            "using the `-e` parameter. Directories can be excluded by "
            "passing regular expressions to the `-edre` parameter."
        ),
    )
    parser.add_argument(
        "requirement",
        nargs="*",
        type=str,
        default=[],
        help=(
            "One or more requirement specifiers or configuration file paths. "
            "If provided, only dependencies of these requirements will be "
            "installed."
        ),
    )
    parser.add_argument(
        "-d",
        "--directory",
        default=["../"],
        type=str,
        action="append",
        help=(
            "A directory in which to search for requirements. "
            "By default, the directory above the current directory is "
            "searched. This argument may be passed more than once to include "
            "multiple locations."
        ),
    )
    parser.add_argument(
        "-e",
        "--exclude",
        default=[],
        type=str,
        action="append",
        help="A comma-separated list of distribution names to exclude",
    )

    parser.add_argument(
        "-edre",
        "--exclude-directory-regular-expression",
        default=list(EXCLUDE_DIRECTORY_REGULAR_EXPRESSIONS),
        type=str,
        action="append",
        help=(
            "Directories matching this regular expression will be excluded "
            "when searching for setup locations This argument may be passed "
            "more than once to exclude directories matching more than one "
            "regular expression. The default for this argument is "
            "equivalent to `-edre {}`".format(
                " -edre ".join(
                    map(quote, EXCLUDE_DIRECTORY_REGULAR_EXPRESSIONS)
                )
            )
        ),
    )
    parser.add_argument(
        "-dr",
        "--dry-run",
        default=False,
        action="store_const",
        const=True,
        help="Print, but do not execute, all `pip install` commands",
    )
    parser.add_argument(
        "-ie",
        "--include-extras",
        default=False,
        action="store_const",
        const=True,
        help="Install all extras for all discovered distributions",
    )
    arguments: argparse.Namespace = parser.parse_args()
    install_editable(
        requirements=arguments.requirement,
        directories=arguments.directory,
        exclude_directory_regular_expressions=(
            arguments.exclude_directory_regular_expression
        ),
        exclude=iter_parse_delimited_values(arguments.exclude),
        dry_run=arguments.dry_run,
        include_extras=arguments.include_extras,
    )


if __name__ == "__main__":
    main()
