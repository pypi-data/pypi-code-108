import itertools
import os
from pathlib import Path, PurePath, PurePosixPath
from typing import List, Union, Iterable

from aim_build.typedefs import PathList, PurePathList, StringList, T


def src_to_obj(files) -> StringList:
    return [x.stem + ".obj" for x in files]


def src_to_o(files) -> StringList:
    return [x.stem + ".o" for x in files]


def to_str(paths) -> StringList:
    return [str(x) for x in paths]


def to_paths(string_paths) -> PathList:
    return [Path(x) for x in string_paths]


def glob(glob_string, paths: PathList) -> List[PathList]:
    return [list(x.glob(glob_string)) for x in paths]


def flatten(list_of_lists: List[List[T]]) -> List[T]:
    return list(itertools.chain.from_iterable(list_of_lists))


def prefix(the_prefix, paths) -> StringList:
    return [the_prefix + str(x) for x in paths]


def postfix(the_postfix, paths) -> StringList:
    return [str(x) + the_postfix for x in paths]


def wrap_quotes(paths: Union[PurePathList, StringList, str]) -> StringList:
    if isinstance(paths, str):
        str_path = str(paths)
        return [f'"{str_path}"']

    str_paths = to_str(paths)
    return [f'"{x}"' for x in str_paths]


def suffix(the_suffix, paths) -> StringList:
    return [str(x) + the_suffix for x in paths]


def prepend_paths(base_path: PurePath, other_paths: Union[List[PurePath], StringList]):
    # Don't need to check if `the_path` is absolute. If it is, the the result of `base_path / the_path` is just the
    # `the_path`. So it does the right thing, even though you might not expect it.
    return [base_path / the_path for the_path in other_paths]


def resolve(paths: PathList):
    return [path.resolve() for path in paths]


def escape_path(word):
    return word.replace("$ ", "$$ ").replace(" ", "$ ").replace(":", "$:")


def relpath(src_path: PurePosixPath, dst_path: PurePosixPath):
    result = os.path.relpath(str(src_path), str(dst_path))
    result = result.replace("\\", "/")
    return PurePosixPath(result)


def relpaths(src_paths: Union[PurePosixPath, List[PurePosixPath]], dst_path: PurePosixPath) -> List[PurePosixPath]:
    if isinstance(src_paths, Iterable):
        return [relpath(src_path, dst_path) for src_path in src_paths]

    return [relpath(src_paths, dst_path)]


def to_path_root(build_path: PurePath) -> PurePath:
    rel_path = PurePosixPath()
    for _ in range(len(build_path.parents)):
        rel_path = rel_path / ".."
    return rel_path


def to_native_path(path: PurePath) -> Path:
    # Have to be careful when converting from posix to windows paths.
    # If you have a posix path object pointing to C:/some/path/somewhere and simply do:
    #   Path(posix_path)
    # Then the result will be C:some\path\somewhere - the \ after the C: drive is missing.
    # However the conversion works, if you convert to a string before constructing the native path object.
    return Path(str(path))


def to_pure_posix_path(path: PurePath) -> PurePosixPath:
    # This function handles some common errors when converting from Windows paths back to PurePosixPaths.
    return PurePosixPath(str(path).replace("\\", "/"))
