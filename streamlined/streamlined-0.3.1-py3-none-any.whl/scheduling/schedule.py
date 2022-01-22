from __future__ import annotations

import asyncio
from asyncio import Queue as AsyncQueue
from asyncio.queues import QueueEmpty
from asyncio.tasks import FIRST_COMPLETED, Task
from contextlib import contextmanager
from functools import partial
from typing import (
    Any,
    AsyncIterable,
    Awaitable,
    Callable,
    ClassVar,
    Dict,
    Iterable,
    List,
    Optional,
    Set,
    Type,
    TypeVar,
)

import networkx as nx
from networkx.classes.digraph import DiGraph
from ray.util.queue import Queue

from ..services import EventNotification
from .unit import Unit

T = TypeVar("T")


@contextmanager
def closing(thing: Any) -> Any:
    try:
        yield thing
    finally:
        try:
            thing.close()
        except AttributeError:
            return


class Schedule:
    """
    Scheduling can be seen as a Graph of Unit.

    More specifically, nodes are units while edges are dependency relationships.

    It offers scheduling by determining which units are ready to execute
    (based primarily on topology ordering) and requirements.

    Events
    --------
    Scheduling also exposes these events:

    + `on_requirements_satisfied(unit)` This event signals an unit is ready (all its requirements are satisfied)

    """

    UNIT_FACTORY: ClassVar[Type[Unit]] = Unit

    _ATTRIBUTE_NAME_FOR_SOURCE: ClassVar[str] = "source"
    _ATTRIBUTE_NAME_FOR_SINK: ClassVar[str] = "sink"

    graph: DiGraph

    @property
    def _source(self) -> Unit:
        return self.graph.graph[self._ATTRIBUTE_NAME_FOR_SOURCE]

    @property
    def _sink(self) -> Unit:
        return self.graph.graph[self._ATTRIBUTE_NAME_FOR_SINK]

    @property
    def units(self) -> Iterable[Unit]:
        """
        Returns a generator of execution units in topologically sorted order.
        """
        try:
            return nx.topological_sort(self.graph)
        except nx.NetworkXUnfeasible:
            return self.graph.nodes()

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._init_events()
        self._init_graph()

    def __add__(self, other: Any) -> Schedule:
        if not isinstance(other, Unit):
            other = Unit(other)

        self.push(other)
        return self

    def __iadd__(self, other: Any) -> Schedule:
        return self.__add__(other)

    def __iter__(self) -> Iterable[Unit]:
        yield from self.walk()

    def __getstate__(self) -> DiGraph:
        return self.graph

    def __setstate__(self, state: DiGraph) -> None:
        self.graph = state

    async def __aiter__(self) -> AsyncIterable[Unit]:
        async for unit in self.walk_async():
            yield unit

    def _init_events(self) -> None:
        self.on_complete = EventNotification()
        self.on_requirements_satisfied = EventNotification()

    def _init_graph(self) -> None:
        self.graph = nx.DiGraph()
        self._init_source_sink()

    def _init_source_sink(self) -> None:
        self._init_terminal_node(self._ATTRIBUTE_NAME_FOR_SOURCE)
        self._init_terminal_node(self._ATTRIBUTE_NAME_FOR_SINK)
        self._add_source_as_prerequisite(self._sink)

    def _add_source_as_prerequisite(self, unit: Unit) -> None:
        unit.require(self._source)

    def _add_sink_as_dependent(self, unit: Unit) -> None:
        self._sink.require(unit)

    def _init_terminal_node(self, attribute_name: str) -> Unit:
        unit = Unit.empty()
        self._init_events_for_unit(unit)
        self.graph.add_node(unit)
        self.graph.graph[attribute_name] = unit
        return unit

    def _init_events_for_unit(self, unit: Unit) -> None:
        # bind event listeners
        unit.on_new_requirement.register(partial(self._track_requirement, dependent=unit))
        unit.on_requirements_satisfied.register(partial(self.on_requirements_satisfied, unit))

    def _track_requirement(
        self,
        prerequisite: Unit,
        dependent: Unit,
    ) -> None:
        self.graph.add_edge(prerequisite, dependent)

    def notify(self, unit: Unit) -> None:
        """
        Notify all dependents that rely on provided unit as prerequisite that this
        requirement has been satisfied.
        """
        self.on_complete(unit)
        for dependent in self.graph.successors(unit):
            unit.notify(dependent)

    def push(
        self,
        unit: Unit,
        has_prerequisites: Optional[bool] = None,
        has_dependents: Optional[bool] = None,
    ) -> Unit:
        """
        Add a callable into current execution schedule.

        After calling `push`, the returned execution unit can record requirements by calling `require`.

        :param _callable: Encapsulates the actual work.
        :param has_prerequisites: Whether this callable will have other
            callables as prerequisites. If False or not specified (default),
            It will have `source` as prerequisite. Specifying True can
            reduce graph complexity. Another usage of specifying True is
            when an execution unit need to dynamically create new execution
            units during enumeration (`walk`
            or `walk_async`). Since `source` has already enumerated past, a
            prerequisite on `source` will prevent the newly created execution
            unit from being called.
        :param has_dependents: Whether this callable will have other
            callables as dependents. If False or not specified (default),
            It will have `sink` as dependent. Specifying True can
            reduce graph complexity.
        :returns: An execution unit.
        """
        self._init_events_for_unit(unit)
        self.graph.add_node(unit)

        if not has_prerequisites:
            self._add_source_as_prerequisite(unit)

        if not has_dependents:
            self._add_sink_as_dependent(unit)

        return unit

    def walk(
        self,
        queue: Optional[Queue] = None,
        enqueue: Optional[Callable[[Unit], None]] = None,
        dequeue: Optional[Callable[..., Unit]] = None,
    ) -> Iterable[Unit]:
        """
        Yield the units as they can be executed (all prerequisites satisfied).

        The units will also be `enqueue` into `queue` when they become ready to execute.

        At each iteration, an unit will be dequeued from `queue` for actual execution.
        """
        if queue is None:
            queue = Queue()
        if enqueue is None:
            enqueue = queue.put
        if dequeue is None:
            dequeue = queue.get

        with closing(queue):
            with self.on_requirements_satisfied.registering(enqueue):
                self.notify(self._source)

                while (unit := dequeue()) != self._sink:
                    yield unit

    async def walk_async(
        self,
        queue: Optional[AsyncQueue[Unit]] = None,
        enqueue: Optional[Callable[[Unit], None]] = None,
        dequeue: Optional[Callable[..., Awaitable[Unit]]] = None,
    ) -> AsyncIterable[Unit]:
        """
        Yield the execution units asynchronously as they can be executed.

        See Also
        --------
        `walk`
        """
        if queue is None:
            queue = AsyncQueue()
        if enqueue is None:
            enqueue = queue.put_nowait
        if dequeue is None:
            dequeue = queue.get

        def queue_task_done(*args: Any, **kwargs: Any) -> None:
            queue.task_done()

        with closing(queue):
            with self.on_requirements_satisfied.registering(enqueue):
                self.notify(self._source)

                with self.on_complete.registering(queue_task_done):
                    while (unit := await dequeue()) != self._sink:
                        yield unit

    async def walk_greedy(self) -> AsyncIterable[List[Unit]]:
        """
        Different from `walk_async`, `walk_greedy` will return all
        units available for execution at each yield.

        While yielding control, the caller should be responsible for
        `notify` the schedule about completed units.

        When no units are available, `walk_greedy` will yield empty list.
        """
        queue: AsyncQueue[Unit] = AsyncQueue()

        def queue_task_done(*args: Any, **kwargs: Any) -> None:
            queue.task_done()

        with closing(queue):
            with self.on_requirements_satisfied.registering(queue.put_nowait):
                self.notify(self._source)

                with self.on_complete.registering(queue_task_done):
                    while True:
                        units: List[Unit] = []
                        try:
                            while True:
                                unit = queue.get_nowait()
                                if unit == self._sink:
                                    return
                                units.append(unit)
                        except QueueEmpty:
                            yield units

    async def work_greedy(self, task_generator: Callable[[Unit], Task[T]]) -> AsyncIterable[T]:
        """
        Similar to `walk_greedy`, `work_greedy` will put all
        available tasks (generated from units) to work and
        yield once a result is ready.
        """
        task_to_unit: Dict[Task[T]] = dict()
        done: Set[Task[T]] = set()
        ongoing: Set[Task[T]] = set()

        async for units in self.walk_greedy():
            for unit in units:
                task = task_generator(unit)
                task_to_unit[task] = unit
                ongoing.add(task)

            if ongoing:
                done_tasks, ongoing = await asyncio.wait(ongoing, return_when=FIRST_COMPLETED)
                for done_task in done_tasks:
                    done.add(done_task)
                    yield done_task.result()
                    self.notify(task_to_unit[done_task])


if __name__ == "__main__":
    import doctest

    doctest.testmod()
