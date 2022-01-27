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


class SanyoNMC(CellType):
    """An NMC (Sanyo UR18650E) is a special cell type and inherited by CellType"""

    """Source: Schmalstieg, J., Käbitz, S., Ecker, M., & Sauer, D. U. (2014). 
    A holistic aging model for Li (NiMnCo) O2 based 18650 lithium-ion batteries. 
    Journal of Power Sources, 257, 325-334."""

    __SOC_HEADER = 'SOC'
    __SOC_IDX = 0
    __OCV_IDX = 1
    __TEMP_IDX = 1
    __C_RATE_IDX = 0
    __ETA_IDX = 1

    __CELL_VOLTAGE = 3.6  # V
    __CELL_CAPACITY = 2.05  # Ah
    __MAX_VOLTAGE: float = 4.2  # V
    __MIN_VOLTAGE: float = 2.5  # V
    __MIN_TEMPERATURE: float = 273.15  # K
    __MAX_TEMPERATURE: float = 313.15  # K
    __MAX_CHARGE_RATE: float = 1.0  # 1/h
    __MAX_DISCHARGE_RATE: float = 3.0  # 1/h
    __SELF_DISCHARGE_RATE: float = 0.0  # X.X%-soc per day, e.g., 0.015 for 1.5% SOC loss per day
    __MASS: float = 0.046  # kg per cell
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
        rint_file: str = battery_data_config.nmc_sanyo_rint_file
        internal_resistance = pd.read_csv(rint_file)  # Ohm
        self.__log.warn('No Rint data for this cell. internal Resistance from Molicel is assumed.')
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
        a1 = -7.7487
        a2 = -0.0974
        a3 = 1.2023
        a4 = 3.9977
        b1 = -0.1714
        b2 = 2.6526
        k0 = 2.3885
        k1 = 2.1430
        k2 = -0.6287
        k3 = -1.6708
        k4 = 1.6161
        k5 = 0.7234
        soc = battery_state.soc

        ocv = k0 + \
              k1 / (1 + math.exp(a1 * (soc - b1))) + \
              k2 / (1 + math.exp(a2 * (soc - b2))) + \
              k3 / (1 + math.exp(a3 * (soc - 1))) +\
              k4 / (1 + math.exp(a4 * soc)) +\
              k5 * soc

        return ocv * self.get_serial_scale()

    def get_internal_resistance(self, battery_state: LithiumIonState) -> float:
        # internal resistance from Molicel!
        soc = battery_state.soc
        soc = self.check_soc_range(soc)
        if battery_state.is_charge:
            # internal resistance for charge
            res = self.__rint_interp1d_ch(soc)
            self.__log.debug('res charging: ' + str(res / self.get_parallel_scale() * self.get_serial_scale()))
        else:
            # internal resistance for discharge
            res = self.__rint_interp1d_dch(soc)
            self.__log.debug('res discharging: ' + str(res / self.get_parallel_scale() * self.get_serial_scale()))
        return float(res) / self.get_parallel_scale() * self.get_serial_scale()

    def close(self):
        self.__log.close()
