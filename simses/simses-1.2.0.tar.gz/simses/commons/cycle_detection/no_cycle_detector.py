from simses.commons.state.technology.storage import StorageTechnologyState
from .cycle_detector import CycleDetector


class NoCycleDetector(CycleDetector):

    def __init__(self):
        super().__init__()

    def cycle_detected(self, time: float, state: StorageTechnologyState) -> bool:
        return False

    def get_depth_of_cycle(self) -> float:
        return 0

    def get_delta_full_equivalent_cycle(self) -> float:
        return 0

    def get_crate(self) -> float:
        return 0

    def get_full_equivalent_cycle(self) -> float:
        return 0

    def _update_cycle_steps(self, soc: float, time_passed: float) -> None:
        pass

    def get_mean_soc(self) -> float:
        return 0

    def _reset_cycle(self, soc:float, time_passed: float) -> None:
        pass

    def reset(self) -> None:
        pass

    def close(self) -> None:
        pass
