# -*- coding: utf-8 -*-
"""file-system utils"""
from itertools import chain
from os import (
    DirEntry,
    fspath as _fspath,
    makedirs,
    path,
    scandir as _scandir,
    sep,
    stat,
    utime,
    walk,
)
from pathlib import Path
from time import time

from xtyping import (
    Any,
    Callable,
    FsPath,
    Iterable,
    Iterator,
    List,
    Literal,
    Optional,
    Tuple,
    Union,
)

__all__ = (
    "dirpath_gen",
    "dirs_gen",
    "exists",
    "extension",
    "file_lines_gen",
    "file_size",
    "filecmp",
    "filepath_gen",
    "filepath_mtimedelta_sec",
    "files_dirs_gen",
    "files_gen",
    "fspath",
    "is_dir",
    "is_file",
    "is_link",
    "isdir",
    "isfile",
    "islink",
    "lbin",
    "lbytes",
    "lbytes_gen",
    "lstr",
    "lstring",
    "path_gen",
    "rbin",
    "rbin_gen",
    "rbytes",
    "rbytes_gen",
    "rstr",
    "rstring",
    "sbin",
    "sbytes",
    "scandir_list",
    "sep_join",
    "sep_lstrip",
    "sep_rstrip",
    "sep_split",
    "sep_strip",
    "shebang",
    "sstr",
    "sstring",
    "touch",
    "walk_gen",
    "wbin",
    "wbytes",
    "wstr",
    "wstring",
)


def fspath(fspath: FsPath) -> str:
    """Alias for os._fspath; returns fspath string for any type of path"""
    return _fspath(fspath)


def is_file(fspath: FsPath) -> bool:
    """Return True if the given path is a file; False otherwise"""
    return path.isfile(_fspath(fspath))


def is_dir(fspath: FsPath) -> bool:
    """Return True if the given path is a directory; False otherwise"""
    return path.isdir(_fspath(fspath))


def is_link(fspath: FsPath) -> bool:
    """Return True if the given path is a link; False otherwise"""
    return path.islink(_fspath(fspath))


def exists(fspath: FsPath) -> bool:
    """Return True if the given path exists; False otherwise"""
    return path.exists(_fspath(fspath))


isfile = is_file
isdir = is_dir
islink = is_link


def file_size(fspath: FsPath) -> int:
    """Return the size of the given file(path) in bytes

    Args:
        fspath (FsPath): Filepath as a string or pathlib.Path object

    Returns:
        int: size of the fspath in bytes

    """
    return stat(fspath).st_size


def scandir(dirpath: FsPath = ".") -> Iterable[DirEntry]:
    """Typed version of os.scandir"""
    return _scandir(fspath(dirpath))


def scandir_list(dirpath: FsPath = ".") -> List[DirEntry]:
    """Return a list of os.DirEntry objects

    Args:
        dirpath: Dirpath to scan

    Returns:
        List[DirEntry]: List of os.DirEntry objects

    """
    return list(_scandir(_fspath(dirpath)))


def filepath_mtimedelta_sec(filepath: FsPath) -> float:
    """Return the seconds since the file(path) was last modified"""
    return time() - path.getmtime(_fspath(filepath))


def touch(fspath: FsPath) -> None:
    """Create an empty file given a fspath

    Args:
        fspath (FsPath): File-system path for where to make an empty file

    """
    if not path.exists(str(fspath)):
        makedirs(path.dirname(str(fspath)), exist_ok=True)
        with open(fspath, "a"):
            utime(fspath, None)


