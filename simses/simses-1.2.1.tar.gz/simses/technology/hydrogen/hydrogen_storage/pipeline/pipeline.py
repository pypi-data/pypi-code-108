from abc import abstractmethod

from simses.technology.hydrogen.hydrogen_storage.hydrogen_storage import HydrogenStorage


class Pipeline(HydrogenStorage):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def calculate_inijected_hydrogen(self, time_diff, hydrogen_outflow) -> None:
        pass

    @abstractmethod
    def get_injected_hydrogen(self) -> float:
        pass

    @abstractmethod
    def get_tank_pressure(self) -> float:
        pass
