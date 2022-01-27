from simses.commons.timeseries.interpolation.interpolation import Interpolation
from simses.commons.timeseries.timevalue import TimeValue


class LinearInterpolation(Interpolation):
    """
    Linear interpolation behaviour
    """

    def __init__(self):
        super().__init__()

    def interpolate(selfself, time: float, recent: TimeValue, last: TimeValue) -> float:
        factor = (time - last.time) / (recent.time - last.time)
        return factor * recent.value + (1 - factor) * last.value

    def close(self) -> None:
        pass