def files_gen(
    dirpath: FsPath = ".",
    *,
    abspath: bool = True,
    topdown: bool = True,
    onerror: Optional[Callable[[OSError], Any]] = None,
    followlinks: bool = False,
) -> Iterator[str]:
    r"""Yield file-paths beneath a given dirpath (defaults to os.getcwd())

    Args:
        dirpath: Directory path to walk down/through.
        abspath (bool): Yield the absolute path
        onerror: Function called on OSError
        topdown: Not applicable
        followlinks: Follow links

    Returns:
        Generator object that yields file-paths (absolute or relative)

    Examples:
        >>> tmpdir = 'files_gen.doctest'
        >>> from os import makedirs; makedirs(tmpdir, exist_ok=True)
        >>> filepath_parts = [
        ...     ("dir", "file1.txt"),
        ...     ("dir", "file2.txt"),
        ...     ("dir", "file3.txt"),
        ...     ("dir", "dir2", "file1.txt"),
        ...     ("dir", "dir2", "file2.txt"),
        ...     ("dir", "dir2", "file3.txt"),
        ...     ("dir", "dir2a", "file1.txt"),
        ...     ("dir", "dir2a", "file2.txt"),
        ...     ("dir", "dir2a", "file3.txt"),
        ... ]
        >>> from shellfish.fs import touch
        >>> expected_files = []
        >>> for f in filepath_parts:
        ...     fspath = path.join(*f)
        ...     fspath = path.join(tmpdir, fspath)
        ...     dirpath = path.dirname(fspath)
        ...     expected_files.append(fspath)
        ...     makedirs(dirpath, exist_ok=True)
        ...     touch(fspath)
        >>> from pprint import pprint
        >>> expected_files = [el.replace('\\', '/') for el in expected_files]
        >>> pprint(expected_files)
        ['files_gen.doctest/dir/file1.txt',
         'files_gen.doctest/dir/file2.txt',
         'files_gen.doctest/dir/file3.txt',
         'files_gen.doctest/dir/dir2/file1.txt',
         'files_gen.doctest/dir/dir2/file2.txt',
         'files_gen.doctest/dir/dir2/file3.txt',
         'files_gen.doctest/dir/dir2a/file1.txt',
         'files_gen.doctest/dir/dir2a/file2.txt',
         'files_gen.doctest/dir/dir2a/file3.txt']
        >>> files_list = list(sorted(set(files_gen(tmpdir))))
        >>> files_list = [el.replace('\\', '/') for el in files_list]
        >>> pprint(files_list)
        ['files_gen.doctest/dir/dir2/file1.txt',
         'files_gen.doctest/dir/dir2/file2.txt',
         'files_gen.doctest/dir/dir2/file3.txt',
         'files_gen.doctest/dir/dir2a/file1.txt',
         'files_gen.doctest/dir/dir2a/file2.txt',
         'files_gen.doctest/dir/dir2a/file3.txt',
         'files_gen.doctest/dir/file1.txt',
         'files_gen.doctest/dir/file2.txt',
         'files_gen.doctest/dir/file3.txt']
        >>> pprint(list(sorted(set(expected_files))))
        ['files_gen.doctest/dir/dir2/file1.txt',
         'files_gen.doctest/dir/dir2/file2.txt',
         'files_gen.doctest/dir/dir2/file3.txt',
         'files_gen.doctest/dir/dir2a/file1.txt',
         'files_gen.doctest/dir/dir2a/file2.txt',
         'files_gen.doctest/dir/dir2a/file3.txt',
         'files_gen.doctest/dir/file1.txt',
         'files_gen.doctest/dir/file2.txt',
         'files_gen.doctest/dir/file3.txt']
        >>> list(sorted(set(files_list))) == list(sorted(set(expected_files)))
        True
        >>> from shutil import rmtree
        >>> rmtree(tmpdir)

    """
    dirpath = str(dirpath)
    return (
        filepath if abspath else str(filepath).replace(dirpath, "").strip(sep)
        for filepath in (
            path.join(pwd, filename)
            for pwd, dirs, files in walk(
                str(dirpath),
                topdown=topdown,
                onerror=onerror,
                followlinks=followlinks,
            )
            for filename in files
        )
    )


