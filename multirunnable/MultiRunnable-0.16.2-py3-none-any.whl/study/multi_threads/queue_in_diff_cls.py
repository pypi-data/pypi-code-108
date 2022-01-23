from enum import Enum


class MultiThreadingQueueType:

    from queue import Queue, SimpleQueue, LifoQueue, PriorityQueue

    Queue = Queue()
    SimpleQueue = SimpleQueue()
    LifoQueue = LifoQueue()
    PriorityQueue = PriorityQueue()



class CoroutineQueueType:

    from gevent.queue import Queue, SimpleQueue, JoinableQueue, PriorityQueue, LifoQueue

    Queue = Queue
    SimpleQueue = SimpleQueue
    JoinableQueue = JoinableQueue
    PriorityQueue = PriorityQueue
    LifoQueue = LifoQueue



if __name__ == '__main__':

    __queue = MultiThreadingQueueType.Queue
    print("Queue object: ", __queue)
