import math

from simses.commons.state.technology.lithium_ion import LithiumIonState
from simses.technology.lithium_ion.cell.type import CellType
from simses.commons.log import Logger
from simses.technology.lithium_ion.degradation.calendar.calendar_degradation import \
    CalendarDegradationModel

class LGMJ1_NMCCalendarDegradationModel(CalendarDegradationModel):

    def __init__(self, cell_type: CellType):
        super().__init__(cell_type)
        self.__log: Logger = Logger(type(self).__name__)

        self.__capacity_loss = 0
        self.__initial_capacity = self._cell.get_nominal_capacity()
        self.__capacity_loss_cal = cell_type.get_calendar_capacity_loss_start()

        self.__A_QLOSS = -0.00315  # constant
        self.__B_QLOSS = 0.4467  # constant

        self.__resistance_increase = 0
        self.__rinc_calendar = 0

        self.__A_RINC = 0.00012736  # constant

    # Source: Khiem Trad
    # D2.3 – Report containing aging test profiles and test results
    # Everlasting, February 2020

    def calculate_degradation(self, time: float, battery_state: LithiumIonState) -> None:
        time_passed = time - battery_state.time
        temp = battery_state.temperature

        qloss: float = self.__capacity_loss_cal  # in pu
        virtual_time: float = (((1 - qloss) * 100 - 100) / (self.__A_QLOSS * temp + self.__B_QLOSS)) ** 2

        rel_capacity_status = lambda time: ((self.__A_QLOSS * temp + self.__B_QLOSS) * math.sqrt(time) + 100) / 100

        total_time = virtual_time + time_passed / 86400  # in days

        capacity_loss = (1 - rel_capacity_status(total_time)) - self.__capacity_loss_cal
        # Total calendrical capacity loss
        self.__capacity_loss_cal += capacity_loss
        # Delta calendrical capacity loss
        self.__capacity_loss = capacity_loss * self.__initial_capacity

    # Source: Zilberman I., Sturm J., Jossen A.
    # Reversible self-discharge and calendar aging of 18650 nickel-rich silicon-graphite lithium-ion cells
    # Journal of Power Sources, https://doi.org/10.1016/j.jpowsour.2019.03.109

    def calculate_resistance_increase(self, time: float, battery_state: LithiumIonState) -> None:
        rinc = self.__rinc_calendar
        time_passed = time - battery_state.time
        virtual_time: float = rinc / self.__A_RINC
        rel_resistance_increase = lambda time: (self.__A_RINC * time)
        total_time = virtual_time + time_passed / 86400  # in days
        resistance_increase = (rel_resistance_increase(total_time)) - self.__rinc_calendar
        self.__rinc_calendar += resistance_increase
        self.__resistance_increase = resistance_increase

    def get_degradation(self) -> float:
        return self.__capacity_loss

    def get_resistance_increase(self) -> float:
        return self.__resistance_increase

    def reset(self, battery_state: LithiumIonState) -> None:
        self.__capacity_loss = 0
        self.__resistance_increase = 0

    def close(self) -> None:
        pass
