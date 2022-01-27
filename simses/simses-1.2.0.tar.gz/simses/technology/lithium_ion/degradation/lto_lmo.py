from simses.commons.config.simulation.battery import BatteryConfig
from simses.commons.cycle_detection.cycle_detector import CycleDetector
from simses.technology.lithium_ion.cell.type import CellType
from simses.technology.lithium_ion.degradation.calendar.lto_lmo import LTOLMOCalendarDegradationModel
from simses.technology.lithium_ion.degradation.cyclic.lto_lmo import LTOLMOCyclicDegradationModel
from simses.technology.lithium_ion.degradation.degradation_model import DegradationModel


class LTOLMODegradationModel(DegradationModel):

    def __init__(self, cell_type: CellType, cycle_detector: CycleDetector, battery_config: BatteryConfig):
        super().__init__(cell_type, LTOLMOCyclicDegradationModel(cell_type, cycle_detector),
                         LTOLMOCalendarDegradationModel(cell_type), cycle_detector, battery_config)
