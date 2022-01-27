from simses.commons.constants import Hydrogen
from simses.technology.hydrogen.hydrogen_storage.pipeline.pipeline import Pipeline


class SimplePipeline(Pipeline):

    """calculates total mass of produced and injected hydrogen in kg"""

    def __init__(self, storage_pressure: float):
        super().__init__()
        self.__injected_hydrogen = 0  # kg
        self.__storage_pressure = storage_pressure

    def calculate_inijected_hydrogen(self, time_diff: float, hydrogen_outflow: float) -> None:
        self.__injected_hydrogen = time_diff * hydrogen_outflow * 2.0 * Hydrogen.MOLAR_MASS_HYDROGEN # kg

    def calculate_soc(self, time_diff: float, hydrogen_net_flow: float) -> None:
        pass

    def get_injected_hydrogen(self) -> float:
        return self.__injected_hydrogen

    def get_tank_pressure(self) -> float:
        return self.__storage_pressure

    def get_soc(self) -> float:
        return 0.5

    def get_capacity(self) -> float:
        return 1000000

    def close(self) -> None:
        pass
