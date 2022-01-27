from simses.commons.log import Logger
from simses.commons.state.technology.redox_flow import RedoxFlowState
from simses.technology.redox_flow.pump_algorithm.abstract_pump_algorithm import PumpAlgorithm
from simses.technology.redox_flow.stack.electrolyte.abstract_electrolyte import ElectrolyteSystem
from simses.technology.redox_flow.stack.abstract_stack import StackModule


class ConstantPressurePulsed(PumpAlgorithm):
    """Pump algorithm with a fix pressure drop that pulses the discharge and charge flow rate for a certain time period
    when the voltage is drops below the minimal voltage (discharging) or rises above the maximal voltage (charging)."""

    """The value for the pressure drop needs to be specified for the selected stack module. This pump algorithm should 
    only be used when the selected stack type considers changes in the internal resistance due to the pump stops. This
    is currently implemented for the stack modules IndustrialStack1500W and IndustrialStack9000W."""
    __PRESSURE_DROP = 16000  # Pa
    __PUMP_TIME = 90  # s

    def __init__(self, stack_module: StackModule, pump, electrolyte_system: ElectrolyteSystem, time_step: int):
        super().__init__(pump)
        self.__log: Logger = Logger(type(self).__name__)
        self.__stack_module: StackModule = stack_module
        self.__electrolyte_system: ElectrolyteSystem = electrolyte_system
        self.__pressure_drop_anolyte = self.__PRESSURE_DROP
        self.__pressure_drop_catholyte = self.__PRESSURE_DROP
        self.__pump_time = self.__PUMP_TIME
        self.__hydraulic_resistance = stack_module.get_hydraulic_resistance()
        self.__max_voltage = self.__stack_module.get_max_voltage()
        self.__min_voltage = self.__stack_module.get_min_voltage()
        self.__time_step = time_step

    def get_pressure_drop_catholyte(self, redox_flow_state: RedoxFlowState):
        voltage = redox_flow_state.voltage
        power = redox_flow_state.power
        time_pump = redox_flow_state.time_pump

        if (((voltage >= self.__max_voltage or voltage <= self.__min_voltage) or 0 < time_pump < self.__pump_time) and
                power != 0):
            self.__pressure_drop_catholyte = self.__PRESSURE_DROP
            if time_pump < 0:
                time_pump = 0
            time_pump += self.__time_step
        else:
            self.__pressure_drop_catholyte = 0
            if time_pump > 0:
                time_pump = 0
            time_pump -= self.__time_step

        redox_flow_state.time_pump = time_pump
        return self.__pressure_drop_catholyte

    def get_pressure_drop_anolyte(self, redox_flow_state: RedoxFlowState):
        voltage = redox_flow_state.voltage
        power = redox_flow_state.power
        time_pump = redox_flow_state.time_pump

        if (((voltage > self.__max_voltage or voltage < self.__min_voltage) or 0 < time_pump < self.__pump_time)
                and power != 0):
            self.__pressure_drop_anolyte = self.__PRESSURE_DROP
        else:
            self.__pressure_drop_anolyte = 0

        return self.__pressure_drop_anolyte

    def get_flow_rate_anolyte(self, redox_flow_state: RedoxFlowState):
        flow_rate = (self.__pressure_drop_catholyte / (self.__hydraulic_resistance *
                     self.__electrolyte_system.get_viscosity_anolyte(redox_flow_state)))
        return flow_rate

    def get_flow_rate_catholyte(self, redox_flow_state: RedoxFlowState):
        flow_rate = (self.__pressure_drop_catholyte / (self.__hydraulic_resistance *
                     self.__electrolyte_system.get_viscosity_catholyte(redox_flow_state)))
        return flow_rate

    def get_flow_rate_max(self):
        flow_rate_max = (self.__PRESSURE_DROP / (self.__hydraulic_resistance *
                         self.__electrolyte_system.get_min_viscosity()))
        return flow_rate_max

    def get_flow_rate_min(self):
        flow_rate_min = (self.__PRESSURE_DROP / (self.__hydraulic_resistance *
                         self.__electrolyte_system.get_max_viscosity()))
        return flow_rate_min

    def close(self):
        super().close()
        self.__log.close()
        self.__stack_module.close()
        self.__electrolyte_system.close()
