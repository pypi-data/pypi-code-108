from . import Bar


class LoadBar(Bar):
    active_power: float
    reactive_power: float

    def __init__(self, name: str, active_power: float, reactive_power: float):
        super().__init__(name)
        self.active_power = active_power
        self.reactive_power = reactive_power
        self.power = self.active_power + 1j * self.reactive_power
