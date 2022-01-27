from abc import ABC, abstractmethod

from simses.commons.state.technology.redox_flow import RedoxFlowState


class ElectrolyteSystem(ABC):
    """The ElectrolyteSystem describes the properties of the liquid storage medium of the redox flow battery."""

    def __init__(self, capacity: float):
        self.FARADAY = 96485  # As/mol
        self.__capacity = capacity

    def get_start_capacity(self) -> float:
        """
        Returns the total start capacity of the electrolyte of the redox flow system.

        Returns
        -------
        float:
            Start capacity in Wh.
        """
        return self.__capacity

    @abstractmethod
    def get_vanadium_concentration(self) -> float:
        """
        Returns the total vanadium concentration of the electrolyte.

        Returns
        -------
        float :
            total vanadium concentration of the electrolyte in mol/m^3.
        """
        pass

    @abstractmethod
    def get_viscosity_anolyte(self, redox_flow_state: RedoxFlowState) -> float:
        """
        Determines the anolyte viscosity depending on state-of-charge (SOC) and temperature.

        Parameters
        ----------
        redox_flow_state : RedoxFlowState
            Current state of redox_flow.

        Returns
        -------
        float:
            Analyte viscosity in Pas.
        """
        pass

    @abstractmethod
    def get_viscosity_catholyte(self, redox_flow_state: RedoxFlowState) -> float:
        """
        Determines the anolyte viscosity depending on the state-of-charge (SOC) and temperature.

        Parameters
        ----------
        redox_flow_state : RedoxFlowState
            Current state of redox_flow.

        Returns
        -------
        float:
            Catholyte viscosity in Pas.
        """
        pass

    @abstractmethod
    def get_min_viscosity(self) -> float:
        """
        Determines the minimal viscosity during operation of the redox flow battery.

        Returns
        -------
        float:
            Minimal viscosity in Pas
        """
        pass

    @abstractmethod
    def get_max_viscosity(self) -> float:
        """
        Determines the maximal viscosity during operation of the redox flow battery.

        Returns
        -------
        float:
            Maximal viscosity in Pas.
        """
        pass

    @abstractmethod
    def get_max_temperature(self) -> float:
        """
        Returns the maximal temperature of the electrolyte.

        Returns
        -------
        float:
            Maximal electrolyte temperature in K.
        """
        pass

    @abstractmethod
    def get_min_temperature(self) -> float:
        """
        Returns the minimal temperature of the electrolyte.

        Returns
        -------
        float:
            Minimal electrolyte temperature in K.
        """
        pass

    @abstractmethod
    def get_capacity_density(self) -> float:
        """
        Returns the volume specific capacity density of the electrolyte in As/m^3.

        Returns
        -------
        float:
            Volume specific capacity density in As/m^3.
        """
        pass

    def get_electrolyte_density(self) -> float:
        """
        Returns the mean density of the electrolyte in kg/m^3.

        Returns
        -------
        float:
            Density of the electrolyte in kg/m^3.
        """
        pass

    @abstractmethod
    def close(self):
        """Closing all resources in ElectrolyteSystem."""
        pass
