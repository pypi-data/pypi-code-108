import os
import argparse
import tomli
import tomli_w
from io import StringIO
from dataclasses import dataclass
from pkg_resources import Distribution
from configparser import ConfigParser, SectionProxy
from typing import (
    Dict,
    Iterable,
    IO,
    List,
    Callable,
    Set,
    Union,
    Tuple,
    Any,
    Optional,
)
from packaging.specifiers import Specifier, SpecifierSet
from packaging.requirements import Requirement
from packaging.version import Version, LegacyVersion, parse as parse_version
from more_itertools import unique_everseen
from ..utilities import iter_parse_delimited_values
from .utilities import (
    normalize_name,
    get_installed_distributions,
    is_requirement_string,
)


def get_updated_requirement_string(
    requirement_string: str, ignore: Iterable[str] = ()
) -> str:
    """
    This function accepts a requirement string, and returns a requirement
    string updated to reflect the version of the requirement installed
    in the current environment
    """
    return _get_updated_requirement_string(
        requirement_string, set(map(normalize_name, ignore))
    )


@dataclass
class _Version:
    """
    Instances of this class can be be passed as `self` in a call
    to `packaging.version.Version.__str__`, and thereby can facilitate
    operations to mimic mutability for the aforementioned class.
    """

    epoch: int
    release: Tuple[int, ...]
    pre: Any
    post: Any
    dev: Any
    local: Any


def _update_requirement_specifiers(
    requirement: Requirement, installed_version_string: str
) -> None:
    """
    This function updates specifier version numbers for a requirement
    to match the installed version of the package
    """
    installed_version: Union[Version, LegacyVersion] = parse_version(
        installed_version_string
    )
    specifier: Specifier
    updated_specifier_strings: List[str] = []
    for specifier in requirement.specifier:  # type: ignore
        # Only update requirement to match our installed version
        # if the requirement is *inclusive*
        if ("=" in specifier.operator) and ("!" not in specifier.operator):
            specifier_version: Union[Version, LegacyVersion] = parse_version(
                specifier.version
            )
            assert installed_version.release is not None
            if specifier_version.release is None:
                updated_specifier_strings.append(f"{specifier.operator}")
            else:
                greater_or_equal_specificity: bool = len(
                    specifier_version.release
                ) >= len(installed_version.release)
                specifier_version_data: _Version = _Version(
                    epoch=installed_version.epoch,
                    # Truncate the updated version requirement at the same
                    # level of specificity as the old
                    release=installed_version.release[
                        : len(specifier_version.release)
                    ],
                    pre=(
                        installed_version.pre
                        if greater_or_equal_specificity
                        else None
                    ),
                    post=(
                        installed_version.post
                        if greater_or_equal_specificity
                        else None
                    ),
                    dev=(
                        installed_version.dev
                        if greater_or_equal_specificity
                        else None
                    ),
                    local=(
                        installed_version.local
                        if greater_or_equal_specificity
                        else None
                    ),
                )
                version_string: str = Version.__str__(
                    specifier_version_data  # type: ignore
                )
                updated_specifier_strings.append(
                    f"{specifier.operator}{version_string}"
                )
        else:
            updated_specifier_strings.append(str(specifier))
    requirement.specifier = SpecifierSet(",".join(updated_specifier_strings))


def _get_updated_requirement_string(
    requirement_string: str, ignore: Set[str]
) -> str:
    """
    This function updates version numbers in a requirement string to match
    those installed in the current environment
    """
    # Skip empty requirement strings
    if not is_requirement_string(requirement_string):
        return requirement_string
    requirement: Requirement = Requirement(requirement_string)
    name: str = normalize_name(requirement.name)
    if name in ignore:
        return requirement_string
    try:
        distribution: Distribution = get_installed_distributions()[name]
        _update_requirement_specifiers(requirement, distribution.version)
    except KeyError:
        # If the requirement isn't installed, we can't update the version
        pass
    return str(requirement)


def _normalize_ignore_argument(ignore: Iterable[str]) -> Set[str]:
    ignore_set: Set[str]
    # Normalize/harmonize excluded project names
    if isinstance(ignore, str):
        ignore = (ignore,)
    ignore_set = set(map(normalize_name, ignore))
    return ignore_set