def dirs_gen(
    dirpath: FsPath = ".",
    *,
    abspath: bool = True,
    topdown: bool = True,
    onerror: Optional[Callable[[OSError], Any]] = None,
    followlinks: bool = False,
) -> Iterator[str]:
    r"""Yield directory-paths beneath a dirpath (defaults to os.getcwd())

    Args:
        dirpath: Directory path to walk down/through.
        abspath (bool): Yield the absolute path
        onerror: Function called on OSError
        topdown: Not applicable
        followlinks: Follow links

    Returns:
        Generator object that yields directory paths (absolute or relative)

    Examples:
        >>> tmpdir = 'dirs_gen.doctest'
        >>> from os import makedirs; makedirs(tmpdir, exist_ok=True)
        >>> filepath_parts = [
        ...     ("dir", "file1.txt"),
        ...     ("dir", "file2.txt"),
        ...     ("dir", "file3.txt"),
        ...     ("dir", "dir2", "file1.txt"),
        ...     ("dir", "dir2", "file2.txt"),
        ...     ("dir", "dir2", "file3.txt"),
        ...     ("dir", "dir2a", "file1.txt"),
        ...     ("dir", "dir2a", "file2.txt"),
        ...     ("dir", "dir2a", "file3.txt"),
        ... ]
        >>> from shellfish.fs import touch
        >>> expected_dirs = []
        >>> expected_files = []
        >>> for f in filepath_parts:
        ...     fspath = path.join(*f)
        ...     fspath = path.join(tmpdir, fspath)
        ...     dirpath = path.dirname(fspath)
        ...     expected_files.append(fspath)
        ...     expected_dirs.append(dirpath)
        ...     makedirs(dirpath, exist_ok=True)
        ...     touch(fspath)
        >>> expected_dirs = list(sorted(set(expected_dirs)))
        >>> from pprint import pprint
        >>> expected_files = [el.replace('\\', '/') for el in expected_files]
        >>> pprint(expected_files)
        ['dirs_gen.doctest/dir/file1.txt',
         'dirs_gen.doctest/dir/file2.txt',
         'dirs_gen.doctest/dir/file3.txt',
         'dirs_gen.doctest/dir/dir2/file1.txt',
         'dirs_gen.doctest/dir/dir2/file2.txt',
         'dirs_gen.doctest/dir/dir2/file3.txt',
         'dirs_gen.doctest/dir/dir2a/file1.txt',
         'dirs_gen.doctest/dir/dir2a/file2.txt',
         'dirs_gen.doctest/dir/dir2a/file3.txt']
        >>> expected_dirs = [el.replace('\\', '/') for el in expected_dirs]
        >>> pprint(expected_dirs)
        ['dirs_gen.doctest/dir',
         'dirs_gen.doctest/dir/dir2',
         'dirs_gen.doctest/dir/dir2a']
        >>> _files = list(files_gen(tmpdir))
        >>> _dirs = list(dirs_gen(tmpdir))
        >>> files_n_dirs_list = list(sorted(set(_files + _dirs)))
        >>> files_n_dirs_list = [el.replace('\\', '/') for el in files_n_dirs_list]
        >>> pprint(files_n_dirs_list)
        ['dirs_gen.doctest',
         'dirs_gen.doctest/dir',
         'dirs_gen.doctest/dir/dir2',
         'dirs_gen.doctest/dir/dir2/file1.txt',
         'dirs_gen.doctest/dir/dir2/file2.txt',
         'dirs_gen.doctest/dir/dir2/file3.txt',
         'dirs_gen.doctest/dir/dir2a',
         'dirs_gen.doctest/dir/dir2a/file1.txt',
         'dirs_gen.doctest/dir/dir2a/file2.txt',
         'dirs_gen.doctest/dir/dir2a/file3.txt',
         'dirs_gen.doctest/dir/file1.txt',
         'dirs_gen.doctest/dir/file2.txt',
         'dirs_gen.doctest/dir/file3.txt']
        >>> expected = sorted(set(expected_files + expected_dirs + [tmpdir]))
        >>> expected = [el.replace('\\', '/') for el in expected]
        >>> pprint(expected)
        ['dirs_gen.doctest',
         'dirs_gen.doctest/dir',
         'dirs_gen.doctest/dir/dir2',
         'dirs_gen.doctest/dir/dir2/file1.txt',
         'dirs_gen.doctest/dir/dir2/file2.txt',
         'dirs_gen.doctest/dir/dir2/file3.txt',
         'dirs_gen.doctest/dir/dir2a',
         'dirs_gen.doctest/dir/dir2a/file1.txt',
         'dirs_gen.doctest/dir/dir2a/file2.txt',
         'dirs_gen.doctest/dir/dir2a/file3.txt',
         'dirs_gen.doctest/dir/file1.txt',
         'dirs_gen.doctest/dir/file2.txt',
         'dirs_gen.doctest/dir/file3.txt']
        >>> files_n_dirs_list == expected
        True
        >>> from shutil import rmtree
        >>> rmtree(tmpdir)

    """
    return (
        dirpath if abspath else str(dirpath).replace(dirpath, "").strip(sep)
        for dirpath in (
            pwd
            for pwd, dirs, files in walk(
                str(dirpath),
                onerror=onerror,
                topdown=topdown,
                followlinks=followlinks,
            )
        )
    )


