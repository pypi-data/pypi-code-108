from abc import ABC, abstractmethod

from simses.commons.state.energy_management import EnergyManagementState
from simses.commons.state.system import SystemState


class OperationStrategy(ABC):
    """
    Algorithm to determine output power of the ESS for the next timestep.
    """

    def __init__(self, priority: float):
        super().__init__()
        self.__priority = priority

    @abstractmethod
    def next(self, time: float, system_state: SystemState, power: float = 0) -> float:
        """
        Provides the next value for the output power of the ESS.

        Parameters
        ----------
        time : float
        system_state : SystemState
        power : float
            Power value for stacked operation strategy.

        Returns
        -------
        float
            Output power for the ESS in the next timestep.
        """
        pass

    @abstractmethod
    def update(self, energy_management_state: EnergyManagementState) -> None:
        """
        In-place update of energy management state variables

        Parameters
        ----------
        energy_management_state : state for energy management

        Returns
        -------

        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """
        Clearing internal values of operations strateggy

        Returns
        -------

        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Closing open resources"""
        pass

    @property
    def priority(self):
        """Defines the priority of the operation strategy in a multiuse case
        VERY_HIGH = 0
        HIGH = 1
        MEDIUM = 2
        LOW = 3
        VERY_LOW = 4"""
        return self.__priority

    @staticmethod
    def sort(strategies: []) -> None:
        """Sorts the order in which the operation strategies are applied in a multiuse case"""
        strategies.sort(key=lambda strategy: strategy.priority, reverse=True)
