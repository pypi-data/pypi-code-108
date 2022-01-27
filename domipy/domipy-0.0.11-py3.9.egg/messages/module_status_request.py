"""
:author: Thomas Delaet <thomas@delaet.org>
"""
import domipy

COMMAND_CODE = "__MODULE_STATUS__"


class ModuleStatusRequest(domipy.Command):
    """
        Request module status
    """
    def __init__(self, moduleType, serialNumber):
        domipy.Command.__init__(self, moduleType, serialNumber)
        self.moduleType = moduleType

    def command(self):
        return "{:3}{:>6}%S".format(self.moduleType, self.serialNumber)
        #return "{:3}{:>6}-4".format(self.moduleType, self.serialNumber)

domipy.register_command(COMMAND_CODE, ModuleStatusRequest)
