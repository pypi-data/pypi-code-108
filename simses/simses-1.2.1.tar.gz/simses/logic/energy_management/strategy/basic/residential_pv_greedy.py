from simses.commons.profile.power.generation import GenerationProfile
from simses.commons.profile.power.power_profile import PowerProfile
from simses.commons.state.energy_management import EnergyManagementState
from simses.commons.state.system import SystemState
from simses.logic.energy_management.strategy.operation_priority import OperationPriority
from simses.logic.energy_management.strategy.operation_strategy import OperationStrategy


class ResidentialPvGreedy(OperationStrategy):
    """
    Operation Strategy for a residential home storage system in combination with PV generation.
    The algorithm fills the BESS as fast as possible without consideration for the grid by meeting the residual load
    at all times.
    """

    def __init__(self, power_profile: PowerProfile, pv_generation_profile: GenerationProfile):
        super().__init__(OperationPriority.MEDIUM)
        self.__load_profile: PowerProfile = power_profile
        self.__pv_profile: GenerationProfile = pv_generation_profile
        self.__pv_power = 0
        self.__load_power = 0

    def next(self, time: float, system_state: SystemState, power: float = 0) -> float:
        self.__load_power = self.__load_profile.next(time)
        self.__pv_power = self.__pv_profile.next(time)
        residual_charge_power = self.__pv_power - self.__load_power
        return residual_charge_power

    def update(self, energy_management_state: EnergyManagementState) -> None:
        energy_management_state.pv_power = self.__pv_power
        energy_management_state.load_power = self.__load_power

    def clear(self) -> None:
        self.__pv_power = 0.0
        self.__load_power = 0.0

    def close(self) -> None:
        self.__load_profile.close()
        self.__pv_profile.close()
