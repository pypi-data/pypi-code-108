from __future__ import annotations

from typing import Any, Callable, ClassVar, Dict, Iterable, Optional

from .service import Service


class DependencyTracking(Service):
    """
    Track instances that are prerequisites for this instance.

    >>> setup = DependencyTracking.empty()
    >>> running = DependencyTracking(prerequisites=[setup])
    >>> teardown = DependencyTracking(prerequisites=[running])

    >>> setup.are_requirements_satisfied
    True
    >>> setup.notify(running)
    >>> running.are_requirements_satisfied
    True
    >>> teardown.acknowledge(running)
    >>> teardown.are_requirements_satisfied
    True
    """

    REQUIREMENTS_FACTORY: ClassVar[Callable[[], Dict[DependencyTracking, bool]]] = dict

    _requirements: Dict[DependencyTracking, bool]

    @property
    def prerequisites(self) -> Iterable[DependencyTracking]:
        return self._requirements.keys()

    @property
    def are_requirements_satisfied(self) -> bool:
        return all(self._requirements.values())

    @classmethod
    def empty(cls, *args: Any, **kwargs: Any) -> DependencyTracking:
        return cls(*args, **kwargs)

    def __init__(
        self,
        *args: Any,
        prerequisites: Optional[Iterable[DependencyTracking]] = None,
        **kwargs: Any
    ):
        super().__init__(*args, **kwargs)
        self._init_requirements(prerequisites)

    def _init_requirements(self, prerequisites: Optional[Iterable[DependencyTracking]]) -> None:
        self._requirements = self.REQUIREMENTS_FACTORY()

        if prerequisites:
            for prerequisite in prerequisites:
                self.require(prerequisite)

    def require(self, prerequisite: DependencyTracking) -> None:
        """Add an instance as a prerequisite."""
        self._requirements[prerequisite] = False

    def acknowledge(self, prerequisite: DependencyTracking) -> None:
        """Acknowledge a prerequisite is satisfied."""
        self._requirements[prerequisite] = True

    def notify(self, dependent: DependencyTracking) -> None:
        """Notify a dependency that this instance as a prerequisite is satisfied."""
        dependent.acknowledge(self)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
