from simses.commons.log import Logger
from simses.technology.hydrogen.fuel_cell.stack.stack_model import FuelCellStackModel


class NoFuelCell(FuelCellStackModel):
    """An No-Fuelcell is a special typ of a Fuelcell"""

    def __init__(self):
        super().__init__()
        self.__log: Logger = Logger(type(self).__name__)

    def calculate(self, power: float):
        self.__voltage = 1  # V
        self.__current = 0  # A
        self.__hydrogen_consumption = 0  # mol/s

    def get_current(self):
        #print('the current is: ' + str(self.__current) + ' mA')
        return self.__current

    def get_hydrogen_consumption(self):
        #print('the massflow of hydrogen ist: ' + str(self.__mass_flow_h2) + ' mol/s')
        return self.__hydrogen_consumption

    def get_voltage(self):
        #print('the voltage is: ' + str(self.__voltage) + ' V')
        return self.__voltage

    def get_nominal_stack_power(self):
        return 0

    def get_number_cells(self):
        return 0

    def get_geom_area_stack(self):
        return 1

    def get_heat_capactiy_stack(self):
        return 0

    def close(self):
        self.__log.close()

