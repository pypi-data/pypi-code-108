from abc import abstractmethod, ABC

from simses.commons.constants import Hydrogen
from simses.commons.state.technology.electrolyzer import ElectrolyzerState


class PressureModel(ABC):
    """
    PressureModelEl calculates the pressure development at the cathode of the electrolyzer in dependency of the
    hydrogenproductionrate, the hydrogenoutflow and the temperature
    """

    def __init__(self):
        super().__init__()

    def update(self, time: float, state: ElectrolyzerState):
        self.calculate(time, state)
        state.pressure_cathode = self.get_pressure_cathode()  # bar
        state.pressure_anode = self.get_pressure_anode()  # bar   anode pressure is not varied -> stays constant
        state.hydrogen_outflow = self.get_h2_outflow()
        state.total_hydrogen_production += state.hydrogen_outflow * (time - state.time) * 2 * Hydrogen.MOLAR_MASS_HYDROGEN
        state.oxygen_outflow = self.get_o2_outflow()
        state.water_outflow_cathode = self.get_h2o_outflow_cathode()
        state.water_outflow_anode = self.get_h2o_outflow_anode()

    @abstractmethod
    def calculate(self, time, state: ElectrolyzerState) -> None:
        pass

    @abstractmethod
    def get_pressure_cathode(self) -> float:
        pass

    @abstractmethod
    def get_pressure_anode(self) -> float:
        pass

    @abstractmethod
    def get_h2_outflow(self) -> float:
        pass

    @abstractmethod
    def get_o2_outflow(self) -> float:
        pass

    @abstractmethod
    def get_h2o_outflow_cathode(self) -> float:
        pass

    @abstractmethod
    def get_h2o_outflow_anode(self) -> float:
        pass

    def close(self) -> None:
        """ Closing all resources in pressure model """
        pass