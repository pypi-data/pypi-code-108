"""Contains the MagicTodoMixin class definition."""

from __future__ import annotations

import abc
import datetime as dt
from functools import total_ordering
from typing import Any, List, Tuple, Type, TypeVar

from eris import ErisError, Err, Ok, Result

from ._todo import Todo, TodoMixin
from .types import LineSpell, Metadata, Priority, TodoSpell


M = TypeVar("M", bound="MagicTodoMixin")


@total_ordering
class MagicTodoMixin(TodoMixin, abc.ABC):
    """Mixin class that implements the Todo protocol."""

    to_line_spells: List[LineSpell] = []
    todo_spells: List[TodoSpell] = []
    from_line_spells: List[LineSpell] = []

    def __init__(self: M, todo: Todo):
        self._todo = todo
        self.todo = self.cast_todo_spells(todo).unwrap()

    @classmethod
    def from_line(cls: Type[M], line: str) -> Result[M, ErisError]:
        """Converts a string into a MagicTodo object."""
        line = cls.cast_from_line_spells(line)
        todo_result = Todo.from_line(line)

        err: Err[Any, ErisError]
        if isinstance(todo_result, Err):
            err = Err(
                "Failed to construct basic Todo object inside of MagicTodo."
            )
            return err.chain(todo_result)

        todo = todo_result.ok()
        if error := cls.cast_todo_spells(todo).err():
            err = Err(f"Failed spell validation for this todo: todo={todo!r}")
            return err.chain(error)

        return Ok(cls(todo))

    def to_line(self: M) -> str:
        """Converts this MagicTodo back to a string."""
        line = self.todo.to_line()
        line = self.cast_to_line_spells(line)
        return line

    @classmethod
    def cast_todo_spells(cls: Type[M], todo: Todo) -> Result[Todo, ErisError]:
        """Casts all spells associated with this MagicTodo on `todo`."""
        new_todo = todo.new()
        for todo_spell in cls.todo_spells:
            new_todo_result = todo_spell(new_todo)
            if isinstance(new_todo_result, Err):
                err: Err[Any, ErisError] = Err(
                    f"The {todo_spell.__name__!r} spell failed while"
                    " processing this todo."
                )
                return err.chain(new_todo_result)

            new_todo = new_todo_result.ok()

        return Ok(new_todo)

    @classmethod
    def cast_from_line_spells(cls: Type[M], line: str) -> str:
        """Casts all from_line spells on `line`."""
        for line_spell in cls.from_line_spells:
            line = line_spell(line)
        return line

    def cast_to_line_spells(self: M, line: str) -> str:
        """Casts all to_line spells on `line`."""
        for line_spell in self.to_line_spells:
            line = line_spell(line)
        return line

    def new(self: M, **kwargs: Any) -> M:
        """Creates a new Todo using the current Todo's attrs as defaults."""
        return type(self)(self.todo.new(**kwargs))

    @property
    def contexts(self: M) -> Tuple[str, ...]:  # noqa: D102
        return self.todo.contexts

    @property
    def create_date(self: M) -> dt.date | None:  # noqa: D102
        return self.todo.create_date

    @property
    def desc(self: M) -> str:  # noqa: D102
        return self.todo.desc

    @property
    def done_date(self: M) -> dt.date | None:  # noqa: D102
        return self.todo.done_date

    @property
    def done(self: M) -> bool:  # noqa: D102
        return self.todo.done

    @property
    def metadata(self: M) -> Metadata:  # noqa: D102
        return self.todo.metadata

    @property
    def priority(self: M) -> Priority:  # noqa: D102
        return self.todo.priority

    @property
    def projects(self: M) -> Tuple[str, ...]:  # noqa: D102
        return self.todo.projects
