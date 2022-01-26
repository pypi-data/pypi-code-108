# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3
"""
Module building on behaviour from the builtin functools  module
"""

from functools import lru_cache, wraps
from typing import Any, Callable, Optional, TypeVar, cast

from .globals import prefix_name

F = TypeVar("F", bound=Callable[..., Any])


def prefix_aware_cache(func: F) -> F:
    """
    A variant of functools.lru_cache which treats the prefix as if it were an argument
    """

    @wraps(func)
    @lru_cache(maxsize=None)
    def inner(prefix: Optional[str], *args, **kwargs):
        return func(*args, **kwargs)

    @wraps(func)
    def prefix_wrapper(*args, **kwargs):
        return inner(prefix_name(), *args, **kwargs)

    prefix_wrapper.cache_clear = inner.cache_clear  # type: ignore
    return cast(F, prefix_wrapper)


_VFS_CACHE_FUNCS = []


def vfs_cache(func: F) -> F:
    """
    A variant of functools.lru_cache which treats the prefix as if it were an argument
    """
    global _VFS_CACHE_FUNCS

    @wraps(func)
    @prefix_aware_cache
    def inner(*args, **kwargs):
        return func(*args, **kwargs)

    _VFS_CACHE_FUNCS.append(inner)

    return cast(F, inner)


def clear_vfs_cache():
    for func in _VFS_CACHE_FUNCS:
        func.cache_clear()  # type: ignore
