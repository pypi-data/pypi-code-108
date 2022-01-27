from simses.commons.config.simulation.battery import BatteryConfig
from simses.commons.cycle_detection.cycle_detector import CycleDetector
from simses.technology.lithium_ion.cell.type import CellType
from simses.technology.lithium_ion.degradation.calendar.nmc_molicel import \
    MolicelNMCCalendarDegradationModel
from simses.technology.lithium_ion.degradation.cyclic.nmc_molicel import \
    MolicelNMCCyclicDegradationModel
from simses.technology.lithium_ion.degradation.degradation_model import DegradationModel


class DaimlerLMODegradationModel(DegradationModel):
    """ Degradation Model for Second-Life cell. Specific model unknown, therefore using different existing
    degradation models from SimSES."""

    def __init__(self, cell_type: CellType, cycle_detector: CycleDetector, battery_config: BatteryConfig):
        super().__init__(cell_type, MolicelNMCCyclicDegradationModel(cell_type, cycle_detector),
                         MolicelNMCCalendarDegradationModel(cell_type), cycle_detector, battery_config,
                         initial_degradation_possible=True)
