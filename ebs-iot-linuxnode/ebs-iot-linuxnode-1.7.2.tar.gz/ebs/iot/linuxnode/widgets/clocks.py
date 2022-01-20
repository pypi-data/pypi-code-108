
from twisted.internet.task import deferLater
from twisted.internet.defer import CancelledError
from .labels import SelfScalingLabel

import arrow


class ClockBase(object):
    def __init__(self, node):
        self._node = node
        self._update_task = None
        super(ClockBase, self).__init__()

    def update(self):
        raise NotImplementedError

    def start(self):
        self._node.log.info("Starting Update Task for {0}".format(self))
        self.step()

    def step(self):
        self.update()
        self._update_task = deferLater(self._node.reactor, 1, self.step)

        def _cancel_handler(failure):
            failure.trap(CancelledError)

        self._update_task.addErrback(_cancel_handler)

        return self._update_task

    def stop(self):
        self._node.log.info("Stopping Update Task for {0}".format(self))
        if self._update_task:
            self._update_task.cancel()


class SimpleDigitalClock(ClockBase, SelfScalingLabel):
    def __init__(self, node, **kwargs):
        ClockBase.__init__(self, node)
        SelfScalingLabel.__init__(self, **kwargs)

    def update(self):
        self.text = arrow.now().format("HH:mm:ss")
