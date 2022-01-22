import logging
import re
import subprocess
import sys
from os.path import expanduser
from pathlib import Path
from typing import List

from venv_management.driver import Driver
from venv_management.errors import CommandNotFound, ImplementationNotFound, PythonNotFound
from venv_management.utilities import sub_shell_command, get_status_output, shell_is_interactive, \
    remove_interactive_shell_warnings, parse_package_arg

logger = logging.getLogger(__name__)

DESTINATION_PATTERN = r"dest=([^,]+)"
DESTINATION_REGEX = re.compile(DESTINATION_PATTERN)

NO_SUCH_PYTHON_PATTERN = r"failed to find interpreter for Builtin discover of python_spec='([^']*)'"
NO_SUCH_PYTHON_REGEX = re.compile(NO_SUCH_PYTHON_PATTERN)

class VirtualEnvWrapperDriver(Driver):


    def _check_availability(self):
        try:
            self.list_virtual_envs()
        except CommandNotFound:
            raise ImplementationNotFound(f"No implementation for {self.name}")


    def list_virtual_envs(self) -> List[str]:
        """A list of virtualenv names.

        Returns:
            A list of string names in case-sensitive alphanumeric order.

        Raises:
            FileNotFoundError: If virtualenvwrapper.sh could not be located.
        """
        # Accommodate the fact that virtualenvwrapper is not disciplined about success/failure exit codes
        # https://bitbucket.org/virtualenvwrapper/virtualenvwrapper/issues/283/some-commands-give-non-zero-exit-codes
        lsvirtualenv_command = "lsvirtualenv -b"
        command = sub_shell_command(lsvirtualenv_command)
        logger.debug(command)
        success_statuses = {0, 1}
        status, output = get_status_output(command, success_statuses=success_statuses)
        if status in success_statuses:
            return output.splitlines(keepends=False)
        logger.error(output)
        if status == 127:
            raise CommandNotFound(output)
        raise RuntimeError(output)

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

            setuptools: If True, or 'latest' the latest pip will be installed. If False, setuptools
                will not be installed. If 'bundled', the bundled version will be installed. If a
                specific version string is given, that version will be installed.

            wheel: If True, or 'latest' the latest pip will be installed. If False, wheel will not
                be installed. If 'bundled', the bundled version will be installed. If a specific
                version string is given, that version will be installed.

        Returns:
            The Path to the root of the virtualenv, or None if the path could not be determined.

        Raises:
            PythonNotFound: If the requested Python version could not be found.
            RuntimeError: If the virtualenv could not be created.
        """
        project_path_arg = f"-a {project_path}" if project_path else ""
        packages_args = [f"-i {package}" for package in packages] if packages else []
        requirements_arg = f"-r{requirements_file}" if requirements_file else ""
        python_arg = f"--python={python}" if python else ""
        system_site_packages_arg = "--system-site-packages" if system_site_packages else ""
        pip_arg = parse_package_arg("pip", pip)
        setuptools_arg = parse_package_arg("setuptools", setuptools)
        wheel_arg = parse_package_arg("wheel", wheel)

        args = " ".join(
            (
                project_path_arg,
                *packages_args,
                requirements_arg,
                python_arg,
                system_site_packages_arg,
                pip_arg,
                setuptools_arg,
                wheel_arg,
            )
        )

        command = sub_shell_command(f"mkvirtualenv {name} {args}")
        logger.info(command)
        # Accommodate the fact that virtualenvwrapper is not disciplined about success/failure exit codes
        # https://bitbucket.org/virtualenvwrapper/virtualenvwrapper/issues/283/some-commands-give-non-zero-exit-codes
        success_statuses = {0, 1}
        status, output = get_status_output(command, success_statuses=success_statuses)
        if status not in success_statuses:
            raise RuntimeError(f"Could not run {command}")
        m = NO_SUCH_PYTHON_REGEX.search(output)
        if m is not None:
            raise PythonNotFound(f"Could not locate Python {python} ; {m.group(0)}")
        lines = output.splitlines(keepends=False)
        for line in lines:
            logger.debug("line = %s", line)
            m = DESTINATION_REGEX.search(line)
            if m is not None:
                dest = m.group(1)
                logger.debug("Found dest = %s", dest)
                return Path(dest)
        message = "Could not find dest for virtualenv {name!r}"
        logger.warning(message)
        raise RuntimeError(message)

    def remove_virtual_env(self, name):
        """Remove a virtual environment.

        Args:
            name: The name of the virtual environment to remove.

        Raises:
            ValueError: If there is no environment with the given name.
            RuntimeError: If the virtualenv could not be removed.
        """
        if not name:
            # When provided with an empty string, rmvirtualenv removes all virtual environments (!)
            # https://bitbucket.org/virtualenvwrapper/virtualenvwrapper/issues/346/rmvirtualenv-removes-all-virtualenvs
            raise ValueError("The name passed to remove_virtual_env cannot be empty")
        command = sub_shell_command(f"rmvirtualenv {name}")
        logger.debug("command = %r", command)
        process = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding=sys.getdefaultencoding()
        )
        # rmvirtualenv returns success (0) even when it fails because no such environment exists
        # https://bitbucket.org/virtualenvwrapper/virtualenvwrapper/issues/283/some-commands-give-non-zero-exit-codes
        # but it does return a message on stderr
        stderr = process.stderr
        if shell_is_interactive():
            stderr = remove_interactive_shell_warnings(stderr)
        if len(stderr) != 0:
            raise ValueError(stderr)

    def resolve_virtual_env(self, name: str) -> Path:
        if not name:
            raise ValueError("The name passed to resolve_virtual_env cannot be empty")
        if name not in self.list_virtual_envs():
            raise ValueError(f"No virtual environment called {name!r} to remove")
        command = sub_shell_command("echo ${WORKON_HOME}")
        logger.debug("command = %r", command)
        status, output = get_status_output(command)
        workon_home = Path(expanduser(output)) if len(output) > 0 else Path.home() / ".virtualenvs"
        return workon_home / name