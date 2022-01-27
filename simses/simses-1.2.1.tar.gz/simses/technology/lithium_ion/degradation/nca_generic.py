from simses.commons.config.simulation.battery import BatteryConfig
from simses.commons.cycle_detection.cycle_detector import CycleDetector
from simses.technology.lithium_ion.cell.type import CellType
from simses.technology.lithium_ion.degradation.calendar.nca_generic import NCAGenericCalendarDegradationModel
from simses.technology.lithium_ion.degradation.cyclic.nca_generic import NCAGenericCyclicDegradationModel
from simses.technology.lithium_ion.degradation.degradation_model import DegradationModel


class NCAGenericDegradationModel(DegradationModel):

    def __init__(self, cell_type: CellType, cycle_detector: CycleDetector, battery_config: BatteryConfig):
        super().__init__(cell_type,
                         NCAGenericCyclicDegradationModel(cell_type, cycle_detector),
                         NCAGenericCalendarDegradationModel(cell_type),
                         cycle_detector, battery_config)
