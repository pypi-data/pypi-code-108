from simses.commons.profile.power.power_profile import PowerProfile
from simses.commons.config.simulation.energy_management import EnergyManagementConfig
from simses.commons.state.energy_management import EnergyManagementState
from simses.commons.state.system import SystemState
from simses.logic.energy_management.strategy.operation_priority import OperationPriority
from simses.logic.energy_management.strategy.operation_strategy import OperationStrategy


class EvChargerWithBuffer(OperationStrategy):
    """
    EvChargerWithBuffer is a basic operation strategy which simulates an EV charging station with a buffer storage.
    The algorithm requires the following profiles and parameters:
    - A load profile that contains the required power for charging the EV
    - The maximal grid power is set in the 'ENERGY_MANAGEMENT' section as 'MAX_POWER'

    Whenever the requested EV power is above the power threshold (depends on data) the EV is charged with the required
    power (Max AC power from grid + buffer storage discharge).
    Whenever the SOC is below the SOC threshold and the power below its threshold the buffer storage is charged with
    the maximal AC power from the grid.
    """

    def __init__(self, power_profile: PowerProfile, ems_config: EnergyManagementConfig):
        super().__init__(OperationPriority.MEDIUM)
        self.__load_profile: PowerProfile = power_profile
        self.__max_ac_grid_power:  float = ems_config.max_power # e.g. 32000
        self.__power: float = 0.0
        self.__soc_threshold: float = 0.98
        self.__power_threshold: float = 50.0

    def next(self, time: float, system_state: SystemState, power: float = 0) -> float:
        self.__power = self.__load_profile.next(time)
        if self.__power > self.__power_threshold or system_state.soc < self.__soc_threshold:
            return self.__max_ac_grid_power - self.__power
        else:
            return 0

    def update(self, energy_management_state: EnergyManagementState) -> None:
        energy_management_state.load_power = self.__power

    def clear(self) -> None:
        self.__power = 0.0

    def close(self) -> None:
        self.__load_profile.close()
