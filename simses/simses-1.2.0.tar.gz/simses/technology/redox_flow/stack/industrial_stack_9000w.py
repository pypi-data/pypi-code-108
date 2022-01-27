import numpy as np
import scipy.interpolate

import pandas as pd
import scipy.interpolate

from simses.commons.config.data.redox_flow import RedoxFlowDataConfig
from simses.commons.config.simulation.redox_flow import RedoxFlowConfig
from simses.commons.log import Logger
from simses.commons.state.technology.redox_flow import RedoxFlowState
from simses.technology.redox_flow.stack.electrolyte.abstract_electrolyte import ElectrolyteSystem
from simses.technology.redox_flow.stack.abstract_stack import StackModule


class IndustrialStack9000W(StackModule):
    """IndustrialStack9000W is a scaled up version of IndustrialStack1500W to achieve a higher stack power. The flow
    length is kept constant."""

    __STACK_POWER_NOM = 9000  # W
    __CELL_NUMBER = 40  # -
    __CELL_AREA = 1500  # cm^2
    __ELECTRODE_THICKNESS = 0.55  # cm
    __ELECTRODE_POROSITY = 0.93  # -
    __MIN_CELL_VOLTAGE = 1.23  # V
    __MAX_CELL_VOLTAGE = 1.54  # V
    __SELF_DISCHARGE_CURRENT = 0.96  # A
    __DEPENDENT_PARAMETERS = False

    def __init__(self, electrolyte_system: ElectrolyteSystem, voltage: float, power: float,
                 redox_flow_data_config: RedoxFlowDataConfig, redox_flow_config: RedoxFlowConfig):
        super().__init__(electrolyte_system, voltage, power, self.__CELL_NUMBER, self.__STACK_POWER_NOM,
                         redox_flow_config)
        self.__log: Logger = Logger(__name__)
        self.__SHUNT_FILE = redox_flow_data_config.industrial_stack_9000w_shunt_current
        self.__shunt_current = pd.read_csv(self.__SHUNT_FILE, header=None)  # A
        self.__shunt_current_mat = self.__shunt_current.iloc[1:, 1:]
        self.__soc_arr = self.__shunt_current.iloc[1:, 0]
        self.__current_arr = self.__shunt_current.iloc[0, 1:]
        self.__shunt_interp2d = scipy.interpolate.interp2d(self.__current_arr, self.__soc_arr, self.__shunt_current_mat,
                                                           kind='linear')
        self.__hydraulic_resistance = 8.8e9 * (self._SERIAL_SCALE * self._PARALLEL_SCALE) ** -0.92
        soc_arr = np.array(
            [0, 5.21, 9.63, 14.16, 19.88, 25.73, 30.55, 34.66, 39.67, 45.01, 49.93, 54.89, 59.9, 64.95, 69.98, 74.95,
             79.84, 84.63, 89.98, 95.4, 100.0])
        ocv_arr = np.array(
            [1.226, 1.258, 1.281, 1.30, 1.319, 1.336, 1.349, 1.361, 1.372, 1.383, 1.394, 1.405, 1.416, 1.428, 1.439,
             1.453, 1.463, 1.477, 1.493, 1.514, 1.537])

        self.__ocv_interp1d = scipy.interpolate.interp1d(soc_arr / 100, ocv_arr, kind='linear')

    def get_open_circuit_voltage(self, redox_flow_state: RedoxFlowState) -> float:
        soc_stack = redox_flow_state.soc_stack
        ocv_stack = self.__ocv_interp1d(soc_stack) * self.__CELL_NUMBER
        return ocv_stack * self.get_serial_scale()

    def get_nominal_voltage_cell(self) -> float:
        """Calculated at SOC 50 %."""
        nominal_voltage_cell = 1.39
        return nominal_voltage_cell

    def get_internal_resistance(self, redox_flow_state: RedoxFlowState) -> float:
        power = redox_flow_state.power
        pressure_drop = redox_flow_state.pressure_drop_anolyte
        time_pump = redox_flow_state.time_pump
        power_per_stack = power / (self.get_parallel_scale() * self.get_serial_scale())
        rint_base = 1.8 * self.get_cell_per_stack() / self.get_specific_cell_area()
        if 3000 < abs(power_per_stack) < 6000 and pressure_drop == 0 and 0 > time_pump > -450:
            rint_pump = 0.009 + 0.027 * (abs(time_pump) / 450)
        else:
            rint_pump = 0
        rint = rint_base + rint_pump
        self.__log.debug('Resistant stack: ' + str(rint) + ' Ohm, resistant module: ' +
                         str(rint / self.get_parallel_scale() * self.get_serial_scale()))
        return float(rint / self.get_parallel_scale() * self.get_serial_scale())

    def get_cell_per_stack(self) -> int:
        return self.__CELL_NUMBER

    def get_min_voltage(self) -> float:
        return self.__MIN_CELL_VOLTAGE * self.get_cell_per_stack() * self.get_serial_scale()

    def get_max_voltage(self) -> float:
        return self.__MAX_CELL_VOLTAGE * self.get_cell_per_stack() * self.get_serial_scale()

    def get_self_discharge_current(self, redox_flow_state: RedoxFlowState) -> float:
        soc_stack = redox_flow_state.soc_stack
        current = redox_flow_state.current / self.get_parallel_scale()
        shunt_current_equivalent_single_stack = float(self.__shunt_interp2d(current, soc_stack))
        shunt_current_equivalent_total = shunt_current_equivalent_single_stack * (
                    0.196 * self.get_serial_scale() ** 2 + 0.143 * self.get_serial_scale() + 0.56)
        self_discharge_current = self.__SELF_DISCHARGE_CURRENT * soc_stack
        self_discharge_current_total = ((shunt_current_equivalent_total + self_discharge_current) *
                                        self.get_cell_per_stack() * self.get_serial_scale() * self.get_parallel_scale())
        return self_discharge_current_total

    def get_specific_cell_area(self) -> float:
        return self.__CELL_AREA

    def get_electrode_thickness(self) -> float:
        return self.__ELECTRODE_THICKNESS / 100

    def get_electrode_porosity(self) -> float:
        return self.__ELECTRODE_POROSITY

    def get_hydraulic_resistance(self) -> float:
        return self.__hydraulic_resistance

    def dependent_parameters(self) -> bool:
        return self.__DEPENDENT_PARAMETERS

    def close(self):
        super().close()
        self.__log.close()
