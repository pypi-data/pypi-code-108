import math
from simses.commons.state.technology.lithium_ion import LithiumIonState
from simses.technology.lithium_ion.cell.type import CellType
from simses.technology.lithium_ion.degradation.calendar.calendar_degradation import \
    CalendarDegradationModel


class PanasonicNCACalendarDegradationModel(CalendarDegradationModel):

    __capacity_loss = 0
    __resistance_increase = 0

    __TEMP_REF = 298.15  # K
    __SOC_REF = 0.5  # pu
    __R = 8.3144598  # J/(K*mol)

    __K_REF_QLOSS = 0.0013  # pu*s^(-0.5)
    __A_CAL_QLOSS = 1.630861630861708  # fit parameter for voltage dependence - quadratic term
    __B_CAL_QLOSS = - 10.723723723724325  # fit parameter for voltage dependence - linear term
    __C_CAL_QLOSS = 18.351282051283220  # fit parameter for voltage dependence - constant term
    __EA_QLOSS = 32681  # J/mol

    __K_REF_RINC = 0.001211111111111  # pu*s^(-0.5)
    __A_RINC = 3.238585817688798 * 10 ** -8  # fit parameter for resistance increase - soc dependence - 4th order term
    __B_RINC = - 5.557556793759961 * 10 ** -6  # fit parameter for resistance increase - soc dependence - 3rd order term
    __C_RINC = 3.654685225712923 * 10 ** -4  # fit parameter for resistance increase - soc dependence - 2nd order term
    __D_RINC = - 0.008173737926571  # fit parameter for resistance increase - soc dependence - 1st order term
    __E_RINC = 0.466408440817863  # fit parameter for resistance increase - soc dependence - constant term
    __EA_RINC = 2.796216012248313 * 10 ** 4  # J/mol

    # Values based on MA Yuhui Geng (data originally from Peter Keil)

    def __init__(self, cell_type: CellType):
        super().__init__(cell_type)
        self.__capacity_loss_cal = cell_type.get_calendar_capacity_loss_start()
        self.__rinc_cal = 0

    def calculate_degradation(self, time: float, battery_state: LithiumIonState) -> None:
        time_passed = time - battery_state.time
        temp = battery_state.temperature
        # Open circuit voltage is used for calendar degradation model
        voltage = self._cell.get_open_circuit_voltage(battery_state) / self._cell.get_serial_scale()

        qloss: float = self.__capacity_loss_cal

        virtual_time = (qloss / (
                self.__K_REF_QLOSS * math.exp(-self.__EA_QLOSS / self.__R * (1 / temp - 1 / self.__TEMP_REF)) * (
                self.__A_CAL_QLOSS * voltage ** 2 + self.__B_CAL_QLOSS * voltage + self.__C_CAL_QLOSS))) ** 2  # days

        rel_capacity_loss = lambda time: self.__K_REF_QLOSS * math.exp(
            -self.__EA_QLOSS / self.__R * (1 / temp - 1 / self.__TEMP_REF)) * (
                                                 self.__A_CAL_QLOSS * voltage ** 2 + self.__B_CAL_QLOSS * voltage + self.__C_CAL_QLOSS) * time ** 0.5

        capacity_loss = rel_capacity_loss(virtual_time + time_passed / 86400) - self.__capacity_loss_cal

        self.__capacity_loss = capacity_loss * self._cell.get_nominal_capacity()  # Ah
        self.__capacity_loss_cal += capacity_loss

    def calculate_resistance_increase(self, time: float, battery_state: LithiumIonState) -> None:
        time_passed = time - battery_state.time
        soc = battery_state.soc
        temp = battery_state.temperature
        rinc_cal = self.__rinc_cal

        virtual_time = (rinc_cal / (
                self.__K_REF_RINC * math.exp(-self.__EA_RINC / self.__R * (1 / temp - 1 / self.__TEMP_REF)) * (
                self.__A_RINC * (soc*100) ** 4 + self.__B_RINC * (soc*100) ** 3 + self.__C_RINC *
                (soc*100) ** 2 + self.__D_RINC * soc * 100 + self.__E_RINC)))

        rel_resistance_increase = lambda time: self.__K_REF_RINC * math.exp(
            -self.__EA_RINC / self.__R * (1 / temp - 1 / self.__TEMP_REF)) * (
                                                       self.__A_RINC * (soc*100) ** 4 + self.__B_RINC * (soc*100) ** 3 +
                                                       self.__C_RINC * (soc*100) ** 2 + self.__D_RINC * (soc*100) + self.__E_RINC) \
                                               * time

        resistance_increase = rel_resistance_increase(virtual_time + time_passed / 86400) - self.__rinc_cal

        self.__rinc_cal += resistance_increase
        self.__resistance_increase = resistance_increase  # pu

    def get_degradation(self) -> float:
        return self.__capacity_loss

    def get_resistance_increase(self) -> float:
        return self.__resistance_increase

    def reset(self, battery_state: LithiumIonState) -> None:
        self.__capacity_loss_cal = 0
        self.__rinc_cal = 0

    def close(self) -> None:
        pass
