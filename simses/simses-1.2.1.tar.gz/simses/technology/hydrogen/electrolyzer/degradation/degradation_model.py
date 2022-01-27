from abc import ABC, abstractmethod

from simses.commons.log import Logger
from simses.commons.state.technology.electrolyzer import ElectrolyzerState
from simses.technology.hydrogen.electrolyzer.degradation.calendar.calendar_degradation import \
    CalendarDegradationModel
from simses.technology.hydrogen.electrolyzer.degradation.cyclic.cyclic_degradation import \
    CyclicDegradationModel


class DegradationModel(ABC):
    """
    Model for the degradation_model_el behavior of the electrolyzer by analysing the resistance increase and exchange current density.
    """

    def __init__(self, cyclic_degradation_model: CyclicDegradationModel, calendar_degradation_model: CalendarDegradationModel):
        super().__init__()
        self.__log: Logger = Logger(type(self).__name__)
        self.__calendar_degradation_model: CalendarDegradationModel = calendar_degradation_model
        self.__cyclic_degradation_model: CyclicDegradationModel = cyclic_degradation_model

    def update(self, time:float, state: ElectrolyzerState) -> None:
        """
        Updating the resistance and exchange current density of the electrolyzer through the degradation_model_el model.

        Parameters
        ----------
        time : float
            Current timestamp.
        state : HydrogenState
            Current state of the hydrogen storage system.

        Returns
        -------

        """
        self.calculate_degradation(time, state)

        # Resistance increase
        if state.resistance_increase_cyclic + self.__cyclic_degradation_model.get_resistance_increase() <= 0:  # check that cyclic resistance is not getting smaller than its inital value
            state.resistance_increase_cyclic = 0
        else:
            state.resistance_increase_cyclic += self.__cyclic_degradation_model.get_resistance_increase()
        state.resistance_increase_calendar = self.__calendar_degradation_model.get_resistance_increase()
        state.resistance_increase = state.resistance_increase_cyclic + state.resistance_increase_calendar

        self.__log.debug('Resistance increase cyclic: ' + str(state.resistance_increase_cyclic))
        self.__log.debug('Resistance increase calendric: ' + str(state.resistance_increase_calendar))
        self.__log.debug('Resistance increase total: ' + str(state.resistance_increase))

        # Exchangecurrent decrease
        state.exchange_current_decrease_cyclic = self.__cyclic_degradation_model.get_exchange_current_dens_decrease()
        state.exchange_current_decrease_calendar = self.__calendar_degradation_model.get_exchange_current_dens_decrease()
        state.exchange_current_decrease = state.exchange_current_decrease_cyclic + \
                                          state.exchange_current_decrease_calendar
        self.__log.debug('Exchange current density decrease cyclic: ' + str(state.exchange_current_decrease_cyclic))
        self.__log.debug('Exchange current density decrease calendric: ' + str(state.exchange_current_decrease_calendar))
        self.__log.debug('Exchange current density decrease total: ' + str(state.exchange_current_decrease))

        self.calculate_soh(state)
        state.soh = self.get_soh_el()

    def calculate_degradation(self, time: float, state: ElectrolyzerState) -> None:
        """
        Calculates degradation parameters of the specific electrolyzer

        Parameters
        ----------
        time : float
            Current timestamp.
        state : HydrogenState
            Current state of the Electrolyzer.

        Returns
        -------
        """

        self.__calendar_degradation_model.calculate_degradation(state)
        self.__cyclic_degradation_model.calculate_degradation(time, state)

    @abstractmethod
    def calculate_soh(self, state: ElectrolyzerState) -> None:
        """
        Calculates the SOH of the electrolyzer

        Parameters
        ----------
        state : HydrogenState
            Current state of health of the electrolyzer.

        Returns
        -------

        """
    pass

    @abstractmethod
    def get_soh_el(self):
        pass


    def close(self) -> None:
        """
        Closing all resources in degradation_model_el model

        Returns
        -------

        """
        self.__log.close()
        self.__calendar_degradation_model.close()
        self.__cyclic_degradation_model.close()
