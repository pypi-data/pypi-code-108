"""
:author: Zilvinas Binisevicius <zilvinas@binis.me>
"""
import domipy
from domipy.messages import SetAnalogOutputMessage

class SetDimmer(SetAnalogOutputMessage):

    def __init__(self, serialNumber, value):
        SetAnalogOutputMessage.__init__(self, "DIM", serialNumber, "%D", value)

class StartDimmer(domipy.Command):
    """
        Start dimmer action
    """
    def __init__(self, serialNumber):
        domipy.Command.__init__(self, "DIM", serialNumber, "%DB")

class StopDimmer(domipy.Command):
    """
        Stop dimmer action
    """
    def __init__(self, serialNumber):
        domipy.Command.__init__(self, "DIM", serialNumber, "%DE")

class IncrementDimmer(domipy.Command):
    """
        Increment dimmer
    """
    def __init__(self, serialNumber, value):
        domipy.Command.__init__(self, "DIM", serialNumber, "%I%D", value)

class DecrementDimmer(domipy.Command):
    """
        Decrement dimmer
    """
    def __init__(self, serialNumber, value):
        domipy.Command.__init__(self, "DIM", serialNumber, "%O%D", value)
