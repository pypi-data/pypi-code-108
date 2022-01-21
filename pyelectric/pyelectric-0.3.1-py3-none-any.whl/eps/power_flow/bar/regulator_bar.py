from . import Bar


class RegulatorBar(Bar):
    voltage_module: float
    active_power: float

    def __init__(self, name: str, voltage_module: float, active_power: float):
        super().__init__(name)
        self.voltage_module = voltage_module
        self.active_power = active_power
