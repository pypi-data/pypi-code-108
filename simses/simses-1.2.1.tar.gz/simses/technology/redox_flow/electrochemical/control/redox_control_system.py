from simses.commons.config.simulation.redox_flow import RedoxFlowConfig
from simses.commons.log import Logger
from simses.commons.state.technology.redox_flow import RedoxFlowState
from simses.technology.redox_flow.pump_algorithm.abstract_pump_algorithm import PumpAlgorithm
from simses.technology.redox_flow.stack.electrolyte.abstract_electrolyte import ElectrolyteSystem
from simses.technology.redox_flow.stack.abstract_stack import StackModule


class RedoxControlSystem:
    """RedoxControlSystem class for redox flow batteries. It contains queries to check whether the operation
    conditions are met."""

    def __init__(self, stack_module: StackModule, electrolyte_system: ElectrolyteSystem, pump_algorithm: PumpAlgorithm,
                 redox_flow_config: RedoxFlowConfig):
        self.__log: Logger = Logger(type(self).__name__)
        self.__stack_module: StackModule = stack_module
        self.__electrolyte_system: ElectrolyteSystem = electrolyte_system
        self.__pump_algorithm: PumpAlgorithm = pump_algorithm
        self.__soc_min = redox_flow_config.min_soc
        self.__soc_max = redox_flow_config.max_soc
        self.__FARADAY = self.__electrolyte_system.FARADAY

    def check_temperature(self, redox_flow_state: RedoxFlowState) -> bool:
        """
        Checks if the temperature of the electrolyte is within the operation range.

        Parameters
        ----------
        redox_flow_state : RedoxFlowState
            Current state of redox_flow.

        Returns
        -------
        bool:
            True if the temperature is within the operation range.
        """
        return (self.__electrolyte_system.get_min_temperature() <= redox_flow_state.temperature <=
                self.__electrolyte_system.get_max_temperature())

    def check_voltage_in_range(self, redox_flow_state: RedoxFlowState) -> bool:
        """
        Checks if voltage is in range between maximal and minimal stack module voltage.

        Parameters
        ----------
        redox_flow_state : RedoxFlowState
            Current state of redox_flow.

        Returns
        -------
        bool:
            True if voltage is between max. and min. stack module voltage.
        """
        return (self.__stack_module.get_min_voltage() <= redox_flow_state.voltage <=
                self.__stack_module.get_max_voltage())

    def voltage_in_range(self, redox_flow_state: RedoxFlowState) -> float:
        """
        If the voltage is outside of the maximal or minimal stack module voltage, then it is set to the maximal or
        minimal value.

        Parameters
        ----------
        redox_flow_state : RedoxFlowState
            Current state of redox_flow.

        Returns
        -------
        float:
            Voltage in V.
        """
        voltage_target = redox_flow_state.voltage
        if ((voltage_target > redox_flow_state.open_circuit_voltage) and (voltage_target >
            self.__stack_module.get_max_voltage())):
            voltage = max(redox_flow_state.open_circuit_voltage, self.__stack_module.get_max_voltage())
        elif ((voltage_target < redox_flow_state.open_circuit_voltage) and (voltage_target <
              self.__stack_module.get_min_voltage())):
            voltage = min(redox_flow_state.open_circuit_voltage, self.__stack_module.get_min_voltage())
        else:
            voltage = max(min(voltage_target, self.__stack_module.get_max_voltage()),
                          self.__stack_module.get_min_voltage())
        return voltage

    def check_soc_in_range(self, redox_flow_state: RedoxFlowState, delta_soc: float, delta_soc_stack: float) -> bool:
        """
        Checks if the state-of-charge (SOC) is to high or to low for charging or discharging.

        Parameters
        ----------
        redox_flow_state : RedoxFlowState
            Current state of redox_flow.
        delta_soc: float
            State-of-charge in p.u.
        delta_soc_stack: float
            State-of-charge in the stack in p.u.


        Returns
        -------
        bool:
            True if SOC of the system and in the stack is in range for charging or discharging.
        """
        if redox_flow_state.is_charge and (((redox_flow_state.soc + delta_soc) >= self.__soc_max) or
                                           ((redox_flow_state.soc_stack + delta_soc_stack) >= 1)):
            return False
        elif not redox_flow_state.is_charge and (((redox_flow_state.soc + delta_soc) <= self.__soc_min) or
                                                 ((redox_flow_state.soc_stack + delta_soc_stack) <= 0)):
            return False
        else:
            return True

    def check_current_in_range(self, redox_flow_state: RedoxFlowState, time: float) -> bool:
        """
        Checks if the current is in range. The maximal and minimal current are defined to have enough reactants at the
        current flow rate or in the stack electrolyte volume.

        Parameters
        ----------
        redox_flow_state : RedoxFlowState
            Current state of redox_flow.
        time : float
            Current simulation time in s.

        Returns
        -------
        bool:
            True if current is in range.
        """
        if redox_flow_state.current > self.get_max_current(redox_flow_state, time):
            self.__log.warn('Flow Rate for charging is to low')
            return False
        elif redox_flow_state.current < self.get_min_current(redox_flow_state, time):
            self.__log.warn('Flow Rate for discharging is to low')
            return False
        else:
            return True

    def get_min_current(self, redox_flow_state: RedoxFlowState, time: float) -> float:
        """
        Determines the minimal faraday current of a stack module (maximal discharge current) based on the flow rate.
        If the flow rate is 0, the electrolyte volume in the stack modules and the still usable concentration of
        reactants is used for calculation.

        Parameters
        ----------
        redox_flow_state : RedoxFlowState
            Current state of redox_flow.
        time : float
            Current simulation time in s.

        Returns
        -------
        float:
            Minimal faraday current (=max discharge current) in A.
        """
        soc_stack = redox_flow_state.soc_stack
        flow_rate = min(self.__pump_algorithm.get_flow_rate_anolyte(redox_flow_state),
                        self.__pump_algorithm.get_flow_rate_catholyte(redox_flow_state))
        time_step = time - redox_flow_state.time
        if flow_rate == 0.0:
            min_current = (-soc_stack * self.__FARADAY * self.__electrolyte_system.get_vanadium_concentration() *
                           self.__stack_module.get_stacks_electrolyte_volume() / time_step /
                           (self.__stack_module.get_serial_scale() * self.__stack_module.get_cell_per_stack()))
        else:
            min_current = (-soc_stack * self.__FARADAY * self.__electrolyte_system.get_vanadium_concentration() *
                           flow_rate / (self.__stack_module.get_serial_scale() *
                           self.__stack_module.get_cell_per_stack()))
        return min_current

    def get_max_current(self, redox_flow_state: RedoxFlowState, time: float) -> float:
        """
        Determines the maximal faraday current of a stack module (maximal charge current) based on the flow rate.
        If the flow rate is 0, the electrolyte volume in the stack modules and the still usable concentration of
        reactants is used for calculation.

        Parameters
        ----------
        redox_flow_state : RedoxFlowState
            Current state of redox_flow.
        time : float
            Current simulation time in s.

        Returns
        -------
        float:
            Maximal faraday current (=max charge current) in A.
        """
        soc_stack = redox_flow_state.soc_stack
        flow_rate = min(self.__pump_algorithm.get_flow_rate_anolyte(redox_flow_state),
                        self.__pump_algorithm.get_flow_rate_catholyte(redox_flow_state))
        time_step = time - redox_flow_state.time
        if flow_rate == 0.0:
            max_current = ((1 - soc_stack) * self.__FARADAY * self.__electrolyte_system.get_vanadium_concentration() *
                           self.__stack_module.get_stacks_electrolyte_volume() / time_step /
                           (self.__stack_module.get_serial_scale() * self.__stack_module.get_cell_per_stack()))
        else:
            max_current = ((1 - soc_stack) * self.__FARADAY * self.__electrolyte_system.get_vanadium_concentration() *
                           flow_rate / (self.__stack_module.get_serial_scale() *
                           self.__stack_module.get_cell_per_stack()))
        return max_current

    def battery_fulfillment_calc(self, redox_flow_state: RedoxFlowState) -> None:
        """
        Calculates the battery fulfillment [0, 1].

        Parameters
        ----------
        redox_flow_state : RedoxFlowState
            Current state of redox_flow.

        Returns
        -------
        """
        power_is = redox_flow_state.power
        power_target = redox_flow_state.power_in
        if abs(power_is - power_target) < 1e-8:
            redox_flow_state.fulfillment = 1.0
        elif power_target == 0:
            self.__log.error('Power should be 0, but is ' + str(power_is) + ' A. Check BMS function.')
            redox_flow_state.fulfillment = 0.0
        else:
            redox_flow_state.fulfillment = abs(power_is / power_target)
            if redox_flow_state.fulfillment < 0 or redox_flow_state.fulfillment > 1:
                self.__log.error('Fulfillment should be between 0 and 1, but is ' +
                                 str(redox_flow_state.fulfillment) + '. Check BMS functions.')

    def set_max_power(self, redox_flow_state: RedoxFlowState) -> None:
        max_power: float = self.__stack_module.get_max_power()
        redox_flow_state.max_charge_power = 0.0 if redox_flow_state.soc > self.__soc_max else max_power
        redox_flow_state.max_discharge_power = 0.0 if redox_flow_state.soc < self.__soc_min else max_power

    def close(self):
        """Closing all resources in RedoxControlSystem."""
        self.__log.close()
        self.__stack_module.close()
        self.__electrolyte_system.close()
        self.__pump_algorithm.close()
