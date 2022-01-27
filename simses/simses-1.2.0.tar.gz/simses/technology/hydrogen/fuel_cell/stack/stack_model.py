from abc import ABC, abstractmethod

from simses.commons.state.technology.fuel_cell import FuelCellState


class FuelCellStackModel(ABC):

    def __init__(self):
        super().__init__()

    def update(self, power: float, state: FuelCellState) -> None:
        """
        Updates current, voltage and hydrogen flow of hydrogen state

        Parameters
        ----------
        power :
        state :

        Returns
        -------

        """
        self.calculate(power)
        state.current = self.get_current()
        state.voltage = self.get_voltage()
        state.hydrogen_use = self.get_hydrogen_consumption()
        # state.power = self.get_power()
        state.current_density = self.get_current_density()


    @abstractmethod
    def calculate(self, power) -> None:
        """
        Calculates current, voltage and hydrogen consumption based on input power
        Parameters
        ----------
        power : input power in W

        Returns
        -------

        """
        pass

    @abstractmethod
    def get_current(self):
        """
        return electrical current in A

        Returns
        -------

        """
        pass

    @abstractmethod
    def get_voltage(self):
        """
        Return of electrical voltage in V

        Returns
        -------

        """
        pass

    @abstractmethod
    def get_hydrogen_consumption(self):
        """
        Return of hydrogen consumption in mol/s

        Returns
        -------

        """
        return self.get_hydrogen_consumption()

    def get_current_density(self) -> float:
        """
        return electrical current of the electrolyzer stack in A cm-2

        Returns
        -------

        """
        return self.get_current() / self.get_geom_area_stack()

    @abstractmethod
    def get_nominal_stack_power(self):
        pass

    @abstractmethod
    def get_number_cells(self):
        pass

    @abstractmethod
    def get_geom_area_stack(self):
        pass


    @abstractmethod
    def get_heat_capactiy_stack(self):
        pass

    @abstractmethod
    def close(self):
        pass
