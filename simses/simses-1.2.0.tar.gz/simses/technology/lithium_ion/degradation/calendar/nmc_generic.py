from simses.commons.state.technology.lithium_ion import LithiumIonState
from simses.technology.lithium_ion.cell.type import CellType
from simses.technology.lithium_ion.degradation.calendar.calendar_degradation import CalendarDegradationModel

import numpy as np


class NMCGenericCalendarDegradationModel(CalendarDegradationModel):

    def __init__(self, cell_type: CellType):
        super().__init__(cell_type)
        self.__capacity_loss = 0
        self.__total_time_passed = 0
        self.__initial_capacity = self._cell.get_nominal_capacity()

        # parameters
        self.__z = 0.906104076057115
        self.__a = 49682.160495028
        self.__b = 88064.4869404265
        self.__c = 80178.9612040684
        self.__d = -94184.3923417739
        self.__e = 37100.1433032213
        self.__f = 1312.95148919778

        # constants
        self.__R = 8.314462  # universal gas constant

    def time_dependency(self, time_passed):
        # degradation depends on time as a power law function
        return time_passed ** self.__z

    def temperature_dependency(self, temp):
        # degradation depends on temperature as arrhenius function
        return self.__a * np.exp(- self.__b / (self.__R * temp))

    def soc_dependency(self, soc):
        # degradation depends on soc as a cubic function
        return self.__c * soc**3 + self.__d * soc**2 + self.__e * soc + self.__f

    def calculate_degradation(self, time: float, battery_state: LithiumIonState) -> None:
        self.__total_time_passed += time - battery_state.time
        timestep = time - battery_state.time
        state_of_charge: float = battery_state.soc
        temperature: float = battery_state.temperature

        # calculate degradation in percent (divide by 100 to get p.u.)
        capacity_loss_after = self.time_dependency(self.__total_time_passed) * \
                              self.temperature_dependency(temperature) * \
                              self.soc_dependency(state_of_charge)
        capacity_loss_before = self.time_dependency(self.__total_time_passed - timestep) * \
                              self.temperature_dependency(temperature) * \
                              self.soc_dependency(state_of_charge)

        self.__capacity_loss = (capacity_loss_after - capacity_loss_before) / 100.0 * self.__initial_capacity

    def calculate_resistance_increase(self, time: float, battery_state: LithiumIonState) -> None:
        # no resistance increase calculated for generic degradation model
        pass

    def get_degradation(self) -> float:
        degradation = self.__capacity_loss
        self.__capacity_loss = 0
        return degradation

    def get_resistance_increase(self) -> float:
        # no resistance increase calculated for generic degradation model
        return 0

    def reset(self, battery_state: LithiumIonState) -> None:
        self.__capacity_loss = 0
        self.__total_time_passed = 0

    def close(self) -> None:
        pass
