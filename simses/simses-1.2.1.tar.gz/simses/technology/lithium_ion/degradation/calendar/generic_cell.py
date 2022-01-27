import math

from simses.commons.config.simulation.battery import BatteryConfig
from simses.commons.log import Logger
from simses.commons.state.technology.lithium_ion import LithiumIonState
from simses.technology.lithium_ion.cell.type import CellType
from simses.technology.lithium_ion.degradation.calendar.calendar_degradation import \
    CalendarDegradationModel


class GenericCellCalendarDegradationModel(CalendarDegradationModel):

    def __init__(self, cell_type: CellType, battery_config: BatteryConfig):
        super().__init__(cell_type)
        self.__log: Logger = Logger(type(self).__name__)
        self.__total_capacity_decrease = 0
        self.__capacity_decrease = 0
        self.__total_time_passed = 0
        self.__initial_capacity = self._cell.get_nominal_capacity()
        self.__end_of_life_duration = battery_config.max_calendar_lifetime * 365. * 24. * 60. * 60.
        self.__end_of_life = battery_config.eol # EOL criteria xy%.
        self.__log.info('Considering ' + str(self.__end_of_life_duration) + ' years over lifetime')

    def calculate_degradation(self, time: float, battery_state: LithiumIonState) -> None:
        # Calendar degradation in dummy cell is a function of sqrt(t)
        self.__total_time_passed += time - battery_state.time
        self.__capacity_decrease = math.sqrt(self.__total_time_passed) * (1 - self.__end_of_life) / \
                                   math.sqrt(self.__end_of_life_duration) # in p.u

        self.__capacity_decrease = self.__capacity_decrease * self.__initial_capacity

    def calculate_resistance_increase(self, time: float, battery_state: LithiumIonState) -> None:
        pass # No resistance increase in dummy cell model

    def get_degradation(self) -> float:
        degradation = self.__capacity_decrease - self.__total_capacity_decrease
        # Update total capacity decrease
        self.__total_capacity_decrease = self.__capacity_decrease
        return degradation

    def get_resistance_increase(self) -> float:
        return 0 # No resistance increase in dummy cell model

    def reset(self, battery_state: LithiumIonState) -> None:
        self.__capacity_decrease = 0
        self.__total_capacity_decrease = 0
        self.__total_time_passed = 0

    def close(self) -> None:
        self.__log.close()
