from abc import abstractmethod, ABC

from simses.commons.state.technology.fuel_cell import FuelCellState


class PressureModel(ABC):
    """
    PressureModelEl calculates the pressure development at the cathode of the electrolyzer in dependency of the
    hydrogenproductionrate, the hydrogenoutflow and the temperature
    """

    # MOLAR_MASS_HYDROGEN = 1.00794 * 10 ** (-3) # kg/mol
    # FARADAY_CONST: float = 96485.3321  # As/mol
    # IDEAL_GAS_CONST: float = 8.314462  # J/(mol K)
    # HEAT_CAPACITY_WATER: float = 4184  # J/(kg K)
    # MOLAR_MASS_WATER: float = 0.018015  # kg/mol
    # HYDROGEN_ISENTROP_EXPONENT = 1.0498  # # from: "Wasserstoff in der Fahrzeugtechnik"
    # HYDROGEN_REAL_GAS_FACTOR = 1  # valid for pressures << 13 bar and temperatures >> 33 K

    def __init__(self):
        super().__init__()

    def update(self, time: float, state: FuelCellState):
        self.calculate(time, state)
        state.pressure_cathode_fc = self.get_pressure_cathode_fc()  # bar
        state.pressure_anode_fc = self.get_pressure_anode_fc()  # bar   anode pressure is not varied -> stays constant
        state.hydrogen_use = self.get_h2_inflow()
        state.oxygen_use = self.get_o2_inflow()

    @abstractmethod
    def calculate(self, time, state: FuelCellState) -> None:
        pass

    @abstractmethod
    def get_pressure_cathode_fc(self) -> float:
        pass

    @abstractmethod
    def get_pressure_anode_fc(self) -> float:
        pass

    @abstractmethod
    def get_h2_inflow(self) -> float:
        pass

    @abstractmethod
    def get_o2_inflow(self) -> float:
        pass

    def close(self) -> None:
        """ Closing all resources in pressure model """
        pass
