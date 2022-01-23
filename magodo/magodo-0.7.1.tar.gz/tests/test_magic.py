"""Test that we can create custom MagicTodo classes."""

from __future__ import annotations

from typing import List, Type

from pytest import mark

from magodo import MagicTodoMixin, Todo
from magodo._shared import to_date
from magodo.types import AbstractMagicTodo, TodoSpell

from .shared import MagicTodo


params = mark.parametrize


def to_test_line(line: str) -> str:
    """Prepends 'test |' to `line`."""
    return "test | " + line


def from_test_line(line: str) -> str:
    """Removes 'test | ' from `line`."""
    return line.replace("test | ", "")


class LineTodo(MagicTodoMixin):
    """MagicTodo that adds 'test | ' to the beginning of each line."""

    from_line_spells = [from_test_line]
    to_line_spells = [to_test_line]
    todo_spells: List[TodoSpell] = []


@params(
    "line,magic_todo_type,todo,etodo",
    [
        (
            "x:1030 2022-01-12 Some done todo.",
            MagicTodo,
            Todo(
                desc="x:1030 2022-01-12 Some done todo.",
                metadata={"x": "1030"},
            ),
            Todo(
                desc="Some done todo. | dtime:1030",
                done=True,
                create_date=to_date("2022-01-12"),
                metadata={"dtime": "1030"},
            ),
        ),
        (
            "x:1030 2022-01-12 Some done todo with a @ctx.",
            MagicTodo,
            Todo(
                desc="x:1030 2022-01-12 Some done todo with a @ctx.",
                contexts=("ctx",),
                metadata={"x": "1030"},
            ),
            Todo(
                desc="Some done todo with a ctx. | @ctx dtime:1030",
                contexts=("ctx",),
                done=True,
                create_date=to_date("2022-01-12"),
                metadata={"dtime": "1030"},
            ),
        ),
    ],
)
def test_magic_todo(
    line: str,
    magic_todo_type: Type[AbstractMagicTodo[Todo]],
    todo: Todo,
    etodo: Todo,
) -> None:
    """Test the MagicTodo.from_line() function."""
    actual = magic_todo_type.from_line(line).unwrap()
    expected = magic_todo_type(todo)
    assert expected.todo == etodo
    assert repr(actual) == repr(expected)


@params("line", ["foo bar baz", "test | foo bar baz"])
def test_line_todo(line: str) -> None:
    """Test that to_line and from_line spells work."""
    todo = LineTodo.from_line(line).unwrap()
    assert todo.desc == "foo bar baz"
    assert todo.to_line() == "test | foo bar baz"
