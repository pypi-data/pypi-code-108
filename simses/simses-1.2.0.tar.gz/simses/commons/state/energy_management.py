from simses.commons.state.abstract_state import State


class EnergyManagementState(State):
    """
    Current State of the Energy Management (PV, Load, etc..)
    """

    LOAD_POWER = 'Load in W'
    PV_POWER = 'PV Generation in W'
    FCR_MAX_POWER = 'Power reserved for FCR in W'
    IDM_POWER = 'Power delivered for IDM in W'
    PEAKSHAVING_LIMIT = 'Peak Shaving Limit in W'

    def __init__(self):
        super().__init__()
        self._initialize()

    @property
    def load_power(self) -> float:
        return self.get(self.LOAD_POWER)

    @load_power.setter
    def load_power(self, value: float) -> None:
        self.set(self.LOAD_POWER, value)

    @property
    def pv_power(self) -> float:
        return self.get(self.PV_POWER)

    @pv_power.setter
    def pv_power(self, value: float) -> None:
        self.set(self.PV_POWER, value)

    @property
    def fcr_max_power(self) -> float:
        return self.get(self.FCR_MAX_POWER)

    @fcr_max_power.setter
    def fcr_max_power(self, value: float) -> None:
        self.set(self.FCR_MAX_POWER, value)

    @property
    def idm_power(self) -> float:
        return self.get(self.IDM_POWER)

    @idm_power.setter
    def idm_power(self, value: float) -> None:
        self.set(self.IDM_POWER, value)

    @property
    def peakshaving_limit(self) -> float:
        return self.get(self.PEAKSHAVING_LIMIT)

    @peakshaving_limit.setter
    def peakshaving_limit(self, value: float) -> None:
        self.set(self.PEAKSHAVING_LIMIT, value)

    @property
    def id(self) -> str:
        return 'EMS'

    @classmethod
    def sum_parallel(cls, system_states: []):
        raise Exception('sum_parallel is not implemented for EnergyManagementState')

    @classmethod
    def sum_serial(cls, states: []):
        raise Exception('sum_serial is not implemented for EnergyManagementState')
