import math
from datetime import datetime

from simses.system.auxiliary.auxiliary import Auxiliary
from simses.system.dc_coupling.generation.dc_generation import DcGeneration


class PvDcGeneration(DcGeneration):

    """
    PvDcGeneration provides a basic algorithm imitating a pv plant with the same power each day.
    """

    def __init__(self, peak_power: float):
        super().__init__()
        self.__power = 0.0
        self.__peak_power: float = peak_power
        self.__peak_time: float = 12.0  # hour of day
        self.__time_variance: float = 1.0  # hour

    def get_power(self) -> float:
        return self.__power

    def calculate_power(self, time: float) -> None:
        tstmp = datetime.utcfromtimestamp(time)
        hour = tstmp.hour + tstmp.minute / 60. + tstmp.second / 3600.
        if 6 < hour < 18:
            self.__power = self.__peak_power * self.__daily_power_distribution_of(hour)
        else:
            self.__power = 0.0

    def __daily_power_distribution_of(self, hour: float) -> float:
        return math.exp(-.5 * ((hour - self.__peak_time) / self.__time_variance)**2) \
               / (self.__time_variance * math.sqrt(2*math.pi))

    def get_auxiliaries(self) -> [Auxiliary]:
        return list()

    def close(self):
        pass
