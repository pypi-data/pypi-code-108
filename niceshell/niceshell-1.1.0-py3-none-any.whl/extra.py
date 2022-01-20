import regex as re

from .core import expose_tilde, quotes_wrapper, shell

__all__ = ["force_sudo_password_promt", "get_root_privileges",
           "get_root_privileges_or_exit", "has_root_privileges", "list_dirs",
           "list_files"]


def force_sudo_password_promt():
    '''Next shell commands with sudo will prompt a password.'''
    shell("sudo -K").wait()


def get_root_privileges():
    """
    Shows sudo password prompt. Returns True if correct password has been
    entered, otherwise returns False (e.g., Ctrl+C was pressed).
    """
    return not shell("sudo true").exit_code()


def get_root_privileges_or_exit(exit_code: int = 1):
    """
    If correct password has been entered then next shell commands with sudo
    won't prompt a password, otherwise exits program with exit_code.
    """
    get_root_privileges()
    if not has_root_privileges():
        exit(exit_code)


def has_root_privileges():
    '''Checks if sudo command can be executed without password prompt.'''
    return not shell("sudo -n true").exit_code()


def list_dirs(path: str = '.', with_errors=False):
    """
    Returns list of accessible directories that are located in path. Also
    stderr can be returned (e.g., check for accessibility of directories or
    path).

    Parameters:
        path (str): directory of needed subdirectories. Default is '.'.
        with_errors (bool): if True also returns stderr. Default is False.

    Raises:
        TypeError: if path's type isn't str.
        ValueError: if path doesn't exist or inaccessible.

    Returns:
        (List[str] | Tuple[List[str], str]): list of accessible directories
        (and stderr).
    """
    if not isinstance(path, str):
        raise TypeError("path's type must be str.")
    path = expose_tilde(quotes_wrapper(path))
    path = re.sub(r'(?<=[^\\])\*', '"*"', path)  # Expose wildcard (*)
    path = re.sub(r'\\\*', '*', path)  # Preserve '*'
    paths = shell(f"ls -d -- {path}").get_lines()
    if len(paths) != 1:
        raise ValueError("Invalid path.")
    path = paths[0]
    process = shell(Rf"ls -ALp {path} | grep / | sed 's|/$||'")
    dirs = process.get_lines()
    if with_errors:
        return (dirs, process.error_output())
    return dirs


def list_files(path: str = '.', with_errors=False):
    """
    Returns list of accessible files that are located in path. Also stderr can
    be returned (e.g., check for accessibility of files or path).

    Parameters:
        path (str): directory of needed files. Default is '.'.
        with_errors (bool): if True also returns stderr. Default is False.

    Raises:
        TypeError: if path's type isn't str.
        ValueError: if path doesn't exist or inaccessible.

    Returns:
        (List[str] | Tuple[List[str], str]): list of accessible files (and
        stderr).
    """
    if not isinstance(path, str):
        raise TypeError("path's type must be str.")
    path = expose_tilde(quotes_wrapper(path))
    path = re.sub(r'(?<=[^\\])\*', '"*"', path)  # Expose wildcard (*)
    path = re.sub(r'\\\*', '*', path)  # Preserve '*'
    paths = shell(f"ls -d -- {path}").get_lines()
    if len(paths) != 1:
        raise ValueError("Invalid path.")
    path = paths[0]
    process = shell(Rf"ls -ALp {path} | grep -v /")
    files = process.get_lines()
    if with_errors:
        return (files, process.error_output())
    return files
