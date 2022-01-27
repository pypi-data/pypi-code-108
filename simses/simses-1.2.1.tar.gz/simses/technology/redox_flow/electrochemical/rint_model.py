from math import sqrt

from simses.commons.log import Logger
from simses.commons.state.technology.redox_flow import RedoxFlowState
from simses.technology.redox_flow.pump_algorithm.abstract_pump_algorithm import PumpAlgorithm
from simses.technology.redox_flow.electrochemical.control.redox_control_system import RedoxControlSystem
from simses.technology.redox_flow.electrochemical.abstract_electrochemical import ElectrochemicalModel
from simses.technology.redox_flow.stack.electrolyte.abstract_electrolyte import ElectrolyteSystem
from simses.technology.redox_flow.stack.abstract_stack import StackModule


class RintModel(ElectrochemicalModel):
    """Equivalent circuit model that calculates the current and voltage of the redox flow stack module based on an
    internal resistance."""

    def __init__(self, stack_module: StackModule, control_system: RedoxControlSystem,
                 electrolyte_system: ElectrolyteSystem, pump_algorithm: PumpAlgorithm):
        super().__init__()
        self.__log: Logger = Logger(type(self).__name__)
        self.__stack_module: StackModule = stack_module
        self.__control_system: RedoxControlSystem = control_system
        self.__electrolyte_system: ElectrolyteSystem = electrolyte_system
        self.__pump_algorithm = pump_algorithm
        self.__FARADAY = self.__electrolyte_system.FARADAY
        self.__concentration_V = self.__electrolyte_system.get_vanadium_concentration()  # mol/m^3

    def update(self, time: float, redox_flow_state: RedoxFlowState) -> None:
        ocv: float = self.__stack_module.get_open_circuit_voltage(redox_flow_state)  # V
        redox_flow_state.open_circuit_voltage = ocv
        redox_flow_state.power = redox_flow_state.power_in
        rint: float = self.__stack_module.get_internal_resistance(redox_flow_state)  # Ohm

        # power check
        if abs(redox_flow_state.power) > self.__stack_module.get_max_power():
            if redox_flow_state.power < 0:
                redox_flow_state.power = -self.__stack_module.get_max_power()
            else:
                redox_flow_state.power = self.__stack_module.get_max_power()
        if (ocv ** 2 + 4 * rint * redox_flow_state.power) < 0:
            redox_flow_state.voltage = ocv
        else:
            redox_flow_state.voltage = (ocv + sqrt(ocv ** 2 + 4 * rint * redox_flow_state.power)) / 2
        self.__log.debug('System OCV: ' + str(ocv) + ', system voltage: ' + str(redox_flow_state.voltage))

        # Check temperature
        if not self.__control_system.check_temperature(redox_flow_state):
            self.__log.error('Electrolyte temperature is not in range. Destruction of the system is possible. HVAC must '
                            'be adjusted.')

        # Voltage check
        if not self.__control_system.check_voltage_in_range(redox_flow_state):
            self.__log.warn('Voltage ' + str(redox_flow_state.voltage) + ' V is not in range and is adjusted to ' +
                            str(self.__control_system.voltage_in_range(redox_flow_state)))
            redox_flow_state.voltage = self.__control_system.voltage_in_range(redox_flow_state)

        redox_flow_state.current = (redox_flow_state.voltage - ocv) / rint

        # Current check
        if not self.__control_system.check_current_in_range(redox_flow_state, time):
            self.__log.warn('Current ' + str(redox_flow_state.current) + ' A is not in range. Max value ' + str(
                self.__control_system.get_max_current(redox_flow_state, time)) + 'A, min value ' + str(
                self.__control_system.get_min_current(redox_flow_state, time)) + ' A.')
            if redox_flow_state.current > 0:
                redox_flow_state.current = self.__control_system.get_max_current(redox_flow_state, time)
            else:
                redox_flow_state.current = self.__control_system.get_min_current(redox_flow_state, time)
            redox_flow_state.voltage = redox_flow_state.current * rint + ocv
            self.__log.debug('Current after control system check: ' + str(redox_flow_state.current) + ', Voltage: ' +
                             str(redox_flow_state.voltage) + ' V.')

        delta_soc, delta_soc_stack, soc_stack = self.__calculate_soc(time, redox_flow_state, self.__stack_module)

        # SOC check
        if not self.__control_system.check_soc_in_range(redox_flow_state, delta_soc, delta_soc_stack):
            self.__log.warn('RFB should not be charged/discharged due to SOC restrictions. SOC: ' + str(
                redox_flow_state.soc) + ', power (' + str(redox_flow_state.power) + ') is set to 0')
            redox_flow_state.current = 0.0
            redox_flow_state.voltage = ocv
            redox_flow_state.flow_rate_catholyte = 0.0
            redox_flow_state.flow_rate_anolyte = 0.0
            delta_soc, delta_soc_stack, soc_stack = self.__calculate_soc(time, redox_flow_state, self.__stack_module)

        redox_flow_state.power = redox_flow_state.current * redox_flow_state.voltage
        redox_flow_state.power_loss = rint * redox_flow_state.current ** 2
        redox_flow_state.internal_resistance = rint
        redox_flow_state.soc_stack = soc_stack + delta_soc_stack
        redox_flow_state.soc = redox_flow_state.soc + delta_soc
        self.__log.debug('New SOC: ' + str(redox_flow_state.soc))

        # Battery fulfillment
        self.__control_system.battery_fulfillment_calc(redox_flow_state)

        # setting max power
        self.__control_system.set_max_power(redox_flow_state)

    def __calculate_soc(self, time: float, redox_flow_state: RedoxFlowState, stack_module: StackModule):
        """
        Calculates the state-of-charge (SOC) of the system and in the cells of the stack module.

        Parameters
        ----------
         time : float
            Current simulation time in s.
        redox_flow_state : RedoxFlowState
            Current state of redox_flow.
        stack_module : StackModule
            Type of redox flow battery stack module.

        Returns
        -------
            delta_soc in p.u.
            delta_soc_stack in p.u.
        """
        cell_num_stack = stack_module.get_cell_per_stack()
        self_discharge_current: float = stack_module.get_self_discharge_current(redox_flow_state)
        soc_stack = redox_flow_state.soc_stack
        delta_soc_stack = 0.0
        soc = redox_flow_state.soc
        capacity_amps = redox_flow_state.capacity * 3600 / self.__stack_module.get_nominal_voltage_cell()  # As

        if redox_flow_state.flow_rate_anolyte == 0 or redox_flow_state.flow_rate_catholyte == 0:
            if redox_flow_state.current == 0:
                self_discharge_current = 0   # for no self-discharge during standby
            delta_soc_stack = (redox_flow_state.current * cell_num_stack * stack_module.get_serial_scale() -
                               self_discharge_current) * (time - redox_flow_state.time) / (self.__FARADAY *
                               self.__concentration_V * stack_module.get_stacks_electrolyte_volume())
            if (soc_stack + delta_soc_stack) < 0.001:
                # soc_stack can't be 0, because then some formula become invalid (e.g. OCV calculation)
                self.__log.warn('Stack is totally discharged.')
                self_discharge_current = 0
                delta_soc_stack = 0.0
        delta_soc = ((redox_flow_state.current * cell_num_stack * stack_module.get_serial_scale() -
                      self_discharge_current) * (time - redox_flow_state.time) / capacity_amps)
        self.__log.debug('Current: ' + str(redox_flow_state.current) + ' , SD-Current: ' +
                         str(self_discharge_current/(cell_num_stack * stack_module.get_serial_scale())))
        if not (self.__pump_algorithm.get_flow_rate_anolyte(redox_flow_state) == 0 or
                self.__pump_algorithm.get_flow_rate_catholyte(redox_flow_state) == 0):
            if (soc + delta_soc) < 0.001:
                delta_soc_stack = 0
            else:
                delta_soc_stack = delta_soc
            soc_stack = redox_flow_state.soc
        return delta_soc, delta_soc_stack, soc_stack

    def close(self) -> None:
        super().close()
        self.__log.close()
        self.__stack_module.close()
        self.__control_system.close()
        self.__electrolyte_system.close()
