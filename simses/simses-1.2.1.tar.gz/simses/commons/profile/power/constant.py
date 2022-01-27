from simses.commons.profile.power.power_profile import PowerProfile


class ConstantPowerProfile(PowerProfile):

    """
    ConstantPowerProfile delivers a constant power value over time.
    """

    def __init__(self, power: float = 0.0, scaling_factor: float = 1.0):
        """
        Constructor of ConstantPowerProfile

        Parameters
        ----------
        power :
            constant power applied in W, default: 0.0
        scaling_factor :
            linear scaling of values, default: 1.0
        """
        super().__init__()
        self.__power: float = power
        self.__scaling_factor: float = scaling_factor

    def next(self, time: float) -> float:
        return self.__power * self.__scaling_factor

    def close(self) -> None:
        pass