def files_dirs_gen(
    dirpath: FsPath = ".",
    *,
    abspath: bool = True,
    topdown: bool = True,
    onerror: Optional[Callable[[OSError], Any]] = None,
    followlinks: bool = False,
) -> Tuple[Iterator[str], Iterator[str]]:
    r"""Return a files_gen() and a dirs_gen() in one swell-foop

    Args:
        dirpath: Directory path to walk down/through.
        abspath (bool): Yield the absolute path
        onerror: Function called on OSError
        topdown: Not applicable
        followlinks: Follow links

    Returns:
        A tuple of two generators (files_gen(), dirs_gen())


    Examples:
        >>> tmpdir = 'files_dirs_gen.doctest'
        >>> from os import makedirs; makedirs(tmpdir, exist_ok=True)
        >>> filepath_parts = [
        ...     ("dir", "file1.txt"),
        ...     ("dir", "file2.txt"),
        ...     ("dir", "file3.txt"),
        ...     ("dir", "dir2", "file1.txt"),
        ...     ("dir", "dir2", "file2.txt"),
        ...     ("dir", "dir2", "file3.txt"),
        ...     ("dir", "dir2a", "file1.txt"),
        ...     ("dir", "dir2a", "file2.txt"),
        ...     ("dir", "dir2a", "file3.txt"),
        ... ]
        >>> from shellfish.fs import touch
        >>> expected_dirs = []
        >>> expected_files = []
        >>> for f in filepath_parts:
        ...     fspath = path.join(*f)
        ...     fspath = path.join(tmpdir, fspath)
        ...     dirpath = path.dirname(fspath)
        ...     expected_files.append(fspath)
        ...     expected_dirs.append(dirpath)
        ...     makedirs(dirpath, exist_ok=True)
        ...     touch(fspath)
        >>> expected_dirs = list(sorted(set(expected_dirs)))
        >>> from pprint import pprint
        >>> expected_files = [el.replace('\\', '/') for el in expected_files]
        >>> pprint(expected_files)
        ['files_dirs_gen.doctest/dir/file1.txt',
         'files_dirs_gen.doctest/dir/file2.txt',
         'files_dirs_gen.doctest/dir/file3.txt',
         'files_dirs_gen.doctest/dir/dir2/file1.txt',
         'files_dirs_gen.doctest/dir/dir2/file2.txt',
         'files_dirs_gen.doctest/dir/dir2/file3.txt',
         'files_dirs_gen.doctest/dir/dir2a/file1.txt',
         'files_dirs_gen.doctest/dir/dir2a/file2.txt',
         'files_dirs_gen.doctest/dir/dir2a/file3.txt']
        >>> expected_dirs = [el.replace('\\', '/') for el in expected_dirs]
        >>> pprint(expected_dirs)
        ['files_dirs_gen.doctest/dir',
         'files_dirs_gen.doctest/dir/dir2',
         'files_dirs_gen.doctest/dir/dir2a']
        >>> _files, _dirs = files_dirs_gen(tmpdir)
        >>> _files = list(_files)
        >>> _dirs = list(_dirs)
        >>> files_n_dirs_list = list(sorted(set(_files + _dirs)))
        >>> files_n_dirs_list = [el.replace('\\', '/') for el in files_n_dirs_list]
        >>> pprint(files_n_dirs_list)
        ['files_dirs_gen.doctest',
         'files_dirs_gen.doctest/dir',
         'files_dirs_gen.doctest/dir/dir2',
         'files_dirs_gen.doctest/dir/dir2/file1.txt',
         'files_dirs_gen.doctest/dir/dir2/file2.txt',
         'files_dirs_gen.doctest/dir/dir2/file3.txt',
         'files_dirs_gen.doctest/dir/dir2a',
         'files_dirs_gen.doctest/dir/dir2a/file1.txt',
         'files_dirs_gen.doctest/dir/dir2a/file2.txt',
         'files_dirs_gen.doctest/dir/dir2a/file3.txt',
         'files_dirs_gen.doctest/dir/file1.txt',
         'files_dirs_gen.doctest/dir/file2.txt',
         'files_dirs_gen.doctest/dir/file3.txt']
        >>> expected = sorted(set(expected_files + expected_dirs + [tmpdir]))
        >>> expected = [el.replace('\\', '/') for el in expected]
        >>> pprint(expected)
        ['files_dirs_gen.doctest',
         'files_dirs_gen.doctest/dir',
         'files_dirs_gen.doctest/dir/dir2',
         'files_dirs_gen.doctest/dir/dir2/file1.txt',
         'files_dirs_gen.doctest/dir/dir2/file2.txt',
         'files_dirs_gen.doctest/dir/dir2/file3.txt',
         'files_dirs_gen.doctest/dir/dir2a',
         'files_dirs_gen.doctest/dir/dir2a/file1.txt',
         'files_dirs_gen.doctest/dir/dir2a/file2.txt',
         'files_dirs_gen.doctest/dir/dir2a/file3.txt',
         'files_dirs_gen.doctest/dir/file1.txt',
         'files_dirs_gen.doctest/dir/file2.txt',
         'files_dirs_gen.doctest/dir/file3.txt']
        >>> files_n_dirs_list == expected
        True
        >>> from shutil import rmtree
        >>> rmtree(tmpdir)

    """
    return files_gen(
        dirpath,
        abspath=abspath,
        followlinks=followlinks,
        onerror=onerror,
        topdown=topdown,
    ), dirs_gen(
        dirpath,
        abspath=abspath,
        followlinks=followlinks,
        onerror=onerror,
        topdown=topdown,
    )


