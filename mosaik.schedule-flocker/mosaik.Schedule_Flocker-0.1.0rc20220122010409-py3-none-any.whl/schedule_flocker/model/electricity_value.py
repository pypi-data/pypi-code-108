import attr
from attr.validators import instance_of


@attr.s
class ElectricityValue(object):
    stepSize: int = attr.ib(validator=instance_of(int))
    # no validator since power reactive power, active power and start time
    # may be floats or integer for now
    powerActive = attr.ib()
    powerReactive = attr.ib()
    startTime = attr.ib()

    def __getitem__(self, key):
        if key == 'start_time' or key == 'startTime':
            return self.startTime
        elif key == 'step_size' or key == 'stepSize':
            return self.stepSize
        elif key == 'power_active' or key == 'powerActive':
            return self.powerActive
        elif key == 'power_reactive' or key == 'powerReactive':
            return self.powerReactive
        else:
            raise ValueError("Invalid key passed")

    def __setitem__(self, key, value):
        if key == 'start_time' or key == 'startTime':
            self.startTime = value
        elif key == 'step_size' or key == 'stepSize':
            self.stepSize = value
        elif key == 'power_active' or key == 'powerActive':
            self.powerActive = value
        elif key == 'power_reactive' or key == 'powerReactive':
            self.powerReactive = value
        else:
            raise ValueError("Invalid key passed")

    def __mul__(self, other):
        self.powerActive *= other
        return self

    @property
    def value(self):
        return self.powerActive

    @value.setter
    def value(self, value):
        self.powerActive = value
