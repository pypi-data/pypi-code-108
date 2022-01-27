from simses.commons.state.technology.storage import StorageTechnologyState


class HydrogenState(StorageTechnologyState):
    """
    Current physical state of the hydrogen storage components with the main electrical parameters.
    """

    SYSTEM_AC_ID: str = 'StorageSystemAC'
    SYSTEM_DC_ID: str = 'StorageSystemDC'
    SOC: str = 'SOC in p.u.'
    SOH = 'State of health in p.u.'
    POWER: str = 'Power in W'
    VOLTAGE: str = 'voltage of hydrogen system in V'
    CURRENT: str = 'current of hydrogen storage system in A'
    POWER_LOSS: str = 'Power loss in W'
    CAPACITY: str = 'capacity in Wh'
    FULFILLMENT: str = 'fulfillment in p.u.'
    TEMPERATURE: str = 'temperature in K'
    MAX_CHARGE_POWER = 'Maximum charging power in W'
    MAX_DISCHARGE_POWER = 'Maximum discharging power in W'

    def __init__(self, system_id: int, storage_id: int):
        super().__init__()
        self._initialize()
        self.set(self.SYSTEM_AC_ID, system_id)
        self.set(self.SYSTEM_DC_ID, storage_id)

    @property
    def is_charge(self) -> bool:
        return self.power > 0

    @property
    def voltage(self) -> float:
        return self.get(self.VOLTAGE)

    @voltage.setter
    def voltage(self, value: float) -> None:
        self.set(self.VOLTAGE, value)

    @property
    def power(self) -> float:
        return self.get(self.POWER)

    @power.setter
    def power(self, value: float) -> None:
        self.set(self.POWER, value)

    @property
    def current(self) -> float:
        return self.get(self.CURRENT)

    @current.setter
    def current(self, value: float) -> None:
        self.set(self.CURRENT, value)

    @property
    def power_loss(self) -> float:
        return self.get(self.POWER_LOSS)

    @power_loss.setter
    def power_loss(self, value: float) -> None:
        self.set(self.POWER_LOSS, value)

    @property
    def soc(self) -> float:
        return self.get(self.SOC)

    @soc.setter
    def soc(self, value: float) -> None:
        self.set(self.SOC, value)

    @property
    def soh(self) -> float:
        return self.get(self.SOH)

    @soh.setter
    def soh(self, value: float) -> None:
        self.set(self.SOH, value)

    @property
    def capacity(self) -> float:
        return self.get(self.CAPACITY)

    @capacity.setter
    def capacity(self, value: float):
        self.set(self.CAPACITY, value)

    @property
    def fulfillment(self) -> float:
        return self.get(self.FULFILLMENT)

    @fulfillment.setter
    def fulfillment(self, value: float):
        self.set(self.FULFILLMENT, value)

    @property
    def temperature(self) -> float:
        return self.get(self.TEMPERATURE)

    @temperature.setter
    def temperature(self, value: float) -> None:
        self.set(self.TEMPERATURE, value)

    @property
    def id(self) -> str:
        return 'HYDROGEN' + str(self.get(self.SYSTEM_AC_ID)) + str(self.get(self.SYSTEM_DC_ID))

    @classmethod
    def sum_parallel(cls, states: []):
        pass

    @classmethod
    def sum_serial(cls, states: []):
        pass

    @property
    def max_charge_power(self) -> float:
        return self.get(self.MAX_CHARGE_POWER)

    @max_charge_power.setter
    def max_charge_power(self, value: float) -> None:
        self.set(self.MAX_CHARGE_POWER, value)

    @property
    def max_discharge_power(self) -> float:
        return self.get(self.MAX_DISCHARGE_POWER)

    @max_discharge_power.setter
    def max_discharge_power(self, value: float) -> None:
        self.set(self.MAX_DISCHARGE_POWER, value)
