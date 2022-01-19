from __future__ import annotations

from typing import Any, Callable, ClassVar, Iterable, Optional, Type, Union

from ..services import DependencyTracking, EventNotification
from .requirements import Dependency, Requirements

Predicate = Callable[[], bool]


class Unit(DependencyTracking):
    """
    Provides EventNotification when all prerequisites are satisfied and when execution completed.
    """

    REQUIREMENTS_FACTORY: ClassVar[Type[Requirements[Unit]]] = Requirements
    _requirements: Requirements[Unit]
    value: Any

    @classmethod
    def empty(cls) -> Unit:
        return cls(None)

    @property
    def dependencies(self) -> Iterable[Dependency[Unit]]:
        for prerequisite in self._requirements.prerequisites:
            yield Dependency(
                prerequisite.prerequisite, self, prerequisite.condition, prerequisite.condition
            )

    def __init__(self, value: Any):
        super().__init__()
        self.value = value

    def __repr__(self) -> str:
        return f"Unit({repr(self.value)})"

    def __getattr__(self, name: str) -> Any:
        return getattr(self.value, name)

    def require(
        self,
        prerequisite: Unit,
        condition: Optional[Predicate] = None,
        group: Optional[Union[Any, Iterable[Any]]] = None,
    ) -> None:
        if condition:
            self._requirements.conditions[prerequisite] = condition
        if group:
            try:
                for _group in group:
                    self.add_to_group(prerequisite, _group)
            except TypeError:
                self.add_to_group(prerequisite, group)
        return super().require(prerequisite)

    def add_to_group(self, prerequisite: Unit, group: Any) -> None:
        """
        Add a prerequisite into a requirement group.

        When all prerequisites in a requirement group are satisfied, the requirements of this execution unit is considered satisfied.

        All prerequisites are automatically in a default requirement group.
        """
        self._requirements.groups[group] = prerequisite

    @property
    def on_new_requirement(self) -> EventNotification:
        return self._requirements.on_new_requirement

    @property
    def on_requirements_satisfied(self) -> EventNotification:
        return self._requirements.on_requirements_satisfied
