"""The catch-all module for the tests.data package."""

from pathlib import Path
from typing import List, cast

from pytest import param


def get_all_todo_paths() -> List[Path]:
    """Returns the full path of every todo.txt file in the todos directory."""
    todo_dir_path = Path(__file__).absolute().parent / "todos"

    result = []

    for txt_or_dir in todo_dir_path.glob("*"):
        if txt_or_dir.is_file() and txt_or_dir.suffix != ".txt":
            continue

        P = cast(Path, param(txt_or_dir, id=txt_or_dir.stem))
        result.append(P)

    return result
