from __future__ import annotations

from typing import TYPE_CHECKING
from pathlib import Path

if TYPE_CHECKING:
    from oarepo_model_builder.builder import ModelBuilder


def ensure_parent_modules(builder: ModelBuilder, path: Path,
                          *,
                          ends_at: str = None, max_depth=5):
    depth = 0
    path = path.parent
    # 1st sanity check - maximum depth, path must not be a UNC drive name
    while path and path.name and depth < max_depth:
        depth += 1
        # 2nd sanity check - the path must not contain .git
        if builder.filesystem.exists(path.joinpath('.git')):
            break

        init_py_path = path.joinpath('__init__.py')

        # get python output so that other can write into it if required
        # and there are no disk-level conflicts
        builder.get_output('python', init_py_path)

        if path.name == ends_at:
            break
        path = path.parent
