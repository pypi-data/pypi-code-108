import math
import pandas as pd
from simses.commons.state.technology.lithium_ion import LithiumIonState
from simses.technology.lithium_ion.cell.type import CellType
from simses.technology.lithium_ion.degradation.calendar.calendar_degradation import \
    CalendarDegradationModel
from simses.commons.config.data.battery import BatteryDataConfig
from simses.commons.config.simulation.battery import BatteryConfig


class SonyLFPCalendarDegradationModel(CalendarDegradationModel):

    def __init__(self, cell_type: CellType, battery_data_config: BatteryDataConfig, battery_config: BatteryConfig):
        super().__init__(cell_type)
        self.__initial_capacity = self._cell.get_nominal_capacity()

        # Source SONY_US26650FTC1_Product Specification and Naumann, Maik, et al.
        # "Analysis and modeling of calendar aging of a commercial LiFePO4/graphite cell."
        # Journal of Energy Storage 17 (2018): 153-169.
        # DOI: https://doi.org/10.1016/j.est.2018.01.019

        self.__capacity_loss = 0
        self.__capacity_loss_calendar_relative = cell_type.get_calendar_capacity_loss_start()
        self.__resistance_increase = 0

        self.__TEMP_REF = 298.15  # K
        self.__SOC_REF = 1  # pu
        self.__R = 8.3144598  # J/(K*mol)

        # # original parameters
        # self.__A_QLOSS = -2059.8  # K
        # self.__B_QLOSS = 9.2644  # constant
        # self.__K_REF_QLOSS = 1.2571 * 10 ** (-5)  # pu*s^(-0.5)
        # self.__C_QLOSS = 2.8575  # constant
        # self.__D_QLOSS = 0.60225  # constant
        # self.__EA_QLOSS = 17126  # J/mol
        #
        # self.__A_RINC = -8638.8  # K
        # self.__B_RINC = 29.992  # constant
        # self.__K_REF_RINC = 3.4194 * 10 ** (-10)  # pu*s^(-0.5)
        # self.__C_RINC = -3.3903  # constant
        # self.__D_RINC = 1.5604  # constant
        # self.__EA_RINC = 71827  # J/mol

        # read in parameters from CSV
        model_number = battery_config.degradation_model_number
        values_cap_model = pd.read_csv(battery_data_config.lfp_sony_degradation_capacity_file, skiprows=lambda x: x not in [0, model_number]).values.tolist()[0]
        values_res_model = pd.read_csv(battery_data_config.lfp_sony_degradation_resistance_file, skiprows=lambda x: x not in [0, model_number]).values.tolist()[0]
        # print("\nUsing the following cyc degradation model: \tNumber: " + str(model_number) + "\tIdentifier: " +
        #       values_cap_model[0])
        self.__K_REF_QLOSS = values_cap_model[1]  # pu*s^(-0.5)
        self.__EA_QLOSS = values_cap_model[2]  # J/mol
        self.__C_QLOSS = values_cap_model[3]  # constant
        self.__D_QLOSS = values_cap_model[4]  # constant

        self.__K_REF_RINC = values_res_model[1]  # pu*s^(-0.5)
        self.__EA_RINC = values_res_model[2]  # J/mol
        self.__C_RINC = values_res_model[3]  # constant
        self.__D_RINC = values_res_model[4]  # constant

    def calculate_degradation(self, time: float, battery_state: LithiumIonState) -> None:
        self.__capacity_loss = 0
        time_passed = time - battery_state.time
        soc = battery_state.soc
        temp = battery_state.temperature

        # calculate stress factor dependent coefficients
        k_temp_qloss = self.__K_REF_QLOSS * math.exp(-self.__EA_QLOSS / self.__R * (1 / temp - 1 / self.__TEMP_REF))
        k_soc_qloss = self.__C_QLOSS * (soc - 0.5) ** 3 + self.__D_QLOSS

        # calculate capacity loss based on virtual time and past calendar degradation
        virtual_time = (self.__capacity_loss_calendar_relative / (k_temp_qloss * k_soc_qloss)) ** 2  # seconds
        capacity_loss = k_temp_qloss * k_soc_qloss * (virtual_time + time_passed) ** 0.5  # total cal. qloss in p.u.
        capacity_loss -= self.__capacity_loss_calendar_relative  # relative qloss in pu in current timestep

        self.__capacity_loss_calendar_relative += capacity_loss  # tracking calendar capacity loss in p.u.
        self.__capacity_loss = capacity_loss * self.__initial_capacity  # relative qloss in Ah in current timestep

    def calculate_resistance_increase(self, time: float, battery_state: LithiumIonState) -> None:
        soc = battery_state.soc
        temp = battery_state.temperature
        time_passed = time - battery_state.time

        k_temp_qloss = self.__K_REF_RINC * math.exp(-self.__EA_RINC / self.__R * (1 / temp - 1 / self.__TEMP_REF))
        k_soc_qloss = self.__C_RINC * (soc - 0.5) ** 2 + self.__D_RINC

        resistance_increase = k_temp_qloss * k_soc_qloss * time_passed
        self.__resistance_increase = resistance_increase  # pu

    def get_degradation(self) -> float:
        return self.__capacity_loss

    def get_resistance_increase(self) -> float:
        return self.__resistance_increase

    def reset(self, battery_state: LithiumIonState) -> None:
        self.__capacity_loss = 0
        self.__resistance_increase = 0

    def close(self) -> None:
        pass
