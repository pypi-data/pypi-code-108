
class TimeValue:
    """
    TimeValue is a data class with a timestamp connected to value.
    """

    def __init__(self, tstmp: float, value: float):
        """
        Constructor of TimeValue

        Parameters
        ----------
        tstmp :
            epoch timestamp in s
        value :
            value connected to timestamp
        """
        self.__tstmp: float = tstmp
        self.__value: float = value

    @property
    def time(self) -> float:
        return self.__tstmp

    @time.setter
    def time(self, value: float) -> None:
        self.__tstmp = value

    @property
    def value(self) -> float:
        return self.__value

    @value.setter
    def value(self, value: float) -> None:
        self.__value = value

    def __str__(self) -> str:
        return '\n(' + str(self.time) + ', ' + str(self.value) + ')'

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def sort_by_time(data: list, descending: bool = False) -> None:
        """
        In-place sorting of list with TimeValue objects by time (ascending)

        Parameters
        ----------
        descending :
            reverse sorting of data list, default: False
        data :
            list of TimeValue objects

        Returns
        -------

        """
        data.sort(key=lambda x: x.time, reverse=descending)
