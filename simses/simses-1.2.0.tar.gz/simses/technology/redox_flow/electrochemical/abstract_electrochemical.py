from abc import ABC, abstractmethod

from simses.commons.state.technology.redox_flow import RedoxFlowState


class ElectrochemicalModel(ABC):
    """Model that calculates the current and voltage of the redox flow stack module."""

    def __init__(self):
        super().__init__()

    @abstractmethod
    def update(self, time: float, redox_flow_state: RedoxFlowState) -> None:
        """
        Updating power (if changes due to redox flow management system), current, voltage, power loss and soc of
        redox_flow_state. In the update function the control system requests are implemented.

        Parameters
        ----------
        time : float
            Current simulation time in s.
        redox_flow_state : RedoxFlowState
            Current state of redox_flow.

        Returns
        -------
            None
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Closing all resources in ElectrochemicalModel."""
        pass
