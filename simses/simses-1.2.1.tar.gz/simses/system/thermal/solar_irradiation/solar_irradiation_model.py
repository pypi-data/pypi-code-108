from abc import ABC, abstractmethod


class SolarIrradiationModel(ABC):
    """
        SolarIrradiationModel calculates the total incident solar irradiation on the selected housing object at any
        given time for a specified location.
        Solar irradiation time series data from various sources:
        """

    def __init__(self):
        super().__init__()
        pass

    @abstractmethod
    def get_heat_load(self, time: float) -> float:
        """
        This method is called from the system thermal model, and returns thermal power on container surfaces
        :param time:
        :return: thermal power, or 0 (depending on chosen sub-class)
        """
        pass

    @abstractmethod
    def get_global_horizontal_irradiance(self,time_step) -> float:
        """
        Returns the value of global horizontal irradiance for specified timestep for selected location (in W/m2)
        :param time_step:
        :return: irradiance, or 0 (depending on chosen sub-class)
        """
        pass

    @abstractmethod
    def create_instance(self):
        """
        reinstantiates the SolarIrradiationModel
        :return: SolarIrradiationModel
        """
        pass

    @abstractmethod
    def close(self):
        """
        closes all open resources in solar irradiation model

        Parameters
        ----------

        Returns
        -------

        """
        pass
