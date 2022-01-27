from simses.commons.config.simulation.battery import BatteryConfig
from simses.commons.cycle_detection.cycle_detector import CycleDetector
from simses.technology.lithium_ion.cell.type import CellType
from simses.technology.lithium_ion.degradation.calendar.nmc_sanyo_ur18650e import \
    SanyoNMCCalendarDegradationModel
from simses.technology.lithium_ion.degradation.cyclic.nmc_sanyo_ur18650e import \
    SanyoNMCCyclicDegradationModel
from simses.technology.lithium_ion.degradation.degradation_model import DegradationModel


class SanyoNMCDegradationModel(DegradationModel):
    def __init__(self, cell_type: CellType, cycle_detector: CycleDetector, battery_config: BatteryConfig):
        super().__init__(cell_type, SanyoNMCCyclicDegradationModel(cell_type, cycle_detector),
                         SanyoNMCCalendarDegradationModel(cell_type), cycle_detector,
                         battery_config)