def get_updated_requirements_txt(data: str, ignore: Iterable[str] = ()) -> str:
    """
    Return the contents of a **requirements.txt** file, updated to reflect the
    currently installed project versions, excluding those specified in
    `ignore`.

    Parameters:

    - data (str): The contents of a **setup.cfg** file
    - ignore ([str]): One or more project names to leave as-is
    """
    ignore_set: Set[str] = _normalize_ignore_argument(ignore)

    def get_updated_requirement_string(requirement: str) -> str:
        return _get_updated_requirement_string(requirement, ignore=ignore_set)

    return "\n".join(map(get_updated_requirement_string, data.split("\n")))


def get_updated_setup_cfg(
    data: str, ignore: Iterable[str] = (), all_extra_name: str = ""
) -> str:
    """
    Return the contents of a **setup.cfg** file, updated to reflect the
    currently installed project versions, excluding those specified in
    `ignore`.

    Parameters:

    - data (str): The contents of a **setup.cfg** file
    - ignore ([str]): One or more project names to leave as-is
    - all_extra_name (str): A name under which to store an extra which
      consolidates requirements from all other extras
    """
    ignore_set: Set[str] = _normalize_ignore_argument(ignore)

    def get_updated_requirement_string(requirement: str) -> str:
        return _get_updated_requirement_string(requirement, ignore=ignore_set)

    # Parse
    parser: ConfigParser = ConfigParser()
    parser.read_string(data)
    # Update
    if ("options" in parser) and ("install_requires" in parser["options"]):
        parser["options"]["install_requires"] = "\n".join(
            map(  # type: ignore
                get_updated_requirement_string,
                parser["options"]["install_requires"].split("\n"),
            )
        )
    if "options.extras_require" in parser:
        extras_require: SectionProxy = parser["options.extras_require"]
        all_extra_requirements: List[str] = []
        extra_name: str
        extra_requirements_string: str
        extra_requirements: List[str]
        for extra_name, extra_requirements_string in extras_require.items():
            if extra_name != all_extra_name:
                extra_requirements = list(
                    map(
                        get_updated_requirement_string,
                        extra_requirements_string.split("\n"),
                    )
                )
                if all_extra_name:
                    all_extra_requirements += extra_requirements
                extras_require[extra_name] = "\n".join(extra_requirements)
        # If a name was specified for an all-encompasing extra,
        # we de-duplicate and update or create that extra
        if all_extra_name:
            # We pre-pend an empty requirement string in order to]
            # force new-line creation at the beginning of the extra
            extras_require[all_extra_name] = "\n".join(
                unique_everseen([""] + all_extra_requirements)
            )
    # Return as a string
    setup_cfg_io: IO[str]
    with StringIO() as setup_cfg_io:
        parser.write(setup_cfg_io)
        setup_cfg_io.seek(0)
        return setup_cfg_io.read()


def get_updated_tox_ini(data: str, ignore: Iterable[str] = ()) -> str:
    """
    Return the contents of a **tox.ini** file, updated to reflect the
    currently installed project versions, excluding those specified in
    `ignore`.

    Parameters:

    - data (str): The contents of a **tox.ini** file
    - ignore ([str]): One or more project names to leave as-is
    """
    ignore_set: Set[str] = _normalize_ignore_argument(ignore)

    def get_updated_requirement_string(requirement: str) -> str:
        prefix: Optional[str] = None
        if ":" in requirement:
            prefix, requirement = requirement.split(":", maxsplit=1)
        requirement = _get_updated_requirement_string(
            requirement, ignore=ignore_set
        )
        if prefix is not None:
            requirement = f"{prefix}: {requirement.lstrip()}"
        return requirement

    # Parse
    parser: ConfigParser = ConfigParser()
    parser.read_string(data)

    def update_section_options(section_name: str, option_name: str) -> None:
        if parser.has_option(section_name, option_name):
            parser.set(
                section_name,
                option_name,
                "\n".join(
                    map(
                        get_updated_requirement_string,
                        parser.get(section_name, option_name).split("\n"),
                    )
                ),
            )

    def update_section(section_name: str) -> None:
        update_section_options(section_name, "deps")
        if section_name == "tox":
            update_section_options(section_name, "requires")

    # Update
    list(map(update_section, parser.sections()))
    # Return as a string
    tox_ini_io: IO[str]
    with StringIO() as tox_ini_io:
        parser.write(tox_ini_io)
        tox_ini_io.seek(0)
        return tox_ini_io.read()


