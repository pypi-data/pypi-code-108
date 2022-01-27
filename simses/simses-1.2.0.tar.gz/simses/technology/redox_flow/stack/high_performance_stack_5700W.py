from math import log10
import pandas as pd
import scipy.interpolate

from simses.commons.config.data.redox_flow import RedoxFlowDataConfig
from simses.commons.config.simulation.redox_flow import RedoxFlowConfig
from simses.commons.log import Logger
from simses.commons.state.technology.redox_flow import RedoxFlowState
from simses.technology.redox_flow.stack.electrolyte.abstract_electrolyte import ElectrolyteSystem
from simses.technology.redox_flow.stack.abstract_stack import StackModule


class HighPerformanceStack5700W(StackModule):
    """HighPerformanceStack5700W describes a stack based on laboratory measurement cell data at ZAE Bayern from Tobias
    Greese with high-performance electrodes in an interdigitated flow design. The data is scaled up to a 20-cell stack
    with 1000 cm^2 cell area.
    The internal resistance is dependent of the current density. The dependency from SOC and flow rate is neglected. """

    """The nominal power is calculated for an SOC range from 20 % to 80 % and the listed parameters. It corresponds to 
    the power that can be obtained over this SOC range."""
    __STACK_POWER_NOM = 5700  # W
    __CELL_NUMBER = 12  # -
    __CELL_AREA = 1000  # cm^2
    __ELECTRODE_THICKNESS = 0.033  # cm; thin carbon papers
    __ELECTRODE_POROSITY = 0.85  # -
    __MIN_CELL_VOLTAGE = 1.2  # V
    __MAX_CELL_VOLTAGE = 1.6  # V
    __HYDRAULIC_RESISTANCE = 3.082E10  # 1/m^3
    __DEPENDENT_PARAMETERS = True

    def __init__(self, electrolyte_system: ElectrolyteSystem, voltage: float, power: float,
                 redox_flow_data_config: RedoxFlowDataConfig, redox_flow_config: RedoxFlowConfig):
        super().__init__(electrolyte_system, voltage, power, self.__CELL_NUMBER, self.__STACK_POWER_NOM,
                         redox_flow_config)
        self.__log: Logger = Logger(__name__)
        self.__electrolyte_system: ElectrolyteSystem = electrolyte_system
        self.__RINT_FILE = redox_flow_data_config.rfb_rint_file_hp_stack
        self.__SD_FILE = redox_flow_data_config.high_performance_stack_self_discharge
        self.__SHUNT_FILE = redox_flow_data_config.high_performance_stack_shunt
        pd.set_option('precision', 9)
        self.__internal_resistance = pd.read_csv(self.__RINT_FILE, header=None)  # Ohm
        self.__i_rint_arr = self.__internal_resistance.iloc[0, :]
        self.__rint = self.__internal_resistance.iloc[1, :]
        self.__rint_inter1d = scipy.interpolate.interp1d(self.__i_rint_arr, self.__rint, kind='linear',
                                                         fill_value='extrapolate')
        self.__self_discharge_current = pd.read_csv(self.__SD_FILE, header=None)  # mA/cm^2
        self.__i_stack_sd_arr = self.__self_discharge_current.iloc[0, :]
        self.__i_sd_arr = self.__self_discharge_current.iloc[1, :]
        self.__i_sd_inter1d = scipy.interpolate.interp1d(self.__i_stack_sd_arr, self.__i_sd_arr, kind='linear',
                                                         fill_value='extrapolate')
        self.__shunt_current = pd.read_csv(self.__SHUNT_FILE, header=None)  # A
        self.__shunt_current_mat = self.__shunt_current.iloc[1:, 1:]
        self.__soc_arr = self.__shunt_current.iloc[1:, 0]
        self.__current_arr = self.__shunt_current.iloc[0, 1:]
        self.__shunt_interp2d = scipy.interpolate.interp2d(self.__current_arr, self.__soc_arr, self.__shunt_current_mat,
                                                           kind='linear')

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
        current_density = redox_flow_state.current / self.get_specific_cell_area() / self.get_parallel_scale() * 1000
        # mA/cm^2
        resistance = self.__rint_inter1d(current_density)
        self.__log.debug('Resistance stack: ' + str(resistance) + ' Ohm, resistance charging module:'
                         + str(resistance / self.get_parallel_scale() * self.get_serial_scale()))
        return float(resistance / self.get_parallel_scale() * self.get_serial_scale())

    def get_cell_per_stack(self) -> int:
        return self.__CELL_NUMBER

    def get_min_voltage(self) -> float:
        return self.__MIN_CELL_VOLTAGE * self.get_cell_per_stack() * self.get_serial_scale()

    def get_max_voltage(self) -> float:
        return self.__MAX_CELL_VOLTAGE * self.get_cell_per_stack() * self.get_serial_scale()

    def get_self_discharge_current(self, redox_flow_state: RedoxFlowState) -> float:
        current_density = abs(redox_flow_state.current / self.get_specific_cell_area() / self.get_parallel_scale() *
                              1000)  # mA/cm^2
        self_discharge_membrane = self.__i_sd_inter1d(current_density) / 1000 * self.get_specific_cell_area()
        current_stack = redox_flow_state.current / self.get_parallel_scale()
        self_discharge_shunt = (float(self.__shunt_interp2d(redox_flow_state.soc_stack, current_stack)))
        total_self_discharge_current = self_discharge_membrane + self_discharge_shunt
        return (total_self_discharge_current * self.get_cell_per_stack() * self.get_serial_scale() *
                self.get_parallel_scale())

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
