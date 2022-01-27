import pandas as pd

from simses.commons.config.simulation.battery import BatteryConfig
from simses.commons.log import Logger
from simses.commons.state.technology.lithium_ion import LithiumIonState
from simses.technology.lithium_ion.cell.electric.default import DefaultElectricalCellProperties
from simses.technology.lithium_ion.cell.electric.properties import ElectricalCellProperties
from simses.technology.lithium_ion.cell.format.abstract import CellFormat
from simses.technology.lithium_ion.cell.format.round import RoundCell
from simses.technology.lithium_ion.cell.thermal.default import DefaultThermalCellProperties
from simses.technology.lithium_ion.cell.thermal.properties import ThermalCellProperties
from simses.technology.lithium_ion.cell.type import CellType


class GenericCell(CellType):
    """An GenericCell is a special cell type and inherited by CellType"""

    __INTERNAL_RESISTANCE: float = 0.010  # Ohm

    __DIAMETER: float = 22  # mm
    __LENGTH: float = 70  # mm

    __ELECTRICAL_PROPS: ElectricalCellProperties = DefaultElectricalCellProperties()
    __THERMAL_PROPS: ThermalCellProperties = DefaultThermalCellProperties()
    __CELL_FORMAT: CellFormat = RoundCell(__DIAMETER, __LENGTH)

    pd.set_option('precision', 9)

    def __init__(self, voltage: float, capacity: float, soh: float, battery_config: BatteryConfig):
        super().__init__(voltage, capacity, soh, self.__ELECTRICAL_PROPS, self.__THERMAL_PROPS, self.__CELL_FORMAT,
                         battery_config)
        self.__log: Logger = Logger(type(self).__name__)

    def get_open_circuit_voltage(self, battery_state: LithiumIonState) -> float:
        return (3.0 + battery_state.soc) * self.get_serial_scale()

    def get_internal_resistance(self, battery_state: LithiumIonState) -> float:
        return float(self.__INTERNAL_RESISTANCE / self.get_parallel_scale() * self.get_serial_scale())

    def close(self):
        self.__log.close()
