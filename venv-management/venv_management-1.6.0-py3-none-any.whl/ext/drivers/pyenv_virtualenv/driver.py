import logging
from pathlib import Path
from typing import List

from venv_management.driver import Driver
from venv_management.errors import ImplementationNotFound

logger = logging.getLogger(__name__)

class PyEnvVirtualEnvDriver(Driver):


    def _check_availability(self):
        # TODO: Not yet implemented
        raise ImplementationNotFound(f"No implementation for {self.name}")



    def list_virtual_envs(self) -> List[str]:
        """A list of virtualenv names.

        Returns:
            A list of string names in case-sensitive alphanumeric order.

        Raises:
            FileNotFoundError: If virtualenvwrapper.sh could not be located.
        """
        raise NotImplementedError

    def make_virtual_env(
            self,
            name,
            *,
            python=None,
            project_path=None,
            packages=None,
            requirements_file=None,
            system_site_packages=False,
            pip=True,
            setuptools=True,
            wheel=True,
    ):
        """Make a virtual env.

        Args:
            name: The name of the virtual environment.

            project_path: An optional path to a project which will be associated with the
                new virtual environment.

            packages: An optional sequence of package names for packages to be installed.

            requirements_file: An optional path to a requirements file to be installed.

            python: The target interpreter for which to create a virtual environment, either
                the name of the executable, or full path.

            system_site_packages: If True, give access to the system site packages.

            pip: If True, or 'latest' the latest pip will be installed. If False, pip will not
                be installed. If 'bundled', the bundled version will be installed. If a specific
                version string is given, that version will be installed.

            setuptools: If True, or 'latest' the latest pip will be installed. If False, pip will not
                be installed. If 'bundled', the bundled version will be installed. If a specific
                version string is given, that version will be installed.

            wheel: If True, or 'latest' the latest pip will be installed. If False, pip will not
                be installed. If 'bundled', the bundled version will be installed. If a specific
                version string is given, that version will be installed.

        Returns:
            The Path to the root of the virtualenv, or None if the path could not be determined.

        Raises:
            CommandNotFound: If the the required command could not be found.
            RuntimeError: If the virtualenv could not be created.
        """
        raise NotImplementedError

    def remove_virtual_env(self, name):
        """Remove a virtual environment.

        Args:
            name: The name of the virtual environment to remove.

        Raises:
            ValueError: If there is no environment with the given name.
            RuntimeError: If the virtualenv could not be removed.
        """
        raise NotImplementedError

    def resolve_virtual_env(self, name: str) -> Path:
        raise NotImplementedError