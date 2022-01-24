from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any, Union


def import_string(_import_string: str, root: Union[str, Path, None] = None) -> Any:
    """Import an object from a string"""
    import_from, import_name = _import_string.split(":")
    try:
        *import_path, import_filename = import_from.split(".")
        import_filepath = Path(*import_path, import_filename + ".py")
        if root:
            import_filepath = Path(root) / import_filepath
        if import_filepath.exists():
            sys.path.append(str(import_filepath.parent.resolve(True)))
            import_from = import_filename
    finally:
        module = importlib.import_module(import_from)
    return getattr(module, import_name)
