from simses.commons.log import Logger
from simses.commons.state.technology.hydrogen import HydrogenState
from simses.commons.utils.utilities import format_float
from simses.commons.config.simulation.hydrogen import HydrogenConfig


class HydrogenManagementSystem:

    def __init__(self, min_power_electroyzer: float, max_power_electrolyzer: float, max_power_fuel_cell: float, config: HydrogenConfig):
        self.__log: Logger = Logger(type(self).__name__)
        self.__min_charge_power: float = min_power_electroyzer
        self.__max_charge_power: float = max_power_electrolyzer  # max power is greater than nominal power
        self.__max_discharge_power: float = - max_power_fuel_cell  # max power is greater than nominal power
        self.__max_soc: float = config.max_soc
        self.__min_soc: float = config.min_soc

    def update(self, time: float, state: HydrogenState) -> None:
        """Updating power and fulfillment factor in order to check restrictions"""
        power_target = state.power
        state.power = self.__get_max_power(time, state)
        self.__set_fulfillment(power_target, state)

    def __get_max_power(self, time: float, state: HydrogenState) -> float:
        if not self.__power_in_range(state):
            self.__log.warn("Power out of range: " + format_float(state.power))
        power = max(min(state.power, self.__max_charge_power), self.__max_discharge_power)
        if 0 < power < self.__min_charge_power:
            power = 0
        soc_charge_power = self.__soc_max_charge_power(time, state)
        soc_discharge_power = self.__soc_max_discharge_power(time, state)
        if not soc_discharge_power < power < soc_charge_power:
            self.__log.warn('Power is limited due to SOC.')
        power = max(min(power, soc_charge_power), soc_discharge_power)
        return power

    def __power_in_range(self, state: HydrogenState):
        return self.__max_discharge_power < state.power < self.__max_charge_power # TODO Sign Error?

    def __soc_max_charge_power(self, time: float, state: HydrogenState) -> float:
        denergy = (self.__max_soc - state.soc) * state.capacity
        power = denergy / (time - state.time) * 3600
        return max(0.0, power)

    def __soc_max_discharge_power(self, time: float, state: HydrogenState) -> float:
        denergy = (state.soc - self.__min_soc) * state.capacity
        power = denergy / (time - state.time) * 3600
        return min(0.0, -power)

    def __set_fulfillment(self, power_target: float, state: HydrogenState) -> None:
        power_is = state.power
        if abs(power_is - power_target) < 1e-8:
            state.fulfillment = 1.0
        elif power_target == 0:
            self.__log.error('Power should be 0, but is ' + str(power_is) + ' W. Check BMS function')
            state.fulfillment = 0.0
        else:
            state.fulfillment = abs(power_is / power_target)
            if state.fulfillment < 0.0 or state.fulfillment > 1.0:
                self.__log.error('Fulfillment should be between 0 and 1 , but is ' +
                                 format_float(state.fulfillment) + ' p.u.. Check BMS function')

    def close(self) -> None:
        """Closing all resources"""
        self.__log.close()
