"""Test that TodoGroup objects work as they should."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pytest import mark, param
from syrupy.assertion import SnapshotAssertion as Snapshot

from magodo import TodoGroup

from .data import get_all_todo_paths
from .shared import MagicTodo


params = mark.parametrize


@params("todo_file", get_all_todo_paths())
@params(
    "kwargs",
    [
        param({}, id="none"),
        param({"desc": "Double colons"}, id="desc"),
        param({"contexts": ["high"]}, id="ctx"),
    ],
)
def test_group_from_path(
    snapshot: Snapshot, todo_file: Path, kwargs: dict[str, Any]
) -> None:
    """Test the TodoGroup.from_path() function."""
    todo_group = TodoGroup.from_path(MagicTodo, todo_file)
    todo_group = todo_group.filter_by(**kwargs)
    assert [repr(todo) for todo in todo_group] == snapshot
