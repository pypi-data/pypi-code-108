from simses.commons.state.system import SystemState
from simses.logic.power_distribution.power_distributor import PowerDistributor


class EqualPowerDistributor(PowerDistributor):

    """
    EqualPowerDistributor distributes the power equally to all system independent of their current state.
    """

    def __init__(self):
        super().__init__()
        self.__number: float = 1.0

    def set(self, time: float, states: [SystemState], power) -> None:
        self.__number = len(states)

    def get_power_for(self, power: float, state: SystemState) -> float:
        return power / self.__number
