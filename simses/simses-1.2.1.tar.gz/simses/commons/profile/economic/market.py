from abc import ABC, abstractmethod


class MarketProfile(ABC):
    """
    Profile of market prices for a time frame.
    """
    def __init__(self):
        super().__init__()

    @abstractmethod
    def next(self, time: float) -> float:
        """
        provides the next market data (price) of a specific market

        Parameters
        ----------

        Returns
        -------
        float
            next price signal
        """
        pass

    @abstractmethod
    def initialize_profile(self) -> None:
        pass

    @abstractmethod
    def close(self):
        """
        Closing all open resources in market profile

        Parameters
        ----------

        Returns
        -------

        """
        pass
