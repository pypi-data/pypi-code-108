from datetime import datetime

from simses.commons.log import Logger
from simses.commons.state.system import SystemState
from simses.commons.utils.utilities import format_float
from simses.logic.power_distribution.power_distributor import PowerDistributor
from simses.logic.power_distribution.state import PowerDistributorState


class TechnologyBasedPowerDistributor(PowerDistributor):

    """
    TechnologyBasedPowerDistributor distributes the power depend on the current state and storage technology used.
    A priority list for the technology is used for the order of execution. In addition, TechnologyBasedPowerDistributor
    tries to rebalance the SOC of the various storage devices if possible.
    """

    __SOC_REGULAR_MAX: float = 0.75
    __SOC_REGULAR_MIN: float = 0.25
    __SOC_MAX: float = 0.99
    __SOC_MIN: float = 0.01
    __SOC_THRESHOLD: float = 0.05
    __SOC_TARGET: float = 0.52

    __MIN_REBALANCE_POWER: float = 11000  # W

    __DO_LOG: bool = False
    __DO_REBALANCING: bool = True
    __BALANCE_LOWER_PRIORITY: bool = True
    __BALANCE_ONLY_ONE_DIRECTION: bool = True

    def __init__(self, priorities: [str], storage_systems: dict):
        super().__init__()
        self.__log: Logger = Logger(type(self).__name__)
        self.__states: [PowerDistributorState] = list()
        for priority in priorities:
            for system_id, technology in storage_systems.items():
                if technology == priority:
                    self.__states.append(PowerDistributorState(sys_id=system_id, storage_technology=technology))

    def set(self, time: float, states: [SystemState], power) -> None:
        for state in states:
            pd_state: PowerDistributorState = self.__get_pd_state_for(state)
            pd_state.max_charge_power = state.max_charge_power
            pd_state.max_discharge_power = state.max_discharge_power
            pd_state.soc = state.soc
            pd_state.capacity = state.capacity
            pd_state.time_delta = time - state.time
            pd_state.rebalance_charge_power = 0.0
            pd_state.rebalance_discharge_power = 0.0

    def __soc_max_discharge_power(self, state: PowerDistributorState) -> float:
        denergy = max(0.0, state.soc - self.__SOC_TARGET) * state.capacity
        power = denergy / state.time_delta * 3600.0
        return power

    def __soc_max_charge_power(self, state: PowerDistributorState) -> float:
        denergy = max(0.0, self.__SOC_TARGET - state.soc) * state.capacity
        power = denergy / state.time_delta * 3600.0
        return power

    def __get_pd_state_for(self, state: SystemState) -> PowerDistributorState:
        id: int = self.__get_id_from(state)
        for pd_state in self.__states:
            if pd_state.sys_id == id:
                return pd_state
        self.__log.error('No state found for dc system id ' + str(id))

    def __get_id_from(self, state: SystemState) -> int:
        return int(state.get(SystemState.SYSTEM_DC_ID))

    def __is_charge(self, power: float) -> bool:
        return power > 0.0

    def __search_rebalance_partner(self, rebalance_charge_power: dict, rebalance_discharge_power: dict) -> None:
        for pd_state_charge in self.__states:
            priority_charge: int = self.__states.index(pd_state_charge)
            for pd_state_discharge in self.__states:
                priority_discharge: int = self.__states.index(pd_state_discharge)
                if pd_state_charge.sys_id == pd_state_discharge.sys_id:
                    continue
                if self.__BALANCE_ONLY_ONE_DIRECTION:
                    if self.__BALANCE_LOWER_PRIORITY:
                        if priority_discharge >= priority_charge:
                            continue
                    else:
                        if priority_discharge <= priority_charge:
                            continue
                if pd_state_charge.soc + self.__SOC_THRESHOLD < self.__SOC_REGULAR_MIN < pd_state_discharge.soc - self.__SOC_THRESHOLD \
                        or pd_state_charge.soc + self.__SOC_THRESHOLD < self.__SOC_REGULAR_MAX < pd_state_discharge.soc - self.__SOC_THRESHOLD:
                    possible_charge_power: float = rebalance_charge_power[pd_state_charge.sys_id]
                    possible_discharge_power: float = rebalance_discharge_power[pd_state_discharge.sys_id]
                    possible_charge_power = max(0.0, min(possible_charge_power, self.__soc_max_charge_power(pd_state_charge)))
                    possible_discharge_power = max(0.0, min(possible_discharge_power, self.__soc_max_discharge_power(pd_state_discharge)))
                    possible_charge_power -= pd_state_charge.rebalance_charge_power
                    possible_discharge_power -= pd_state_discharge.rebalance_discharge_power
                    possible_recharge: float = max(0.0, min(possible_charge_power, possible_discharge_power))
                    if possible_recharge > self.__MIN_REBALANCE_POWER:
                        pd_state_charge.rebalance_charge_power += possible_recharge
                        pd_state_discharge.rebalance_discharge_power += possible_recharge

    def __get_regular_charge_power(self, state: PowerDistributorState) -> float:
        return 0.0 if state.soc > self.__SOC_REGULAR_MAX else state.max_charge_power

    def __get_max_charge_power(self, state: PowerDistributorState) -> float:
        return 0.0 if state.soc > self.__SOC_MAX else state.max_charge_power

    def __get_regular_discharge_power(self, state: PowerDistributorState) -> float:
        return 0.0 if state.soc < self.__SOC_REGULAR_MIN else state.max_discharge_power

    def __get_max_discharge_power(self, state: PowerDistributorState) -> float:
        return 0.0 if state.soc < self.__SOC_MIN else state.max_discharge_power

    def __get_regular_power_from(self, is_charge: bool, state: PowerDistributorState) -> float:
        if is_charge:
            return self.__get_regular_charge_power(state)
        else:
            return self.__get_regular_discharge_power(state)

    def __get_max_power_from(self, is_charge: bool, state: PowerDistributorState) -> float:
        if is_charge:
            return self.__get_max_charge_power(state)
        else:
            return self.__get_max_discharge_power(state)

    def get_power_for(self, power_target: float, state: SystemState) -> float:
        is_charge: bool = self.__is_charge(power_target)
        remaining_power: float = abs(power_target)
        local_power: float = 0.0
        emergency_power: float = 0.0
        balancing_power: float = 0.0
        id: int = self.__get_id_from(state)
        rebalance_charge_power: dict = dict()
        rebalance_discharge_power: dict = dict()
        for pd_state in self.__states:
            regular_available_power: float = self.__get_regular_power_from(is_charge, pd_state)
            allocation_power: float = max(0.0, min(remaining_power, regular_available_power))
            if pd_state.sys_id == id:
                local_power = allocation_power
                remaining_power -= abs(local_power)
            else:
                remaining_power -= allocation_power
            if is_charge:
                rebalance_charge_power[pd_state.sys_id] = regular_available_power - allocation_power
                rebalance_discharge_power[pd_state.sys_id] = self.__get_regular_discharge_power(pd_state)
            else:
                rebalance_charge_power[pd_state.sys_id] = self.__get_regular_charge_power(pd_state)
                rebalance_discharge_power[pd_state.sys_id] = regular_available_power - allocation_power
        if remaining_power > 0.0:
            for pd_state in self.__states:
                max_available_power: float = self.__get_max_power_from(is_charge, pd_state)
                if pd_state.sys_id == id:
                    emergency_power = max(0.0, min(remaining_power, max_available_power - local_power))
                    remaining_power -= abs(emergency_power)
                else:
                    regular_available_power: float = self.__get_regular_power_from(is_charge, pd_state)
                    remaining_power -= min(remaining_power, max_available_power - regular_available_power)
                rebalance_charge_power[pd_state.sys_id] = 0.0
                rebalance_discharge_power[pd_state.sys_id] = 0.0
        if self.__DO_REBALANCING:
            self.__search_rebalance_partner(rebalance_charge_power, rebalance_discharge_power)
            pd_state: PowerDistributorState = self.__get_pd_state_for(state)
            balancing_power = pd_state.rebalance_charge_power - pd_state.rebalance_discharge_power
            if abs(balancing_power) > 0.0 and self.__DO_LOG:
                self.__log.error('Rebalancing ' + str(id) + ' with ' + str(int(balancing_power/1000.0)) + ' kW, '
                                    'SOC:' + format_float(state.soc) + ' @ ' + str(datetime.fromtimestamp(state.time)))
        local_power += emergency_power
        if is_charge:
            return local_power + balancing_power
        else:
            return -local_power + balancing_power

    def close(self):
        self.__log.close()
