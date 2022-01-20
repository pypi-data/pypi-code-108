import logging


class Tracker():
    def __init__(self, store):
        self.store = store
        self.logger = logging.getLogger(__name__)

    def track(self, val, name, epoch=None, step=None):
        self.logger.debug('tracking %s', name)
        self.store.track(val, name, epoch, step)

