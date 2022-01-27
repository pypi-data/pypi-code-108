import pandas as pd
import scipy.interpolate
from simses.commons.config.data.battery import BatteryDataConfig
from simses.commons.state.technology.lithium_ion import LithiumIonState
from simses.technology.lithium_ion.cell.type import CellType
from simses.technology.lithium_ion.degradation.calendar.calendar_degradation import CalendarDegradationModel


class MolicelNMCCalendarDegradationModel(CalendarDegradationModel):

    # Values based on MA Ni Chuanqin (EES, TUM) and adapted from Yulong Zhao in order to have the same structure
    # as in the aging models of Maik Neumann (SonyLFP)

    __SOC_IDX = 0
    __TEMP_IDX = 1
    __LENGTH_TEMP_ARRAY = 40

    def __init__(self, cell_type: CellType, battery_data_config: BatteryDataConfig):
        super().__init__(cell_type)
        self.__rinc_cal = 0
        self.__capacity_loss = 0
        self.__resistance_increase = 0
        self.__initial_capacity = cell_type.get_nominal_capacity()
        self.__capacity_loss_calendar = cell_type.get_calendar_capacity_loss_start()

        capacity_cal_file: str = battery_data_config.nmc_molicel_capacity_cal_file
        capacity_cal = pd.read_csv(capacity_cal_file)  # -
        capacity_cal_mat = capacity_cal.iloc[:(self.__LENGTH_TEMP_ARRAY + 1), 2:]
        soc_arr = capacity_cal.iloc[:, self.__SOC_IDX]
        temp_arr = capacity_cal.iloc[:(self.__LENGTH_TEMP_ARRAY + 1), self.__TEMP_IDX]
        self.__capacity_cal_interp1d = scipy.interpolate.interp2d(soc_arr, temp_arr.T, capacity_cal_mat, kind='linear')

        ri_cal_file: str = battery_data_config.nmc_molicel_ri_cal_file
        ri_cal = pd.read_csv(ri_cal_file)  # -
        ri_cal_mat = ri_cal.iloc[:(self.__LENGTH_TEMP_ARRAY + 1), 2:]
        soc_arr = ri_cal.iloc[:, self.__SOC_IDX]
        temp_arr = ri_cal.iloc[:(self.__LENGTH_TEMP_ARRAY + 1), self.__TEMP_IDX]
        self.__ri_cal_interp1d = scipy.interpolate.interp2d(soc_arr, temp_arr.T, ri_cal_mat, kind='linear')

    def calculate_degradation(self, time: float, battery_state: LithiumIonState) -> None:
        time_passed = time - battery_state.time
        qloss: float = self.__capacity_loss_calendar # only calendar losses

        k_capacity_cal = self.get_stressfkt_ca_cal(battery_state)
        virtual_time = (qloss/k_capacity_cal)**(4/3) # virtual aging time in weeks

        capacity_loss = k_capacity_cal*(virtual_time + time_passed/(86400*7))**0.75 - qloss # pu

        self.__capacity_loss_calendar += capacity_loss  # pu
        self.__capacity_loss = capacity_loss * self.__initial_capacity # Ah

    def calculate_resistance_increase(self, time: float, battery_state: LithiumIonState) -> None:
        time_passed = time - battery_state.time
        rinc_cal = self.__rinc_cal
        k_ri_cal = self.get_stressfkt_ri_cal(battery_state)

        virtual_time = (rinc_cal/k_ri_cal)**2

        resistance_increase = k_ri_cal*(virtual_time + time_passed/(86400*7))**0.5 - rinc_cal
        self.__resistance_increase = resistance_increase  # pu
        self.__rinc_cal += resistance_increase

    def get_degradation(self) -> float:
        return self.__capacity_loss

    def get_resistance_increase(self) -> float:
        return self.__resistance_increase

    def get_stressfkt_ca_cal(self, battery_state: LithiumIonState) -> float:
        """
        get the stress factor for calendar aging capacity loss

        Parameters
        ----------
        battery_state : state including soc and temperature

        Returns
        -------
        float : stress parameters of calendar aging (capacity loss)

        """
        return float(self.__capacity_cal_interp1d(battery_state.soc, battery_state.temperature))

    def get_stressfkt_ri_cal(self, battery_state: LithiumIonState) -> float:
        """
        get the stress factor for calendar aging resistance increase

        Parameters
        ----------
        battery_state : state including soc and temperature

        Returns
        -------
        float : stress parameters of calendar aging (resistance increase)

        """
        return float(self.__ri_cal_interp1d(battery_state.soc, battery_state.temperature))

    def reset(self, battery_state: LithiumIonState) -> None:
        self.__rinc_cal = 0
        self.__capacity_loss = 0
        self.__resistance_increase = 0

    def close(self) -> None:
        pass
