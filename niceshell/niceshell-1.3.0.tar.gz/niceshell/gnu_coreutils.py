from os import chdir
from typing import Iterable, Union

import regex as re

from .core import *

__all__ = ["cd", "cp", "ln", "ls", "mv", "pwd", "rm"]


def cd(path: str = '',
       short_args: Union[str, Iterable[str]] = [],
       test=False) -> Union[Shell, str]:
    R"""
    Wrapper for cd command from GNU Core Utilities.
    Note: Path will be wrapped in quotes, but '~' will still work (will
    be expanded) as well as wildcard (*). To treat '*' as normal character put
    backslash before it. This function changes directory using os.chdir().

    Parameters:
        path (str): directory that needs to be a new cwd aka present/current
            working directory. Default is '' (aka $HOME).
        short_args (str | Iterable[str]): string or array of short arguments.
            Prefix-dash is ignored. Default is [] (no short arguments).
        test (bool): return command itself without its execution (for test
            purposes). Default is False.

    Raises:
        TypeError: path's type isn't str.

    Returns:
        (Shell | str): Shell object of executing command or the command itself.
    """
    if not isinstance(path, str):
        raise TypeError("path's type must be str.")
    if path:
        path = expose_tilde(quotes_wrapper(path))
        path = re.sub(r'(?<=[^\\])\*', '"*"', path)  # Expose wildcard (*)
        path = re.sub(r'\\\*', '*', path)  # Preserve '*'
    args = normalize_short_and_long_args(
        short_args, [], ShortArgsOption.APART)
    command = f"cd {args} -- {path}".strip()
    if test:
        return command
    else:
        process = Shell(command)
        if process.exit_code() == 0:
            # Necessary if wildcard is present in path
            process2 = Shell(command + '; echo "|$PWD|"')
            new_pwd = process2.output().split('|')[-2]
            chdir(new_pwd)
        return process


def cp(source_path: Union[str, Iterable[str]],
       destination_path: str,
       batch=False,
       sudo=False,
       short_args: Union[str, Iterable[str]] = [],
       long_args: Iterable[str] = [],
       test=False) -> Union[Shell, str]:
    """
    Wrapper for cp command from GNU Core Utilities.
    Note: destination_path is always wrapped in quotes. If source_path and/or
    destination_path are/is wrapped in quotes (batch=False), '~' will still
    work (will be expanded).

    Parameters:
        source_path (str | Iterable[str]): file(s) and/or directory(-ies) that
            is/are need to be copied.
        destination_path (str): destination directory for source files/dirs.
        batch (bool): wraps source_path in double quotes if False. Default is
            False.
        sudo (bool): adds sudo at the begining of cp command. Default is False.
        short_args (str | Iterable[str]): string or array of short arguments.
            Prefix-dash is ignored. Default is [] (no short arguments).
        long_args (Iterable[str]): array of long arguments. Prefix-dashes are
            ignored. Default is [] (no long arguments).
        test (bool): return command itself without its execution (for test
            purposes). Default is False.

    Raises:
        TypeError: source_path's type isn't (str | Iterable[str]) or
            destination_path's type isn't str.

    Returns:
        (Shell | str): Shell object of executing command or the command itself.
    """
    if (not isinstance(source_path, (str, Iterable)) or
        not all(isinstance(e, str) for e in source_path) or
            (not isinstance(source_path, str) and len(source_path) == 0)):
        raise TypeError("source_path's type must be str or Iterable[str].")
    if not isinstance(destination_path, str):
        raise TypeError("destination_path's type must be str.")
    if batch:
        # Concatenate anything but str (batch)
        if not isinstance(source_path, str):
            source_path = ' '.join(source_path)
    else:
        source_path = expose_tilde(quotes_wrapper(source_path))
    destination_path = expose_tilde(quotes_wrapper(destination_path))
    sudo = "sudo" if sudo else ''
    args = normalize_short_and_long_args(
        short_args, long_args, ShortArgsOption.APART)
    command = f"{sudo} cp {args} -- {source_path} {destination_path}".strip()
    if test:
        return command
    else:
        return Shell(command)


