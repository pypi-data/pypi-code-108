from abc import abstractmethod


class NehushtanMessageQueue:
    """
    This is a simplest model of Message Queue.
    Since 0.4.12
    Since 0.4.16 use `enqueue and dequeue` instead of `push and pop`
    """

    def __init__(self):
        pass

    @abstractmethod
    def enqueue(self, item: str, queue_name: str):
        pass

    @abstractmethod
    def dequeue(self, queue_name: str):
        pass
