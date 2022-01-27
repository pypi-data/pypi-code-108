import pandas as pd

from simses.commons.config.data.fuel_cell import FuelCellDataConfig
from simses.commons.constants import Hydrogen
from simses.commons.log import Logger
from simses.technology.hydrogen.fuel_cell.stack.stack_model import \
    FuelCellStackModel


class JupiterFuelCell(FuelCellStackModel):

    """
    A Jupiter-Fuelcell is a special typ of a PEM-Fuelcell with an open cathode from SFC Energy:
    https://www.efoy-pro.com/efoy-pro/efoy-jupiter-2-5/
    """

    __POWER_HEADER = 'cellpower at 1 bar'
    __VOLTAGE_IDX = 1
    __POWER_IDX = 1
    __CURRENT_IDX = 0
    __MAX_POWER_Cell = 48.9494
    __NUMBER_CELLS = 46  # möglich sind [10,12,13,18,20,28,36,39,46,56,64,66,70,73,80]

    def __init__(self, fuel_cell_maximal_power: float, fuel_cell_data_config: FuelCellDataConfig):
        super(JupiterFuelCell, self).__init__()

        self.__log: Logger = Logger(type(self).__name__)
        self.__SPEC_MAX_POWER = 0.49  # W/cm2
        self.__NOM_STACK_POWER = fuel_cell_maximal_power
        self.__GEOM_AREA = 250  # cm2
        self.__PC_FILE = fuel_cell_data_config.jupiter_fuel_cell_pc_file
        self.__POWER_FILE = fuel_cell_data_config.jupiter_fuel_cell_power_file
        self.__mass_flow_h2 = 0  # mol/s
        self.__MAX_CURRENT_DENSITY = 5  # A/cm2
        self.__MIN_CURRENT_DENSITY = 0  # mA
        self.__HEAT_CAPACITY = Hydrogen.EPS
        self.__polarization_curve = pd.read_csv(self.__PC_FILE)  # V/(mA/cm2) per cell
        self.__power_curve = pd.read_csv(self.__POWER_FILE)  # W/cm2 per cell
        self.__current_arr = self.__polarization_curve.iloc[:, self.__CURRENT_IDX] * self.__GEOM_AREA  # mA
        self.__polarization_arr = self.__polarization_curve.iloc[:, self.__VOLTAGE_IDX] * self.__NUMBER_CELLS  # V
        self.__power_arr = self.__power_curve.iloc[:, self.__POWER_IDX] * self.__GEOM_AREA * self.__NUMBER_CELLS  # W


    def calculate(self, power) -> None:
        power_abs = abs(power)
        power_idx = abs(self.__power_curve[self.__POWER_HEADER]
                        * self.__GEOM_AREA * self.__NUMBER_CELLS - power_abs).idxmin()  # hier wird eine positive Leistung erwartet!!!
        self.__voltage = self.__polarization_curve.iloc[power_idx, self.__VOLTAGE_IDX] * self.__NUMBER_CELLS  # V
        self.__current = - self.__power_curve.iloc[power_idx, self.__CURRENT_IDX] * self.__GEOM_AREA  # mA
        self.__hydrogen_consumption = self.__current / (2 * Hydrogen.FARADAY_CONST) * self.__NUMBER_CELLS  # mol/s
        self.__power = - self.__power_curve.iloc[power_idx, self.__POWER_IDX] * self.__GEOM_AREA * self.__NUMBER_CELLS  # W
        a = 1

    def get_current(self):
        # print('the current is: ' + str(self.__current) + ' mA')
        return self.__current

    def get_voltage(self):
        # print('the voltage is: ' + str(self.__voltage) + ' V')
        return self.__voltage

    def get_hydrogen_consumption(self):
        # print('the massflow of hydrogen ist: ' + str(self.__mass_flow_h2) + ' mol/s')
        return - self.__hydrogen_consumption  # positive value

    def get_nominal_stack_power(self):
        return self.__NOM_STACK_POWER

    # def get_power(self):
    #     return self.__power

    def get_number_cells(self):
        return self.__NUMBER_CELLS

    # def get_max_spec_power(self):
    #     return self.get_max_spec_power()

    def get_geom_area_stack(self):
        return self.__GEOM_AREA

    def get_heat_capactiy_stack(self):
        return self.__HEAT_CAPACITY

    def get_current_density(self) -> float:
        return self.__current / self.__GEOM_AREA

    def close(self):
        self.__log.close()

