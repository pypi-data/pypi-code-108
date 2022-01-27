from abc import ABC, abstractmethod

from simses.commons.state.technology.electrolyzer import ElectrolyzerState


class CyclicDegradationModel(ABC):
    """
    Degradation Model for the cyclic aging of the Electrolyzer.
    """

    def __init__(self):
        super().__init__()

    def calculate_degradation(self, time: float, state: ElectrolyzerState):
        self.calculate_resistance_increase(time, state)
        self.calculate_exchange_current_dens_decrerase(state)

    @abstractmethod
    def calculate_resistance_increase(self, time: float, state: ElectrolyzerState) -> None:
        """
        update the cyclic internal resistance increase of a electrolyzer
        Parameters
        ----------
            time: Float
            state : HydrogenState

        Returns
        -------

        """
        pass

    @abstractmethod
    def calculate_exchange_current_dens_decrerase(self, state: ElectrolyzerState):
        """
        update the cyclic decrease of the exchange current denisty of the electrolyzer
        :param state:
        :return:
        """
        pass

    @abstractmethod
    def get_resistance_increase(self) -> float:
        """
        get the updated calendary resistance increase
        Returns
        -------
        float:
            resistance increase in [p.u.]
        """
        pass

    @abstractmethod
    def get_exchange_current_dens_decrease(self) -> float:
        """
        get the updated caledric exchange current density decrease
        :return:
        """

    @abstractmethod
    def reset(self, hydrogen_state: ElectrolyzerState) -> None:
        """
        resets all values within a calendar degradation model, if electrolyzer is replaced
        Parameters
        ----------
            hydrogen_state : HydrogenState

        Returns
        -------
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """
        Closing all resources in calendar degradation model

        Returns
        -------

        """
        pass
