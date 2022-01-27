from abc import ABC, abstractmethod

from simses.commons.state.system import SystemState


class PowerDistributor(ABC):

    """
    PowerDistributor incorporates a logic on how to distribute power between several systems. The logic is based on the
    system state of each system.
    """

    def __init__(self):
        super().__init__()

    @abstractmethod
    def set(self, time: float, states: [SystemState], power: float) -> None:
        """
        Setting information from all system states necessary for the PowerDistributor

        Parameters
        ----------
        time :
            current simulation time as epoch time
        states :
            list of current system states
        power :
            overall power to be distributed to all systems
        """
        pass

    @abstractmethod
    def get_power_for(self, power: float, state: SystemState) -> float:
        """
        Calculates the power share of the overall to be distributed power to a specific system specified with system state

        Parameters
        ----------
        power :
            overall power to be distributed to all systems
        state :
            system state of system to calculate a specific power share of power

        Returns
        -------
        float:
            power share of specified system with corresponding system state
        """
        pass

    def close(self):
        pass
