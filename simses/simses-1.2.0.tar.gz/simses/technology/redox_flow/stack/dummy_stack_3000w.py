from math import log10

from simses.commons.config.simulation.redox_flow import RedoxFlowConfig
from simses.commons.log import Logger
from simses.commons.state.technology.redox_flow import RedoxFlowState
from simses.technology.redox_flow.stack.electrolyte.abstract_electrolyte import ElectrolyteSystem
from simses.technology.redox_flow.stack.abstract_stack import StackModule


class DummyStack3000W(StackModule):
    """DummyStack3000W describes a dummy stack with a constant internal resistance. The dependency of the
    resistance from SOC, flow rate and current is neglected. This stack type can be used to easily implement other stack
    parameters."""

    """The nominal power is calculated for an SOC range from 20 % to 80 % and the listed parameters. It corresponds to 
    the power that can be obtained over this SOC range."""
    __STACK_POWER_NOM = 3000  # W
    __CELL_NUMBER = 20  # -
    __INTERNAL_RESISTANCE_CELL = 1  # Ohm cm^2
    __CELL_AREA = 1000  # cm^2
    __ELECTRODE_THICKNESS = 0.37  # cm
    __ELECTRODE_POROSITY = 0.9  # -
    __MIN_CELL_VOLTAGE = 1.2  # V
    __MAX_CELL_VOLTAGE = 1.6  # V
    __SELF_DISCHARGE_CURRENT_DENS = 1  # mA/cm^2
    __HYDRAULIC_RESISTANCE = 5.969E10  # 1/m^3
    __DEPENDENT_PARAMETERS = False

    def __init__(self, electrolyte_system: ElectrolyteSystem, voltage: float, power: float,
                 redox_flow_config: RedoxFlowConfig):
        super().__init__(electrolyte_system, voltage, power, self.__CELL_NUMBER, self.__STACK_POWER_NOM,
                         redox_flow_config)
        self.__log: Logger = Logger(__name__)
        self.__electrolyte_system: ElectrolyteSystem = electrolyte_system

    def get_open_circuit_voltage(self, redox_flow_state: RedoxFlowState) -> float:
        """
        Literature source: Fink, Holger. Untersuchung von Verlustmechanismen in Vanadium-Flussbatterien. Diss.
        Technische Universität München, 2019.
        equation 5.18, assumption: SOH = 100 %, therefore ver = 0.5
        """
        concentration_v = self.__electrolyte_system.get_vanadium_concentration()
        soc_stack = redox_flow_state.soc_stack
        # equation is defined for SOC = ]0-1[
        if soc_stack > 0.999:
            soc_stack = 0.999
        if soc_stack < 0.001:
            soc_stack = 0.001
        temperature = redox_flow_state.temperature
        concentration_h_start = 2.6  # mol/l
        ocv_cell = (1.255 + 0.07 + 0.059 * temperature / 298.15 * log10((soc_stack / (1 - soc_stack) *
                    (concentration_h_start + concentration_v / 1000 * (soc_stack + 0.5)))**2 * (concentration_h_start +
                    concentration_v / 1000 * (soc_stack - 0.5))))
        self.__log.debug('OCV cell: ' + str(ocv_cell) + ' V')
        return ocv_cell * self.get_cell_per_stack() * self.get_serial_scale()

    def get_nominal_voltage_cell(self) -> float:
        """Calculated for a temperature of 25 °C and at SOC 50 %."""
        nominal_voltage_cell = 1.423
        return nominal_voltage_cell

    def get_internal_resistance(self, redox_flow_state: RedoxFlowState) -> float:
        resistance = self.__INTERNAL_RESISTANCE_CELL / self.get_specific_cell_area()
        return resistance * self.get_cell_per_stack() * self.get_serial_scale() / self.get_parallel_scale()

    def get_cell_per_stack(self) -> int:
        return self.__CELL_NUMBER

    def get_min_voltage(self) -> float:
        return self.__MIN_CELL_VOLTAGE * self.get_cell_per_stack() * self.get_serial_scale()

    def get_max_voltage(self) -> float:
        return self.__MAX_CELL_VOLTAGE * self.get_cell_per_stack() * self.get_serial_scale()

    def get_self_discharge_current(self, redox_flow_state: RedoxFlowState) -> float:
        return (self.__SELF_DISCHARGE_CURRENT_DENS / 1000 * self.get_specific_cell_area() * self.get_cell_per_stack() *
                self.get_serial_scale() * self.get_parallel_scale())

    def get_specific_cell_area(self) -> float:
        return self.__CELL_AREA

    def get_electrode_thickness(self) -> float:
        return self.__ELECTRODE_THICKNESS / 100

    def get_electrode_porosity(self) -> float:
        return self.__ELECTRODE_POROSITY

    def get_hydraulic_resistance(self) -> float:
        return self.__HYDRAULIC_RESISTANCE / (self.get_serial_scale() * self.get_parallel_scale())

    def dependent_parameters(self) -> bool:
        return self.__DEPENDENT_PARAMETERS

    def close(self):
        super().close()
        self.__log.close()
        self.__electrolyte_system.close()
