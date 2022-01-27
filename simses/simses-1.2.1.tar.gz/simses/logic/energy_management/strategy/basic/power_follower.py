from simses.commons.profile.power.power_profile import PowerProfile
from simses.commons.state.energy_management import EnergyManagementState
from simses.commons.state.system import SystemState
from simses.logic.energy_management.strategy.operation_priority import OperationPriority
from simses.logic.energy_management.strategy.operation_strategy import OperationStrategy


class PowerFollower(OperationStrategy):

    """
    PowerFollower is a basic operation strategy which just forwards a given power profile to the storage system.
    """

    def __init__(self, power_profile: PowerProfile):
        super().__init__(OperationPriority.MEDIUM)
        self.__power_profile: PowerProfile = power_profile
        self.__power: float = 0.0

    def next(self, time: float, system_state: SystemState, power: float = 0) -> float:
        self.__power = self.__power_profile.next(time)
        return -1.0 * self.__power

    def update(self, energy_management_state: EnergyManagementState) -> None:
        energy_management_state.load_power = self.__power

    def clear(self) -> None:
        self.__power = 0.0

    def close(self) -> None:
        self.__power_profile.close()
