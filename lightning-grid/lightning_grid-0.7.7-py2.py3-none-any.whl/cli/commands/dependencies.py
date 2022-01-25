import os
from pathlib import Path
import time
from typing import Optional

import click
from yaspin import yaspin

import grid.sdk.env as env
from grid.sdk.source_code.dependency_manager import (
    CONDA_MANAGER,
    CondaManager,
    DependencyManagerBase,
    find_package_manager,
    PIP_MANAGER,
    PipManager,
)
from grid.sdk.source_code.git import execute_git_command

PIP_REQUIREMENTS_FILE = "requirements.txt"
CONDA_REQUIREMENTS_FILE = "environment.yml"
WARNING_STR = click.style('WARNING', fg='yellow')


def wait_spinner(seconds=5):
    with yaspin():
        while seconds:
            time.sleep(1)
            seconds -= 1


class DependencyMixin:
    @staticmethod
    def _get_manager(repo_root) -> DependencyManagerBase:
        files = os.listdir(repo_root)
        conda_env = os.getenv("CONDA_DEFAULT_ENV")
        warning_str = click.style('WARNING', fg='yellow')
        if CONDA_REQUIREMENTS_FILE in files:
            if PIP_REQUIREMENTS_FILE in files:  # skipcq: PYL-R1705
                click.echo(
                    f"{warning_str} Found both {CONDA_REQUIREMENTS_FILE} "
                    f"and {PIP_REQUIREMENTS_FILE}. Defaulting to "
                    f"{PIP_REQUIREMENTS_FILE}"
                )
                manager_class = PipManager
            else:
                manager_class = CondaManager
        elif PIP_REQUIREMENTS_FILE in files:
            manager_class = PipManager
        elif conda_env:
            manager_class = CondaManager
        else:
            manager_class = PipManager
        return manager_class()

    @staticmethod
    def _guess_manager_from_dependency_file(dependency_file) -> DependencyManagerBase:
        """
        If user provides the dependency file instead of letting us find it from the root,
        use this function to create the Manager. If dependency_file is not provided,
        use `_get_manager`
        """
        package_manager = find_package_manager(dependency_file)
        if package_manager == PIP_MANAGER:
            return PipManager(dependency_file=dependency_file)
        if package_manager == CONDA_MANAGER:
            return CondaManager(dependency_file=dependency_file)

        raise RuntimeError("Unknown package manager")

    def serialize_dependencies(self,
                               config_path: Optional[str] = None,
                               dependency_file: Optional[str] = None) -> Optional[Path]:
        """
        Serialize dependency information to the corresponding source.

        Write python dependencies to the corresponding dependency listing
        (requirements.txt or environment.yml) and system dependencies to
        grid config (config.yml). Both write operations are actually offloaded
        downstream to the dependency manager object. Also fetches warnings
        from the dependency manager and echo to the user's terminal

        config:
            Grid config either read from the file provided by the user or the
            default generated one

        Returns
        -------
        Path to the requirement file
        """
        check_status = self._check_dependency_listing(do_diff_check=False, ignore_warnings=False)
        if not check_status:
            click.echo("Dependency check failed. Cannot sync environment")
            return None

        repo_root = execute_git_command(['rev-parse', '--show-toplevel'])
        try:
            if dependency_file:
                deps_manager = self._guess_manager_from_dependency_file(dependency_file)
            else:
                deps_manager = self._get_manager(repo_root)
        except Exception as e:  # noqa
            # it's already being checked by `check_dependency_listing`
            raise RuntimeError("Exception while initializing dependency manager")

        deps_manager.write_spec()
        deps_manager.write_config(config_path)
        return deps_manager.req_file

    def _check_dependency_listing(
        self,
        do_diff_check=True,
        ignore_warnings=env.IGNORE_WARNINGS,
        repo_root=execute_git_command(['rev-parse', '--show-toplevel']),
        dependency_file=None,
    ):
        """
        Evaluate if dependency listing is correct or not

        Determines the package manager employed by the user to specify
        application dependencies, setting up the appropriate interaction
        classes used to query one of the various package managers available
        as the system resolves dependency versions. Should no requirement file
        exist which specifies needed libraries+versions, this method provides
        the logic through which users are asked to select how they would like
        to proceed - automatic heuristic based generation or manual.

        Parameters
        ----------
        do_diff_check: bool
            Check for the diff between requirements file and the environment. This
            is True by default but `serialize_dependencies` checks this explicitly
            as part of serializing the dependencies and hence will set as False
        ignore_warnings: bool
            Should warnings be ignored. Should be removed when we move
            click component out of SDK -> TODO
        repo_root: str
            Root of the repository. Defaults to git root

        Returns
        -------
        Return False if check fails. True otherwise
        """
        if ignore_warnings:
            return True

        # Assuming the requirements file is always at the repo root if not passed
        # through dependency_file argument
        files = os.listdir(repo_root)

        try:
            if dependency_file:
                deps_manager = self._guess_manager_from_dependency_file(dependency_file)
            else:
                deps_manager = self._get_manager(repo_root)
        except Exception as e:  # noqa

            # ==============================================
            # Case 1: Initializing dependency manager failed
            # ==============================================
            # Ignoring to avoid internal errors to go to users
            if PIP_REQUIREMENTS_FILE not in files and CONDA_REQUIREMENTS_FILE not in files:
                message = f"""

        {WARNING_STR}
        No requirements.txt or environment.yml found. Your build could crash
        or not start.
        """

                click.echo(message)
                wait_spinner(seconds=2)
            return False

        # =====================================
        # Case 2: Requirements file not present
        # =====================================
        if PIP_REQUIREMENTS_FILE not in files and CONDA_REQUIREMENTS_FILE not in files:
            deps_found = "\n        ".join(deps_manager.source_deps)
            message = f"""

        {WARNING_STR}
        No requirements.txt or environment.yml found but we identified below
        dependencies from your source. Your build could crash or not
        start.

        {deps_found}
        """

            click.echo(message)
            wait_spinner(seconds=2)
            return False

        # ===========================================================
        # Case 3: Packages found imported for which spec is not found
        # ===========================================================
        missing = "\n        ".join(deps_manager.get_missing())
        if missing:
            message = f"""

        {WARNING_STR}

        Your requirements.txt or environment.yml are missing the following packages:

        {missing}

        Your experiment could crash if these are missing!
        Add them yourself or try `grid sync-env`
        """
            click.echo(message)
            wait_spinner(seconds=2)
            return False

        # ==============================================
        # Case 4: Incomplete/different-spec requirements
        # ==============================================
        if do_diff_check and deps_manager.has_change:
            message = f"""
        {WARNING_STR}
        Incomplete requirements.txt or environment.yml found
        Your build could crash or not start.

        Run `grid sync-env` to auto-populate the changed packages
        """
            click.echo(message)
            wait_spinner(seconds=2)
            return False

        # Returning True if all looks good
        return True
