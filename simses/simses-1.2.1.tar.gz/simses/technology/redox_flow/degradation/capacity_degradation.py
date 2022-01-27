from abc import ABC, abstractmethod

from simses.commons.state.technology.redox_flow import RedoxFlowState


class CapacityDegradationModel(ABC):
    """Model for the capacity degradation effects of a redox flow battery, which can not be reversed by electrolyte
    remixing."""
    def __init__(self, capacity: float):
        super().__init__()
        self.__capacity_start = capacity

    def update(self, time: float, redox_flow_state: RedoxFlowState) -> None:
        """
        Calculates the capacity degradation and updates the value as well as the state-of-health (SOH).

        Parameters
        ----------
        time : float
            Current simulation time in s.
        redox_flow_state : RedoxFlowState
            Current state of redox_flow.

        Returns
        -------

        """
        redox_flow_state.capacity -= self.get_capacity_degradation(time, redox_flow_state)  # Wh
        redox_flow_state.soh = redox_flow_state.capacity / self.__capacity_start

    @abstractmethod
    def get_capacity_degradation(self, time: float, redox_flow_state: RedoxFlowState) -> float:
        """
        Determination of the capacity degradation.

        Parameters
        ----------
        time : float
            Current simulation time in s.
        redox_flow_state : RedoxFlowState
            Current state of redox_flow.

        Returns
        -------
        float :
            Capacity degradation per time step in Wh.
        """
        pass

    @abstractmethod
    def close(self):
        """Closing all resources in CapacityDegradationModel."""
        pass
