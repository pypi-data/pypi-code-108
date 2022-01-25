import importlib
import itertools
import os
import sys
from errno import ENOENT, ENOTDIR, EBADF, ELOOP
from pathlib import Path
from types import ModuleType
from typing import Iterator
from typing import Optional
from typing import Union

# EBADF - guard against macOS `stat` throwing EBADF

# The following function, variables and comments were
# copied from cpython 3.9 Lib/pathlib.py file.

_IGNORED_ERRORS = (ENOENT, ENOTDIR, EBADF, ELOOP)

_IGNORED_WINERRORS = (
    21,  # ERROR_NOT_READY - drive exists but is not accessible
    1921,  # ERROR_CANT_RESOLVE_FILENAME - fix for broken symlink pointing to itself
)


def _ignore_error(exception):
    return (
            getattr(exception, "errno", None) in _IGNORED_ERRORS
            or getattr(exception, "winerror", None) in _IGNORED_WINERRORS
    )


def visit(
        path: str,
) -> Iterator["os.DirEntry[str]"]:
    """Walk a directory recursively, in breadth-first order.

    Entries at each directory level are sorted by name.
    """

    # Skip entries with symlink loops and other brokenness,
    # so the caller doesn't have to deal with it.
    entries = []

    for entry in os.scandir(path):
        try:
            entry.is_file()
        except OSError as err:
            if _ignore_error(err):
                continue
            raise
        entries.append(entry)

    entries.sort(key=lambda entry: entry.name)

    yield from entries

    for entry in entries:
        if entry.is_dir():
            yield from visit(entry.path)


class ImportMismatchError(ImportError):
    """
    Raised on import_from_path() if there is a mismatch of __file__'s.

    Raised when importing different filenames that has the same basename
    but its parent directory is not a package.Use package to reorg cases
    structure instead.for example:

    "/tests1/test_foo.py" and "/tests2/test_foo.py".
    """


def import_from_path(
        module_path: Union[str, "os.PathLike[str]"],
) -> ModuleType:
    """
    Import and return a module from the given module file.

    :raises ImportMismatchError:
        If after importing the given `path` and the module `__file__`
        are different. See ImportMismatchError for details.
    """

    path = Path(module_path)

    if not path.exists():
        raise ImportError(path)

    package_path = resolve_package_path(path)

    if package_path is None:
        # Do not allow same module in different dirs.
        package_root = path.parent
        module_name = path.stem
    else:

        package_root = package_path.parent
        names = list(path.with_suffix("").relative_to(package_root).parts)
        if names[-1] == "__init__":
            names.pop()
        module_name = ".".join(names)

    package_root = package_root.absolute()

    if str(package_root) != sys.path[0]:
        sys.path.insert(0, str(package_root))

    sys.path.insert(0, str(path.parent.absolute()))
    module = importlib.import_module(module_name)

    module_file = module.__file__
    try:
        is_same = os.path.samefile(str(module_path), module_file)
    except FileNotFoundError:
        is_same = False

    if not is_same:
        raise ImportMismatchError(module_name, module_file, path)

    sys.path.remove(sys.path[0])

    return module


def ensure_remove_module(module_name: str):
    """
    Ensure the module removed form sys.modules.
    Ignore the KeyError.
    """
    try:
        sys.modules.pop(module_name)
    except KeyError:
        pass


def resolve_package_path(path: Path) -> Optional[Path]:
    """
    Return the Python package path by looking for the last
    directory upwards which still contains an __init__.py.

    Returns None if the path is not in a package.
    """
    result = None
    file = (path,) if path.is_dir() else ()
    chain = itertools.chain(file, path.parents)

    def is_package(p: Path):
        return p.is_dir() and p.joinpath("__init__.py").is_file()

    for parent in itertools.takewhile(is_package, chain):
        result = parent

    return result


def name_package_from_path(path: Path, root: Path):
    path = path.with_suffix("")
    try:
        relative_path = path.relative_to(root)
    except ValueError:
        parts = path.parts[1:]
    else:
        parts = relative_path.parts

    return ".".join(parts)
