import argparse
import sys
from itertools import chain
from typing import Iterable
from .requirements.utilities import (
    get_installed_distributions,
    get_requirements_required_distribution_names,
)
from .utilities import run


def uninstall_all(exclude: Iterable[str] = (), dry_run: bool = False) -> None:
    """
    Uninstall all distributions except for those requirementS specified
    in `exclude`.

    Parameters:

    - exclude ([str]): One or more requirement specifiers (for example:
      "requirement-name[extra-a,extra-b]" or ".[extra-a, extra-b]) and/or paths
      to a setup.cfg, pyproject.toml, tox.ini or requirements.txt file
    """
    name: str
    uninstall_distribution_names: str = " ".join(
        sorted(
            (
                set(get_installed_distributions().keys())
                - get_requirements_required_distribution_names(
                    chain(
                        ("pip", "setuptools", "wheel", "distribute"), exclude
                    )
                )
            ),
            key=lambda name: name.lower(),
        )
    )
    if uninstall_distribution_names:
        command: str = (
            f"{sys.executable} -m "
            f"pip uninstall -y {uninstall_distribution_names}"
        )
        if dry_run:
            print(command)
        else:
            run(command, echo=True)
    else:
        print("# No distributions found to uninstall")


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="daves-dev-tools uninstall-all",
        description=(
            "This command will uninstall all distributions "
            "installed in the same environment as that from which this "
            "command is executed, excluding any specified by "
            "`-e EXCLUDE`"
        ),
    )
    parser.add_argument(
        "-e",
        "--exclude",
        default=[],
        type=str,
        action="append",
        help=(
            "One or more distribution specifiers, requirement files, "
            "setup.cfg files, pyproject.toml files, or tox.ini files "
            "denoting packages to exclude (along with all of their "
            "requirements) from those distributions to be "
            "uninstalled"
        ),
    )
    parser.add_argument(
        "-dr",
        "--dry-run",
        default=False,
        const=True,
        action="store_const",
        help=(
            "Print, but do not execute, the assembled `pip uninstall` command "
            "which, absent this flag, would be executed"
        ),
    )
    arguments: argparse.Namespace = parser.parse_args()
    uninstall_all(exclude=arguments.exclude, dry_run=arguments.dry_run)


if __name__ == "__main__":
    main()