def walk_gen(
    dirpath: FsPath = ".",
    *,
    abspath: bool = True,
    topdown: bool = True,
    onerror: Optional[Callable[[OSError], Any]] = None,
    followlinks: bool = False,
) -> Iterator[str]:
    r"""Yield all paths beneath a given dirpath (defaults to os.getcwd())

    Args:
        dirpath: Directory path to walk down/through.
        abspath (bool): Yield the absolute path
        onerror: Function called on OSError
        topdown: Not applicable
        followlinks: Follow links

    Returns:
        Generator object that yields directory paths (absolute or relative)

    Examples:
        >>> tmpdir = 'walk_gen.doctest'
        >>> from os import makedirs; makedirs(tmpdir, exist_ok=True)
        >>> filepath_parts = [
        ...     ("dir", "file1.txt"),
        ...     ("dir", "file2.txt"),
        ...     ("dir", "file3.txt"),
        ...     ("dir", "dir2", "file1.txt"),
        ...     ("dir", "dir2", "file2.txt"),
        ...     ("dir", "dir2", "file3.txt"),
        ...     ("dir", "dir2a", "file1.txt"),
        ...     ("dir", "dir2a", "file2.txt"),
        ...     ("dir", "dir2a", "file3.txt"),
        ... ]
        >>> from shellfish.fs import touch
        >>> expected_dirs = []
        >>> expected_files = []
        >>> for f in filepath_parts:
        ...     fspath = path.join(*f).replace('\\', '/')
        ...     fspath = path.join(tmpdir, fspath).replace('\\', '/')
        ...     dirpath = path.dirname(fspath)
        ...     expected_files.append(fspath)
        ...     expected_dirs.append(dirpath)
        ...     makedirs(dirpath, exist_ok=True)
        ...     touch(fspath)
        >>> expected_dirs = [el.replace('\\', '/') for el in sorted(set(expected_dirs))]
        >>> from pprint import pprint
        >>> pprint(expected_files)
        ['walk_gen.doctest/dir/file1.txt',
         'walk_gen.doctest/dir/file2.txt',
         'walk_gen.doctest/dir/file3.txt',
         'walk_gen.doctest/dir/dir2/file1.txt',
         'walk_gen.doctest/dir/dir2/file2.txt',
         'walk_gen.doctest/dir/dir2/file3.txt',
         'walk_gen.doctest/dir/dir2a/file1.txt',
         'walk_gen.doctest/dir/dir2a/file2.txt',
         'walk_gen.doctest/dir/dir2a/file3.txt']
        >>> pprint(expected_dirs)
        ['walk_gen.doctest/dir',
         'walk_gen.doctest/dir/dir2',
         'walk_gen.doctest/dir/dir2a']
        >>> walk_gen_list = list(sorted(set(walk_gen(tmpdir))))
        >>> walk_gen_list = [el.replace('\\', '/') for el in walk_gen_list]
        >>> pprint(walk_gen_list)
        ['walk_gen.doctest',
         'walk_gen.doctest/dir',
         'walk_gen.doctest/dir/dir2',
         'walk_gen.doctest/dir/dir2/file1.txt',
         'walk_gen.doctest/dir/dir2/file2.txt',
         'walk_gen.doctest/dir/dir2/file3.txt',
         'walk_gen.doctest/dir/dir2a',
         'walk_gen.doctest/dir/dir2a/file1.txt',
         'walk_gen.doctest/dir/dir2a/file2.txt',
         'walk_gen.doctest/dir/dir2a/file3.txt',
         'walk_gen.doctest/dir/file1.txt',
         'walk_gen.doctest/dir/file2.txt',
         'walk_gen.doctest/dir/file3.txt']
        >>> expected = sorted(set(expected_files + expected_dirs + [tmpdir]))
        >>> pprint(expected)
        ['walk_gen.doctest',
         'walk_gen.doctest/dir',
         'walk_gen.doctest/dir/dir2',
         'walk_gen.doctest/dir/dir2/file1.txt',
         'walk_gen.doctest/dir/dir2/file2.txt',
         'walk_gen.doctest/dir/dir2/file3.txt',
         'walk_gen.doctest/dir/dir2a',
         'walk_gen.doctest/dir/dir2a/file1.txt',
         'walk_gen.doctest/dir/dir2a/file2.txt',
         'walk_gen.doctest/dir/dir2a/file3.txt',
         'walk_gen.doctest/dir/file1.txt',
         'walk_gen.doctest/dir/file2.txt',
         'walk_gen.doctest/dir/file3.txt']
        >>> walk_gen_list == expected
        True
        >>> from shutil import rmtree
        >>> rmtree(tmpdir)

    """
    dirpath = str(dirpath)
    return (
        str(path_string)
        if abspath
        else str(path_string).replace(dirpath, "").strip(sep)
        for path_string in chain.from_iterable(
            (
                pwd,
                *(path.join(pwd, _dir) for _dir in dirs),
                *(path.join(pwd, _file) for _file in files),
            )
            for pwd, dirs, files in walk(
                dirpath,
                topdown=topdown,
                followlinks=followlinks,
                onerror=onerror,
            )
        )
    )


