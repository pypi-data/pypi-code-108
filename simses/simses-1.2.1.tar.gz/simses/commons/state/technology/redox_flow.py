from simses.commons.state.technology.storage import StorageTechnologyState


class RedoxFlowState(StorageTechnologyState):
    """
    Current physical state of the redox_flow system with the main electrical parameters.
    """

    SYSTEM_AC_ID = 'StorageSystemAC'
    SYSTEM_DC_ID = 'StorageSystemDC'
    SOC = 'SOC in p.u.'
    SOC_STACK = 'SOC in stack in p.u.'
    SOH = 'State of health in p.u.'
    VOLTAGE = 'Voltage in V'
    OPEN_CIRCUIT_VOLTAGE = 'Open circuit voltage (OCV) in V'
    CURRENT = 'Current in A'
    CAPACITY = 'Capacity in Wh'
    INTERNAL_RESISTANCE = 'Internal resistance in Ohm'
    POWER_LOSS = 'Power loss in W'
    POWER_IN = 'Power input in W'
    POWER = 'Power output in W'
    PUMP_POWER = 'Pump power in W'
    PRESSURE_LOSS_ANOLYTE = 'Pressure loss anolyte in W'
    PRESSURE_LOSS_CATHOLYTE = 'Pressure loss catholyte in W'
    FLOW_RATE_ANOLYTE = 'Anolyte flow rate in m^3/s'
    FLOW_RATE_CATHOLYTE = 'Catholyte flow rate in m^3/s'
    PRESSURE_DROP_ANOLYTE = 'Anolyte pressure drop in Pa'
    PRESSURE_DROP_CATHOLYTE = 'Catholyte pressure drop in Pa'
    FULFILLMENT = 'Fulfillment in p.u.'
    TEMPERATURE = 'Electrolyte and stack temperature in K'
    TIME_PUMP = 'Time of pump on or off in s'
    MAX_CHARGE_POWER = 'Maximum charging power in W'
    MAX_DISCHARGE_POWER = 'Maximum discharging power in W'

    def __init__(self, system_id: int, storage_id: int):
        super().__init__()
        self._initialize()
        self.set(self.SYSTEM_AC_ID, system_id)
        self.set(self.SYSTEM_DC_ID, storage_id)

    @property
    def soc(self) -> float:
        return self.get(self.SOC)

    @soc.setter
    def soc(self, value: float) -> None:
        self.set(self.SOC, value)

    @property
    def soc_stack(self) -> float:
        return self.get(self.SOC_STACK)

    @soc_stack.setter
    def soc_stack(self, value: float) -> None:
        self.set(self.SOC_STACK, value)

    @property
    def soh(self) -> float:
        return self.get(self.SOH)

    @soh.setter
    def soh(self, value: float) -> None:
        self.set(self.SOH, value)

    @property
    def voltage(self) -> float:
        return self.get(self.VOLTAGE)

    @voltage.setter
    def voltage(self, value: float) -> None:
        self.set(self.VOLTAGE, value)

    @property
    def open_circuit_voltage(self) -> float:
        return self.get(self.OPEN_CIRCUIT_VOLTAGE)

    @open_circuit_voltage.setter
    def open_circuit_voltage(self, value: float) -> None:
        self.set(self.OPEN_CIRCUIT_VOLTAGE, value)

    @property
    def current(self) -> float:
        return self.get(self.CURRENT)

    @current.setter
    def current(self, value: float) -> None:
        self.set(self.CURRENT, value)

    @property
    def capacity(self) -> float:
        return self.get(self.CAPACITY)

    @capacity.setter
    def capacity(self, value: float) -> None:
        self.set(self.CAPACITY, value)

    @property
    def internal_resistance(self) -> float:
        return self.get(self.INTERNAL_RESISTANCE)

    @internal_resistance.setter
    def internal_resistance(self, value: float) -> None:
        self.set(self.INTERNAL_RESISTANCE, value)

    @property
    def power_loss(self) -> float:
        return self.get(self.POWER_LOSS)

    @power_loss.setter
    def power_loss(self, value: float) -> None:
        self.set(self.POWER_LOSS, value)

    @property
    def power_in(self) -> float:
        return self.get(self.POWER_IN)

    @power_in.setter
    def power_in(self, value: float) -> None:
        self.set(self.POWER_IN, value)

    @property
    def power(self) -> float:
        return self.get(self.POWER)

    @power.setter
    def power(self, value: float) -> None:
        self.set(self.POWER, value)

    @property
    def pump_power(self) -> float:
        return self.get(self.PUMP_POWER)

    @pump_power.setter
    def pump_power(self, value: float) -> None:
        self.set(self.PUMP_POWER, value)

    @property
    def pressure_loss_anolyte(self) -> float:
        return self.get(self.PRESSURE_LOSS_ANOLYTE)

    @pressure_loss_anolyte.setter
    def pressure_loss_anolyte(self, value: float) -> None:
        self.set(self.PRESSURE_LOSS_ANOLYTE, value)

    @property
    def pressure_loss_catholyte(self) -> float:
        return self.get(self.PRESSURE_LOSS_CATHOLYTE)

    @pressure_loss_catholyte.setter
    def pressure_loss_catholyte(self, value: float) -> None:
        self.set(self.PRESSURE_LOSS_CATHOLYTE, value)

    @property
    def flow_rate_anolyte(self) -> float:
        return self.get(self.FLOW_RATE_ANOLYTE)

    @flow_rate_anolyte.setter
    def flow_rate_anolyte(self, value: float) -> None:
        self.set(self.FLOW_RATE_ANOLYTE, value)

    @property
    def flow_rate_catholyte(self) -> float:
        return self.get(self.FLOW_RATE_CATHOLYTE)

    @flow_rate_catholyte.setter
    def flow_rate_catholyte(self, value: float) -> None:
        self.set(self.FLOW_RATE_CATHOLYTE, value)

    @property
    def pressure_drop_anolyte(self) -> float:
        return self.get(self.PRESSURE_DROP_ANOLYTE)

    @pressure_drop_anolyte.setter
    def pressure_drop_anolyte(self, value: float) -> None:
        self.set(self.PRESSURE_DROP_ANOLYTE, value)

    @property
    def pressure_drop_catholyte(self) -> float:
        return self.get(self.PRESSURE_DROP_CATHOLYTE)

    @pressure_drop_catholyte.setter
    def pressure_drop_catholyte(self, value: float) -> None:
        self.set(self.PRESSURE_DROP_CATHOLYTE, value)

    @property
    def fulfillment(self) -> float:
        return self.get(self.FULFILLMENT)

    @fulfillment.setter
    def fulfillment(self, value: float) -> None:
        self.set(self.FULFILLMENT, value)

    @property
    def temperature(self) -> float:
        return self.get(self.TEMPERATURE)

    @temperature.setter
    def temperature(self, value: float) -> None:
        self.set(self.TEMPERATURE, value)

    @property
    def time_pump(self) -> float:
        return self.get(self.TIME_PUMP)

    @time_pump.setter
    def time_pump(self, value: float) -> None:
        self.set(self.TIME_PUMP, value)

    @property
    def id(self) -> str:
        return 'REDOXFLOW' + str(self.get(self.SYSTEM_AC_ID)) + str(self.get(self.SYSTEM_DC_ID))

    @property
    def is_charge(self) -> bool:
        return self.power > 0

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
