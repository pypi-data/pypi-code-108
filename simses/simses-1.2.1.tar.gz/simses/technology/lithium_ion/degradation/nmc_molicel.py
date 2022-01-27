from simses.commons.config.data.battery import BatteryDataConfig
from simses.commons.config.simulation.battery import BatteryConfig
from simses.commons.cycle_detection.cycle_detector import CycleDetector
from simses.technology.lithium_ion.cell.type import CellType
from simses.technology.lithium_ion.degradation.calendar.nmc_molicel import \
    MolicelNMCCalendarDegradationModel
from simses.technology.lithium_ion.degradation.cyclic.nmc_molicel import \
    MolicelNMCCyclicDegradationModel
from simses.technology.lithium_ion.degradation.degradation_model import DegradationModel


class MolicelNMCDegradationModel(DegradationModel):

    def __init__(self, cell_type: CellType, cycle_detector:CycleDetector, battery_config: BatteryConfig, battery_data_config: BatteryDataConfig):
        super().__init__(cell_type, MolicelNMCCyclicDegradationModel(cell_type, cycle_detector, battery_data_config),
                         MolicelNMCCalendarDegradationModel(cell_type, battery_data_config), cycle_detector,
                         battery_config, initial_degradation_possible=True)
