from abc import ABC, abstractmethod


class AmbientThermalModel(ABC):

    """
    AmbientThermalModel provides a temperature of the ambient for the system thermal model calculations.
    """

    def __init__(self):
        super().__init__()
        pass

    @abstractmethod
    def get_temperature(self, time) -> float:
        """
        Returns the ambient temperature

        Parameters
        -------
        time : current simulation time

        Returns
        -------
        float
            ambient temperature in Kelvin
        """
        pass

    @abstractmethod
    def get_initial_temperature(self) -> float:
        """
        Returns the ambient temperature

        Parameters
        -------
        time : current simulation time

        Returns
        -------
        float
            ambient temperature in Kelvin
        """
        pass

    @abstractmethod
    def create_instance(self):
        """
        reinstantiates the AmbientThermalModel
        :return: AmbientThermalModel
        """
        pass

    @abstractmethod
    def close(self):
        """
        closes all open resources in ambient thermal model

        Parameters
        ----------

        Returns
        -------

        """
        pass
