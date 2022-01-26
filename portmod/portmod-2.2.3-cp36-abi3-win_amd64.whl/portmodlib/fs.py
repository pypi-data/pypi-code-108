# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import os
import shutil
import stat
from functools import lru_cache
from shutil import copystat
from typing import Callable, Generator, List, Optional, Set, Tuple, Union

from portmodlib.portmod import _get_hash
from portmodlib.source import HashAlg

# 32MB buffer seems to give the best balance between performance on large files
# and on small files
HASH_BUF_SIZE = 32 * 1024 * 1024

try:
    DirEntryStr = os.DirEntry[str]
except TypeError:
    # Python 3.6 doesn't like subscripting os.DirEntry
    DirEntryStr = os.DirEntry  # type: ignore


def onerror(func, path, exc_info):
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.

    Usage : ``shutil.rmtree(path, onerror=onerror)``
    """
    if not os.access(path, os.W_OK):
        # Is the error an access error ?
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise  # pylint: disable=misplaced-bare-raise


def _move2(src: DirEntryStr, dest: str):
    if os.path.islink(src):
        return os.symlink(os.readlink(src), dest)
    return shutil.move(src.path, dest)


def _patch_file(
    src: os.DirEntry,
    dst: str,
    overwrite: bool = True,
    move_function: Callable[[os.DirEntry, str], None] = _move2,
):
    if os.path.exists(dst) and src.is_file():
        if overwrite:
            os.remove(dst)
        else:
            raise FileExistsError(f"File {dst} already exists")

    move_function(src, dst)


def _iter_files_to_patch(
    src: Union[str, DirEntryStr],
    dst: str,
    *,
    ignore: Callable[[str, List[str]], Set[str]] = None,
    case_sensitive: bool = True,
) -> Generator[Tuple[os.DirEntry, str], None, None]:
    with os.scandir(src) as itr:
        entries = list(itr)
    if ignore is not None:
        ignored_names = ignore(os.fspath(src), [x.name for x in entries])
    else:
        ignored_names = set()

    for entry in entries:
        if entry.name in ignored_names:
            continue
        if case_sensitive:
            dstname = os.path.join(dst, entry.name)
        else:
            dstname = ci_exists(os.path.join(dst, entry.name)) or os.path.join(
                dst, entry.name
            )

        if entry.is_symlink():
            yield (entry, dstname)
        elif entry.is_dir():
            yield from _iter_files_to_patch(
                entry,
                dstname,
                ignore=ignore,
                case_sensitive=case_sensitive,
            )
        else:
            yield (entry, dstname)


# Modified version of shutil.copytree from
# https://github.com/python/cpython
# Python software and documentation are licensed under the
# Python Software Foundation License Version 2
def patch_dir(
    src: Union[str, os.DirEntry],
    dst: str,
    *,
    overwrite: bool = True,
    ignore: Callable[[str, List[str]], Set[str]] = None,
    case_sensitive: bool = True,
    move_function: Callable[[os.DirEntry, str], None] = _move2,
) -> str:
    """
    Copies src ontop of dst

    args:
        src: Source directory to copy from
        dst: Destination directory to copy to
        overwrite: If true, overwrite existing files.
        ignore: A callable which, given a directory and its contents, should return
            a set of files to ignore
        case_sensitive: If False, treat file and directory names as case insensitive
        move_function: The function to use to transfer individual files.
            Default is shutil.move (modified to accept a DirEntry).
            The signature should match shutil.copy2.

    raises:
        FileExistsError

    returns:
        Returns dst
    """

    for src_file, dst_file in _iter_files_to_patch(
        src,
        dst,
        ignore=ignore,
        case_sensitive=case_sensitive,
    ):
        parent_dir = os.path.dirname(dst_file)
        if not os.path.isdir(parent_dir):
            os.makedirs(parent_dir)
            try:
                copystat(os.path.dirname(src_file.path), parent_dir)
            except OSError as why:
                if getattr(why, "winerror", None) is None:
                    raise why

        _patch_file(
            src_file,
            dst_file,
            overwrite=overwrite,
            move_function=move_function,
        )

    return dst


def ci_exists(path: str, *, prefix: Optional[str] = None) -> Optional[str]:
    """
    Checks if a path exists, ignoring case.

    If the path exists but is ambiguous the result is not guaranteed

    args:
        path: The path to check. This path must either be absolute, or be relative to the prefix
        prefix: A leading path to ignore. If path is relative, it is treated as relative to this directory
                If prefix is None, path is treated as relative to the current working directory.

                Case-insensitive checks will not be performed on the components of the prefix
    """
    if os.path.isabs(path) and os.path.exists(path):
        return path

    if os.path.isabs(path):
        partial_path = prefix or "/"
    else:
        partial_path = prefix or os.getcwd()
        if os.path.exists(os.path.join(partial_path, path)):
            return os.path.join(partial_path, path)

    if os.path.isabs(path):
        # Ignore leading empty component when splitting absolute paths
        components = os.path.normpath(path).split(os.sep)[1:]
    else:
        components = os.path.normpath(path).split(os.sep)

    for component in components:
        found = False
        # The entry that exists is not a directory, so it cannot have any contents
        if not os.path.isdir(partial_path):
            return None
        for entryname in os.listdir(partial_path):
            if entryname.lower() == component.lower():
                partial_path = os.path.join(partial_path, entryname)
                found = True
                break
        if not found:
            return None

    if os.path.exists(partial_path):
        return partial_path

    return None


def get_tree_size(path):
    """Return total size of files in given path and subdirs."""
    total = 0
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            total += get_tree_size(entry.path)
        else:
            total += entry.stat(follow_symlinks=False).st_size
    return total


@lru_cache(maxsize=None)
def get_hash(filename: str, funcs=(HashAlg.BLAKE3,)) -> List[str]:
    """Hashes the given file"""
    return _get_hash(filename, [func.value for func in funcs], HASH_BUF_SIZE)


def is_parent(path: str, prefix: str) -> bool:
    """
    Returns true if and only if prefix is a parent directory of path

    args:
        path: An absolute path
        prefix: An absolute path
    returns:
        True if and only if prefix is a parent directory of path
    """
    path = os.path.normpath(os.path.abspath(path))
    prefix = os.path.normpath(os.path.abspath(prefix))
    return (
        os.path.splitdrive(path)[0] == os.path.splitdrive(prefix)[0]
        and os.path.commonpath([path, prefix]) == prefix
    )


def make_unique_filename(path: str, *, case_insensitive: bool = False) -> str:
    numeric_component = 1
    new_name = os.path.basename(path)
    directory = os.path.dirname(path)

    while (case_insensitive and ci_exists(new_name, prefix=directory)) or (
        not case_insensitive and os.path.exists(os.path.join(directory, new_name))
    ):
        name, ext = os.path.splitext(os.path.basename(path))
        new_name = f"{name}.{numeric_component}{ext}"

    return os.path.join(directory, new_name)
