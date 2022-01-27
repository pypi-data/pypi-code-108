from abc import ABC, abstractmethod

from simses.commons.timeseries.timevalue import TimeValue


class Average(ABC):
    """
    Averages values of multiple TimeValues with a specific behaviour (arithmetic mean, median, ...)
    """

    def __init__(self):
        super().__init__()

    @abstractmethod
    def average(self, data: [TimeValue]) -> float:
        """
        Averages values of data

        Parameters
        ----------
        data :
            List of TimeValue objects

        Returns
        -------
        float:
            averaged value
        """
        pass
