from pathlib import Path
from typing import Iterator

from .shared import Mapping

__all__ = [
    'search',
]


def search(root: Path, components: tuple[str, ...]) -> Iterator[tuple[Path, Mapping]]:
    if not components:
        if root.is_file():
            yield root, {}
        else:
            return
    if not root.is_dir():
        return
    current, *rest = components
    rest = tuple(rest)
    for path in root.iterdir():
        for file, mapping in search(path, rest):
            yield file, {
                key: (path.name,) + values if key == current else values
                for key, values in {**{current: ()}, **mapping}.items()
            }
