from __future__ import annotations
from pathlib import Path
from typing import Pattern

from myqueue.task import Task
from myqueue.states import State


class Selection:
    """Object used for selecting tasks."""

    def __init__(self,
                 ids: set[str] | None = None,
                 name: Pattern[str] | None = None,
                 states: set[State] = set(),
                 folders: list[Path] = [],
                 recursive: bool = True,
                 error: Pattern[str] | None = None):
        """Selection.

        Selections is based on:

            ids

        or:

            any combination of name, state, folder and error message.

        Use recursive=True to allow for tasks inside a folder.
        """

        self.ids = ids
        self.name = name
        self.states = states
        self.folders = folders
        self.recursive = recursive
        self.error = error

    def __repr__(self) -> str:
        return (f'Selection({self.ids}, {self.name}, {self.states}, '
                f'{self.folders}, {self.recursive}, {self.error})')

    def select(self, tasks: list[Task]) -> list[Task]:
        """Filter tasks acording to selection object."""
        if self.ids is not None:
            return [task for task in tasks if task.id in self.ids]

        newtasks = []
        for task in tasks:
            if task.state not in self.states:
                continue
            if self.name and not self.name.fullmatch(task.cmd.name):
                continue
            if not any(task.infolder(f, self.recursive) for f in self.folders):
                continue
            if self.error and not self.error.fullmatch(task.error):
                continue
            newtasks.append(task)

        return newtasks
