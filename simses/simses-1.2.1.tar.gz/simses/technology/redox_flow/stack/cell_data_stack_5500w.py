import pandas as pd
import scipy.interpolate
from math import log10

from simses.commons.config.data.redox_flow import RedoxFlowDataConfig
from simses.commons.config.simulation.redox_flow import RedoxFlowConfig
from simses.commons.log import Logger
from simses.commons.state.technology.redox_flow import RedoxFlowState
from simses.technology.redox_flow.stack.electrolyte.abstract_electrolyte import ElectrolyteSystem
from simses.technology.redox_flow.stack.abstract_stack import StackModule


class CellDataStack5500W(StackModule):
    """CellDataStack5500W is a stack based on experimental data of single cell measurements and scaled up to a 40-cell
    stack."""

    """The nominal power is calculated for an SOC range from 20 % to 80 % and the listed parameters. It corresponds to 
        the power that can be obtained over the entire SOC range.  """
    __STACK_POWER_NOM = 5500  # W
    __CELL_NUMBER = 40  # -
    __CELL_AREA = 2160  # cm^2
    __ELECTRODE_THICKNESS = 0.48  # cm
    __ELECTRODE_POROSITY = 0.9  # -
    __MIN_CELL_VOLTAGE = 1.2  # V
    __MAX_CELL_VOLTAGE = 1.6  # V
    __SELF_DISCHARGE_CURRENT_DENS_MEMBRANE = 0.000917  # A/cm^2
    __HYDRAULIC_RESISTANCE = 4.67e10  # 1/m^3
    __DEPENDENT_PARAMETERS = False

    __SOC_IDX = 0
    __TEMP_IDX = 1
    __2D_RINT = False  # True if temperature dependency should be considered in internal resistance.

    def __init__(self, electrolyte_system: ElectrolyteSystem, voltage: float, power: float,
                 redox_flow_data_config: RedoxFlowDataConfig, redox_flow_config: RedoxFlowConfig):
        super().__init__(electrolyte_system, voltage, power, self.__CELL_NUMBER, self.__STACK_POWER_NOM,
                         redox_flow_config)
        self.__log: Logger = Logger(__name__)
        self.__electrolyte_system: ElectrolyteSystem = electrolyte_system
        self.__RINT_FILE = redox_flow_data_config.rfb_rint_file_cell_stack
        self.__SHUNT_FILE = redox_flow_data_config.cell_stack_shunt_current
        pd.set_option('precision', 9)
        self.__shunt_current = pd.read_csv(self.__SHUNT_FILE, header=None)  # A
        self.__shunt_current_mat = self.__shunt_current.iloc[1:, 1:]
        self.__soc_arr = self.__shunt_current.iloc[1:, 0]
        self.__current_arr = self.__shunt_current.iloc[0, 1:]
        self.__shunt_interp2d = scipy.interpolate.interp2d(self.__current_arr, self.__soc_arr, self.__shunt_current_mat,
                                                           kind='linear')
        self.__internal_resistance = pd.read_csv(self.__RINT_FILE)  # Ohm
        self.__soc_rint_arr = self.__internal_resistance.iloc[:, self.__SOC_IDX]
        self.__temp_rint_arr = self.__internal_resistance.iloc[:3, self.__TEMP_IDX]
        if self.__2D_RINT:
            self.__rint_mat_ch = self.__internal_resistance.iloc[:, 2:5]
            self.__rint_mat_dch = self.__internal_resistance.iloc[:, 5:]
            self.__rint_ch_inter2d = scipy.interpolate.interp2d(self.__temp_rint_arr, self.__soc_rint_arr,
                                                                self.__rint_mat_ch, kind='linear', fill_value=None)
            self.__rint_dis_inter2d = scipy.interpolate.interp2d(self.__temp_rint_arr, self.__soc_rint_arr,
                                                                 self.__rint_mat_dch, kind='linear', fill_value=None)
        else:
            self.__rint_mat_ch = self.__internal_resistance.iloc[:, 4]
            self.__rint_mat_dch = self.__internal_resistance.iloc[:, 7]
            self.__rint_ch_inter1d = scipy.interpolate.interp1d(self.__soc_rint_arr, self.__rint_mat_ch, kind='linear',
                                                                fill_value='extrapolate')
            self.__rint_dis_inter1d = scipy.interpolate.interp1d(self.__soc_rint_arr, self.__rint_mat_dch, kind='linear',
                                                                 fill_value='extrapolate')

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
        self.__log.debug('OCV_cell: ' + str(ocv_cell) + ' V')
        return ocv_cell * self.get_cell_per_stack() * self.get_serial_scale()

    def get_nominal_voltage_cell(self) -> float:
        """Calculated for a temperature of 25 °C and at SOC 50 %."""
        nominal_voltage_cell = 1.423
        return nominal_voltage_cell

    def get_internal_resistance(self, redox_flow_state: RedoxFlowState) -> float:
        """
        Experimental data based on single cell measurements at ZAE Bayern.
        Source: SimSES: Möller, Marc et al. A holistic simulation framework for modelingand analyzing stationary energy
        storage systems.
        """
        soc = redox_flow_state.soc
        temp = redox_flow_state.temperature
        if redox_flow_state.is_charge:
            # internal resistance for charging
            if self.__2D_RINT:
                resistance = self.__rint_ch_inter2d(temp, soc)
            else:
                resistance = self.__rint_ch_inter1d(soc)
            self.__log.debug('Resistance charging stack: ' + str(resistance) + ' Ohm, resistance charging module:'
                             + str(resistance / self.get_parallel_scale() * self.get_serial_scale()))
            return float(resistance / self.get_parallel_scale() * self.get_serial_scale())
        else:
            # internal resistance for discharging
            if self.__2D_RINT:
                resistance = self.__rint_dis_inter2d(temp, soc)
            else:
                resistance = self.__rint_dis_inter1d(soc)
            self.__log.debug('Resistance discharging stack: ' + str(resistance) + ' Ohm, resistance discharging module:'
                             + str(resistance / self.get_parallel_scale() * self.get_serial_scale()))
            return float(resistance / self.get_parallel_scale() * self.get_serial_scale())

    def get_cell_per_stack(self) -> int:
        return self.__CELL_NUMBER

    def get_min_voltage(self) -> float:
        return self.__MIN_CELL_VOLTAGE * self.get_cell_per_stack() * self.get_serial_scale()

    def get_max_voltage(self) -> float:
        return self.__MAX_CELL_VOLTAGE * self.get_cell_per_stack() * self.get_serial_scale()

    def get_self_discharge_current(self, redox_flow_state: RedoxFlowState) -> float:
        current_stack = redox_flow_state.current / self.get_parallel_scale()
        self_discharge_shunt = (float(self.__shunt_interp2d(redox_flow_state.soc_stack, current_stack)) *
                                self.get_cell_per_stack() * self.get_serial_scale() * self.get_parallel_scale())
        self_discharge_membrane = (self.__SELF_DISCHARGE_CURRENT_DENS_MEMBRANE * self.get_specific_cell_area() *
                                   self.get_cell_per_stack() * self.get_serial_scale() * self.get_parallel_scale())
        return self_discharge_membrane + self_discharge_shunt

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