def ln(source_path: Union[str, Iterable[str]],
       destination_path: str,
       batch=False,
       sudo=False,
       short_args: Union[str, Iterable[str]] = [],
       long_args: Iterable[str] = [],
       test=False) -> Union[Shell, str]:
    """
    Wrapper for ln command from GNU Core Utilities.
    Note: destination_path is always wrapped in quotes. If source_path and/or
    destination_path are/is wrapped in quotes (batch=False), '~' will still
    work (will be expanded).

    Parameters:
        source_path (str | Iterable[str]): file(s) and/or directory(-ies) of
            which (sym)link(s) is/are need to be created.
        destination_path (str): destination directory for source files/dirs.
        batch (bool): wraps source_path in double quotes if False. Default is
            False.
        sudo (bool): adds sudo at the begining of ln command. Default is False.
        short_args (str | Iterable[str]): string or array of short arguments.
            Prefix-dash is ignored. Default is [] (no short arguments).
        long_args (Iterable[str]): array of long arguments. Prefix-dashes are
            ignored. Default is [] (no long arguments).
        test (bool): return command itself without its execution (for test
            purposes). Default is False.

    Raises:
        TypeError: source_path's type isn't (str | Iterable[str]) or
            destination_path's type isn't str.

    Returns:
        (Shell | str): Shell object of executing command or the command itself.
    """
    if (not isinstance(source_path, (str, Iterable)) or
        not all(isinstance(e, str) for e in source_path) or
            (not isinstance(source_path, str) and len(source_path) == 0)):
        raise TypeError("source_path's type must be str or Iterable[str].")
    if not isinstance(destination_path, str):
        raise TypeError("destination_path's type must be str.")
    if batch:
        # Concatenate anything but str (batch)
        if not isinstance(source_path, str):
            source_path = ' '.join(source_path)
    else:
        source_path = expose_tilde(quotes_wrapper(source_path))
    destination_path = expose_tilde(quotes_wrapper(destination_path))
    sudo = "sudo" if sudo else ''
    args = normalize_short_and_long_args(
        short_args, long_args, ShortArgsOption.APART)
    command = f"{sudo} ln {args} -- {source_path} {destination_path}".strip()
    if test:
        return command
    else:
        return Shell(command)


def ls(path: Union[str, Iterable[str]] = '',
       batch=False,
       sudo=False,
       short_args: Union[str, Iterable[str]] = [],
       long_args: Iterable[str] = [],
       test=False) -> Union[Shell, str]:
    """
    Wrapper for ls command from GNU Core Utilities.
    Note: If path is wrapped in quotes (batch=False), '~' will still work (will
    be expanded).

    Parameters:
        path (str | Iterable[str]): directory(-ies) of which content is need to
            be gathered. Default is '' (aka present/current working directory).
        batch (bool): wraps path in double quotes if False. Default is False.
        sudo (bool): adds sudo at the begining of ls command. Default is False.
        short_args (str | Iterable[str]): string or array of short arguments.
            Prefix-dash is ignored. Default is [] (no short arguments).
        long_args (Iterable[str]): array of long arguments. Prefix-dashes are
            ignored. Default is [] (no long arguments).
        test (bool): return command itself without its execution (for test
            purposes). Default is False.

    Raises:
        TypeError: path's type isn't (str | Iterable[str]).

    Returns:
        (Shell | str): Shell object of executing command or the command itself.
    """
    if (not isinstance(path, (str, Iterable)) or
            not all(isinstance(e, str) for e in path)):
        raise TypeError("path's type must be str or Iterable[str].")
    if list(path) in ([], ['']):  # Edge cases
        path = ''
    if batch:
        if not isinstance(path, str):  # Concatenate anything but str (batch)
            path = ' '.join(path)
    elif path != '':  # Don't wrap emptiness in double quotes
        path = expose_tilde(quotes_wrapper(path))
    sudo = "sudo" if sudo else ''
    args = normalize_short_and_long_args(
        short_args, long_args, ShortArgsOption.APART)
    command = f"{sudo} ls {args} -- {path}".strip()
    if test:
        return command
    else:
        return Shell(command)


