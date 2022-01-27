from simses.commons.profile.power.generation import GenerationProfile
from simses.commons.state.energy_management import EnergyManagementState
from simses.commons.state.system import SystemState
from simses.logic.energy_management.strategy.operation_priority import OperationPriority
from simses.logic.energy_management.strategy.operation_strategy import OperationStrategy


class UseAllRenewableEnergy(OperationStrategy):
    """
    This operation strategy is for a plant that uses the whole energy provided by a renewable energy source.
    This strategy is implemented especially for an electrolyzer which produces hydrogen with the energy out
    of a solar or a wind energy plant.
    """
    def __init__(self, pv_generation_profile: GenerationProfile):
        super().__init__(OperationPriority.MEDIUM)
        self.__pv_profile: GenerationProfile = pv_generation_profile
        self.__pv_power = 0
        self.__load_power = 0

    def next(self, time: float, system_state: SystemState, power: float = 0) -> float:
        self.__pv_power = self.__pv_profile.next(time)
        return self.__pv_power

    def update(self, energy_management_state: EnergyManagementState) -> None:
        energy_management_state.pv_power = self.__pv_power
        energy_management_state.load_power = self.__load_power

    def clear(self) -> None:
        self.__pv_power = 0.0
        self.__load_power = 0.0

    def close(self) -> None:
        self.__pv_profile.close()