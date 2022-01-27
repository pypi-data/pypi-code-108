from simses.commons.state.technology.lithium_ion import LithiumIonState
from simses.technology.lithium_ion.cell.type import CellType
from simses.technology.lithium_ion.degradation.calendar.calendar_degradation import CalendarDegradationModel


class NCAGenericCalendarDegradationModel(CalendarDegradationModel):

    def __init__(self, cell_type: CellType):
        super().__init__(cell_type)
        self.__capacity_loss = 0
        self.__total_time_passed = 0
        self.__initial_capacity = self._cell.get_nominal_capacity()

        # parameters
        self.__z = 0.409609637073964
        self.__a = 0.00461276336758222
        self.__b = 15.2653523010812
        self.__c = 0.119518828585308
        self.__d = 0.0639038983833157
        self.__e = 1
        self.__f = 1

    def time_dependency(self, time_passed):
        # degradation depends on time as a power law function
        return time_passed ** self.__z

    def temperature_dependency(self, temp):
        # degradation depends on temperature as a power law function
        return self.__a * (temp / 273.15) ** self.__b

    def soc_dependency(self, soc):
        # degradation depends on soc as a linear function
        return self.__c * soc + self.__d

    def calculate_degradation(self, time: float, battery_state: LithiumIonState) -> None:
        self.__total_time_passed += time - battery_state.time
        timestep = time - battery_state.time
        state_of_charge: float = battery_state.soc
        temperature: float = battery_state.temperature

        # calculate degradation in percent (divide by 100 to get p.u.) with function 5 from MA Sandner
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
