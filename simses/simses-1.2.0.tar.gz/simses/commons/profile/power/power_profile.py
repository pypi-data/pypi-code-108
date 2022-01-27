from abc import ABC, abstractmethod


class PowerProfile(ABC):
    """
    Power Profile for the energy management system of the ESS.
    """

    def __init__(self):
        super().__init__()

    @abstractmethod
    def next(self, time: float) -> float:
        """
        provides the power for the next step of a specific load or generator (e.g. Household load profile)

        Parameters
        ----------
        time : current timestamp of the simulation

        Returns
        -------
        float
            power for the next step
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """
        Closing all open resources in power profile

        Parameters
        ----------

        Returns
        -------

        """
        pass