def filepath_gen(
    dirpath: FsPath = ".",
    *,
    abspath: bool = False,
    topdown: bool = True,
    onerror: Optional[Callable[[OSError], Any]] = None,
    followlinks: bool = False,
) -> Iterator[Path]:
    r"""Yield all filepaths as pathlib.Path objects beneath a dirpath"""
    return (
        Path(el)
        for el in files_gen(
            dirpath=dirpath,
            abspath=abspath,
            topdown=topdown,
            onerror=onerror,
            followlinks=followlinks,
        )
    )


def dirpath_gen(
    dirpath: FsPath = ".",
    *,
    abspath: bool = False,
    topdown: bool = True,
    onerror: Optional[Callable[[OSError], Any]] = None,
    followlinks: bool = False,
) -> Iterator[Path]:
    r"""Yield all dirpaths as pathlib.Path objects beneath a dirpath"""
    return (
        Path(el)
        for el in dirs_gen(
            dirpath=dirpath,
            abspath=abspath,
            topdown=topdown,
            onerror=onerror,
            followlinks=followlinks,
        )
    )


def path_gen(
    dirpath: FsPath = ".",
    *,
    abspath: bool = False,
    topdown: bool = True,
    onerror: Optional[Callable[[OSError], Any]] = None,
    followlinks: bool = False,
) -> Iterator[Path]:
    r"""Yield all filepaths as pathlib.Path objects beneath a dirpath"""
    return (
        Path(el)
        for el in walk_gen(
            dirpath=dirpath,
            abspath=abspath,
            topdown=topdown,
            onerror=onerror,
            followlinks=followlinks,
        )
    )


