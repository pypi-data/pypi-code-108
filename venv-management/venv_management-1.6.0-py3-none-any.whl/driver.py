"""The virtualenvwrapper driver interface and factories.
"""

from abc import abstractmethod
from pathlib import Path
from typing import List

from venv_management.errors import ImplementationNotFound
from venv_management.extension import Extension, ExtensionError, create_extension, list_extensions

KIND = "driver"

DRIVER_NAMESPACE = f"venv_management.{KIND}"


class Driver(Extension):
    """Defines the interface for a virtualenvwrapper-equivalent driver."""

    def _kind(self):
        return KIND

    def __init__(self, name):
        """
        Args:
            name: The name of the driver.

        Raises:
            ImplementationNotFound: If the the virtualenvwrapper implementation corresponding
             to the concrete driver type is not available.
        """
        super().__init__(name)
        self._check_availability()

    @abstractmethod
    def _check_availability(self):
        """Check that the particular virtualenvwrapper implementation required is available.

        Implementations of this method should either succeed or raise ImplementationNotFound.

        Raises:
            ImplementationNotFound: If the implementation is not available.
        """
        raise NotImplementedError

    @abstractmethod
    def list_virtual_envs(self) -> List[str]:
        """The virtual environments available to this package.

        Returns:
            A list of virtual environment names which can be manipulated by this package.
        """
        raise NotImplementedError

    @abstractmethod
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
            PythonNotFound: If the requested Python version could not be found.
            CommandNotFound: If the required command could not be found.
            RuntimeError: If the virtualenv could not be created.
        """
        raise NotImplementedError

    @abstractmethod
    def remove_virtual_env(self, name: str):
        """Remove a virtual environment.

        Args:
            name: The name of the virtual environment to be removed.

        Raises:
            ValueError: If the name is empty.
        """
        raise NotImplementedError

    @abstractmethod
    def resolve_virtual_env(self, name: str) -> Path:
        """Obtain a path the the a virtual environment directory.

        Args:
            name: The name of the virtual environment.

        Returns:
            The path of the named virtual environment.

        Raises:
            ValueError: If there is no virtual environment with the supplied name.
        """
        raise NotImplementedError


class DriverExtensionError(ExtensionError):
    """Indicates that an error specific to a driver extension occurred."""


def create_driver(driver_name) -> Driver:
    """Create a driver

    Args:
        driver_name: The name of the driver to create.

    Returns:
        A Driver instance.

    Raises:
        ImplementationNotFoundError: If a driver could be created but the driver could not find
            a working virtualenvwrapper (or equivalent) implementation.
    """
    driver = create_extension(
        kind=KIND,
        namespace=DRIVER_NAMESPACE,
        name=driver_name,
        exception_type=DriverExtensionError,
    )
    return driver


def driver_names() -> List[Driver]:
    """A list of available driver extensions.

    There is no guarantee that the listed drivers are backed by functioning virtualenvwrapper
    implementations.
    """
    return list_extensions(DRIVER_NAMESPACE)

_driver = None

def driver() -> Driver:
    """Obtain a Driver instance.

    Returns:
        A Driver corresponding to an available virtualenvwrapper implementation.

    Raises:
        ImplementationNotFound: If no suitable virtualenvwrapper installation was found
    """
    global _driver
    if _driver is None:
        for driver_name in driver_names():
            try:
                d = create_driver(driver_name)
            except ImplementationNotFound:
                pass
            else:
                _driver = d
                break
        else:  # no-break
            raise ImplementationNotFound("No suitable virtualenvwrapper installation found")
    return _driver
