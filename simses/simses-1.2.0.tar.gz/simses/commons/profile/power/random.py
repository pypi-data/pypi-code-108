from random import Random

from simses.commons.profile.power.power_profile import PowerProfile


class RandomPowerProfile(PowerProfile):
    """
    RandomPowerProfile is a specific implementation of PowerProfile. It delivers a random power value for each timestep.
    Power series are reproducable - the used Random class uses the a specific seed for calculating random numbers.
    """

    def __init__(self, start_time: float, max_power: float = 1500.0, power_offset: float = 0.0,
                 scaling_factor: float = 1.0, time_increment: float = 1.0):
        """
        Constructor for RandomPowerProfile

        Parameters
        ----------
        max_power :
            cut off power in W for positive and negative values, default: 1500.0
        power_offset :
            power offset in W around which the random values are floating, default: 0.0
        scaling_factor :
            linear scaling of values, default: 1
        """
        super().__init__()
        self.__power: float = 0.0  # W
        self.__max_power: float = max_power  # W
        self.__d_power: float = max_power / 10.0  # W
        self.__random: Random = Random(93823341)
        self.__scaling_factor: float = scaling_factor
        self.__power_offset: float = power_offset
        self.__time: float = start_time
        self.__time_increment: float = time_increment

    def next(self, time: float) -> float:
        average: [float] = list()
        while self.__time <= time:
            dpower = self.__random.uniform(-self.__d_power, self.__d_power)
            self.__power = max(-self.__max_power, min(self.__max_power, self.__power + dpower))
            average.append(self.__power)
            self.__time += self.__time_increment
        power = sum(average) / len(average) if average else self.__power
        return power * self.__scaling_factor + self.__power_offset

    def close(self) -> None:
        pass
