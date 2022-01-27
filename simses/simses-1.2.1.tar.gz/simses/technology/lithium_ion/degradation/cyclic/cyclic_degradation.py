from abc import ABC, abstractmethod

from simses.commons.cycle_detection.cycle_detector import CycleDetector
from simses.commons.state.technology.lithium_ion import LithiumIonState
from simses.technology.lithium_ion.cell.type import CellType


class CyclicDegradationModel(ABC):

    def __init__(self, cell_type: CellType, cycle_detector: CycleDetector):
        super().__init__()
        self._cell: CellType = cell_type
        self._cycle_detector: CycleDetector = cycle_detector

    @abstractmethod
    def calculate_degradation(self, battery_state: LithiumIonState) -> None:
        """
        update the cyclic capacity loss of a battery
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
    def calculate_resistance_increase(self, battery_state: LithiumIonState) -> None:
        """
        update the cyclic internal resistance increase of a battery
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
        get the updated cyclic capacity loss til the current recognized half cycle (differential capacity loss)

        Returns
        -------
        float:
            differential cyclic capacity loss til the current recognized half cycle in [Ah]
        """
        pass

    @abstractmethod
    def get_resistance_increase(self) -> float:
        """
        get the updated cyclic resistance increase caused the current recognized half cycle (differential increase)
        Returns
        -------
        float:
            differential resistance increase caused by the current step in [p.u.]
        """
        pass

    @abstractmethod
    def reset(self, lithium_ion_state: LithiumIonState) -> None:
        """
        resets all values within a cyclic degradation model, if battery is replaced

        Parameters
        ----------
            lithium_ion_state : LithiumIonState; current State of the lithium_ion

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
