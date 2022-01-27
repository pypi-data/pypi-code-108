from abc import ABC, abstractmethod

from simses.commons.state.technology.storage import StorageTechnologyState
from simses.system.auxiliary.auxiliary import Auxiliary


class StorageTechnology(ABC):
    """Abstract class for all technologies"""

    def __init__(self):
        pass

    @abstractmethod
    def distribute_and_run(self, time: float, current: float, voltage: float):
        """
        starts the update process of a data

        Parameters
        ----------
        time : current simulation time
        current : requested current for a data
        voltage : dc voltage for a data

        Returns
        -------

        """
        pass

    @abstractmethod
    def wait(self):
        pass

    @abstractmethod
    def get_auxiliaries(self) -> [Auxiliary]:
        pass

    @property
    @abstractmethod
    def state(self) -> StorageTechnologyState:
        """
        function to get the data state

        Parameters
        -------

        Returns
        -------
            StorageTechnologyState : specific data state

        """
        pass

    @property
    @abstractmethod
    def volume(self) -> float:
        """
        Volume of storage technology in m3

        Returns
        -------

        """
        pass

    @property
    @abstractmethod
    def mass(self) -> float:
        """
        Mass of storage technology in kg

        Returns
        -------

        """
        pass

    @property
    @abstractmethod
    def surface_area(self) -> float:
        """
        Surface area of storage technology in m2

        Returns
        -------

        """
        pass

    @property
    @abstractmethod
    def specific_heat(self) -> float:
        """
               Specific heat of storage technology in J/(kgK)

               Returns
               -------

               """
        pass

    @property
    @abstractmethod
    def convection_coefficient(self) -> float:
        """
                determines the convective heat transfer coefficient of a battery cell

                Returns
                -------
                float:
                    convective heat transfer coefficient in W/(m^2*K)
                """
        pass

    @abstractmethod
    def get_system_parameters(self) -> dict:
        """
        All system parameters inherited by the storage technology

        Returns
        -------

        """
        pass

    @abstractmethod
    def close(self):
        """
        Closing all open resources in a data

        Parameters
        ----------

        Returns
        -------

        """
        pass