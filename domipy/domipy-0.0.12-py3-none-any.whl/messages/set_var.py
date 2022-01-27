import domipy

class SwitchValueMessage(domipy.Command):
    def __init__(self, moduleType, serialNumber):
        domipy.Command.__init__(self, moduleType, serialNumber)
        