def mv(source_path: Union[str, Iterable[str]],
       destination_path: str,
       batch=False,
       sudo=False,
       short_args: Union[str, Iterable[str]] = [],
       long_args: Iterable[str] = [],
       test=False) -> Union[Shell, str]:
    """
    Wrapper for mv command from GNU Core Utilities.
    Note: destination_path is always wrapped in quotes. If source_path and/or
    destination_path are/is wrapped in quotes (batch=False), '~' will still
    work (will be expanded).

    Parameters:
        source_path (str | Iterable[str]): file(s) and/or directory(-ies) that
            is/are need to be moved/renamed.
        destination_path (str): destination directory for source files/dirs.
        batch (bool): wraps source_path in double quotes if False. Default is
            False.
        sudo (bool): adds sudo at the begining of mv command. Default is False.
        short_args (str | Iterable[str]): string or array of short arguments.
            Prefix-dash is ignored. Default is [] (no short arguments).
        long_args (Iterable[str]): array of long arguments. Prefix-dashes are
            ignored. Default is [] (no long arguments).
        test (bool): return command itself without its execution (for test
            purposes). Default is False.

    Raises:
        TypeError: source_path's type isn't (str | Iterable[str]) or
            destination_path's type isn't str.

    Returns:
        (Shell | str): Shell object of executing command or the command itself.
    """
    if (not isinstance(source_path, (str, Iterable)) or
        not all(isinstance(e, str) for e in source_path) or
            (not isinstance(source_path, str) and len(source_path) == 0)):
        raise TypeError("source_path's type must be str or Iterable[str].")
    if not isinstance(destination_path, str):
        raise TypeError("destination_path's type must be str.")
    if batch:
        # Concatenate anything but str (batch)
        if not isinstance(source_path, str):
            source_path = ' '.join(source_path)
    else:
        source_path = expose_tilde(quotes_wrapper(source_path))
    destination_path = expose_tilde(quotes_wrapper(destination_path))
    sudo = "sudo" if sudo else ''
    args = normalize_short_and_long_args(
        short_args, long_args, ShortArgsOption.APART)
    command = f"{sudo} mv {args} -- {source_path} {destination_path}".strip()
    if test:
        return command
    else:
        return Shell(command)


def pwd(short_args: Union[str, Iterable[str]] = [],
        long_args: Iterable[str] = []) -> Union[str, Shell]:
    """
    Returns present/current working directory (str) if no parameters have been
    passed, otherwise returns Shell object.

    Parameters:
        short_args (str | Iterable[str]): string or array of short arguments.
            Prefix-dash is ignored. Default is [] (no short arguments).
        long_args (Iterable[str]): array of long arguments. Prefix-dashes are
            ignored. Default is [] (no long arguments).

    Returns:
        Union[str, Shell]: PWD string if called without parameters, otherwise
            Shell object.
    """
    args = normalize_short_and_long_args(
        short_args, long_args, ShortArgsOption.APART)
    process = Shell(f"pwd {args}".strip())
    if short_args == [] and long_args == []:
        return process.output()[:-1]
    return process


def rm(path: Union[str, Iterable[str]],
       batch=False,
       sudo=False,
       short_args: Union[str, Iterable[str]] = [],
       long_args: Iterable[str] = [],
       test=False) -> Union[Shell, str]:
    """
    Wrapper for rm command from GNU Core Utilities.
    Note: If path is wrapped in quotes (batch=False), '~' will still work (will
    be expanded).

        source_path (str | Iterable[str]): file(s) and/or directory(-ies) that
            is/are need to be removed.
    Parameters:
        path (str | Iterable[str]): file(s) and/or directory(-ies) that is/are
            need to be removed.
        batch (bool): wraps path in double quotes if False. Default is False.
        sudo (bool): adds sudo at the begining of rm command. Default is False.
        short_args (str | Iterable[str]): string or array of short arguments.
            Prefix-dash is ignored. Default is [] (no short arguments).
        long_args (Iterable[str]): array of long arguments. Prefix-dashes are
            ignored. Default is [] (no long arguments).
        test (bool): return command itself without its execution (for test
            purposes). Default is False.

    Raises:
        TypeError: path's type isn't (str | Iterable[str]).

    Returns:
        (Shell | str): Shell object of executing command or the command itself.
    """
    if (not isinstance(path, (str, Iterable)) or
        not all(isinstance(e, str) for e in path) or
            (not isinstance(path, str) and len(path) == 0)):
        raise TypeError("path's type must be str or Iterable[str].")
    if batch:
        # Concatenate anything but str (batch)
        if not isinstance(path, str):
            path = ' '.join(path)
    else:
        path = expose_tilde(quotes_wrapper(path))
    sudo = "sudo" if sudo else ''
    args = normalize_short_and_long_args(
        short_args, long_args, ShortArgsOption.APART)
    command = f"{sudo} rm {args} -- {path}".strip()
    if test:
        return command
    else:
        return Shell(command)
