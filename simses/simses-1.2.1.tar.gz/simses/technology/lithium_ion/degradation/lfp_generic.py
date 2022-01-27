from simses.commons.config.simulation.battery import BatteryConfig
from simses.commons.cycle_detection.cycle_detector import CycleDetector
from simses.technology.lithium_ion.cell.type import CellType
from simses.technology.lithium_ion.degradation.calendar.lfp_generic import LFPGenericCalendarDegradationModel
from simses.technology.lithium_ion.degradation.cyclic.lfp_generic import LFPGenericCyclicDegradationModel
from simses.technology.lithium_ion.degradation.degradation_model import DegradationModel


class LFPGenericDegradationModel(DegradationModel):

    def __init__(self, cell_type: CellType, cycle_detector: CycleDetector, battery_config: BatteryConfig):
        super().__init__(cell_type,
                         LFPGenericCyclicDegradationModel(cell_type, cycle_detector),
                         LFPGenericCalendarDegradationModel(cell_type),
                         cycle_detector, battery_config)
