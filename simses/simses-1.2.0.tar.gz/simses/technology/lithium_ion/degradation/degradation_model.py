from abc import ABC

from simses.commons.config.simulation.battery import BatteryConfig
from simses.commons.cycle_detection.cycle_detector import CycleDetector
from simses.commons.error import EndOfLifeError
from simses.commons.log import Logger
from simses.commons.state.technology.lithium_ion import LithiumIonState
from simses.technology.lithium_ion.cell.type import CellType
from simses.technology.lithium_ion.degradation.calendar.calendar_degradation import \
    CalendarDegradationModel
from simses.technology.lithium_ion.degradation.cyclic.cyclic_degradation import \
    CyclicDegradationModel


class DegradationModel(ABC):
    """
    Model for the degradation behavior of the ESS by analysing the resistance increase and capacity decrease.
    """

    def __init__(self,
                 cell: CellType,
                 cyclic_degradation_model: CyclicDegradationModel,
                 calendar_degradation_model: CalendarDegradationModel,
                 cycle_detector: CycleDetector,
                 battery_config: BatteryConfig,
                 initial_degradation_possible: bool = False):
        super().__init__()
        self.__log: Logger = Logger(type(self).__name__)
        self.__calendar_degradation_model: CalendarDegradationModel = calendar_degradation_model
        self.__cyclic_degradation_model: CyclicDegradationModel = cyclic_degradation_model
        self.__cycle_detector: CycleDetector = cycle_detector
        self.__cell: CellType = cell
        self.__end_of_life: float = battery_config.eol
        self.__start_state_of_health: float = cell.get_soh_start()
        self.__total_capacity_loss: float = 0.0
        if self.__start_state_of_health < 1.0 and not initial_degradation_possible:
            raise Exception('\nThe degradation model for the cell type ' + type(cell).__name__ +
                            ' does not allow a start SOH < 1 (here START_SOH = ' + str(self.__start_state_of_health) + ').\n'
                            'Please change the cell type or select START_SOH = 1 in the config file. ')
        # Exception if start SOH is below EOL criterium
        if self.__start_state_of_health < self.__end_of_life:
            raise Exception('\nThe start SOH is below the EOL threshold. '
                            'Please choose a start SOH larger than the EOL threshold. Current values:'
                            + '\nSTART_SOH = ' + str(self.__start_state_of_health)
                            + '\nEOL = ' + str(self.__end_of_life))

    def update(self, time: float, battery_state: LithiumIonState) -> None:
        """
        Updating the capacity and resistance of the lithium_ion through the degradation model.

        Parameters
        ----------
        time : float
            Current timestamp.
        battery_state : LithiumIonState
            Current state of the lithium_ion.

        Returns
        -------

        """
        self.calculate_degradation(time, battery_state)

        # Capacity losses
        battery_state.capacity_loss_cyclic = self.__cyclic_degradation_model.get_degradation() \
                                             * battery_state.nominal_voltage
        battery_state.capacity_loss_calendric = self.__calendar_degradation_model.get_degradation() \
                                                * battery_state.nominal_voltage
        dcapacity: float = 0.0
        dcapacity += battery_state.capacity_loss_cyclic
        dcapacity += battery_state.capacity_loss_calendric
        dcapacity += battery_state.capacity_loss_other

        self.__total_capacity_loss += dcapacity
        # Assumption: capacity losses lead to energy losses within battery (recovery effects are neglected!)
        battery_state.soe -= max(0.0, min(dcapacity, battery_state.soe))
        battery_state.capacity = self.__cell.get_capacity(battery_state) * self.__start_state_of_health * battery_state.nominal_voltage - self.__total_capacity_loss

        self.__log.debug('Capacity loss cyclic: ' + str(battery_state.capacity_loss_cyclic))
        self.__log.debug('Capacity loss calendric: ' + str(battery_state.capacity_loss_calendric))
        self.__log.debug('Capacity loss other: ' + str(battery_state.capacity_loss_other))
        self.__log.debug('Capacity loss total: ' + str(battery_state.capacity_loss_cyclic
                                                       + battery_state.capacity_loss_calendric))

        # Resistance increase
        battery_state.resistance_increase_cyclic = self.__cyclic_degradation_model.get_resistance_increase()
        battery_state.resistance_increase_calendric = self.__calendar_degradation_model.get_resistance_increase()
        battery_state.resistance_increase += (battery_state.resistance_increase_cyclic
                                              + battery_state.resistance_increase_calendric
                                              + battery_state.resistance_increase_other)

        self.__log.debug('Resistance increase cyclic: ' + str(battery_state.resistance_increase_cyclic))
        self.__log.debug('Resistance increase calendric: ' + str(battery_state.resistance_increase_calendric))
        self.__log.debug('Resistance increase other: ' + str(battery_state.resistance_increase_other))
        self.__log.debug('Resistance increase total: ' + str(battery_state.resistance_increase_cyclic
                                                             + battery_state.resistance_increase_calendric))

        battery_state.soh = battery_state.capacity / (self.__cell.get_capacity(battery_state) * battery_state.nominal_voltage)
        self.check_battery_replacement(battery_state)

        battery_state.internal_resistance = self.__cell.get_internal_resistance(battery_state) * \
                                            (1 + battery_state.resistance_increase)
        self.__log.debug('Capacity: ' + str(battery_state.capacity * battery_state.nominal_voltage))
        self.__log.debug('Internal Resistance: ' + str(battery_state.internal_resistance))

    def calculate_degradation(self, time: float, battery_state: LithiumIonState) -> None:
        """
        Calculates the resistance increase and capacity decrease (calendar always and
        cyclic only, if a cycle was detected)

        Parameters
        ----------
        time : float
            Current timestamp.
        battery_state : LithiumIonState
            Current state of the lithium_ion.

        Returns
        -------
        """

        self.__calendar_degradation_model.calculate_degradation(time, battery_state)
        self.__calendar_degradation_model.calculate_resistance_increase(time, battery_state)
        # Cyclic Aging only if cycle is detected
        if self.__cycle_detector.cycle_detected(time, battery_state):
            self.__cyclic_degradation_model.calculate_degradation(battery_state)
            self.__cyclic_degradation_model.calculate_resistance_increase(battery_state)

    def check_battery_replacement(self, battery_state: LithiumIonState) -> None:
        """
        Checks eol criteria and replaces the battery has to be replaced if necessary

        Parameters
        ----------
        battery_state : LithiumIonState
            Current state of the lithium_ion.

        Returns
        -------

        """
        soh = battery_state.soh
        self.__log.debug('SOH: ' + str(soh * 100) + '%')
        if soh < self.__end_of_life:
            raise EndOfLifeError ('Battery SOH is below End of life criteria')
            # self.__log.info('Battery SOH is below End of life criteria (' + str(self.__end_of_life) +
            #                 '). Battery is replaced')
            # battery_state.capacity = self.__cell.get_capacity(battery_state) * battery_state.nominal_voltage
            # battery_state.resistance_increase = 0
            # # resets specific values within a the degradation models
            # self.__calendar_degradation_model.reset(battery_state)
            # self.__cyclic_degradation_model.reset(battery_state)
            # self.__cycle_detector.reset()

    def close(self) -> None:
        """
        Closing all resources in degradation model

        Returns
        -------

        """
        self.__log.close()
        self.__calendar_degradation_model.close()
        self.__cyclic_degradation_model.close()
        self.__cycle_detector.close()
