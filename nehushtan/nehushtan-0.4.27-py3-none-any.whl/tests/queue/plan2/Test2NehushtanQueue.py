from nehushtan.queue.NehushtanQueue import NehushtanQueue
from nehushtan.queue.NehushtanQueueDelegate import NehushtanQueueDelegate
from nehushtan.queue.NehushtanQueueTaskDelegate import NehushtanQueueTaskDelegate


class Test2NehushtanQueue(NehushtanQueue):
    def __init__(self, delegate: NehushtanQueueDelegate, task_delegate: NehushtanQueueTaskDelegate):
        super().__init__(delegate, task_delegate)
