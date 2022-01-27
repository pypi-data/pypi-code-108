"""Helper functions for paths manipulation."""
import os
import pathlib
import operator
from contextlib import contextmanager
import inspect


def get_cfp(real: bool = False, fdir: bool = False) -> str:
    """Return caller's current file path.

    Args:
        real: if True, return full path, otherwise relative path
            (default: {False})
        fdir: file's directory path will be returned instead
            (default: {False}).
    """
    frame = inspect.stack()[1]
    p = frame[0].f_code.co_filename
    if real:
        p = os.path.realpath(p)
    if fdir:
        p = os.path.dirname(p)
    return p


@contextmanager
def chdir_tmp(path: str) -> None:
    """Change current working directory temporarily."""
    oldpwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldpwd)


def get_ancestor(path: str, level=1):
    """Return ancestor path object by specified level."""
    path_obj = pathlib.Path(path)
    if not level:
        return path_obj
    path_to_parents = '.'.join(['parent' for i in range(level)])
    f = operator.attrgetter(path_to_parents)
    return f(path_obj)


def get_ancestor_name(path: str, level=1) -> str:
    """Return ancestor path name by specified level.

    >>> get_ancestor_name('a/b', level=0)
    'b'
    >>> get_ancestor_name('a/b.py', level=0)
    'b.py'
    >>> get_ancestor_name('a/b')
    'a'
    >>> get_ancestor_name('a/b/c.py', level=2)
    'a'
    >>> get_ancestor_name('a/b/c.py', level=3)
    ''
    """
    return get_ancestor(path, level=level).name


def get_parent_name(path: str) -> str:
    """Return parent path name.

    Deprecated: use get_ancestor_name.

    >>> get_parent_name('a/b')
    'a'
    >>> get_parent_name('a/b/c.py')
    'b'
    >>> get_parent_name('a')
    ''
    >>> get_parent_name('a.py')
    ''
    >>> get_parent_name('a/')
    ''
    >>> get_parent_name('')
    ''
    """
    return get_ancestor_name(path, level=1)
