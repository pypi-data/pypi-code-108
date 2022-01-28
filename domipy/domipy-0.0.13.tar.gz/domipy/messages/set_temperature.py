"""
:author: Zilvinas Binisevicius <zilvinas@binis.me>
"""
import domipy


class SetTemperatureMessage(domipy.Command):
    """
    Set temperature
    """
    def __init__(self, moduleType, serialNumber, value):
        domipy.Command.__init__(self, moduleType, serialNumber.strip(), -1, "%T", value)

class SetTemperatureModeMessage(domipy.Command):
    """
    Set temperature mode
    1 - Absense
    2 - Automatic
    5 - COmfort
    6 - Frost
    """
    def __init__(self, moduleType, serialNumber, value):
        domipy.Command.__init__(self, moduleType, serialNumber.strip(), -1,  "%M", value)

class SetTemperatureAutomaticMessage(domipy.Command):
    """
    Set AUTOMATIC mode
    """
    def __init__(self, moduleType, serialNumber):
        domipy.Command.__init__(self, moduleType, serialNumber.strip(), -1, "%M", 2)

class SetTemperatureAbsenceMessage(domipy.Command):
    """
    Set ABSEBSE mode
    """
    def __init__(self, moduleType, serialNumber):
        domipy.Command.__init__(self, moduleType, serialNumber.strip(), -1, "%M", 1)

class SetTemperatureComfortMessage(domipy.Command):
    """
    Set COMFORT mode
    """
    def __init__(self, moduleType, serialNumber):
        domipy.Command.__init__(self, moduleType, serialNumber.strip(), -1, "%M", 5)

class SetTemperatureFrostMessage(domipy.Command):
    """
    Set FROST mode
    """
    def __init__(self, moduleType, serialNumber):
        domipy.Command.__init__(self, moduleType, serialNumber.strip(), -1, "%M", 6)

class SetTemperatureSetPointMessage(domipy.Command):
    """
    Set temperature
    """
    def __init__(self, moduleType, serialNumber, value):
        domipy.Command.__init__(self, moduleType, serialNumber.strip(), -1, "%T", value)
