from .core import (
    expose_tilde,
    normalize_short_and_long_args,
    quotes_wrapper,
    shell,
    Shell,
    ShortArgsOption
)
from .extra import (
    force_sudo_password_promt,
    get_root_privileges,
    get_root_privileges_or_exit,
    has_root_privileges,
    list_dirs,
    list_files
)
from .gnu_coreutils import cd, cp, ln, ls, mv, rm

__all__ = ["cd", "cp", "expose_tilde", "force_sudo_password_promt",
           "get_root_privileges", "get_root_privileges_or_exit", "GID",
           "GROUP", "has_root_privileges", "HOME", "list_dirs", "list_files",
           "ln", "ls", "mv", "normalize_short_and_long_args", "quotes_wrapper",
           "rm", "shell", "Shell", "ShortArgsOption", "UID", "USER"]
__author__ = "Andrew Voynov"
__version__ = "1.1.0"

GID = Shell("id -g").output()[:-1]
GROUP = Shell("id -gn").output()[:-1]
HOME = Shell("printf ~").output()
UID = Shell("id -u").output()[:-1]
USER = Shell("id -un").output()[:-1]
