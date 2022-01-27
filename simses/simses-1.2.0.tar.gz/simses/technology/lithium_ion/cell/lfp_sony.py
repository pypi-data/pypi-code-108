import math
import pandas as pd
import scipy.interpolate
from simses.commons.config.data.battery import BatteryDataConfig
from simses.commons.config.simulation.battery import BatteryConfig
from simses.commons.log import Logger
from simses.commons.state.technology.lithium_ion import LithiumIonState
from simses.technology.lithium_ion.cell.electric.properties import ElectricalCellProperties
from simses.technology.lithium_ion.cell.format.abstract import CellFormat
from simses.technology.lithium_ion.cell.format.round_26650 import RoundCell26650
from simses.technology.lithium_ion.cell.thermal.properties import ThermalCellProperties
from simses.technology.lithium_ion.cell.type import CellType


class SonyLFP(CellType):
    """
    Source SONY_US26650FTC1_Product Specification and Naumann, Maik. Techno-economic evaluation of stationary
    lithium_ion energy storage systems with special consideration of aging.
    PhD Thesis. Technical University Munich, 2018.
    """

    __SOC_HEADER: str = 'SOC'
    __SOC_IDX: int = 0
    __TEMP_IDX: int = 1
    __C_RATE_IDX: int = 0
    __ETA_IDX: int = 1

    __CELL_VOLTAGE: float = 3.2  # V
    __CELL_CAPACITY: float = 3.0  # Ah
    __MAX_VOLTAGE: float = 3.6  # V
    __MIN_VOLTAGE: float = 2.0  # V
    __MAX_CHARGE_RATE: float = 1.0  # 1/h
    __MAX_DISCHARGE_RATE: float = 6.6  # 1/h
    __SELF_DISCHARGE_RATE: float = 0.1 / (365 / 12)  # X.X%-soc per day, e.g., 0.1 % per month
    __COULOMB_EFFICIENCY: float = 1.0  # p.u.

    __MIN_TEMPERATURE: float = 273.15  # K
    __MAX_TEMPERATURE: float = 333.15  # K
    __SPECIFIC_HEAT: float = 1001  # J/kgK
    __CONVECTION_COEFFICIENT: float = 15  # W/m2K
    __MASS: float = 0.07  # kg per cell

    __ELECTRICAL_PROPS: ElectricalCellProperties = ElectricalCellProperties(__CELL_VOLTAGE, __CELL_CAPACITY,
                                                                            __MIN_VOLTAGE, __MAX_VOLTAGE,
                                                                            __MAX_CHARGE_RATE, __MAX_DISCHARGE_RATE,
                                                                            __SELF_DISCHARGE_RATE, __COULOMB_EFFICIENCY)
    __THERMAL_PROPS: ThermalCellProperties = ThermalCellProperties(__MIN_TEMPERATURE, __MAX_TEMPERATURE, __MASS,
                                                                   __SPECIFIC_HEAT, __CONVECTION_COEFFICIENT)
    __CELL_FORMAT: CellFormat = RoundCell26650()

    pd.set_option('precision', 9)

    def __init__(self, voltage: float, capacity: float, soh: float, battery_config: BatteryConfig,
                 battery_data_config: BatteryDataConfig):
        super().__init__(voltage, capacity, soh, self.__ELECTRICAL_PROPS, self.__THERMAL_PROPS, self.__CELL_FORMAT,
                         battery_config)
        self.__log: Logger = Logger(type(self).__name__)
        rint_file: str = battery_data_config.lfp_sony_rint_file
        internal_resistance = pd.read_csv(rint_file)  # Ohm
        # SOC array has only 11 entries 0:0.1:1
        soc_arr = internal_resistance.iloc[:, self.__SOC_IDX]
        # Temperature array has only 4 values (283.15 K, 298.15 K, 313.15 K, 333.15 K)
        temp_arr = internal_resistance.iloc[:4, self.__TEMP_IDX]
        # internal resistance for charge, Column 2:5 for charging
        rint_mat_ch = internal_resistance.iloc[:, 2:6]
        # internal resistance for discharge, Column 6:9 for charging
        rint_mat_dch = internal_resistance.iloc[:, 6:]
        self.__rint_ch_interp2d = scipy.interpolate.interp2d(temp_arr.T, soc_arr, rint_mat_ch, kind='linear')
        self.__rint_dch_interp2d = scipy.interpolate.interp2d(temp_arr.T, soc_arr, rint_mat_dch, kind='linear')

    def get_open_circuit_voltage(self, battery_state: LithiumIonState) -> float:
        '''Parameters build with ocv fitting'''
        a1 = -116.2064
        a2 = -22.4512
        a3 = 358.9072
        a4 = 499.9994
        b1 = -0.1572
        b2 = -0.0944
        k0 = 2.0020
        k1 = -3.3160
        k2 = 4.9996
        k3 = -0.4574
        k4 = -1.3646
        k5 = 0.1251

        soc = battery_state.soc

        ocv = k0 + \
              k1 / (1 + math.exp(a1 * (soc - b1))) + \
              k2 / (1 + math.exp(a2 * (soc - b2))) + \
              k3 / (1 + math.exp(a3 * (soc - 1))) +\
              k4 / (1 + math.exp(a4 * soc)) +\
              k5 * soc

        return ocv * self.get_serial_scale()

    def get_internal_resistance(self, battery_state: LithiumIonState) -> float:
        if battery_state.is_charge:
            rint = self.__rint_ch_interp2d(battery_state.temperature, battery_state.soc)
        else:
            rint = self.__rint_dch_interp2d(battery_state.temperature, battery_state.soc)
        return float(rint) / self.get_parallel_scale() * self.get_serial_scale()

    def close(self):
        self.__log.close()
