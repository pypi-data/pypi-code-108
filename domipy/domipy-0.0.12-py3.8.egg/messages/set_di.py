"""
Simulate digital inputs
:author: Zilvinas Binisevicius <zilvinas@binis.me>
"""
import domipy


class DigitalShortPush(domipy.Command):
    """Simulate SHORT signal on digital input"""
    def __init__(self, moduleType, serialNumber):
        domipy.Command.__init__(self, moduleType, serialNumber, "%P1")

class DigitalLongPush(domipy.Command):
    """Simulate LONG signal on digital input"""
    def __init__(self, moduleType, serialNumber):
        domipy.Command.__init__(self, moduleType, serialNumber, "%P3")

class DigitalShortPushEnd(domipy.Command):
    """Simulate End of Short signal on digital input"""
    def __init__(self, moduleType, serialNumber):
        domipy.Command.__init__(self, moduleType, serialNumber, "%P2")

class DigitalLongPushEnd(domipy.Command):
    """Simulate End of Long signal on digital input"""
    def __init__(self, moduleType, serialNumber):
        domipy.Command.__init__(self, moduleType, serialNumber, "%P4")