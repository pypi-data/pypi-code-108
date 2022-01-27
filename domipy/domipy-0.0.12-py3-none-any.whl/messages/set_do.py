"""
:author: Zilvinas Binisevicius <zilvinas@binis.me>
"""
import domipy


class SetDigitalOutputMessage(domipy.Command):
    def __init__(self, moduleType, serialNumber, channel, value):
        val = 1 if value > 0 else 0
        print("val={}", val)
        domipy.Command.__init__(self, moduleType, serialNumber, channel, "%I", val)

class SetDigitalOutputOnMessage(domipy.Command):
    def __init__(self, moduleType, serialNumber, channel):
        domipy.Command.__init__(self, moduleType, serialNumber, channel, "%I")

class SetDigitalOutputOffMessage(domipy.Command):
    def __init__(self, moduleType, serialNumber, channel):
        domipy.Command.__init__(self, moduleType, serialNumber, channel, "%O")

class TogleDigitalOutputMessage(domipy.Command):
    def __init__(self, moduleType, serialNumber, channel):
        domipy.Command.__init__(self, moduleType, serialNumber, channel, "")

""" Cover support added """
class SetDigitalOutputOpenMessage(domipy.Command):
    def __init__(self, moduleType, serialNumber, channel):
        domipy.Command.__init__(self, moduleType, serialNumber, channel*2, "%H")

class SetDigitalOutputCloseMessage(domipy.Command):
    def __init__(self, moduleType, serialNumber, channel):
        domipy.Command.__init__(self, moduleType, serialNumber, channel*2 + 1, "%L")

class SetDigitalOutputStopMessage(domipy.Command):
    def __init__(self, moduleType, serialNumber, channel):
        domipy.Command.__init__(self, moduleType, serialNumber, channel*2, "%O")
