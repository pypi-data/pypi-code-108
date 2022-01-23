"""Tests for the magodo package."""

from __future__ import annotations

from typing import Sequence, cast

from pytest import mark

from magodo import DEFAULT_PRIORITY, Todo
from magodo._shared import to_date
from magodo.types import AbstractTodo

from .shared import MagicTodo


params = mark.parametrize


@params(
    "line,expect_todo",
    [
        ("no priority todo", Todo(desc="no priority todo")),
        (f"({DEFAULT_PRIORITY}) basic todo", Todo(desc="basic todo")),
        (
            f"({DEFAULT_PRIORITY}) 2022-01-10 todo with create date",
            Todo(
                desc="todo with create date",
                create_date=to_date("2022-01-10"),
            ),
        ),
        (
            f"({DEFAULT_PRIORITY}) 2022-03-04 2022-01-10 todo with done date",
            Todo(
                desc="todo with done date",
                create_date=to_date("2022-01-10"),
                done_date=to_date("2022-03-04"),
            ),
        ),
        (
            f"x ({DEFAULT_PRIORITY}) 2022-01-10 done todo",
            Todo(
                desc="done todo",
                create_date=to_date("2022-01-10"),
                done=True,
            ),
        ),
        (
            "x (A) todo with priority",
            Todo(
                desc="todo with priority",
                done=True,
                priority="A",
            ),
        ),
        (
            f"({DEFAULT_PRIORITY}) todo for +some +project",
            Todo(
                desc="todo for +some +project",
                projects=("some", "project"),
            ),
        ),
        (
            f"({DEFAULT_PRIORITY}) todo for +some +project and a @context.",
            Todo(
                desc="todo for +some +project and a @context.",
                projects=("some", "project"),
                contexts=("context",),
            ),
        ),
        (
            f"({DEFAULT_PRIORITY}) todo with +some meta:data and a @context"
            " due:2022-12-31",
            Todo(
                desc="todo with +some meta:data and a @context due:2022-12-31",
                projects=("some",),
                contexts=("context",),
                metadata={"meta": "data", "due": "2022-12-31"},
            ),
        ),
        (
            f"({DEFAULT_PRIORITY}) todo with some dep:123,10,20,30, another"
            " dep:456, and a 3rd dep:789... foo:bar @crazy",
            Todo(
                desc=(
                    "todo with some dep:123,10,20,30, another dep:456, and a"
                    " 3rd dep:789... foo:bar @crazy"
                ),
                contexts=("crazy",),
                metadata={"dep": ["123", "10", "20", "30"], "foo": "bar"},
            ),
        ),
        (
            "x:1030 2022-01-12 Some done todo with a @ctx.",
            Todo(
                desc="x:1030 2022-01-12 Some done todo with a @ctx.",
                contexts=("ctx",),
                metadata={"x": "1030"},
            ),
        ),
        (
            "o +regression @test Do +duplicate +duplicate @keys @keys"
            " foo:bar,baz foo:bar foo:boom bar:BAR still show when they should"
            " be ignored?",
            MagicTodo(
                Todo(
                    desc=(
                        "o Do duplicate duplicate keys keys still show when"
                        " they should be ignored? | @keys @test +duplicate"
                        " +regression bar:BAR foo:bar,baz"
                    ),
                    contexts=(
                        "test",
                        "keys",
                    ),
                    projects=(
                        "regression",
                        "duplicate",
                    ),
                    metadata={"foo": ["bar", "baz"], "bar": "BAR"},
                )
            ),
        ),
    ],
)
def test_todo(line: str, expect_todo: AbstractTodo) -> None:
    """Test the Todo type."""
    actual = cast(MagicTodo, type(expect_todo).from_line(line).unwrap())

    assert actual.desc == expect_todo.desc
    assert actual.priority == expect_todo.priority
    assert actual.create_date == expect_todo.create_date
    assert actual.done_date == expect_todo.done_date
    assert actual.projects == expect_todo.projects
    assert actual.contexts == expect_todo.contexts
    assert actual.done == expect_todo.done
    assert actual.metadata == expect_todo.metadata


@params(
    "todos,idxs",
    [
        (
            [
                Todo("baz", priority="M"),
                Todo("foo", priority="G"),
                Todo("o bar"),
            ],
            [1, 0, 2],
        ),
        (
            [Todo("o foo"), Todo("o bar"), Todo("o baz", done=True)],
            [1, 0, 2],
        ),
        (
            [
                Todo("o foo"),
                Todo("o foo"),
                Todo("o A", done_date=to_date("2022-01-01")),
                Todo(
                    "o B",
                    done_date=to_date("1999-01-01"),
                    metadata={"dtime": "0123"},
                ),
                Todo(
                    "o C",
                    done_date=to_date("2022-01-01"),
                    metadata={"dtime": "1100"},
                ),
                Todo(
                    "o D",
                    done_date=to_date("2022-01-01"),
                    metadata={"dtime": "1000"},
                ),
            ],
            [0, 1, 3, 2, 5, 4],
        ),
    ],
)
def test_sort(todos: Sequence[Todo], idxs: Sequence[int]) -> None:
    """Test that Todo objects sort properly."""
    assert len(todos) == len(idxs)
    N = len(todos)

    expected = [todos[idxs[i]] for i in range(N)]
    assert sorted(todos) == expected

    magic_todos = [MagicTodo(todo) for todo in todos]
    magic_expected = [magic_todos[idxs[i]] for i in range(N)]
    assert sorted(magic_todos) == magic_expected
