from abc import ABC, abstractmethod

from simses.commons.state.technology.electrolyzer import ElectrolyzerState


class ElectrolyzerStackModel(ABC):

    def __init__(self):
        super().__init__()

    def update(self, power: float, state: ElectrolyzerState) -> None:
        """
        Updates hydrogen states that are corrolated with the electrolyzer such as current, voltage, hydrogen production,
        water use and temperature

        Parameters
        ----------
        state :

        Returns
        -------

        """
        self.calculate(power, state)
        state.current = self.get_current()
        state.current_density = self.get_current_density()
        state.voltage = self.get_voltage()
        state.hydrogen_production = self.get_hydrogen_production()
        state.oxygen_production = self.get_oxygen_production()
        state.water_use = self.get_water_use()
        state.part_pressure_h2 = self.get_partial_pressure_h2()
        state.part_pressure_o2 = self.get_partial_pressure_o2()
        state.sat_pressure_h2o = self.get_sat_pressure_h2o()

    @abstractmethod
    def calculate(self, power: float, state: ElectrolyzerState) -> None:
        """
        Calculates current, voltage and hydrogen generation based on input power

        Parameters
        ----------
        power : input power in W
        temperature: temperature of electrolyzer in K
        pressure_anode: relative pressure on anode side of electrolyzer in barg (relative to 1 bar)
        pressure_cathode: relative pressure on cathode side of electrolyzer in barg (relative to 1 bar)

        Returns
        -------

        """
        pass

    @abstractmethod
    def get_reference_voltage_eol(self, resistance_increase: float, exchange_currentdensity_decrease: float) -> float:
        """
        return voltage at defined operation point for state of degradation

        :return:
        """
        pass

    @abstractmethod
    def get_current(self) -> float:
        """
        return electrical current of the electrolyzer stack in A

        Returns
        -------

        """
        pass

    @abstractmethod
    def get_current_density(self) -> float:
        """
        return electrical current of the electrolyzer stack in A cm-2

        Returns
        -------

        """
        pass

    @abstractmethod
    def get_voltage(self) -> float:
        """
        Return of electrical voltage of electrolyzer stack in V

        Returns
        -------

        """
        pass

    @abstractmethod
    def get_hydrogen_production(self) -> float:
        """
        Return of total hydrogen generation of the stack in mol/s

        Returns
        -------

        """
        pass

    @abstractmethod
    def get_oxygen_production(self) -> float:
        """
        Return of total oxygen generation of the stack in mol/s

        Returns
        -------

        """
        pass

    @abstractmethod
    def get_water_use(self) -> float:
        """
        Return of water use of electrolyzer stack at anode side

        Returns
        -------

        """
        pass

    @abstractmethod
    def get_number_cells(self) -> float:
        """
        Returns number of serial electrolyseur cells
        -------

        """
        pass

    @abstractmethod
    def get_geom_area_stack(self) -> float:
        """
        Returns geometric area of one cell
        -------

        """
        pass

    @abstractmethod
    def get_nominal_stack_power(self) -> float:
        """
        Returns nominal_stack_power of electrolyzer
        -------

        """
        pass

    @abstractmethod
    def get_heat_capacity_stack(self) -> float:
        """
        Returns nominal_stack_power of electrolyzer
        -------

        """
        pass

    @abstractmethod
    def get_thermal_resistance_stack(self) -> float:
        """
        Returns thermal resistance of electrolyzer
        -------

        """
        pass

    @abstractmethod
    def get_partial_pressure_h2(self) -> float:
        """
        Returns partial pressure of hydrogen at cathode side of electrolyzer
        -------

        """
        pass

    @abstractmethod
    def get_partial_pressure_o2(self) -> float:
        """
        Returns partial pressure of oxigen at anode side of electrolyzer
        -------

        """
        pass

    @abstractmethod
    def get_sat_pressure_h2o(self) -> float:
        """
        Returns staturation pressure of h2o for given temperature
        -------

        """
        pass

    @abstractmethod
    def get_water_in_stack(self) -> float:
        """
        Returns amount of water that is present in the stack
        -------

        """

    @abstractmethod
    def get_nominal_current_density(self) -> float:
        pass

    @abstractmethod
    def close(self) -> None:
        pass
