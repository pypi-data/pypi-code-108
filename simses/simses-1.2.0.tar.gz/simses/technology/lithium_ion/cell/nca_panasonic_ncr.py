import math

import pandas as pd
import scipy.interpolate
from numpy import asarray

from simses.commons.config.data.battery import BatteryDataConfig
from simses.commons.config.simulation.battery import BatteryConfig
from simses.commons.log import Logger
from simses.commons.state.technology.lithium_ion import LithiumIonState
from simses.technology.lithium_ion.cell.electric.properties import ElectricalCellProperties
from simses.technology.lithium_ion.cell.format.abstract import CellFormat
from simses.technology.lithium_ion.cell.format.round_18650 import RoundCell18650
from simses.technology.lithium_ion.cell.thermal.properties import ThermalCellProperties
from simses.technology.lithium_ion.cell.type import CellType


class PanasonicNCA(CellType):
    """An NCA (PanasonicNCR) is a special cell type and inherited by CellType"""
    """Source: 
    P. Keil, S. F. Schuster, J. Wilhelm, J. Travi, A. Hauser, R. C.Karl, A. Jossen, 
    Calendar aging of lithium-ion batteries, Journal of The Electrochemical Society 163 (9) (2016) 
    A1872–A1880.doi:10.1149/2.0411609jes.
    """

    __SOC_HEADER = 'SOC'
    __SOC_IDX = 0
    __OCV_IDX = 1
    __TEMP_IDX = 1
    __C_RATE_IDX = 0
    __ETA_IDX = 1

    __CELL_VOLTAGE = 3.6  # V
    __CELL_CAPACITY = 2.73  # Ah
    __MAX_VOLTAGE: float = 4.2  # V
    __MIN_VOLTAGE: float = 2.5  # V
    __MIN_TEMPERATURE: float = 273.15  # K
    __MAX_TEMPERATURE: float = 318.15  # K
    __MAX_CHARGE_RATE: float = 0.5  # 1/h
    __MAX_DISCHARGE_RATE: float = 3.5  # 1/h
    __SELF_DISCHARGE_RATE: float = 0.0  # X.X%-soc per day, e.g., 0.015 for 1.5% SOC loss per day
    __MASS: float = 0.044  # kg per cell
    __SPECIFIC_HEAT: float = 1048  # J/kgK
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
        rint_file: str = battery_data_config.nca_panasonicNCR_rint_file
        internal_resistance = pd.read_csv(rint_file)  # Ohm
        soc_arr = internal_resistance.iloc[:, self.__SOC_IDX]
        temp_arr = internal_resistance.iloc[:4, self.__TEMP_IDX]
        rint_mat_ch = internal_resistance.iloc[:, 2]
        rint_mat_dch = internal_resistance.iloc[:, 5]
        self.__rint_interp1d_ch = scipy.interpolate.interp1d(soc_arr, rint_mat_ch, kind='linear')
        self.__rint_interp1d_dch = scipy.interpolate.interp1d(soc_arr, rint_mat_dch, kind='linear')
        self.__log.debug('soc arr size: ' + str(len(soc_arr)) + ', temp arr size: ' + str(
            len(temp_arr.T)) + ', rint ch mat size: ' + str(asarray(rint_mat_ch).shape))
        self.__log.debug('soc arr size: ' + str(len(soc_arr)) + ', temp arr size: ' + str(
            len(temp_arr.T)) + ', rint dch mat size: ' + str(asarray(rint_mat_dch).shape))

    def get_open_circuit_voltage(self, battery_state: LithiumIonState) -> float:
        '''Parameters build with ocv fitting'''
        a1 = -0.3777
        a2 = 10.2859
        a3 = 17.0608
        a4 = -3.7820
        b1 = -5.6272
        b2 = 0.2907
        k0 = 4.9852
        k1 = -2.86523
        k2 = 0.3852
        k3 = -0.1599
        k4 = 1.2256
        k5 = 0.7412

        soc = battery_state.soc

        ocv = k0 + \
              k1 / (1 + math.exp(a1 * (soc - b1))) + \
              k2 / (1 + math.exp(a2 * (soc - b2))) + \
              k3 / (1 + math.exp(a3 * (soc - 1))) +\
              k4 / (1 + math.exp(a4 * soc)) +\
              k5 * soc

        return ocv * self.get_serial_scale()

    def get_internal_resistance(self, battery_state: LithiumIonState) -> float:
        soc: float = self.check_soc_range(battery_state.soc)
        if battery_state.is_charge:
            # internal resistance for charge
            res = self.__rint_interp1d_ch(soc)
            self.__log.debug('res charging: ' + str(res / self.get_parallel_scale() * self.get_serial_scale()))
            return float(res / self.get_parallel_scale() * self.get_serial_scale())
        else:
            # internal resistance for discharge
            res = self.__rint_interp1d_dch(soc)
            self.__log.debug('res discharging: ' + str(res / self.get_parallel_scale() * self.get_serial_scale()))
            return float(res / self.get_parallel_scale() * self.get_serial_scale())

    def close(self):
        self.__log.close()
