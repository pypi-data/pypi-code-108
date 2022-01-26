import datetime
from dataclasses import dataclass, field
from types import FunctionType, TracebackType
from typing import Any, Dict, List, Set, Tuple, Union
from uuid import UUID, uuid4

from roview import rodict, roset

from arrlio.settings import (
    EVENT_TTL,
    EVENTS,
    MESSAGE_ACK_LATE,
    MESSAGE_EXCHANGE,
    MESSAGE_PRIORITY,
    MESSAGE_TTL,
    TASK_ACK_LATE,
    TASK_BIND,
    TASK_PRIORITY,
    TASK_QUEUE,
    TASK_RESULT_RETURN,
    TASK_RESULT_TTL,
    TASK_TIMEOUT,
    TASK_TTL,
)


@dataclass
class TaskData:
    task_id: UUID = field(default_factory=uuid4)
    args: tuple = field(default_factory=tuple)
    kwds: dict = field(default_factory=dict)
    queue: str = None
    priority: int = None
    timeout: int = None
    ttl: int = None
    encrypt: bool = None
    ack_late: bool = None
    result_ttl: int = None
    result_return: bool = None
    result_encrypt: bool = None
    thread: bool = None
    events: bool = None
    event_ttl: int = None
    extra: dict = field(default_factory=dict)
    graph: "Graph" = None


@dataclass(frozen=True)
class Task:
    func: FunctionType
    name: str
    bind: bool = None
    queue: str = None
    priority: int = None
    timeout: int = None
    ttl: int = None
    encrypt: bool = None
    ack_late: bool = None
    result_ttl: int = None
    result_return: bool = None
    result_encrypt: bool = None
    thread: bool = None
    events: bool = None
    event_ttl: int = None

    def __post_init__(self):
        if self.bind is None:
            object.__setattr__(self, "bind", TASK_BIND)
        if self.queue is None:
            object.__setattr__(self, "queue", TASK_QUEUE)
        if self.priority is None:
            object.__setattr__(self, "priority", TASK_PRIORITY)
        if self.timeout is None:
            object.__setattr__(self, "timeout", TASK_TIMEOUT)
        if self.ttl is None:
            object.__setattr__(self, "ttl", TASK_TTL)
        if self.ack_late is None:
            object.__setattr__(self, "ack_late", TASK_ACK_LATE)
        if self.result_ttl is None:
            object.__setattr__(self, "result_ttl", TASK_RESULT_TTL)
        if self.result_return is None:
            object.__setattr__(self, "result_return", TASK_RESULT_RETURN)
        if self.events is None:
            object.__setattr__(self, "events", EVENTS)
        if self.event_ttl is None:
            object.__setattr__(self, "event_ttl", EVENT_TTL)

    def instantiate(self, data: TaskData = None) -> "TaskInstance":
        if data is None:
            data = TaskData()
        if isinstance(data.task_id, str):
            data.task_id = UUID(data.task_id)
        if isinstance(data.args, list):
            data.args = tuple(data.args)
        if data.queue is None:
            data.queue = self.queue
        if data.priority is None:
            data.priority = self.priority
        if data.timeout is None:
            data.timeout = self.timeout
        if data.ttl is None:
            data.ttl = self.ttl
        if data.encrypt is None:
            data.encrypt = self.encrypt
        if data.ack_late is None:
            data.ack_late = self.ack_late
        if data.result_ttl is None:
            data.result_ttl = self.result_ttl
        if data.result_return is None:
            data.result_return = self.result_return
        if data.result_encrypt is None:
            data.result_encrypt = self.result_encrypt
        if data.thread is None:
            data.thread = self.thread
        if data.events is None:
            data.events = self.events
        if data.event_ttl is None:
            data.event_ttl = self.event_ttl
        return TaskInstance(task=self, data=data)

    def __call__(self, *args, **kwds) -> Any:
        return self.instantiate(TaskData(args=args, kwds=kwds))()


@dataclass(frozen=True)
class TaskInstance:
    task: Task
    data: TaskData

    def __call__(self):
        args = self.data.args
        kwds = self.data.kwds
        if self.task.bind:
            args = (self,) + args
        return self.task.func(*args, **kwds)


@dataclass(frozen=True)
class TaskResult:
    res: Any = None
    exc: Union[Exception, Tuple[str, str, str]] = None
    trb: Union[TracebackType, str] = None


@dataclass(frozen=True)
class Message:
    data: Any
    message_id: UUID = field(default_factory=uuid4)
    exchange: str = None
    priority: int = None
    ttl: int = None
    ack_late: bool = None

    def __post_init__(self):
        if self.exchange is None:
            object.__setattr__(self, "exchange", MESSAGE_EXCHANGE)
        if self.priority is None:
            object.__setattr__(self, "priority", MESSAGE_PRIORITY)
        if self.ttl is None:
            object.__setattr__(self, "ttl", MESSAGE_TTL)
        if self.ack_late is None:
            object.__setattr__(self, "ack_late", MESSAGE_ACK_LATE)


@dataclass(frozen=True)
class Event:
    type: str
    datetime: datetime.datetime
    data: dict
    event_id: UUID = field(default_factory=uuid4)


class Graph:
    def __init__(
        self,
        id: str,
        nodes: Dict = None,
        edges: Dict = None,
        roots: Set = None,
    ):
        self.id = id
        self.nodes: Dict[str, List[str]] = rodict({}, nested=True)
        self.edges: Dict[str, Set[str]] = rodict({}, nested=True)
        self.roots: Set[str] = roset(set())
        nodes = nodes or {}
        edges = edges or {}
        roots = roots or set()
        for node_id, (task, kwds) in nodes.items():
            self.add_node(node_id, task, root=node_id in roots, **kwds)
        for node_id_from, nodes_id_to in edges.items():
            for node_id_to in nodes_id_to:
                self.add_edge(node_id_from, node_id_to)

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id} nodes={self.nodes} edges={self.edges} roots={self.roots}"

    def __repr__(self):
        return self.__str__()

    def add_node(self, node_id: str, task: Union[Task, str], root: bool = None, **kwds):
        if node_id in self.nodes:
            raise Exception(f"Node '{node_id}' already in graph")
        if isinstance(task, Task):
            task = task.name
        self.nodes.__original__[node_id] = [task, kwds]
        if root:
            self.roots.__original__.add(node_id)

    def add_edge(self, node_id_from: str, node_id_to: str):
        if node_id_from not in self.nodes:
            raise Exception(f"Node '{node_id_from}' not found in graph")
        if node_id_to not in self.nodes:
            raise Exception(f"Node '{node_id_to}' not found in graph")
        self.edges.__original__.setdefault(node_id_from, set()).add(node_id_to)

    def dict(self):
        return {
            "id": self.id,
            "nodes": self.nodes,
            "edges": self.edges,
            "roots": self.roots,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            nodes=data["nodes"],
            edges=data["edges"],
            roots=data["roots"],
        )
