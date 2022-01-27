from simses.commons.config.simulation.battery import BatteryConfig
from simses.commons.cycle_detection.cycle_detector import CycleDetector
from simses.technology.lithium_ion.cell.type import CellType
from simses.technology.lithium_ion.degradation.calendar.nmc_lgmj1 import LGMJ1_NMCCalendarDegradationModel
from simses.technology.lithium_ion.degradation.cyclic.nmc_lgmj1 import LGMJ1_NMCCyclicDegradationModel
from simses.technology.lithium_ion.degradation.degradation_model import DegradationModel


class LGMJ1_NMCDegradationModel(DegradationModel):

    def __init__(self, cell_type: CellType, cycle_detector: CycleDetector, battery_config: BatteryConfig):
        super().__init__(cell_type, LGMJ1_NMCCyclicDegradationModel(cell_type, cycle_detector),
                         LGMJ1_NMCCalendarDegradationModel(cell_type), cycle_detector, battery_config)
