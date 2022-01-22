from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Callable, ClassVar, Dict, Generic, Iterable, Optional
from typing import OrderedDict as TOrderedDict
from typing import TypeVar

from ..common import TAUTOLOGY_FACTORY, BidirectionalIndex
from ..services import EventNotification, Reaction, after, before

T = TypeVar("T")


class NotifyNewRequirement(Reaction):
    def when(
        self,
        execution_requirements: Requirements[T],
        prerequisite: T,
        is_satisfied: bool,
    ) -> bool:
        return prerequisite not in execution_requirements

    def react(
        self,
        execution_requirements: Requirements[T],
        prerequisite: T,
        is_satisfied: bool,
    ) -> None:
        execution_requirements.groups[execution_requirements.DEFAULT_GROUP] = prerequisite
        execution_requirements.on_new_requirement(prerequisite=prerequisite)


NOTIFY_NEW_REQUIREMENT = NotifyNewRequirement()


class NotifyRequirementsSatisfied(Reaction):
    def when(
        self,
        execution_requirements: Requirements[T],
        prerequisite: T,
        *args: Any,
        **kwargs: Any,
    ) -> bool:
        # since `is_satisfied` might be modified by condition, check directly
        if execution_requirements[prerequisite]:
            for group in execution_requirements.groups[prerequisite]:
                if execution_requirements.are_requirements_satisfied(group):
                    return True

        return False

    def react(
        self,
        execution_requirements: Requirements[T],
        prerequisite: T,
        is_satisfied: bool,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        execution_requirements.on_requirements_satisfied()


NOTIFY_REQUIREMENTS_SATISFIED = NotifyRequirementsSatisfied()


@dataclass
class Prerequisite(Generic[T]):
    prerequisite: T
    condition: Optional[Callable[[], bool]] = None
    group: Any = None


@dataclass
class Dependency(Generic[T]):
    prerequisite: T
    dependent: T
    condition: Optional[Callable[[], bool]] = None
    group: Any = None

    def to_prerequisite(self) -> Prerequisite[T]:
        return Prerequisite(self.prerequisite, self.condition, self.group)


class Requirements(Generic[T], TOrderedDict[T, bool]):
    """
    Requirements is used to model dependencies.

    Examples
    --------

    For example, in package manager like pip, a package `x` might require a package `y` installed with version at least `Vy` and a package `z` installed with version at least `Vz`.

    In other words, `y`, `z` are prerequisites for `x` with conditions like:

    y ─── version ≥ Vy ──┬── x
    z ─── version ≥ Vz ──┘

    This can be constructed as:
    ```
    reqs_for_x = ExecutionRequirements()
    reqs_for_x[y] = False
    reqs_for_x.conditions[y] = version ≥ Vy
    reqs_for_x[z] = False
    reqs_for_x.conditions[z] = version ≥ Vz
    ```

    This can become more complicated when there are different set of
    prerequisite that satisfy the requirements. For example, `x` can also be
    installed when `α` has version at least `Vα`.

    y ─── version ≥ Vy ──┬── x
    z ─── version ≥ Vz ──┘   ║
    α ═══ version ≥ Vα ══════╝

    This introduces the concept of group. `y` and `z` becomes a requirement
    group and `α` becomes another requirement group. There is also a default
    requirement group containing every prerequisite. Since any non-default
    requirement group are subset of default requirement group, if the
    default requirement group is satisfied, at least one other non-default
    requirement group is also satisfied. In hypergraph's terminology, a
    group is the head set of a hyperedge.

    This can be constructed as:
    ```
    reqs_for_x.groups['group1'] = y
    reqs_for_x.groups['group1'] = z
    reqs_for_x.groups['group2'] = α
    ```

    Conditions
    --------
    Condition can be added for a prerequisite.

    When marking a prerequisite as satisfied, the condition is evaluated.
    Only if it evaluates to True will the prerequisite be marked as  satisfied.

    Event Notification
    --------

    ExecutionRequirements will trigger two events

    + `on_new_requirement` will notify when a new prerequisite is added
    + `on_requirements_satisfied` when all prerequisites in a requirement
    group are satisfied.

    Since check for event notification happens when a prerequisite is marked
    as satisfied (set to True), it is possible to trigger
    `on_requirements_satisfied` more than once.

    For example, suppose `y` and `z` are satisfied,
    `on_requirements_satisfied` in `x` will be triggered. If `α` is
    satisfied later, `on_requirements_satisfied` in `x` will be triggered again.

    Also because of the same reason, `on_requirements_satisfied` is only triggered when there exists requirements.

    See Also
    --------
    [Hypergraph](https://en.wikipedia.org/wiki/Hypergraph)

    An example of ![a directed hypergraph](https://en.wikipedia.org/wiki/File:Directed_hypergraph_example.svg).
    """

    DEFAULT_GROUP: ClassVar[str] = "__DEFAULT__"

    conditions: Dict[T, Callable[[], bool]]
    groups: BidirectionalIndex[Any, T]

    @property
    def prerequisites(self) -> Iterable[Prerequisite[T]]:
        for prerequisite in self:
            condition = self.conditions[prerequisite]
            groups = self.groups[prerequisite]
            for group in groups:
                yield Prerequisite(prerequisite, condition, group)

    def __init__(self) -> None:
        super().__init__()
        self._init_events()
        self._init_conditions()
        self._init_groups()

    def _init_conditions(self) -> None:
        self.conditions = defaultdict(TAUTOLOGY_FACTORY)

    def _init_groups(self) -> None:
        self.groups = BidirectionalIndex()

    def _init_events(self) -> None:
        self.on_new_requirement = EventNotification()
        self.on_requirements_satisfied = EventNotification()

    @NOTIFY_NEW_REQUIREMENT.bind(at=before)
    @NOTIFY_REQUIREMENTS_SATISFIED.bind(at=after)
    def __setitem__(self, prerequisite: T, is_satisfied: bool) -> None:
        if is_satisfied:
            is_satisfied = self.conditions[prerequisite]()

        super().__setitem__(prerequisite, is_satisfied)

    def are_requirements_satisfied(self, group: Optional[str] = None) -> bool:
        """
        Check whether all prerequisites are marked as satisfied for a certain group.

        When group is not specified, default group will include all prerequisite.
        """
        if group is None:
            group = self.DEFAULT_GROUP

        return all(self[prerequisite] for prerequisite in self.groups[group])
