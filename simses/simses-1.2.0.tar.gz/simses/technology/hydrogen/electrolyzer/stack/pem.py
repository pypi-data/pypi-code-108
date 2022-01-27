import pandas as pd

from simses.commons.config.data.electrolyzer import ElectrolyzerDataConfig
from simses.commons.constants import Hydrogen
from simses.commons.log import Logger
from simses.commons.state.technology.electrolyzer import ElectrolyzerState
from simses.technology.hydrogen.electrolyzer.stack.stack_model import ElectrolyzerStackModel


class PemElectrolyzer(ElectrolyzerStackModel):
    """An PEM-Electrolyzer is a special typ of an Electrolyzer"""

    __POWER_HEADER = 'cellpower at 1 bar'
    __VOLTAGE_IDX = 1
    __POWER_IDX = 1
    __CURRENT_IDX = 0
    __GEOM_AREA_STACK = 50  # cm2
    __POWER = 100  # W
    __WATER_POWER_DENSITY = 0.125  # kg / kW
    __SPEC_MAX_POWER: float = 10.8  # W/cm2
    __MAX_CURRENT_DENSITY: float = 5.0  # A/cm2
    __MIN_CURRENT_DENSITY: float = 0.0 # mA
    __HEAT_CAPACITY: float = 4.933  # J/K/W from: Operational experience and Control strategies for a stand-alone power system based on renewable energy and hydrogen

    __part_pressure_h2: float = 0.526233372104
    __part_pressure_o2: float = 0.526233372104
    __sat_pressure_h2o: float = 0.466925594058

    def __init__(self, electrolyzer_maximal_power: float, electrolyzer_data_config: ElectrolyzerDataConfig):
        super().__init__()
        self.__log: Logger = Logger(type(self).__name__)
        self.__NOM_STACK_POWER: float = electrolyzer_maximal_power
        self.__MAX_STACK_POWER: float = electrolyzer_maximal_power
        self.__GEOM_AREA_STACK: float = electrolyzer_maximal_power / self.__SPEC_MAX_POWER
        self.__HEAT_CAPACITY_STACK: float = self.__HEAT_CAPACITY * self.__NOM_STACK_POWER
        self.__NUMBER_CELLS: float = 1.0
        self.__PC_FILE = electrolyzer_data_config.pem_electrolyzer_pc_file
        self.__POWER_FILE = electrolyzer_data_config.pem_electrolyzer_power_file
        self.__polarization_curve = pd.read_csv(self.__PC_FILE)  # V/(mA/cm2)
        self.__power_curve = pd.read_csv(self.__POWER_FILE)  # W/cm2
        self.__current_arr = self.__polarization_curve.iloc[:, self.__CURRENT_IDX] * self.__GEOM_AREA_STACK  # mA
        self.__polarization_arr = self.__polarization_curve.iloc[:, self.__VOLTAGE_IDX]  # V
        self.__power_arr = self.__power_curve.iloc[:, self.__POWER_IDX] * self.__GEOM_AREA_STACK  # W
        self.__voltage: float = 0.0
        self.__current: float = 0.0
        self.__hydrogen_generation: float = 0.0

    def calculate(self, power: float, state: ElectrolyzerState):
        power_idx = abs(self.__power_curve[self.__POWER_HEADER] * self.__GEOM_AREA_STACK - power).idxmin()
        self.__voltage = self.__polarization_curve.iloc[power_idx, self.__VOLTAGE_IDX]  # V
        self.__current = self.__power_curve.iloc[power_idx, self.__CURRENT_IDX] * self.__GEOM_AREA_STACK  # mA
        self.__hydrogen_generation = self.__current / (2 * Hydrogen.FARADAY_CONST)  # mol/s

    def get_current(self):
        # print('the current is: ' + str(self.__current) + ' mA')
        return self.__current

    def get_hydrogen_production(self):
        # print('the massflow of hydrogen ist: ' + str(self.__hydrogen_generation) + ' mol/s')
        return self.__hydrogen_generation

    def get_oxygen_production(self):
        return self.__hydrogen_generation / 2

    def get_voltage(self):
        return self.__voltage

    def get_water_use(self):
        return self.__hydrogen_generation  # water use is the same as hydrogen generation

    def get_number_cells(self):
        return self.__NUMBER_CELLS

    def get_nominal_stack_power(self):
        return self.__NOM_STACK_POWER

    def get_heat_capacity_stack(self):
        return self.__HEAT_CAPACITY_STACK

    def get_partial_pressure_h2(self):
        return self.__part_pressure_h2

    def get_partial_pressure_o2(self):
        return self.__part_pressure_o2

    def get_sat_pressure_h2o(self):
        return self.__sat_pressure_h2o

    def get_geom_area_stack(self):
        return self.__GEOM_AREA_STACK

    def get_reference_voltage_eol(self, resistance_increase: float, exchange_currentdensity_decrease: float) -> float:
        return 1.0

    def get_current_density(self) -> float:
        return self.__current / self.get_geom_area_stack()

    def get_water_in_stack(self) -> float:
        return self.__WATER_POWER_DENSITY * self.get_nominal_stack_power() / 1000.0

    def get_nominal_current_density(self) -> float:
        return 2.0

    def close(self):
        self.__log.close()

    def get_thermal_resistance_stack(self) -> float:
        pass
