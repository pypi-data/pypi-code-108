

from os import environ
from twisted.internet.utils import getProcessOutput
from ebs.iot.linuxnode.basemixin import BaseMixin


class BaseShellMixin(BaseMixin):
    # def __init__(self, *args, **kwargs):
    #     self._shell_processes = {}
    #     super(BaseShellMixin, self).__init__(self, *args, **kwargs)

    def _shell_execute(self, command, response_handler):
        if len(command) > 1:
            args = command[1:]
        else:
            args = []
        d = getProcessOutput(command[0], args, env=environ)
        d.addCallback(response_handler)
        return d
