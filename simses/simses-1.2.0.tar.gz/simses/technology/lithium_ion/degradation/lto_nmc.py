from simses.commons.config.simulation.battery import BatteryConfig
from simses.commons.cycle_detection.cycle_detector import CycleDetector
from simses.technology.lithium_ion.cell.type import CellType
from simses.technology.lithium_ion.degradation.calendar.lto_nmc import LTONMCCalendarDegradationModel
from simses.technology.lithium_ion.degradation.cyclic.lto_nmc import LTONMCCyclicDegradationModel
from simses.technology.lithium_ion.degradation.degradation_model import DegradationModel


class LTONMCDegradationModel(DegradationModel):

    def __init__(self, cell_type: CellType, cycle_detector: CycleDetector, battery_config: BatteryConfig):
        super().__init__(cell_type, LTONMCCyclicDegradationModel(cell_type, cycle_detector),
                         LTONMCCalendarDegradationModel(cell_type), cycle_detector, battery_config)
