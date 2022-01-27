from simses.commons.state.technology.lithium_ion import LithiumIonState
from simses.technology.lithium_ion.degradation.cyclic.cyclic_degradation import \
    CyclicDegradationModel


class NoCyclicDegradationModel(CyclicDegradationModel):

    def __init__(self):
        super().__init__(None, None)

    def calculate_degradation(self, battery_state: LithiumIonState) -> None:
        pass

    def calculate_resistance_increase(self, battery_state: LithiumIonState) -> None:
        pass

    def get_degradation(self) -> float:
        return 0

    def get_resistance_increase(self) -> float:
        return 0

    def reset(self, lithium_ion_state: LithiumIonState) -> None:
        pass

    def close(self) -> None:
        pass