def get_updated_pyproject_toml(
    data: str, ignore: Iterable[str] = (), all_extra_name: str = ""
) -> str:
    """
    Return the contents of a **pyproject.toml** file, updated to reflect the
    currently installed project versions, excluding those specified in
    `ignore`.

    Parameters:

    - data (str): The contents of a **pyproject.toml** file
    - ignore ([str]): One or more project names to leave as-is
    """
    ignore_set: Set[str] = _normalize_ignore_argument(ignore)

    def get_updated_requirement_string(requirement: str) -> str:
        return _get_updated_requirement_string(requirement, ignore=ignore_set)

    # Parse
    pyproject: Dict[str, Any] = tomli.loads(data)
    if ("build-system" in pyproject) and (
        "requires" in pyproject["build-system"]
    ):
        pyproject["build-system"]["requires"] = list(
            map(
                get_updated_requirement_string,
                pyproject["build-system"]["requires"],
            )
        )
        return tomli_w.dumps(pyproject)
    return data


def _update(
    path: str, ignore: Iterable[str] = (), all_extra_name: str = ""
) -> None:
    data: str
    update_function: Callable[[str], str]
    kwargs: Dict[str, Union[str, Iterable[str]]] = {}
    base_file_name: str = os.path.basename(path).lower()
    if base_file_name == "setup.cfg":
        update_function = get_updated_setup_cfg
        if all_extra_name:
            kwargs["all_extra_name"] = all_extra_name
    elif base_file_name == "pyproject.toml":
        update_function = get_updated_pyproject_toml
    elif base_file_name == "tox.ini":
        update_function = get_updated_tox_ini
    else:
        update_function = get_updated_requirements_txt
    kwargs["ignore"] = ignore
    file_io: IO[str]
    with open(path) as file_io:
        data = file_io.read()
    updated_data: str = update_function(data, **kwargs)
    if updated_data == data:
        print(f"All requirements were already up-to-date in {path}")
    else:
        print(f"Updating requirements in {path}")
        with open(path, "w") as file_io:
            file_io.write(updated_data)


def update(
    paths: Iterable[str],
    ignore: Iterable[str] = (),
    all_extra_name: str = "",
    verbose: bool = False,
) -> None:
    """
    Update requirement versions in the specified files.

    Parameters:

    - path (str|[str}): One or more local paths to setup.cfg and/or
      requirements.txt files
    - ignore ([str]): One or more project names to ignore (leave as-is)
    - all_extra_name (str): If provided, an extra which consolidates
      the requirements for all other extras will be added/updated to
      *setup.cfg* (this argument is ignored for *requirements.txt* files)
    - verbose (bool): Echo more verbose output
    """
    if isinstance(paths, str):
        paths = (paths,)

    def update_(path: str) -> None:
        _update(path, ignore=ignore, all_extra_name=all_extra_name)

    list(map(update_, paths))


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="daves-dev-tools requirements update"
    )
    parser.add_argument(
        "-i",
        "--ignore",
        default=[],
        type=str,
        action="append",
        help=(
            "A comma-separated list of distributions to ignore (leave "
            "any requirements pertaining to the package as-is) "
        ),
    )
    parser.add_argument(
        "-aen",
        "--all-extra-name",
        default="",
        type=str,
        help=(
            "If provided, an extra which consolidates the requirements "
            "for all other extras will be added/updated to *setup.cfg* (this "
            "argument is ignored for *requirements.txt* files)"
        ),
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_const",
        const=True,
        default=False,
        help="Echo more verbose output",
    )
    parser.add_argument(
        "path",
        nargs="+",
        type=str,
        help=(
            "One or more local paths to a *setup.cfg* and/or "
            "*requirements.txt* file"
        ),
    )
    arguments: argparse.Namespace = parser.parse_args()
    update(
        paths=arguments.path,
        ignore=tuple(iter_parse_delimited_values(arguments.ignore)),
        all_extra_name=arguments.all_extra_name,
        verbose=arguments.verbose,
    )


if __name__ == "__main__":
    main()
