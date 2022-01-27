from simses.commons.config.simulation.battery import BatteryConfig
from simses.commons.cycle_detection.cycle_detector import CycleDetector
from simses.technology.lithium_ion.cell.type import CellType
from simses.technology.lithium_ion.degradation.calendar.nmc_generic import NMCGenericCalendarDegradationModel
from simses.technology.lithium_ion.degradation.cyclic.nmc_generic import NMCGenericCyclicDegradationModel
from simses.technology.lithium_ion.degradation.degradation_model import DegradationModel


class NMCGenericDegradationModel(DegradationModel):

    def __init__(self, cell_type: CellType, cycle_detector: CycleDetector, battery_config: BatteryConfig):
        super().__init__(cell_type,
                         NMCGenericCyclicDegradationModel(cell_type, cycle_detector),
                         NMCGenericCalendarDegradationModel(cell_type),
                         cycle_detector, battery_config)
