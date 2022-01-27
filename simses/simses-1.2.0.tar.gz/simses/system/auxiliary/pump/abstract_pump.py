from abc import ABC, abstractmethod

from simses.system.auxiliary.auxiliary import Auxiliary


class Pump(Auxiliary, ABC):
    """Pump is an auxiliary. It calculates the necessary pump power in W depending on the pressure losses."""
    def __init__(self):
        super().__init__()

    def ac_operation_losses(self) -> float:
        """
        Calculates the ac operation losses.

        Parameters
        ----------

        Returns
        -------
        float:
            Power in W.
        """
        return self.get_pump_power()

    @abstractmethod
    def calculate_pump_power(self, pressure_loss: float) -> None:
        """
        Calculates the pump power in W.

        Parameters
        ----------
        pressure_loss : float
            Current pressure loss in W. It corresponds to the volume flow times the pressure drop.

        Returns
        -------

        """
        pass

    @abstractmethod
    def get_pump_power(self) -> float:
        """
        Gets pump power in W.

        Returns
        -------
        float:
            Pump power in W.
        """
        pass

    @abstractmethod
    def set_eta_pump(self, flow_rate: float, flow_rate_max: float, flow_rate_min: float) -> None:
        """
        Sets pump efficiency.

        Parameters
        ----------
        flow_rate : float
            Current flow rate.
        flow_rate_max : float
            Maximal needed flow rate of the hydraulic system.
        flow_rate_min : float
            Minimal needed flow rate of the hydraulic system.

        Returns
        -------

        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Closing all resources in Pump."""
        super().close()
