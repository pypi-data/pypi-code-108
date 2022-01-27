

class PowerDistributorState:
    """
    PowerDistributorStates contains information for power distribution algorithms.
    """

    def __init__(self, sys_id: int, soh: float = 0.0, soc: float = 0.0, storage_technology: str = None,
                 max_charge_power: float = 0.0, max_discharge_power: float = 0.0):
        """
        Constructor of PowerDistributorStates

        Parameters
        ----------

        sys_id :
            number of ac or dc system
        soh :
            state of health of a system
        soc :
            state of charge of a system
        storage_technology:
            type of storage technology
        """

        self.__soh: float = soh
        self.__id: int = sys_id
        self.__soc: float = soc
        self.__max_charge_power: float = max_charge_power
        self.__max_discharge_power: float = max_discharge_power
        self.__rebalance_charge_power: float = 0.0
        self.__rebalance_discharge_power: float = 0.0
        self.__time_delta: float = 0.0
        self.__capacity: float = 0.0
        self.__storage_technology: str = storage_technology

    @property
    def soh(self) -> float:
        return self.__soh

    @soh.setter
    def soh(self, value: float) -> None:
        self.__soh = value

    @property
    def sys_id(self) -> float:
        return self.__id

    @sys_id.setter
    def sys_id(self, value: float) -> None:
        self.__id = value

    @property
    def soc(self) -> float:
        return self.__soc

    @soc.setter
    def soc(self, value: float) -> None:
        self.__soc = value

    @property
    def time_delta(self) -> float:
        return self.__time_delta

    @time_delta.setter
    def time_delta(self, value: float) -> None:
        self.__time_delta = value

    @property
    def capacity(self) -> float:
        return self.__capacity

    @capacity.setter
    def capacity(self, value: float) -> None:
        self.__capacity = value

    @property
    def storage_technology(self) -> str:
        return self.__storage_technology

    @property
    def max_charge_power(self) -> float:
        return self.__max_charge_power

    @max_charge_power.setter
    def max_charge_power(self, value: float) -> None:
        self.__max_charge_power = value

    @property
    def max_discharge_power(self) -> float:
        return self.__max_discharge_power

    @max_discharge_power.setter
    def max_discharge_power(self, value: float) -> None:
        self.__max_discharge_power = value

    @property
    def rebalance_charge_power(self) -> float:
        return self.__rebalance_charge_power

    @rebalance_charge_power.setter
    def rebalance_charge_power(self, value: float) -> None:
        self.__rebalance_charge_power = value

    @property
    def rebalance_discharge_power(self) -> float:
        return self.__rebalance_discharge_power

    @rebalance_discharge_power.setter
    def rebalance_discharge_power(self, value: float) -> None:
        self.__rebalance_discharge_power = value

    @staticmethod
    def sort_by_soc(data: list, descending: bool = False) -> None:
        """
        In-place sorting of list with PowerDistributorState objects by soc (ascending by default)

        Parameters
        ----------
        descending :
            reverse sorting of data list, default: False
        data :
            list of TimeValue objects

        Returns
        -------

        """
        data.sort(key=lambda x: x.soc, reverse=descending)

    @staticmethod
    def sort_by_soh(data: list, descending: bool = True) -> None:
        """
        In-place sorting of list with PowerDistributorState objects by soh (descending by default)

        Parameters
        ----------
        descending :
            reverse sorting of data list, default: True
        data :
            list of TimeValue objects

        Returns
        -------

        """
        data.sort(key=lambda x: x.soh, reverse=descending)
