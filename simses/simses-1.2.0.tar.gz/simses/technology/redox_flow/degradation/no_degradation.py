from simses.commons.state.technology.redox_flow import RedoxFlowState
from simses.technology.redox_flow.degradation.capacity_degradation import \
    CapacityDegradationModel


class NoDegradation(CapacityDegradationModel):
    """Model with no capacity degradation for a redox flow battery."""

    def __init__(self, capacity: float):
        super().__init__(capacity)

    def get_capacity_degradation(self, time: float, redox_flow_state: RedoxFlowState):
        return 0.0

    def close(self):
        super().close()
