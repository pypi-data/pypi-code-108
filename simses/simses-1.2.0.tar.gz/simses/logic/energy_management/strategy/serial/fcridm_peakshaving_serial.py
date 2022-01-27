from datetime import datetime

from simses.commons.config.simulation.energy_management import EnergyManagementConfig
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.config.simulation.profile import ProfileConfig
from simses.commons.profile.power.power_profile import PowerProfile
from simses.commons.state.energy_management import EnergyManagementState
from simses.commons.state.system import SystemState
from simses.logic.energy_management.strategy.basic.peak_shaving_yapsa import YetAnotherPeakShavingAlgorithm
from simses.logic.energy_management.strategy.operation_priority import OperationPriority
from simses.logic.energy_management.strategy.operation_strategy import OperationStrategy
from simses.logic.energy_management.strategy.stacked.fcr_idm_recharge_stacked import \
    FcrIdmRechargeStacked


class FcrIdmPeakShavingSerial(OperationStrategy):

    __FCR_START = 8  # h
    __FCR_STOP = 15  # h

    def __init__(self, general_config: GeneralSimulationConfig, ems_config: EnergyManagementConfig,
                 profile_config: ProfileConfig, power_profile: PowerProfile):
        super().__init__(OperationPriority.VERY_HIGH)
        self.__fcr_idm_strategy: OperationStrategy = FcrIdmRechargeStacked(general_config, ems_config, profile_config)
        self.__peak_shaving_strategy: OperationStrategy = YetAnotherPeakShavingAlgorithm(power_profile, ems_config)
        self.__strategies: [OperationStrategy] = list()
        self.__strategies.append(self.__fcr_idm_strategy)
        self.__strategies.append(self.__peak_shaving_strategy)

    def next(self, time: float, system_state: SystemState, power: float = 0) -> float:
        tstmp = datetime.utcfromtimestamp(time)
        hour = tstmp.hour + tstmp.minute / 60. + tstmp.second / 3600.
        power_peak_shaving = self.__peak_shaving_strategy.next(time, system_state, power)
        power_fcr = self.__fcr_idm_strategy.next(time, system_state, power)
        if self.__FCR_START <= hour < self.__FCR_STOP:
            self.__peak_shaving_strategy.clear()
            return power_fcr
        else:
            self.__fcr_idm_strategy.clear()
            return power_peak_shaving

    def update(self, energy_management_state: EnergyManagementState) -> None:
        for strategy in self.__strategies:
            strategy.update(energy_management_state)

    def clear(self) -> None:
        for strategy in self.__strategies:
            strategy.clear()

    def close(self) -> None:
        for strategy in self.__strategies:
            strategy.close()
