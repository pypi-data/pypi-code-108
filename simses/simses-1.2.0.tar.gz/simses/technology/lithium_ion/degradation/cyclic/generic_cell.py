from simses.commons.config.simulation.battery import BatteryConfig
from simses.commons.cycle_detection.cycle_detector import CycleDetector
from simses.commons.log import Logger
from simses.commons.state.technology.lithium_ion import LithiumIonState
from simses.technology.lithium_ion.cell.type import CellType
from simses.technology.lithium_ion.degradation.cyclic.cyclic_degradation import \
    CyclicDegradationModel


class GenericCellCyclicDegradationModel(CyclicDegradationModel):

    def __init__(self, cell_type: CellType, cycle_detector: CycleDetector, battery_config: BatteryConfig):
        super().__init__(cell_type, cycle_detector)
        self.__log: Logger = Logger(type(self).__name__)
        self.__total_capacity_decrease = 0
        self.__capacity_decrease = 0
        self.__initial_capacity = self._cell.get_nominal_capacity()
        self.__end_of_life_cycles = battery_config.max_equivalent_full_cycles  # FEC till EOL (=xy%) is reached. 2000 in this case
        self.__end_of_life = battery_config.eol  # EOL criteria xy%.
        self.__log.info('Considering ' + str(self.__end_of_life_cycles) + ' cycles over lifetime')

    def calculate_degradation(self, battery_state: LithiumIonState) -> None:
        # Cyclic degradation in dummy cell is linear
        self.__capacity_decrease = self._cycle_detector.get_full_equivalent_cycle() * \
                                   (1 - self.__end_of_life) / self.__end_of_life_cycles # pu

        self.__capacity_decrease = self.__capacity_decrease * self.__initial_capacity # in Ah

    def calculate_resistance_increase(self, battery_state: LithiumIonState) -> None:
        pass # No resistance increase in dummy cell model

    def get_degradation(self) -> float:
        degradation = self.__capacity_decrease - self.__total_capacity_decrease
        # Update total capacity decrease
        self.__total_capacity_decrease = self.__capacity_decrease
        return degradation

    def get_resistance_increase(self) -> float:
        return 0 # No resistance increase in dummy cell model

    def reset(self, lithium_ion_state: LithiumIonState) -> None:
        self.__capacity_decrease = 0
        self.__total_capacity_decrease = 0

    def close(self) -> None:
        self.__log.close()
