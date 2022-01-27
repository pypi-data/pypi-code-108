import math

import pandas as pd
import scipy.interpolate

from simses.commons.config.data.battery import BatteryDataConfig
from simses.commons.config.simulation.battery import BatteryConfig
from simses.commons.log import Logger
from simses.commons.state.technology.lithium_ion import LithiumIonState
from simses.technology.lithium_ion.cell.electric.properties import ElectricalCellProperties
from simses.technology.lithium_ion.cell.format.abstract import CellFormat
from simses.technology.lithium_ion.cell.format.round_18650 import RoundCell18650
from simses.technology.lithium_ion.cell.thermal.properties import ThermalCellProperties
from simses.technology.lithium_ion.cell.type import CellType


class MolicelNMC(CellType):
    """An NMC (NMC_Molicel) is a special cell type and inherited by CellType"""
    """Source: 
    Schuster, S. F., Bach, T., Fleder, E., Müller, J., Brand, M., Sextl, G., & Jossen, A. (2015). 
    Nonlinear aging characteristics of lithium-ion cells under different operational conditions. 
    Journal of Energy Storage, 1, 44–53. doi:10.1016/j.est.2015.05.003 """

    __SOC_IDX = 0

    __CELL_VOLTAGE = 3.7  # V
    __CELL_CAPACITY = 1.9  # Ah
    __MAX_VOLTAGE: float = 4.25  # V
    __MIN_VOLTAGE: float = 3.0  # V
    __MIN_TEMPERATURE: float = 273.15  # K
    __MAX_TEMPERATURE: float = 318.15  # K
    __MAX_CHARGE_RATE: float = 1.05  # 1/h
    __MAX_DISCHARGE_RATE: float = 2.1  # 1/h
    __SELF_DISCHARGE_RATE: float = 0.0  # X.X%-soc per day, e.g., 0.015 for 1.5% SOC loss per day
    __MASS: float = 0.045  # kg per cell
    __SPECIFIC_HEAT: float = 965  # J/kgK
    __CONVECTION_COEFFICIENT: float = 15  # W/m2K

    __COULOMB_EFFICIENCY: float = 1.0  # p.u.

    __ELECTRICAL_PROPS: ElectricalCellProperties = ElectricalCellProperties(__CELL_VOLTAGE, __CELL_CAPACITY,
                                                                            __MIN_VOLTAGE, __MAX_VOLTAGE,
                                                                            __MAX_CHARGE_RATE, __MAX_DISCHARGE_RATE,
                                                                            __SELF_DISCHARGE_RATE, __COULOMB_EFFICIENCY)
    __THERMAL_PROPS: ThermalCellProperties = ThermalCellProperties(__MIN_TEMPERATURE, __MAX_TEMPERATURE, __MASS,
                                                                   __SPECIFIC_HEAT, __CONVECTION_COEFFICIENT)
    __CELL_FORMAT: CellFormat = RoundCell18650()

    pd.set_option('precision', 9)

    def __init__(self, voltage: float, capacity: float, soh: float, battery_config: BatteryConfig,
                 battery_data_config: BatteryDataConfig):
        super().__init__(voltage, capacity, soh, self.__ELECTRICAL_PROPS, self.__THERMAL_PROPS, self.__CELL_FORMAT,
                         battery_config)

        self.__log: Logger = Logger(type(self).__name__)
        rint_file: str = battery_data_config.nmc_molicel_rint_file
        internal_resistance = pd.read_csv(rint_file)  # Ohm
        soc_arr = internal_resistance.iloc[:, self.__SOC_IDX]
        rint_mat_ch = internal_resistance.iloc[:, 2]
        rint_mat_dch = internal_resistance.iloc[:, 5]
        self.__rint_ch_interp1d = scipy.interpolate.interp1d(soc_arr, rint_mat_ch, kind='linear')
        self.__rint_dch_interp1d = scipy.interpolate.interp1d(soc_arr, rint_mat_dch, kind='linear')

    def get_open_circuit_voltage(self, battery_state: LithiumIonState) -> float:
        '''Parameters build with ocv fitting'''
        a1 = -1.6206
        a2 = -6.9895
        a3 = 1.4458
        a4 = 1.9530
        b1 = 3.4206
        b2 = 0.8759
        k0 = 2.0127
        k1 = 2.7684
        k2 = 1.0698
        k3 = 4.1431
        k4 = -3.8417
        k5 = -0.1856
        soc = battery_state.soc

        ocv = k0 + \
              k1 / (1 + math.exp(a1 * (soc - b1))) + \
              k2 / (1 + math.exp(a2 * (soc - b2))) + \
              k3 / (1 + math.exp(a3 * (soc - 1))) +\
              k4 / (1 + math.exp(a4 * soc)) +\
              k5 * soc

        return ocv * self.get_serial_scale()

    def get_internal_resistance(self, battery_state: LithiumIonState) -> float:
        soc = self.check_soc_range(battery_state.soc)
        if battery_state.is_charge:
            rint = self.__rint_ch_interp1d(soc)
        else:
            rint = self.__rint_dch_interp1d(soc)
        return float(rint) / self.get_parallel_scale() * self.get_serial_scale()

    def close(self):
        self.__log.close()
