from simses.commons.log import Logger
from simses.commons.state.technology.redox_flow import RedoxFlowState
from simses.system.auxiliary.pump.abstract_pump import Pump
from simses.technology.redox_flow.pump_algorithm.abstract_pump_algorithm import PumpAlgorithm
from simses.technology.redox_flow.stack.electrolyte.abstract_electrolyte import ElectrolyteSystem
from simses.technology.redox_flow.stack.abstract_stack import StackModule


class FixFlowRateStartStop(PumpAlgorithm):
    """Pump algorithm with a fixed flow rate. The value is area specific."""

    """
    A area specific flow rate of 0.2 ml/min/cm^2 corresponds to a stoichiometric factor of 2 at a current density of
    50 mA/cm^2 at the highest and lowest state-of-charge (SOC) for a SOC range between 20 % and 80 %.
    For higher current densities and broader SOC-ranges the value must be increased.
    """
    __AREA_SPECIFIC_FLOW_RATE = 0.2  # ml/(min cm^2)

    def __init__(self, stack_module: StackModule, pump: Pump, electrolyte_system: ElectrolyteSystem):
        super().__init__(pump)
        self.__log: Logger = Logger(type(self).__name__)
        self.__stack_module: StackModule = stack_module
        self.__electrolyte_system: ElectrolyteSystem = electrolyte_system
        self.__hydraulic_resistance = self.__stack_module.get_hydraulic_resistance()
        self.__flow_rate_anolyte = (self.__AREA_SPECIFIC_FLOW_RATE * self.__stack_module.get_specific_cell_area() /
                                    1000000 / 60 * self.__stack_module.get_cell_per_stack() *
                                    self.__stack_module.get_serial_scale() * self.__stack_module.get_parallel_scale())
        self.__flow_rate_catholyte = (self.__AREA_SPECIFIC_FLOW_RATE * self.__stack_module.get_specific_cell_area() /
                                      1000000 / 60 * self.__stack_module.get_cell_per_stack() *
                                      self.__stack_module.get_serial_scale() * self.__stack_module.get_parallel_scale())

    def get_pressure_drop_catholyte(self, redox_flow_state: RedoxFlowState) -> float:
        pressure_drop = (self.get_flow_rate_catholyte(redox_flow_state) * self.__hydraulic_resistance *
                         self.__electrolyte_system.get_viscosity_catholyte(redox_flow_state))
        self.__log.debug('Pressure drop for catholyte: ' + str(pressure_drop / 10 ** 5) + ' bar')
        return pressure_drop

    def get_pressure_drop_anolyte(self, redox_flow_state: RedoxFlowState) -> float:
        pressure_drop = (self.get_flow_rate_anolyte(redox_flow_state) * self.__hydraulic_resistance *
                         self.__electrolyte_system.get_viscosity_anolyte(redox_flow_state))
        self.__log.debug('Pressure drop for anolyte: ' + str(pressure_drop / 10 ** 5) + ' bar')
        return pressure_drop

    def get_flow_rate_anolyte(self, redox_flow_state: RedoxFlowState) -> float:
        if redox_flow_state.power == 0:
            flow_rate = 0
        else:
            flow_rate = self.__flow_rate_anolyte
        return flow_rate

    def get_flow_rate_catholyte(self, redox_flow_state: RedoxFlowState) -> float:
        if redox_flow_state.power == 0:
            flow_rate = 0
        else:
            flow_rate = self.__flow_rate_catholyte
        return flow_rate

    def get_flow_rate_max(self) -> float:
        return max(self.__flow_rate_anolyte, self.__flow_rate_catholyte)

    def get_flow_rate_min(self) -> float:
        return min(self.__flow_rate_anolyte, self.__flow_rate_catholyte)

    def close(self):
        super().close()
        self.__log.close()
        self.__stack_module.close()
        self.__electrolyte_system.close()
