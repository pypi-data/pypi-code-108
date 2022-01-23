"""Contains the TodoGroup class definition."""

from __future__ import annotations

import datetime as dt
from logging import Logger
from pathlib import Path
from typing import Generic, Iterable, Iterator, List, Type

from eris import Err
from metaman import cname
from typist import PathLike

from .types import Metadata, Priority, T


logger = Logger(__name__)


class TodoGroup(Generic[T]):
    """Manages a group of Todo objects."""

    def __init__(self, todos: Iterable[T]) -> None:
        self._todos = sorted(todos)

    def __repr__(self) -> str:  # noqa: D105
        return f"{cname(self)}({self._todos})"

    def __iter__(self) -> Iterator[T]:
        """Yields the Todo objects that belong to this group."""
        yield from self._todos

    def __len__(self) -> int:  # noqa: D105
        return len(self._todos)

    @classmethod
    def from_path(cls, todo_type: Type[T], path_like: PathLike) -> TodoGroup:
        """Reads all todo lines from a given file or directory (recursively).

        Pre-conditions:
            * `path_like` exists and is either a file or directory.
        """
        path = Path(path_like)

        assert path.exists(), f"The provided path does not exist: {path}"

        todos: List[T] = []
        if path.is_file():
            logger.debug(
                "Attempting to load todos from text file: file=%r", str(path)
            )

            for line in path.read_text().split("\n"):
                line = line.strip()
                todo_result = todo_type.from_line(line)
                if isinstance(todo_result, Err):
                    continue

                todo = todo_result.ok()
                todos.append(todo)
                logger.debug("New todo loaded: todo=%r", todo)
        else:
            assert path.is_dir(), (
                "The provided path exists but is neither a file nor a"
                f" directory: {path}"
            )

            logger.debug("Loading from directory: dir=%r", str(path))
            for other_path in path.glob("*"):
                if other_path.is_file() and other_path.suffix != ".txt":
                    continue

                other_todo_group = TodoGroup.from_path(todo_type, other_path)
                todos.extend(other_todo_group)

        return cls(todos)

    def filter_by(
        self,
        *,
        contexts: Iterable[str] = None,
        create_date: dt.date = None,
        desc: str = None,
        done_date: dt.date = None,
        done: bool = None,
        metadata: Metadata = None,
        priority: Priority = None,
        projects: Iterable[str] = None,
    ) -> TodoGroup:
        """Filter this group using one or more Todo properties."""
        todos = []

        for todo in self._todos:
            if contexts is not None and not all(
                ctx in todo.contexts for ctx in contexts
            ):
                continue

            if create_date is not None and todo.create_date != create_date:
                continue

            if desc is not None and desc.lower() not in todo.desc.lower():
                continue

            if done_date is not None and todo.done_date != done_date:
                continue

            if done is not None and todo.done != done:
                continue

            if metadata is not None and not all(
                v == todo.metadata.get(k, None) for (k, v) in metadata.items()
            ):
                continue

            if priority is not None and todo.priority != priority:
                continue

            if projects is not None and not all(
                proj in todo.projects for proj in projects
            ):
                continue

            todos.append(todo)

        return TodoGroup(todos)
