from abc import ABC, abstractmethod

from simses.commons.state.technology.lithium_ion import LithiumIonState


class EquivalentCircuitModel(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def update(self, time: float, battery_state: LithiumIonState) -> None:
        """Updating current, voltage, power loss and soc of lithium_ion state"""
        pass

    @abstractmethod
    def close(self) -> None:
        """Closing all resources in lithium_ion model"""
        pass
