from simses.commons.log import Logger
from simses.commons.config.simulation.redox_flow import RedoxFlowConfig
from simses.commons.state.technology.redox_flow import RedoxFlowState
from simses.system.auxiliary.pump.abstract_pump import Pump
from simses.technology.redox_flow.pump_algorithm.abstract_pump_algorithm import PumpAlgorithm
from simses.technology.redox_flow.stack.electrolyte.abstract_electrolyte import ElectrolyteSystem
from simses.technology.redox_flow.stack.abstract_stack import StackModule


class StoichFlowRate(PumpAlgorithm):
    """Pump algorithm with constant stoichimetric factor. The flow rate is calculated using the stoichimetric factor
    and the maximal still usable state-of-charge (SOC) difference for charging or discharging."""

    __STOICHIOMETRIC_FACTOR = 6

    def __init__(self, stack_module: StackModule, pump: Pump, electrolyte_system: ElectrolyteSystem,
                 redox_flow_config: RedoxFlowConfig):
        super().__init__(pump)
        self.__log: Logger = Logger(type(self).__name__)
        self.__stack_module: StackModule = stack_module
        self.__electrolyte_system: ElectrolyteSystem = electrolyte_system
        self.__redox_flow_config: RedoxFlowConfig = redox_flow_config
        self.__current_max_low_soc = self.__stack_module.get_max_current_low_soc()
        self.__current_max_high_soc = self.__stack_module.get_max_current_high_soc()
        self.__hydraulic_resistance = self.__stack_module.get_hydraulic_resistance()
        self.__stoichiometry = self.__STOICHIOMETRIC_FACTOR
        self.__FARADAY = self.__electrolyte_system.FARADAY

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
        return self.get_flow_rate(redox_flow_state)

    def get_flow_rate_catholyte(self, redox_flow_state: RedoxFlowState) -> float:
        return self.get_flow_rate(redox_flow_state)

    def get_flow_rate(self, redox_flow_state: RedoxFlowState) -> float:
        """
        Calculates the flow rate based on an stoichiometric factor.

        Parameters
        ----------
        redox_flow_state : RedoxFlowState
            Current state of redox_flow.

        Returns
        -------
        float :
            Flow rate in m^3/s.
        """
        if redox_flow_state.is_charge:
            delta_soc = 1 - self.get_soc_begin()
        else:
            delta_soc = self.get_soc_begin()
        if delta_soc < 0.001:
            delta_soc = 0.001
        flow_rate = (self.__stoichiometry * abs(redox_flow_state.current) * self.__stack_module.get_cell_per_stack() *
                     self.__stack_module.get_serial_scale() / (self.__FARADAY *
                     self.__electrolyte_system.get_vanadium_concentration() * delta_soc))
        return flow_rate

    def get_flow_rate_max(self) -> float:
        delta_soc_min_low = self.__redox_flow_config.min_soc
        if delta_soc_min_low == 0:
            delta_soc_min_low = 0.001
        flow_rate_max_low_soc = (self.__stoichiometry * self.__current_max_low_soc *
                                 self.__stack_module.get_cell_per_stack() *
                                 self.__stack_module.get_serial_scale() / (self.__FARADAY *
                                 self.__electrolyte_system.get_vanadium_concentration() * delta_soc_min_low))
        delta_soc_min_high = (1 - self.__redox_flow_config.max_soc)
        if delta_soc_min_high == 0:
            delta_soc_min_high = 0.001
        flow_rate_max_high_soc = (self.__stoichiometry * self.__current_max_high_soc *
                                  self.__stack_module.get_cell_per_stack() *
                                  self.__stack_module.get_serial_scale() / (self.__FARADAY *
                                  self.__electrolyte_system.get_vanadium_concentration() * delta_soc_min_high))
        flow_rate_max = max(flow_rate_max_low_soc, flow_rate_max_high_soc)
        self.__log.debug('Max flow rate: ' + str(flow_rate_max))
        return flow_rate_max

    def get_flow_rate_min(self) -> float:
        flow_rate_min = 0.0
        return flow_rate_min

    def close(self):
        super().close()
        self.__log.close()
        self.__stack_module.close()
        self.__electrolyte_system.close()
