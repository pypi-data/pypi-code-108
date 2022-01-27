from abc import ABC, abstractmethod

from simses.system.auxiliary.auxiliary import Auxiliary


class DcLoad(ABC):

    """
    Abstract class for every DC load
    """

    def __init__(self):
        super().__init__()

    @abstractmethod
    def get_power(self) -> float:
        """

        Returns
        -------
        float:
            DC load power in W
        """
        pass

    @abstractmethod
    def calculate_power(self, time: float) -> None:
        """
        Calculates power for next timestep

        Parameters
        ----------
        time :
            timestamp in s
        """
        pass

    @abstractmethod
    def get_auxiliaries(self) -> [Auxiliary]:
        pass

    @abstractmethod
    def close(self) -> None:
        pass
