from simses.commons.config.simulation.battery import BatteryConfig
from simses.commons.cycle_detection.cycle_detector import CycleDetector
from simses.technology.lithium_ion.cell.type import CellType
from simses.technology.lithium_ion.degradation.calendar.generic_cell import \
    GenericCellCalendarDegradationModel
from simses.technology.lithium_ion.degradation.cyclic.generic_cell import \
    GenericCellCyclicDegradationModel
from simses.technology.lithium_ion.degradation.degradation_model import DegradationModel


class GenericCellDegradationModel(DegradationModel):

    def __init__(self, cell_type: CellType, cycle_detector: CycleDetector, battery_config: BatteryConfig):
        super().__init__(cell_type, GenericCellCyclicDegradationModel(cell_type, cycle_detector, battery_config),
                         GenericCellCalendarDegradationModel(cell_type, battery_config), cycle_detector,
                         battery_config)