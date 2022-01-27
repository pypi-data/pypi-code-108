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


class LGMJ1_NMC(CellType):
    """An LG_INR18650MJ1 is a special cell type and inherited by CellType"""

    __SOC_HEADER: str = 'SOC'
    __SOC_IDX: int = 0
    __TEMP_IDX: int = 1
    __C_RATE_IDX: int = 0
    __ETA_IDX: int = 1

    # Source: Datasheet LG INR18650 MJ1

    __CELL_VOLTAGE: float = 3.635  # V
    __CELL_CAPACITY: float = 3.5  # Ah
    __MAX_VOLTAGE: float = 4.2   # V
    __MIN_VOLTAGE: float = 2.5   # V

    __MIN_TEMPERATURE: float = -253.15  # K
    __MAX_TEMPERATURE: float = 333.15  # K
    __MAX_CHARGE_RATE: float = 1.0  # 1/h
    __MAX_DISCHARGE_RATE: float = 2.875  # 1/h

    __MASS: float = 0.049  # kg per cell

    # Source: Zilberman I., Sturm J., Jossen A.
    # Reversible self-discharge and calendar aging of 18650 nickel-rich silicon-graphite lithium-ion cells
    # Journal of Power Sources, https://doi.org/10.1016/j.jpowsour.2019.03.109

    __CELL_RESISTANCE: float = 0.04431  # Ohm # from lmo_daimler Source:
    __SELF_DISCHARGE_RATE: float = 0 # X.X%-soc per month in second step, e.g., 0.015 / (30.5 * 24 * 3600) for 1.5%
    # __SELF_DISCHARGE_RATE: float = 0.0027 / (30.5 * 24 * 3600)  # X.X%-soc per month in second step, e.g., 0.015 / (30.5 * 24 * 3600)

    # Source of specific heat:
    # Steinhardt M., Gillich E.I., Rheinfeld A., Kraft L., Spielbauer M., Bohlen O., Jossen A.
    # Low-effort determination of heat capacity and thermal conductivity for
    # cylindrical 18650 and 21700 lithium-ion cells
    # Journal of Energy Storage, https://doi.org/10.1016/j.est.2021.103065

    __SPECIFIC_HEAT: float = 999.45 # J/kgK
    __CONVECTION_COEFFICIENT: float = 15  # W/m2K convection coefficient of nmc sanyo ur18650e

    __COULOMB_EFFICIENCY: float = 1.0  # p.u.

    __ELECTRICAL_PROPS: ElectricalCellProperties = ElectricalCellProperties(__CELL_VOLTAGE, __CELL_CAPACITY,
                                                                            __MIN_VOLTAGE, __MAX_VOLTAGE,
                                                                            __MAX_CHARGE_RATE, __MAX_DISCHARGE_RATE,
                                                                            __SELF_DISCHARGE_RATE,
                                                                            __COULOMB_EFFICIENCY)
    __THERMAL_PROPS: ThermalCellProperties = ThermalCellProperties(__MIN_TEMPERATURE, __MAX_TEMPERATURE, __MASS,
                                                                   __SPECIFIC_HEAT, __CONVECTION_COEFFICIENT)
    __CELL_FORMAT: CellFormat = RoundCell18650()

    pd.set_option('precision', 9)

    def __init__(self, voltage: float, capacity: float, soh: float, battery_config: BatteryConfig,
                 battery_data_config: BatteryDataConfig):
        super().__init__(voltage, capacity, soh, self.__ELECTRICAL_PROPS, self.__THERMAL_PROPS, self.__CELL_FORMAT,
                         battery_config)
        self.__log: Logger = Logger(type(self).__name__)

    # Source: J. Sturm, A. Rheinfeld, I. Zilberman, F.B. Spingler, S. Kosch, F. Frie, A. Jossen
    # Modeling and simulation of inhomogeneities in a 18650 nickel-rich, silicon-graphite lithium-ion cell
    # during fast charging
    # Journal of Power Sources, https://doi.org/10.1016/j.jpowsour.2018.11.043

    def get_open_circuit_voltage(self, battery_state: LithiumIonState) -> float:
        '''Parameters build with ocv fitting'''
        a1 = 15.2751
        a2 = 49.5206
        a3 = 1.63050
        a4 = 121.702
        b1 = -0.1848
        b2 = -0.6339
        k0 = 4.99612
        k1 = -4.9026
        k2 = 0.55138
        k3 = -1.9184
        k4 = -0.6234
        k5 = 0.15706

        soc = battery_state.soc

        ocv = k0 + \
              k1 / (1 + math.exp(a1 * (soc - b1))) + \
              k2 / (1 + math.exp(a2 * (soc - b2))) + \
              k3 / (1 + math.exp(a3 * (soc - 1))) +\
              k4 / (1 + math.exp(a4 * soc)) +\
              k5 * soc

        return ocv * self.get_serial_scale()

    def get_internal_resistance(self, battery_state: LithiumIonState) -> float:
        return float(self.__CELL_RESISTANCE / self.get_parallel_scale() * self.get_serial_scale())

    def close(self):
        self.__log.close()