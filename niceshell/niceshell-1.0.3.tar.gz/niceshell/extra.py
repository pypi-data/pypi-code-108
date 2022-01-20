from .core import shell

__all__ = ["force_sudo_password_promt", "get_root_privileges",
           "get_root_privileges_or_exit", "has_root_privileges"]


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
