import cmath

from . import Bar


class SlackBar(Bar):
    voltage_module: float
    voltage_angle: float

    def __init__(self, name: str, voltage_module: float, voltage_angle: float = 0):
        super().__init__(name)
        self.voltage_module = voltage_module
        self.voltage_angle = voltage_angle
        self.voltage = cmath.rect(self.voltage_module, self.voltage_angle)
