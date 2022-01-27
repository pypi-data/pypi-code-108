from abc import ABC, abstractmethod


class AcDcConverter(ABC):

    def __init__(self, max_power: float):
        self.__MAX_POWER: float = max_power  # W
        self.__STANDBY_POWER_THRESHOLD: float = max_power * 0.001  # W

    @abstractmethod
    def to_ac(self, power: float, voltage: float) -> float:
        """
        Calculated dc power for discharging process

        Parameters
        ----------
        power : float
            requested ac power in W
        voltage : float
            dc voltage of intermediate circuit in V

        Returns
        -------
        float
            dc power in W

        """
        pass

    @abstractmethod
    def to_dc(self, power: float, voltage: float) -> float:
        """
        Calculated dc power for charging process

        Parameters
        ----------
        power : float
            requested ac power in W
        voltage : float
            dc voltage of intermediate circuit in V

        Returns
        -------
        float
            dc power in W

        """
        pass

    @abstractmethod
    def to_dc_reverse(self, dc_power: float, voltage: float) -> float:
        """
        recalculates ac power in W, if the BMS limits the DC_power

        Parameters
        ----------
        voltage :
            voltage of intermediate circuit in V
        dc_power :
            dc power of intermediate circuit in W

        Returns
        -------
        float
            ac power in W

        """
        pass

    @abstractmethod
    def to_ac_reverse(self, dc_power: float, voltage: float) -> float:
        """
        recalculates ac power in W, if the BMS limits the DC_power

        Parameters
        ----------
        voltage :
            voltage of intermediate circuit in V
        dc_power :
            dc power of intermediate circuit in W

        Returns
        -------
        float
            ac power in W

        """
        pass

    @property
    @abstractmethod
    def volume(self) -> float:
        """
        Volume of acdc converter in m3

        Returns
        -------

        """
        pass

    @property
    @abstractmethod
    def mass(self) -> float:
        """
        Mass of acdc converter in kg

        Returns
        -------

        """
        pass

    @property
    @abstractmethod
    def surface_area(self) -> float:
        """
        Surface area of acdc converter in m2

        Returns
        -------

        """
        pass

    @property
    def max_power(self) -> float:
        """
        returns the maximum ac power of the acdc converter

        Parameters
        -------

        Returns
        -------
            float
                maximum power of the acdc converter (ac power)

        """
        return self.__MAX_POWER

    @property
    def standby_power_threshold(self) -> float:
        """
        returns the ac power threshold for standby

        Returns
        -------

        """
        return self.__STANDBY_POWER_THRESHOLD

    @classmethod
    @abstractmethod
    def create_instance(cls, max_power: float, power_electronics_config: None):
        pass

    @abstractmethod
    def close(self) -> None:
        """
        Closing all open resources in acdc converter

        Parameters
        ----------

        Returns
        -------

        """
        pass