def wbytes(
    filepath: FsPath,
    bites: bytes,
    *,
    append: bool = False,
) -> int:
    """Write/Save bytes to a fspath

    The parameter 'bites' is used instead of 'bytes' to not redefine the
    built-in python bytes object.

    Args:
        filepath: fspath to write to
        bites: Bytes to be written
        append (bool): Append to the file if True, overwrite otherwise; default
            is False

    Returns:
        int: Number of bytes written

    Examples:
        >>> from shellfish.fs import rbytes, wbytes
        >>> fspath = "wbytes.doctest.txt"
        >>> bites_to_save = b"These are some bytes"
        >>> bites_to_save  # they are bytes!
        b'These are some bytes'
        >>> wbytes(fspath, bites_to_save)
        20
        >>> rbytes(fspath)
        b'These are some bytes'
        >>> import os; os.remove(fspath)

    """
    _write_mode = "ab" if append else "wb"
    with open(filepath, _write_mode) as fd:
        nbytes = fd.write(bites)
    return nbytes


def rbytes(filepath: FsPath) -> bytes:
    """Load/Read bytes from a fspath

    Args:
        filepath: fspath read as bytes

    Returns:
        bytes from the fspath

    Examples:
        >>> from shellfish.fs import rbytes, wbytes
        >>> fspath = "rbytes.doctest.txt"
        >>> bites_to_save = b"These are some bytes"
        >>> wbytes(fspath, bites_to_save)
        20
        >>> bites_to_save  # they are bytes!
        b'These are some bytes'
        >>> rbytes(fspath)
        b'These are some bytes'
        >>> import os; os.remove(fspath)

    """
    with open(filepath, "rb") as file:
        return bytes(file.read())


def file_lines_gen(filepath: FsPath, keepends: bool = True) -> Iterable[str]:
    r"""Yield lines from a given fspath

    Args:
        filepath: File to yield lines from
        keepends: Flag to keep the ends of the file lines

    Yields:
        Lines from the given fspath

    Examples:
        >>> string = '\n'.join(str(i) for i in range(1, 10))
        >>> string
        '1\n2\n3\n4\n5\n6\n7\n8\n9'
        >>> fspath = "file_lines_gen.doctest.txt"
        >>> from shellfish.fs import wstring
        >>> wstring(fspath, string)
        17
        >>> for file_line in file_lines_gen(fspath):
        ...     file_line
        '1\n'
        '2\n'
        '3\n'
        '4\n'
        '5\n'
        '6\n'
        '7\n'
        '8\n'
        '9'
        >>> for file_line in file_lines_gen(fspath, keepends=False):
        ...     file_line
        '1'
        '2'
        '3'
        '4'
        '5'
        '6'
        '7'
        '8'
        '9'
        >>> import os; os.remove(fspath)


    """
    with open(filepath) as f:
        if keepends:
            yield from (line for line in f)
        else:
            yield from (line.rstrip("\n").rstrip("\r\n") for line in f)


def rbytes_gen(filepath: FsPath, blocksize: int = 65536) -> Iterable[bytes]:
    """Yield bytes from a given fspath"""
    with open(filepath, "rb") as f:
        while True:
            data = f.read(blocksize)
            if not data:
                break
            yield data


def wbytes_gen(
    filepath: FsPath,
    bytes_gen: Iterable[bytes],
    append: bool = False,
) -> int:
    """Write/Save bytes to a fspath

    Args:
        filepath: fspath to write to
        bytes_gen: Bytes to be written
        append (bool): Append to the file if True, overwrite otherwise; default
            is False

    Returns:
        int: Number of bytes written

    Examples:
        >>> from shellfish.fs import rbytes, wbytes
        >>> fspath = "wbytes_gen.doctest.txt"
        >>> bites_to_save = (b"These are some bytes... ", b"more bytes!")
        >>> bites_to_save  # they are bytes!
        (b'These are some bytes... ', b'more bytes!')
        >>> wbytes_gen(fspath, (b for b in bites_to_save))
        35
        >>> rbytes(fspath)
        b'These are some bytes... more bytes!'
        >>> import os; os.remove(fspath)

    """
    _mode: Literal["ab", "wb"] = "ab" if append else "wb"
    with open(filepath, mode=_mode) as fd:
        nbytes_written = sum(fd.write(chunk) for chunk in bytes_gen)
    return nbytes_written


