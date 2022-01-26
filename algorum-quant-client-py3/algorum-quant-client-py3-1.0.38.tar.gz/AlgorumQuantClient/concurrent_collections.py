import threading
import collections

from .algorum_types import *


class BoundedBlockingQueue(object):
    def __init__(self, capacity: int):
        self.pushing = threading.Semaphore(capacity)
        self.pulling = threading.Semaphore(0)
        self.data = collections.deque()

    def enqueue(self, element: TickData) -> None:
        self.pushing.acquire()
        self.data.append(element)
        self.pulling.release()

    def dequeue(self) -> TickData:
        self.pulling.acquire()
        self.pushing.release()
        return self.data.popleft()

    def size(self) -> int:
        return len(self.data)