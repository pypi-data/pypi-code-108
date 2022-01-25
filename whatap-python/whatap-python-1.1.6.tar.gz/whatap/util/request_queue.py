import time

from whatap import logging
from whatap.util.date_util import DateUtil
from whatap.util.linked_list import LinkedList


class RequestQueue(object):
    def __init__(self, capacity):
        self.capacity = capacity
        self.queue = LinkedList()

    def get(self, timeout=None):
        if not timeout:
            while self.queue.size() <= 0:
                try:
                    time.sleep(0.5)
                except Exception as e:
                    logging.debug(e, extra={'id': 'WA520'}, exc_info=True)
            return self.queue.removeFirst()
        else:
            if self.queue.size() > 0:
                return self.queue.removeFirst()

            timeto = DateUtil.currentTime() + timeout
            while not self.queue.size():
                try:
                    if timeout > 0:
                        time.sleep(5)

                except Exception as e:
                    logging.debug(e, extra={'id': 'WA521'}, exc_info=True)

                if timeto - DateUtil.currentTime() <= 0:
                    break

            if self.queue.size() > 0:
                return self.queue.removeFirst()

            return None

    def put(self, o):
        if self.capacity <= 0 or self.queue.size() < self.capacity:
            self.queue.add(o)
            return True
        else:
            self.failed(o)
            return False

    def size(self):
        return self.queue.size()

    def clear(self):
        self.queue = LinkedList()

    def failed(self, v):
        return

    def overflowed(self, v):
        return
