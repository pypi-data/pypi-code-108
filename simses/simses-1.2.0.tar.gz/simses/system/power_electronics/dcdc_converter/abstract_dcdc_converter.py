from abc import ABC, abstractmethod

from simses.system.auxiliary.auxiliary import Auxiliary


class DcDcConverter(ABC):

    def __init__(self, intermediate_circuit_voltage: float):
        self.__intermediate_circuit_voltage: float = intermediate_circuit_voltage

    @abstractmethod
    def calculate_dc_current(self, dc_power: float, storage_voltage: float) -> None:
        """
        function to calculate the dc current

        Parameters
        ----------
        dc_power : dc input power in W
        storage_voltage : voltage of storage in V

        """
        pass

    @abstractmethod
    def reverse_calculate_dc_current(self, dc_power: float, storage_voltage: float) -> None:
        """
        function to calculate the dc current

        Parameters
        ----------
        dc_power :
            dc input power in W
        storage_voltage :
            voltage of storage in V

        """
        pass

    @property
    @abstractmethod
    def max_power(self) -> float:
        pass

    @property
    def intermediate_circuit_voltage(self) -> float:
        return self.__intermediate_circuit_voltage

    @property
    @abstractmethod
    def dc_power_loss(self) -> float:
        pass

    @property
    @abstractmethod
    def dc_power(self) -> float:
        pass

    @property
    @abstractmethod
    def dc_current(self) -> float:
        pass

    @property
    @abstractmethod
    def volume(self) -> float:
        """
        Volume of dc dc converter in m3

        Returns
        -------

        """
        pass

    @property
    @abstractmethod
    def mass(self) -> float:
        """
        Mass of dc dc converter in kg

        Returns
        -------

        """
        pass

    @property
    @abstractmethod
    def surface_area(self) -> float:
        """
        Surface area of dc dc converter in m2

        Returns
        -------

        """
        pass

    @abstractmethod
    def get_auxiliaries(self) -> [Auxiliary]:
        pass

    @staticmethod
    def _is_charge(power: float) -> bool:
        return power > 0.0

    @abstractmethod
    def close(self) -> None:
        """
        Closing all open resources in dcdc converter

        Parameters
        ----------

        Returns
        -------

        """

        pass
