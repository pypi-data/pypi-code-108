from simses.commons.log import Logger
from simses.commons.timeseries.interpolation.interpolation import Interpolation
from simses.commons.timeseries.timevalue import TimeValue


class LastValue(Interpolation):

    """
    Returns last value of given time range
    """

    def __init__(self):
        super().__init__()
        self.__log: Logger = Logger(type(self).__name__)

    def interpolate(self, time: float, recent: TimeValue, last: TimeValue) -> float:
        if time >= recent.time:
            return recent.value
        elif time >= last.time:
            return last.value
        else:
            self.__log.error('No value found for ' + str(time))
            return last.value

    def close(self) -> None:
        self.__log.close()
