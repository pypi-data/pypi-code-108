import pandas as pd
import math

from simses.commons.config.simulation.battery import BatteryConfig
from simses.commons.log import Logger
from simses.commons.state.technology.lithium_ion import LithiumIonState
from simses.technology.lithium_ion.cell.electric.properties import ElectricalCellProperties
from simses.technology.lithium_ion.cell.format.abstract import CellFormat
from simses.technology.lithium_ion.cell.format.round import RoundCell
from simses.technology.lithium_ion.cell.thermal.properties import ThermalCellProperties
from simses.technology.lithium_ion.cell.type import CellType


class NRELDummyCell(CellType):
    """An GenericCell is a special cell type and inherited by CellType"""

    __CELL_VOLTAGE = 3.7  # V
    __CELL_CAPACITY = 2.5  # Ah
    __MAX_VOLTAGE: float = 4.2  # V
    __MIN_VOLTAGE: float = 3  # V
    __MIN_TEMPERATURE: float = 273.15  # K
    __MAX_TEMPERATURE: float = 333.15  # K
    __MAX_CHARGE_RATE: float = 2.0  # 1/h
    __MAX_DISCHARGE_RATE: float = 2.0  # 1/h
    __SELF_DISCHARGE_RATE: float = 0.0  # X.X%-soc per day, e.g., 0.015 for 1.5% SOC loss per day
    __MASS: float = 0.05  # kg per cell
    __SPECIFIC_HEAT: float = 700  # J/kgK
    __CONVECTION_COEFFICIENT: float = 15  # W/m2K

    __INTERNAL_RESISTANCE: float = 1.155e-3  # Ohm
    __TEMP_REF = 298  # K
    __TEMP_RPT = 318
    __Ea_a01 = 28640  # J
    __a_0_1 = 0.442
    __a_0_2 = -0.199
    __Ea_a02 = -46010  # J/mol
    __R = 8.314  # J/mol/K gas constant
    a_0 = __a_0_1 * math.exp(
        (-__Ea_a01 / __R) * (1 / __TEMP_RPT - 1 / __TEMP_REF)) + __a_0_2 * math.exp(
        (-__Ea_a02 / __R * (1 / __TEMP_RPT - 1 / __TEMP_REF)))  # Base resistance
    __Temperature_dependence_initial_res = math.exp(28640/8.314*(1 / __TEMP_RPT - 1 / __TEMP_REF))

    __DIAMETER: float = 22  # mm
    __LENGTH: float = 70  # mm

    __COULOMB_EFFICIENCY: float = 1.0  # p.u

    __ELECTRICAL_PROPS: ElectricalCellProperties = ElectricalCellProperties(__CELL_VOLTAGE, __CELL_CAPACITY,
                                                                            __MIN_VOLTAGE, __MAX_VOLTAGE,
                                                                            __MAX_CHARGE_RATE, __MAX_DISCHARGE_RATE,
                                                                            __SELF_DISCHARGE_RATE, __COULOMB_EFFICIENCY)
    __THERMAL_PROPS: ThermalCellProperties = ThermalCellProperties(__MIN_TEMPERATURE, __MAX_TEMPERATURE, __MASS,
                                                                   __SPECIFIC_HEAT, __CONVECTION_COEFFICIENT)
    __CELL_FORMAT: CellFormat = RoundCell(__DIAMETER, __LENGTH)

    pd.set_option('precision', 9)

    def __init__(self, voltage: float, capacity: float, soh: float, battery_config: BatteryConfig):
        super().__init__(voltage, capacity, soh, self.__ELECTRICAL_PROPS, self.__THERMAL_PROPS, self.__CELL_FORMAT,
                         battery_config)
        self.__log: Logger = Logger(type(self).__name__)

    def get_open_circuit_voltage(self, battery_state: LithiumIonState) -> float:
        return self.__CELL_VOLTAGE * self.get_serial_scale()

    def get_internal_resistance(self, battery_state: LithiumIonState) -> float:
        return float((self.__INTERNAL_RESISTANCE / self.get_parallel_scale() * self.get_serial_scale())) * \
                    self.__Temperature_dependence_initial_res

    def close(self):
        self.__log.close()
