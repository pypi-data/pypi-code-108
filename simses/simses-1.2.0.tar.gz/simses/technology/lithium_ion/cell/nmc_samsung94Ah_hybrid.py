import math

import numpy as np
import pandas as pd
from scipy import interpolate
from scipy.interpolate import RegularGridInterpolator

from simses.commons.config.data.battery import BatteryDataConfig
from simses.commons.config.simulation.battery import BatteryConfig
from simses.commons.log import Logger
from simses.commons.state.technology.lithium_ion import LithiumIonState
from simses.technology.lithium_ion.cell.electric.properties import ElectricalCellProperties
from simses.technology.lithium_ion.cell.format.abstract import CellFormat
from simses.technology.lithium_ion.cell.format.prismatic import PrismaticCell
from simses.technology.lithium_ion.cell.thermal.properties import ThermalCellProperties
from simses.technology.lithium_ion.cell.type import CellType


class Samsung94AhNMCHybrid(CellType):
    """This hybrid cell class uses a temperature dependent OCV curves as well as SOC, temperature and
    charge/discharge-rate dependent internal resistance from lab tests, combined with a published degradation
    model based on Naumann et al. Note: While the cell parameters are from a NMC cell, the degradation model is from
    a LFP cell."""

    __SOC_HEADER = 'SOC'
    __SOC_IDX = 0
    __TEMP_IDX = 1
    __C_Rate_IDX = 2

    __CELL_VOLTAGE = 3.68  # V
    __CELL_CAPACITY = 94.0  # Ah
    __MAX_VOLTAGE: float = 4.15  # V
    __MIN_VOLTAGE: float = 2.7  # V
    __MIN_TEMPERATURE: float = 233.15  # K
    __MAX_TEMPERATURE: float = 333.15  # K
    __MAX_CHARGE_RATE: float = 2.0  # 1/h
    __MAX_DISCHARGE_RATE: float = 2.0  # 1/h
    __SELF_DISCHARGE_RATE: float = 0.0  # X.X%-soc per day, e.g., 0.015 for 1.5% SOC loss per day
    __MASS: float = 2.1  # kg per cell
    __SPECIFIC_HEAT: float = 1000  # J/kgK
    __CONVECTION_COEFFICIENT: float = 15  # W/m2K

    __HEIGHT: float = 125.0  # mm
    __WIDTH: float = 45.0  # mm
    __LENGTH: float = 173.0  # mm

    __COULOMB_EFFICIENCY: float = 1.0  # p.u

    __ELECTRICAL_PROPS: ElectricalCellProperties = ElectricalCellProperties(__CELL_VOLTAGE, __CELL_CAPACITY,
                                                                            __MIN_VOLTAGE, __MAX_VOLTAGE,
                                                                            __MAX_CHARGE_RATE, __MAX_DISCHARGE_RATE,
                                                                            __SELF_DISCHARGE_RATE, __COULOMB_EFFICIENCY)
    __THERMAL_PROPS: ThermalCellProperties = ThermalCellProperties(__MIN_TEMPERATURE, __MAX_TEMPERATURE, __MASS,
                                                                   __SPECIFIC_HEAT, __CONVECTION_COEFFICIENT)
    __CELL_FORMAT: CellFormat = PrismaticCell(__HEIGHT, __WIDTH, __LENGTH)

    def __init__(self, voltage: float, capacity: float, soh: float, battery_config: BatteryConfig,
                 battery_data_config: BatteryDataConfig):
        super().__init__(voltage, capacity, soh, self.__ELECTRICAL_PROPS, self.__THERMAL_PROPS, self.__CELL_FORMAT,
                         battery_config)
        self.__log: Logger = Logger(type(self).__name__)
        rint_file: str = battery_data_config.nmc_samsung94test_rint_file
        # # Reading out the Ri.csv data
        internal_resistance = pd.read_csv(rint_file)  # Ohm
        soc_arr = internal_resistance.iloc[:, self.__SOC_IDX]
        temp_arr = internal_resistance.iloc[:4, self.__TEMP_IDX]
        c_rate_arr = internal_resistance.iloc[:6, self.__C_Rate_IDX]
        rint_mat_ch = internal_resistance.iloc[:, 3:27]
        rint_mat_dch = internal_resistance.iloc[:, 27:]
        # Converting rint_mat_ch & rint_mat_dch into numpy arrays
        rint_mat_ch = rint_mat_ch.values
        rint_mat_dch = rint_mat_dch.values
        # Initializing empty 3D arrays for Rint_ch, Rint_dch - shape - (6, 21, 4)
        rint_mat_ch_tensor = np.ones((6, 21, 4))
        rint_mat_dch_tensor = np.ones((6, 21, 4))
        cursor = 0
        # Fill both tensors - rint_mat_ch_tensor & rint_mat_dch_tensor - with data from excel sheet
        for i in range(4):
            for j in range(6):
                rint_mat_ch_tensor[j, :, i] = rint_mat_ch_tensor[j, :, i] * rint_mat_ch[:, cursor]
                rint_mat_dch_tensor[j, :, i] = rint_mat_dch_tensor[j, :, i] * rint_mat_dch[:, cursor]
                cursor += 1
        self.__rint_ch_rgi = RegularGridInterpolator((c_rate_arr, soc_arr, temp_arr), rint_mat_ch_tensor)  # interpolation with SOC in p.u.
        self.__rint_dch_rgi = RegularGridInterpolator((c_rate_arr, soc_arr, temp_arr), rint_mat_dch_tensor)  # interpolation with SOC in p.u.

    def get_internal_resistance(self, battery_state: LithiumIonState) -> float:
        # temperature window limited between 5°C and 35°C due to test conditions
        if battery_state.temperature > 308.15:
            temperature: float = 308.15
            self.__log.warn("The cell resistance model is only parameterized up to 35°C.")
        elif battery_state.temperature < 278.15:
            temperature: float = 278.15
            self.__log.warn("The cell resistance model is only parameterized down to 5°C.")
        else:
            temperature: float = battery_state.temperature
        # current power limited between 0.25 C-rate and 1.5 C-rate due to test conditions
        c_rate: float = battery_state.current / self.get_nominal_capacity()
        if c_rate < 0.25:
            c_rate = 0.25
            # self.__log.warn("The cell resistance model only works with minimum current power of 0.25 C-rate.")
        if c_rate > 1.5:
            c_rate = 1.5
            self.__log.warn("The cell resistance model only works with maximum current power of 1.5 C-rate.")
        soc: float = max(0.0, min(1.0, battery_state.soc))
        # interpolation phase Ri - for charge and discharge direction
        if battery_state.is_charge:
            rint = self.__rint_ch_rgi([c_rate, soc, temperature]) / 1000  # division with 1000 - change values into Ohm
        else:
            rint = self.__rint_dch_rgi([c_rate, soc, temperature]) / 1000  # division with 1000 - change values into Ohm
        return float(rint) / self.get_parallel_scale() * self.get_serial_scale()

    def get_open_circuit_voltage(self, battery_state: LithiumIonState) -> float:
        soc = battery_state.soc
        # temperature range for measured values
        temp_arr = np.array([278.15, 288.15, 298.15, 308.15])
        # temperature window limited between 5°C and 35°C due to test conditions
        if battery_state.temperature > 308.15:
            temperature: float = 308.15
            self.__log.warn("The cell OCV model is only parameterized up to 35°C.")
        elif battery_state.temperature < 278.15:
            temperature: float = 278.15
            self.__log.warn("The cell OCV model is only parameterized down to 5°C.")
        else:
            temperature: float = battery_state.temperature

        # curve fit parameters from OCV fitting tool
        a1 = np.array([-23.9972, -12.7184, 3.3479, -2.8352])
        a2 = np.array([-84.1166, -64.9682, -6.7241, 1.3448])
        a3 = np.array([-0.8678, -19.9681, 2.5958, 5.5920])
        a4 = np.array([-2.1020, -7.6012, -61.9684, -68.9266])
        b1 = np.array([0.1387, 0.0995, 0.6350, 0.2969])
        b2 = np.array([0.0041, 0.0024, 1.4376, -1.0537])
        k0 = np.array([3.3630, 4.2083, 4.5868, 4.9401])
        k1 = np.array([0.1576, 1.5088, 3.1768, -1.9207])
        k2 = np.array([0.3128, 0.4996, -3.8418, -4.9977])
        k3 = np.array([4.8573, 0.0915, -4.6932, -0.3352])
        k4 = np.array([-3.3540, -3.0541, 0.3618,  0.3535])
        k5 = np.array([0.8500, 0.9240, 0.9949, 0.9982])

        # calculate ocv for measured temperatures
        ocv_all_temps = np.empty(len(a1))
        for i in range(0, len(a1)):
            ocv_all_temps[i] = k0[i] + \
                  k1[i] / (1 + math.exp(a1[i] * (soc - b1[i]))) + \
                  k2[i] / (1 + math.exp(a2[i] * (soc - b2[i]))) + \
                  k3[i] / (1 + math.exp(a3[i] * (soc - 1))) +\
                  k4[i] / (1 + math.exp(a4[i] * soc)) +\
                  k5[i] * soc
        values_interp = interpolate.interp1d(temp_arr, ocv_all_temps)
        ocv = values_interp(temperature)
        return ocv * self.get_serial_scale()

    def get_capacity(self, battery_state: LithiumIonState) -> float:
        return self.get_nominal_capacity()

    def close(self):
        self.__log.close()
