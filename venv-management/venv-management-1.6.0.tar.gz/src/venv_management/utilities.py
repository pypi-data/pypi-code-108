"""Utility functions.
"""

import os
import subprocess
import sys
import logging
from distutils.util import strtobool
from os.path import expandvars, expanduser
from pathlib import Path
from shutil import which
from typing import List, Tuple

logger = logging.getLogger(__name__)


def sub_shell_command(command, suppress_setup_output=True):
    """Build a command to run a given command in an interactive subshell.

    Args:
        command: The command for the subshell.
        suppress_setup_output: Suppress output from the environment setup command if True,
            (the default), otherwise capture it.

    Returns:
        A string which can be used with the subprocess module.

    Raises:
        ValueError: If the subshell command could not be determined.
    """
    preferred_shell_name = os.environ.get("SHELL", "bash")
    logger.debug("preferred_shell_name from $SHELL = %r", preferred_shell_name)
    shell_name = expandvars(os.environ.get("VENV_MANAGEMENT_SHELL", preferred_shell_name))
    logger.debug("shell_name = %r", shell_name)
    if "fish" in shell_name:
        logger.error("Support for fish not yet added")
        raise NotImplementedError("Support for fish not yet added")
        
    shell_filepath = which(shell_name)
    logger.debug("shell_filepath = %r", shell_filepath)
    if shell_filepath is None:
        raise RuntimeError(f"Could not determine the path to {shell_name}")
    shell_filepath = Path(shell_filepath)
    shell_filename = shell_filepath.name
    logger.debug("shell_filename = %r", shell_filename)
    rc_filename = f".{shell_filename}rc"
    logger.debug("rc_filename = %r", rc_filename)
    rc_filepath = Path.home() / rc_filename
    logger.debug("rc_filepath = %r", rc_filepath)
    interactive = shell_is_interactive()
    logger.debug("interactive = %s", interactive)
    commands = []
    use_setup = strtobool(expandvars(os.environ.get("VENV_MANAGEMENT_USE_SETUP", "yes")))
    setup_filepath_str = os.environ.get("VENV_MANAGEMENT_SETUP_FILEPATH", str(rc_filepath))
    setup_filepath = Path(expanduser(expandvars(setup_filepath_str)))
    if use_setup:
        redirection = " 1>/dev/null 2>&1" if suppress_setup_output else ""
        commands.append(f". {setup_filepath}{redirection}")
    if command:
        commands.append(command)

    logger.debug("setup_filepath = %s", setup_filepath)
    args = [
        str(shell_filepath),
        "-c",  # Run command
        *(["-i"] if interactive else []),
        " && ".join(commands),
    ]
    return args


def shell_is_interactive():
    """True if the shell has been set to interactive.

    Control the setting with the VENV_MANAGEMENT_INTERACTIVE_SHELL environment variable by
    setting it to 'yes' or 'no'.

    Returns:
        True if the shell is interactive, otherwise False.
    """
    return strtobool(expandvars(os.environ.get("VENV_MANAGEMENT_INTERACTIVE_SHELL", "no")))


def get_status_output(cmd: List[str], success_statuses=None) -> Tuple[int, str]:
    """    Return (status, output) of executing cmd in a shell.

    Args:
        cmd: A list of command arguments to be executed.
        success_statuses: A container of integer status codes which indicate success.

    Execute the string 'cmd' in a shell with 'check_output' and
    return a 2-tuple (status, output). Universal newlines mode is used,
    meaning that the result with be decoded to a string.

    A trailing newline is stripped from the output.
    The exit status for the command can be interpreted
    according to the rules for the function 'wait'.
    """
    if success_statuses is None:
        success_statuses = {0}
    logger.debug("command = %r", cmd)
    process = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding=sys.getdefaultencoding()
    )
    status = process.returncode
    stderr = process.stderr
    stdout = process.stdout
    if status in success_statuses:
        data = stdout
        if data[-1:] == '\n':
            data = data[:-1]
    else:
        data = (f"STATUS: {status} ; \n"
                f"STDOUT: {stdout} ; \n"
                f"STDERR: {stderr}"
        )
    logger.debug("status = %d", status)
    logger.debug("data = %s", data)
    return status, data


def has_interactive_warning(line: str):
    """Determine whether a line of text contains a warning emitted by a shell.

    The shell program itself (e.g. bash) can emit warnings under certain circumstances
    which clutter output; for example, when running a shell in interactive mode without
    a connected terminal. This predicate can identify lines of text containing such
    warnings.

    Args:
        line: A string which may contain a shell warning.

    Returns:
        True if the line contains a shell warning, otherwise False.
    """
    return (
            "cannot set terminal process group" in line
            or "Inappropriate ioctl for device" in line
            or "no job control in this shell" in line
    )


def remove_interactive_shell_warnings(lines: str) -> str:
    """Remove shell warnings from lines of text.

    The shell program itself (e.g. bash) can emit warnings under certain circumstances
    which clutter output; for example, when running a shell in interactive mode without
    a connected terminal. This predicate can identify lines of text containing such
    warnings.

    Args:
        lines: A string (possibly multiline) which may contain lines which have shell warnings.

    Returns:
        The argument string without any lines containing matching shell warnings.
    """
    lines = lines.splitlines(keepends=True)
    lines = [line for line in lines if not has_interactive_warning(line)]
    lines = "".join(lines)
    return lines


def compatible_versions(actual_version: str, required_version: str) -> bool:
    """Determine whether two versions are equal.

    Only the dot separated elements in common are taken into account, so
    actual "3.7.4" compared with "3.7" will return True.

    Args:
        actual_version: A dot separated version.
        required_version: A dot separated version.

    Returns:
        True if the actual_version is compatible with the required_version,
        otherwise False.
    """
    return all(
        actual == expected
        for actual, expected in zip(actual_version.split("."), required_version.split("."))
    )


def parse_package_arg(name, arg):
    """Make a command-line argument string specifing whether and which verison of a package to install.

    Args:
        name: The name of the package.
        arg: True if the package is required, False if the package is not required,
            or a string containing a version number if a specific version of the package
            is required.

    Returns:
        A string which can be used as an argument to the virtualenv command.
    """
    if arg == True:
        option = ""
    elif arg == False:
        option = f"--no-{name}"
    else:
        option = f"--{name}={arg}"
    return option
