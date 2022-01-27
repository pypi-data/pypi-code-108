from simses.commons.config.simulation.battery import BatteryConfig
from simses.commons.cycle_detection.cycle_detector import CycleDetector
from simses.technology.lithium_ion.cell.type import CellType
from simses.technology.lithium_ion.degradation.calendar.no_calendar_dedradation import \
    NoCalendarDegradationModel
from simses.technology.lithium_ion.degradation.cyclic.no_cyclic_degradation import \
    NoCyclicDegradationModel
from simses.technology.lithium_ion.degradation.degradation_model import DegradationModel


class NoDegradationModel(DegradationModel):

    def __init__(self, cell: CellType, cycle_detector:CycleDetector, battery_config: BatteryConfig):
        super().__init__(cell, NoCyclicDegradationModel(), NoCalendarDegradationModel(), cycle_detector, battery_config)