import math

from simses.commons.state.technology.lithium_ion import LithiumIonState
from simses.technology.lithium_ion.cell.type import CellType
from simses.commons.log import Logger
from simses.technology.lithium_ion.degradation.calendar.calendar_degradation import \
    CalendarDegradationModel

# Source:
# Thomas Bank, Jan Feldmann, Sebastian Klamor, Stephan Bihn, Dirk Uwe Sauer:
# Extensive aging analysis of high-power lithium titanate oxide batteries:
# Impact of the passive electrode effect
# Journal of Power Sources 473 (2020) 228566, https://doi.org/10.1016/j.jpowsour.2020.228566


class LTONMCCalendarDegradationModel(CalendarDegradationModel):

    def __init__(self, cell_type: CellType):
        super().__init__(cell_type)
        self.__log: Logger = Logger(type(self).__name__)

        self.__capacity_loss = 0
        self.__initial_capacity = self._cell.get_nominal_capacity()
        self.__capacity_loss_cal = cell_type.get_calendar_capacity_loss_start()

        self.__A_QLOSS = -0.3517  # constant
        self.__B_QLOSS = 0.2275  # constant
        self.__C_QLOSS = -0.01189  # constant
        self.__D_QLOSS = 0.008428  # constant
        self.__E_QLOSS = -11.89  # constant
        self.__F_QLOSS = 107.7  # constant

        self.__resistance_increase = 0
        self.__rinc_calendar = 0

        self.__A_RINC = 1/35  # constant

    def calculate_degradation(self, time: float, battery_state: LithiumIonState) -> None:
        time_passed = time - battery_state.time
        soc = battery_state.soc
        # According to the source, if the SOC is smaller then 0.7 there is no calendar aging
        if soc < 0.70:
            capacity_loss = 0
        else:
            qloss: float = self.__capacity_loss_cal  # in pu
            virtual_time: float = ((1 - qloss) * 100 - 100) / (self.__A_QLOSS * soc + self.__B_QLOSS)
            if virtual_time > 35:
                virtual_time: float = ((1 - qloss) * 100 - (self.__E_QLOSS * soc + self.__F_QLOSS)) / (self.__C_QLOSS * soc + self.__D_QLOSS)
                rel_capacity_status = lambda time: ((self.__C_QLOSS * soc + self.__D_QLOSS) * time + (self.__E_QLOSS * soc + self.__F_QLOSS)) / 100
            else:
                rel_capacity_status = lambda time: ((self.__A_QLOSS * soc + self.__B_QLOSS) * time + 100) / 100
            total_time = virtual_time + time_passed / 86400  # in days
            capacity_loss = (1 - rel_capacity_status(total_time)) - self.__capacity_loss_cal
            # Total calendrical capacity loss
        self.__capacity_loss_cal += capacity_loss
        # Delta calendrical capacity loss
        self.__capacity_loss = capacity_loss * self.__initial_capacity

    def calculate_resistance_increase(self, time: float, battery_state: LithiumIonState) -> None:
        rinc = self.__rinc_calendar
        time_passed = time - battery_state.time
        virtual_time: float = (rinc * 100) / self.__A_RINC
        rel_resistance_increase = lambda time: (self.__A_RINC * time) / 100
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
