from simses.commons.constants import Hydrogen
from simses.system.auxiliary.auxiliary import Auxiliary


class WaterHeating(Auxiliary):

    def __init__(self):
        super().__init__()
        self.__heating_power = 0  # W
        self.__heating_efficiency = 1
        self.__delta_temperature = 0

    def ac_operation_losses(self) -> float:
        if self.__delta_temperature >= 0:  # electricity consumption only in case of heating
            return self.__heating_power / self.__heating_efficiency
        else:
            return 0

    def calculate_heating_power(self, water_flow, delta_temperature):
            self.__heating_power = Hydrogen.HEAT_CAPACITY_WATER * water_flow * Hydrogen.MOLAR_MASS_WATER * \
                                   delta_temperature
            self.__delta_temperature = delta_temperature

    def get_heating_power(self):
        return self.__heating_power