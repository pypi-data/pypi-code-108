from abc import ABC, abstractmethod

from simses.commons.state.system import SystemState


class Auxiliary(ABC):

    def __init__(self):
        pass

    def update(self, time: float, state: SystemState) -> None:
        """
        Updating auxiliary losses of state

        Parameters
        ----------
        state :

        Returns
        -------

        """
        state.aux_losses += self.ac_operation_losses()

    @abstractmethod
    def ac_operation_losses(self) -> float:
        """
        Calculates the ac operation losses

        Parameters
        ----------

        Returns
        -------

        """
        pass

    def close(self) -> None:
        """
        Closing all open resources in operation losses

        Parameters
        ----------

        Returns
        -------

        """
        pass
