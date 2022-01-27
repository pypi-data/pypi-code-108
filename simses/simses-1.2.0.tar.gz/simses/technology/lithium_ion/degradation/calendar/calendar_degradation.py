from abc import ABC, abstractmethod

from simses.commons.state.technology.lithium_ion import LithiumIonState
from simses.technology.lithium_ion.cell.type import CellType


class CalendarDegradationModel(ABC):
    """
    Degradation Model for the calendaric aging of the ESS.
    """

    def __init__(self, cell_type: CellType):
        super().__init__()
        self._cell: CellType = cell_type

    @abstractmethod
    def calculate_degradation(self, time: float, battery_state: LithiumIonState) -> None:
        """
        update the calendric capacity loss of a battery
        Attention: without considering internal aging variation the capacity loss calculation is conducted on a
        down-scaled single cell and again up-scaled to module or pack assuming that each single cell has the same
        degradation state
        Parameters
        ----------
            battery_state : LithiumIonState
            Current BatteryState of the lithium_ion. Used to determine if the lithium_ion is charging or discharging.

        Returns
        -------

        """
        pass

    @abstractmethod
    def calculate_resistance_increase(self, time: float, battery_state: LithiumIonState) -> None:
        """
        update the calendric internal resistance increase of a battery
        Attention: without considering internal aging variation the resistance increase calculation is conducted on a
        down-scaled single cell and again up-scaled to module or pack assuming that each single cell has the same
        degradation state
        Parameters
        ----------
            battery_state : LithiumIonState
            Current BatteryState of the lithium_ion. Used to determine if the lithium_ion is charging or discharging.

        Returns
        -------

        """
        pass

    @abstractmethod
    def get_degradation(self) -> float:
        """
        get the updated calendric capacity loss caused by the current calculation step (differential capacity loss)

        Returns
        -------
        float:
            differential capacity loss of the current step in [Ah]
        """
        pass

    @abstractmethod
    def get_resistance_increase(self) -> float:
        """
        get the updated calendric resistance increase til the current step (differential increase)
        Returns
        -------
        float:
            differential resistance increase til the current step in [p.u.]
        """
        pass

    @abstractmethod
    def reset(self, battery_state: LithiumIonState) -> None:
        """
        resets all values within a calendar degradation model, if battery is replaced
        Parameters
        ----------
            battery_state : LithiumIonState; Current BatteryState of the lithium_ion.

        Returns
        -------
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """
        Closing all resources in calendar degradation model

        Returns
        -------

        """
        pass
