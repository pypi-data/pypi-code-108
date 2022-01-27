from abc import ABC, abstractmethod

from simses.commons.timeseries.timevalue import TimeValue


class Interpolation(ABC):
    """
    Interpolation implementations are to interpolate values between values as TimeValue objects. Each implementation
    has a specific interpolation behaviour (linear, splines, ...).
    """

    def __init__(self):
        super().__init__()

    @staticmethod
    def is_necessary(tstmp: float, data: [TimeValue]) -> bool:
        if len(data) == 2:
            return data[-2].time < tstmp <= data[-1].time
        return False

    @abstractmethod
    def interpolate(selfself, time: float, recent: TimeValue, last: TimeValue) -> float:
        """
        Interpolate values of given TimeValue objects to time

        Parameters
        ----------
        time :
            timestamp in s which lies in between recent and last
        recent :
            TimeValue with a timestamp >= time
        last :
            TimeValue with a timestamp <= time

        Returns
        -------
        float:
            interpolated value
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """
        Closing resources in interpolation

        Returns
        -------

        """
        pass
