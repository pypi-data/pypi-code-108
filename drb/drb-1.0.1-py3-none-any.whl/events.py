import logging

logger = logging.getLogger("event")


class Event(object):
    def __init__(self):
        self.callbacks = []

    def notify(self, *args, **kwargs):
        for callback in self.callbacks:
            callback(*args, **kwargs)

    def register(self, callback):
        self.callbacks.append(callback)
        return callback

    def unregister(self, callback):
        self.callbacks.remove(callback)
