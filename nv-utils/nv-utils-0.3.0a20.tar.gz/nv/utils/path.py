from pathlib import Path
from typing import Iterator, Callable, Optional, Union, Collection


__ALL__ = ['iter_files', 'match_suffix']


def match_suffix(path: Path, suffix: Union[str, Collection[str]]) -> bool:
    return path.suffix == suffix if isinstance(suffix, str) else path.suffix in suffix


def iter_files(path: Path,
               recursive: bool = False,
               criteria: Optional[Callable[[Path], bool]] = None
               ) -> Iterator[Path]:
    """
    Iterate through files using pathlib.Path as a reference.
    :param path: pathlib.Path object (or anything that could be converted into, e.g. str)
    :param recursive: iterate through directories recursively
    :param criteria: callable that receives a Path as a single argument and returns True if file is to be included
    :return: iterator
    """
    path = Path(path)
    if not path.is_dir():
        raise NotADirectoryError(f"path must be a directory: {path!r}")

    for child in path.iterdir():
        if recursive and child.is_dir():
            yield from iter_files(child, recursive, criteria)
        elif child.is_file() and not criteria or (criteria and criteria(child)):
            yield child
