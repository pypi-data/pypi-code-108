from simses.commons.log import Logger
from simses.commons.config.simulation.energy_management import EnergyManagementConfig
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.state.energy_management import EnergyManagementState
from simses.commons.state.system import SystemState
from simses.logic.energy_management.strategy.operation_priority import OperationPriority
from simses.logic.energy_management.strategy.operation_strategy import OperationStrategy


class IntradayMarketRecharge(OperationStrategy):
    """
    If the SOC falls below a predefined lower limit or it exceeds an upper limit the \gls{bess} charges or
    discharges by trading energy on the electricity market, in particular the IDM.
    """

    __IDM_TRANSACTION_TIME = 900  # s, 15 min blocks of IDM
    __IDM_LEAD_TIME = 1800  # s, 30 min lead time for IDM transactions

    def __init__(self, general_config: GeneralSimulationConfig, fcr_config: EnergyManagementConfig):
        super().__init__(OperationPriority.LOW)
        self.__log: Logger = Logger(type(self).__name__)
        self.__timestep_start = general_config.start
        if self.__IDM_TRANSACTION_TIME % general_config.timestep != 0:
            self.__log.warn('Timestep is not a least common multiple of the IDM transaction time. '
                            'Thus, the results are distorted and are not valid. '
                            'Rethink your timestep')

        self.__max_idm_power = fcr_config.max_idm_power  # W
        self.__max_fcr_power = fcr_config.max_fcr_power  # W
        self.__soc_max_system = fcr_config.max_soc  # Upper SOC of the system in p.u
        self.__soc_min_system = fcr_config.min_soc  # Lower SOC of the system in p.u
        self.__fcr_reserve = fcr_config.fcr_reserve  # h
        self.__flag_idm_charge = False  # Flag, if IDM is necessary to charge the storage system
        self.__flag_idm_discharge = False  # Flag, if IDM is necessary to discharge the storage system
        self.__idm_power_fcr = 0  # Factor for IDM transaction (0 or 1 at fcr application)
        self.__idm_wait_time = 0  # Counter until idm market starts

    def next(self, time: float, system_state: SystemState, power: float = 0) -> float:
        timestep = time - self.__timestep_start
        self.__timestep_start = time
        total_capacity = system_state.capacity  # Wh
        soc_min = self.__fcr_reserve * self.__max_fcr_power / total_capacity + self.__soc_min_system
        soc_max = (total_capacity - self.__fcr_reserve * self.__max_fcr_power) / total_capacity - \
                  (1 - self.__soc_max_system)
        if time % self.__IDM_TRANSACTION_TIME == 0 and\
                not (self.__flag_idm_discharge or self.__flag_idm_charge):  # check all 15 min, if IDM is necessary
            if system_state.soc < soc_min:
                self.__flag_idm_charge = True
            elif system_state.soc > soc_max:
                self.__flag_idm_discharge = True
        elif self.__flag_idm_charge or self.__flag_idm_discharge:
            self.__idm_wait_time += timestep
        else:
            return 0

        if self.__IDM_LEAD_TIME <= self.__idm_wait_time < self.__IDM_LEAD_TIME + self.__IDM_TRANSACTION_TIME:  # 15 min IDM market
            if self.__flag_idm_charge:
                self.__idm_power_fcr = 1
            else:
                self.__idm_power_fcr = -1
        elif self.__idm_wait_time >= self.__IDM_LEAD_TIME:  # IDM finished. Reset variables
            self.__flag_idm_discharge = False
            self.__flag_idm_charge = False
            self.__idm_wait_time = 0
            self.__idm_power_fcr = 0
            return 0

        return self.__max_idm_power * self.__idm_power_fcr

    def update(self, energy_management_state: EnergyManagementState) -> None:
        energy_management_state.idm_power = self.__max_idm_power * self.__idm_power_fcr

    def clear(self) -> None:
        self.__idm_power_fcr = 0.0

    def close(self) -> None:
        pass
