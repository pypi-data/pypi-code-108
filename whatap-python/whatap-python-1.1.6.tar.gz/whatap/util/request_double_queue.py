import time

from whatap import logging
from whatap.util.linked_list import LinkedList


class RequestDoubleQueue(object):
    def __init__(self, capacity1, capacity2):
        self.capacity1 = capacity1
        self.capacity2 = capacity2
        self.queue1 = LinkedList()
        self.queue2 = LinkedList()

    def get(self):
        while self.queue1.size() <= 0 and self.queue2.size() <= 0:
            try:
                time.sleep(0.5)
            except Exception as e:
                logging.debug(e, extra={'id': 'WA510'}, exc_info=True)

        if self.queue1.size() > 0:
            return self.queue1.removeFirst()
        elif self.queue2.size() > 0:
            return self.queue2.removeFirst()

        return None

    def hasNext(self):
        if self.queue1.hasNext() or self.queue2.hasNext():
            return True
        return False

    def putForce1(self, o):
        return self.putForce(self.queue1, self.capacity1, o)

    def putForce2(self, o):
        return self.putForce(self.queue2, self.capacity2, o)

    def putForce(self, q, sz, o):
        if sz <= 0 or q.size() < self.capacity1:
            q.add(o)
            return True
        else:
            while q.size() >= sz:
                v = q.removeFirst()
                self.overflowed(v)
            q.add(o)
            return False

    def put1(self, o):
        return self.put(self.queue1, self.capacity1, o)

    def put2(self, o):
        return self.put(self.queue1, self.capacity2, o)

    def put(self, queue, capacity, o):
        if capacity <= 0 or queue.size() < capacity:
            queue.add(o)
            return True
        else:
            self.failed(o)
            return False

    def failed(self, v):
        return

    def overflowed(self, v):
        return
