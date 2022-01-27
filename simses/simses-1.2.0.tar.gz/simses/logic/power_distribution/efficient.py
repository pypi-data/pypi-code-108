import numpy

from simses.commons.state.system import SystemState
from simses.logic.power_distribution.power_distributor import PowerDistributor
from simses.logic.power_distribution.state import PowerDistributorState


class EfficientPowerDistributor(PowerDistributor):

    """
    EqualPowerDistributor distributes the power equally to all system independent of their current state.
    """

    __SOC_MIN: float = 0.0
    __SOC_MAX: float = 0.99

    __MIN_POWER_SHARE: float = 0.0

    def __init__(self, max_pe_power: float):
        super().__init__()
        self.__pd_states: [PowerDistributorState] = list()
        self.__MIN_POWER: float = max_pe_power * self.__MIN_POWER_SHARE

    def set(self, time: float, states: [SystemState], power) -> None:
        for state in states:
            pd_state: PowerDistributorState = self.__get_pd_state_for(state)
            pd_state.soc = state.soc
            pd_state.max_charge_power = 0.0 if state.soc > self.__SOC_MAX else state.max_charge_power
            pd_state.max_discharge_power = 0.0 if state.soc < self.__SOC_MIN else state.max_discharge_power

    def __get_id_from(self, state: SystemState) -> int:
        return int(state.get(SystemState.SYSTEM_DC_ID))

    def __get_pd_state_for(self, state: SystemState) -> PowerDistributorState:
        id: int = self.__get_id_from(state)
        for pd_state in self.__pd_states:
            if pd_state.sys_id == id:
                return pd_state
        pd_state: PowerDistributorState = PowerDistributorState(sys_id=id)
        self.__pd_states.append(pd_state)
        return pd_state

    def __is_charge(self, power: float) -> bool:
        return power > 0.0

    def get_power_for(self, power: float, state: SystemState) -> float:
        if abs(power) < self.__MIN_POWER:
            return 0.0
        equal_power_distribution: float = abs(power) / len(self.__pd_states)
        is_charge: bool = self.__is_charge(power)
        id: int = self.__get_id_from(state)
        local_power: float = 0.0
        remaining_power_allocation: float = 0.0
        for pd_state in self.__pd_states:
            available_power: float = max(0.0, min(equal_power_distribution, pd_state.max_charge_power if is_charge else pd_state.max_discharge_power))
            remaining_power_allocation += max(0.0, equal_power_distribution - available_power)
            if pd_state.sys_id == id:
                local_power = available_power
        if remaining_power_allocation > 0.0:
            for pd_state in self.__pd_states:
                available_power: float = pd_state.max_charge_power if is_charge else pd_state.max_discharge_power
                power_allocation = max(0.0, min(remaining_power_allocation, available_power - equal_power_distribution))
                remaining_power_allocation -= power_allocation
                if pd_state.sys_id == id:
                    local_power += power_allocation
        return local_power * numpy.sign(power)
