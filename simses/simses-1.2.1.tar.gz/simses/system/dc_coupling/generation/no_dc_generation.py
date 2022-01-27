from simses.system.auxiliary.auxiliary import Auxiliary
from simses.system.dc_coupling.generation.dc_generation import DcGeneration


class NoDcGeneration(DcGeneration):

    def __init__(self):
        super().__init__()

    def get_power(self) -> float:
        return 0.0

    def calculate_power(self, time: float) -> None:
        pass

    def get_auxiliaries(self) -> [Auxiliary]:
        return list()

    def close(self):
        pass
