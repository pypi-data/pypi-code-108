from abc import ABC, abstractmethod

from simses.commons.state.technology.storage import StorageTechnologyState


class CycleDetector(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def cycle_detected(self, time: float, state: StorageTechnologyState) -> bool:
        """
        Cycle Detector. Returns true if the sign (charging to discharge and vice versa) changes or the SOC reaches the
        maximum or minimum or the end of the simulation is reached

        Parameters
        ----------
        time : current time of the simulation
        state : LithiumIonState, current BatteryState of the lithium_ion state

        Returns
        -------
        bool:
            returns true if a cycle is detected

        """
        pass

    @abstractmethod
    def get_depth_of_cycle(self) -> float:
        """
        Determines the depth of a detected cycle

        Returns
        -------
        float:
            Depth of a detected cycle in p.u.

        """
        pass

    @abstractmethod
    def get_delta_full_equivalent_cycle(self) -> float:
        """
        Determines the delta in full equivalent cycles [0,1]

        Returns
        -------
        float:
            Delta in full equivalent cycles in p.u.

        """
        pass

    @abstractmethod
    def get_crate(self) -> float:
        """
        Determines the mean c-rate of a detected cycle

        Returns
        -------
        float:
            Mean c-rate of a detected cycle in 1/s

        """
        pass

    @abstractmethod
    def get_mean_soc(self) -> float:
        """
        Determines the mean SOC of a detected cycle

        Returns
        -------
        float:
            Mean SOC of a detected cycle in p.u.
        """
        pass

    @abstractmethod
    def get_full_equivalent_cycle(self) -> float:
        """
        Determines the total number of full equivalent cycles

        Returns
        -------
        float:
            Total number of full equivalent cycles

        """
        pass

    @abstractmethod
    def reset(self) -> None:
        """
        resets all values within a degradation model, if battery is replaced

        Returns
        -------

        """
        pass

    @abstractmethod
    def _reset_cycle(self, soc: float, time_passed: float) -> None:
        """
        resets all values within the cycle detector, if a cycle was detected

        Returns
        -------

        """
        pass

    @abstractmethod
    def _update_cycle_steps(self, soc: float, time_passed: float) -> None:
        """
        updates all values within the cycle detector, if no cycle was detected, but the SOC changed

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
