from abc import ABC, abstractmethod

from simses.commons.state.abstract_state import State


class StorageTechnologyState(State, ABC):

    """
    A state with information specifically provided by a storage technology for each simulation timestep.
    """

    def __init__(self):
        super().__init__()

    @property
    @abstractmethod
    def is_charge(self) -> bool:
        """
        Returns True if current state presents a charging process, false otherwise

        Returns
        -------

        """
        pass

    @property
    @abstractmethod
    def voltage(self) -> float:
        """
        DC Voltage in V

        Returns
        -------

        """
        pass

    @property
    @abstractmethod
    def current(self) -> float:
        """
        DC Current in A

        Returns
        -------

        """
        pass

    @property
    @abstractmethod
    def power_loss(self) -> float:
        """
        Power losses in W

        Returns
        -------

        """
        pass

    @property
    @abstractmethod
    def soc(self) -> float:
        """
        SOC in p.u.

        Returns
        -------

        """
        pass

    @property
    @abstractmethod
    def soh(self) -> float:
        """
        SOC in p.u.

        Returns
        -------

        """
        pass

    @property
    @abstractmethod
    def capacity(self) -> float:
        """
        Capacity in Wh

        Returns
        -------

        """
        pass

    @property
    @abstractmethod
    def fulfillment(self) -> float:
        """
        Stage of power fulfillment of storage data in p.u.

        Returns
        -------

        """
        pass

    @property
    @abstractmethod
    def temperature(self) -> float:
        """
        Temperature of storage technology in K

        Returns
        -------

        """
        pass

    @temperature.setter
    def temperature(self, value: float) -> None:
        pass

    @property
    @abstractmethod
    def max_charge_power(self) -> float:
        """
        Current maximum charging power of storage technology in W

        Returns
        -------

        """
        pass

    @property
    @abstractmethod
    def max_discharge_power(self) -> float:
        """
        Current maximum discharging power of storage technology in W

        Returns
        -------

        """
        pass