def rstring(filepath: FsPath) -> str:
    r"""Load/Read a string given a fspath

    Args:
        filepath: Filepath for file to read

    Returns:
        str: String read from given fspath

    Examples:
        ``` python
        >>> from shellfish.fs import rstring, wstring
        >>> fspath = "lstring.doctest.txt"
        >>> sstring(fspath, r'Check out this string')
        21
        >>> lstring(fspath)
        'Check out this string'
        >>> import os; os.remove(fspath)

        ```

    """
    _bytes = rbytes(filepath=filepath)
    try:
        return _bytes.decode(encoding="utf-8")
    except UnicodeDecodeError:  # Catch the unicode decode error
        pass
    return _bytes.decode(encoding="latin2")


def wstring(
    filepath: FsPath,
    string: str,
    *,
    encoding: str = "utf-8",
    append: bool = False,
) -> int:
    """Save/Write a string to fspath

    Args:
        filepath: fspath to write to
        string (str): string to be written
        encoding: String encoding to write file with
        append (bool): Flag to append to file; default = False

    Returns:
        None

    Examples:
        >>> from shellfish.fs import rstring, wstring
        >>> fspath = "sstring.doctest.txt"
        >>> wstring(fspath, r'Check out this string')
        21
        >>> rstring(fspath)
        'Check out this string'
        >>> import os; os.remove(fspath)

    """
    return wbytes(
        filepath=filepath,
        bites=string.encode(encoding),
        append=append,
    )


def extension(fspath: str) -> str:
    """Return the extension for a fspath"""
    return "".join(Path(fspath).suffixes).lstrip(".")


def sep_split(fspath: FsPath) -> Tuple[str, ...]:
    """Split a string on the current platform os.path.sep value"""
    return tuple((el for el in str(fspath).split(sep) if el != sep and el != ""))


def sep_join(path_strings: Iterator[str]) -> str:
    """Join iterable of strings on the current platform os.path.sep value"""
    return sep.join(path_strings)


def sep_strip(fspath: FsPath) -> str:
    """Strip a string of the current platform's os.path.sep value"""
    return str(fspath).strip(sep)


def sep_lstrip(fspath: FsPath) -> str:
    """Left-strip a string of the current platform's os.path.sep value"""
    return str(fspath).lstrip(sep)


def sep_rstrip(fspath: FsPath) -> str:
    """Right-strip a string of the current platform's os.path.sep value"""
    return str(fspath).rstrip(sep)


def filecmp(
    left: FsPath,
    right: FsPath,
    *,
    shallow: bool = True,
    blocksize: int = 65536,
) -> bool:
    """Compare 2 files for equality given their filepaths

    Args:
        left (FsPath): Filepath 1
        right (FsPath): Filepath 2
        shallow (bool): Check only size and modification time if True
        blocksize (int): Chunk size to read files

    Returns:
        True if files are equal, False otherwise

    """
    left_stat = stat(left)
    right_stat = stat(right)
    if (
        shallow
        and left_stat.st_size == right_stat.st_size
        and left_stat.st_mtime == right_stat.st_mtime
    ):
        return True
    if left_stat.st_size != right_stat.st_size:
        return False
    return not any(
        left_chunk != right_chunk
        for left_chunk, right_chunk in zip(
            rbytes_gen(left, blocksize=blocksize),
            rbytes_gen(right, blocksize=blocksize),
        )
    )


def shebang(fspath: FsPath) -> Union[None, str]:
    r"""Get the shebang string given a fspath; Returns None if no shebang

    Args:
        fspath (fspath): Path to file that might have a shebang

    Returns:
        Optional[str]: The shebang string if it exists, None otherwise

    Examples:
        >>> from inspect import getabsfile
        >>> script = 'ashellscript.sh'
        >>> with open(script, 'w') as f:
        ...     f.write('#!/bin/bash\necho "howdy"\n')
        25
        >>> shebang(script)
        '#!/bin/bash'
        >>> from os import remove
        >>> remove(script)

    """
    with open(fspath, "r") as f:
        first = f.readline().replace("\r\n", "\n").strip("\n")
        return first if "#!" in first[:2] else None


# IO function aliases
lbytes = rbin = lbin = rbytes
sbytes = wbin = sbin = wbytes
lstring = rstr = lstr = rstring
sstring = wstr = sstr = wstring
lbytes_gen = rbin_gen = rbytes_gen
sbytes_gen = wbin_gen = wbytes_gen


if __name__ == "__main__":
    from doctest import testmod

    testmod()
