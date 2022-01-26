from collections import deque
from enum import Enum


class OperationType(Enum):
    SUB = 0
    PUB = 1


class Operation:
    def __init__(self, op_type: OperationType, message: str = None, topic: str = "", qos: int = 0,
                 retain: bool = False):
        self.type: OperationType = op_type
        self.message: str = message
        self.topic = topic
        self.qos: int = qos
        self.retain: bool = retain


class OperationQueue:

    def __init__(self):
        self._queue: deque[Operation] = deque()

    def pop(self) -> Operation:
        return self._queue.popleft()

    def push(self, op: Operation) -> None:
        self._queue.append(op)

    def isempty(self) -> bool:
        return len(self._queue) == 0
