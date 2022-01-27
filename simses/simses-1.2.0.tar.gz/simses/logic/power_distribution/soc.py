from simses.commons.state.system import SystemState
from simses.logic.power_distribution.power_distributor import PowerDistributor


class SocBasedPowerDistributor(PowerDistributor):

    """
    The SocBasedPowerDistributor calculates the power share to the systems via an inverse distance weighting algorithm
    according to the system SOC. In charge case, the system with lower SOC receives a higher load - in discharge case
    vice versa.
    """

    __SHARE = 1e-12

    def __init__(self):
        super().__init__()
        self.__reverse_sum: float = 0.0
        self.__sum: float = 0.0

    def set(self, time: float, states: [SystemState], power) -> None:
        sum = 0.0
        reverse_sum = 0.0
        for state in states:
            sum += self.__get_value_from(state)
            reverse_sum += 1.0 / self.__get_value_from(state)
        self.__sum = sum
        self.__reverse_sum = reverse_sum

    def get_power_for(self, power: float, state: SystemState) -> float:
        if self.__is_charge(power):
            # inverse distance weighting for charging
            share: float = (1.0 / self.__get_value_from(state)) / self.__reverse_sum
        else:
            share: float = self.__get_value_from(state) / self.__sum
        return power * share

    def __get_value_from(self, state: SystemState) -> float:
        return max(state.soc, self.__SHARE)

    def __is_charge(self, power: float) -> bool:
        return power > 0
