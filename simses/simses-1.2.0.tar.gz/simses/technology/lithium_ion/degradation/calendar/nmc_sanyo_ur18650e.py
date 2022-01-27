import math
from simses.commons.state.technology.lithium_ion import LithiumIonState
from simses.technology.lithium_ion.cell.type import CellType
from simses.technology.lithium_ion.degradation.calendar.calendar_degradation import \
    CalendarDegradationModel


class SanyoNMCCalendarDegradationModel(CalendarDegradationModel):
    """Source: Schmalstieg, J., Käbitz, S., Ecker, M., & Sauer, D. U. (2014).
    A holistic aging model for Li (NiMnCo) O2 based 18650 lithium-ion batteries.
    Journal of Power Sources, 257, 325-334."""
    __capacity_loss = 0
    __resistance_increase = 0

    def __init__(self, cell_type: CellType):
        super().__init__(cell_type)
        self.__time_total_cap = 0
        self.__time_total_res = 0

    def calculate_degradation(self, time: float, battery_state: LithiumIonState) -> None:
        time_passed = time - battery_state.time
        temp = battery_state.temperature  # cell temperature in K
        voltage = self._cell.get_open_circuit_voltage(battery_state) / self._cell.get_serial_scale()  # single cell voltage
        voltage = max(voltage, 3.149)

        alpha_cap = (7.543 * voltage - 23.75)*10**6*math.exp(-6976/temp)
        # implementation of discretization method as in MA Chuanqin Ni
        total_capacity_t1 = 1 - alpha_cap * (self.__time_total_cap / 86400) ** 0.75  # in p.u.
        total_capacity_t2 = 1 - alpha_cap * ((self.__time_total_cap + time_passed) / 86400) ** 0.75  # in p.u.
        capacity_loss = total_capacity_t1 - total_capacity_t2

        self.__time_total_cap += time_passed
        self.__capacity_loss = capacity_loss * self._cell.get_nominal_capacity()  # Ah

    def calculate_resistance_increase(self, time: float, battery_state: LithiumIonState) -> None:
        time_passed = time - battery_state.time
        temp = battery_state.temperature  # cell temperature in K
        voltage = self._cell.get_open_circuit_voltage(battery_state) / self._cell.get_serial_scale() # single cell voltage
        voltage = max(voltage, 3.097)

        # implementation of discretization method as in MA Chuanqin Ni
        alpha_res = (5.27*voltage - 16.32)*10**5*math.exp(-5986/temp)
        total_resistance_t1 = 1 + alpha_res * (self.__time_total_res / 86400) ** 0.75  # in p.u.
        total_resistance_t2 = 1 + alpha_res * ((self.__time_total_res + time_passed) / 86400) ** 0.75  # in p.u.

        self.__time_total_res += time_passed
        self.__resistance_increase = total_resistance_t2 - total_resistance_t1  # pu

    def get_degradation(self) -> float:
        return self.__capacity_loss

    def get_resistance_increase(self) -> float:
        return self.__resistance_increase

    def reset(self, battery_state: LithiumIonState) -> None:
        self.__capacity_loss = 0
        self.__resistance_increase = 0

    def close(self) -> None:
        pass
