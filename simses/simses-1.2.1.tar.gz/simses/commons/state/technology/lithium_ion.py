from simses.commons.state.technology.storage import StorageTechnologyState


class LithiumIonState(StorageTechnologyState):
    """
    Current physical state of the lithium_ion with the main electrical parameters.
    """

    SYSTEM_AC_ID: str = 'StorageSystemAC'
    SYSTEM_DC_ID: str = 'StorageSystemDC'
    SOC: str = 'SOC in p.u.'
    SOE: str = 'State of energy in Wh'
    SOH: str = 'State of health in p.u.'
    VOLTAGE: str = 'Voltage in V'
    VOLTAGE_OPEN_CIRCUIT: str = 'Open circuit voltage in V'
    NOMINAL_VOLTAGE: str = 'Nominal voltage in V'
    CURRENT: str = 'Current in A'
    TEMPERATURE: str = 'Temperature in K'
    CAPACITY: str = 'Capacity in Wh'
    INTERNAL_RESISTANCE: str = 'Internal resistance in Ohm'
    RESISTANCE_INCREASE: str = 'R increase in p.u.'
    POWER_LOSS: str = 'P_loss in W'
    FULFILLMENT: str = 'Bat_ful in p.u.'
    # VOLTAGE_INPUT: str = 'Voltage input in V'

    MAX_CHARGE_POWER: str = 'Maximum charging power in W'
    MAX_DISCHARGE_POWER: str = 'Maximum discharging power in W'

    CAPACITY_LOSS_CYCLIC: str = 'Cyclic Capacity Loss in Wh'
    CAPACITY_LOSS_CALENDRIC: str = 'Calendric Capacity Loss in Wh'
    CAPACITY_LOSS_OTHER: str = 'Other Capacity Loss in Wh'
    RESISTANCE_INCREASE_CYCLIC: str = 'Cyclic R Increase in p.u.'
    RESISTANCE_INCREASE_CALENDRIC: str = 'Calendric R Increase in p.u.'
    RESISTANCE_INCREASE_OTHER: str = 'Other R Increase in p.u.'


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
    def soe(self) -> float:
        return self.get(self.SOE)

    @soe.setter
    def soe(self, value: float) -> None:
        self.set(self.SOE, value)

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
    def voltage_open_circuit(self) -> float:
        return self.get(self.VOLTAGE_OPEN_CIRCUIT)

    @voltage_open_circuit.setter
    def voltage_open_circuit(self, value: float) -> None:
        self.set(self.VOLTAGE_OPEN_CIRCUIT, value)

    @property
    def nominal_voltage(self) -> float:
        return self.get(self.NOMINAL_VOLTAGE)

    @nominal_voltage.setter
    def nominal_voltage(self, value: float) -> None:
        self.set(self.NOMINAL_VOLTAGE, value)

    @property
    def current(self) -> float:
        return self.get(self.CURRENT)

    @current.setter
    def current(self, value: float) -> None:
        self.set(self.CURRENT, value)

    @property
    def temperature(self) -> float:
        return self.get(self.TEMPERATURE)

    @temperature.setter
    def temperature(self, value: float) -> None:
        self.set(self.TEMPERATURE, value)

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
    def resistance_increase(self) -> float:
        return self.get(self.RESISTANCE_INCREASE)

    @resistance_increase.setter
    def resistance_increase(self, value: float) -> None:
        self.set(self.RESISTANCE_INCREASE, value)

    @property
    def power_loss(self) -> float:
        return self.get(self.POWER_LOSS)

    @power_loss.setter
    def power_loss(self, value: float) -> None:
        self.set(self.POWER_LOSS, value)

    @property
    def fulfillment(self) -> float:
        return self.get(self.FULFILLMENT)

    @fulfillment.setter
    def fulfillment(self, value: float) -> None:
        self.set(self.FULFILLMENT, value)

    # @property
    # def voltage_input(self) -> float:
    #     return self.get(self.VOLTAGE_INPUT)

    # @voltage_input.setter
    # def voltage_input(self, value: float) -> None:
    #     self.set(self.VOLTAGE_INPUT, value)

    @property
    def id(self) -> str:
        return 'LIION' + str(self.get(self.SYSTEM_AC_ID)) + str(self.get(self.SYSTEM_DC_ID))

    @property
    def is_charge(self) -> bool:
        return self.current > 0

    @classmethod
    def sum_parallel(cls, battery_states: []):
        """
        Classmethod to calculate the combined BatteryState over several batteries connected in parallel.

        Parameters
        ----------
        battery_states : List
            List of BatteryState which are connected in parallel.

        Returns
        -------
        battery_state:
            Combined BatteryState over the parallel BatteryStates.
        """
        # TODO check and improvement necessary (MM)
        battery_state = LithiumIonState(0, 0)
        for bs in battery_states:
            battery_state.add(bs)
        # get non average values
        resistance = cls.sum_reverse(cls.INTERNAL_RESISTANCE, battery_states)
        current = battery_state.current
        capacity = battery_state.capacity
        power_loss = battery_state.power_loss
        max_charge = battery_state.max_charge_power
        max_discharge = battery_state.max_discharge_power
        # calculate capacity weighted values
        soc = 0
        soh = 0
        for state in battery_states:
            capacity_ratio = state.capacity / capacity
            soc += state.soc * capacity_ratio
            soh += state.soh * capacity_ratio
        # average values
        size = len(battery_states)
        battery_state.divide_by(size)
        # set capacity weighted values
        battery_state.soc = soc
        battery_state.soh = soh
        # set non average values
        battery_state.internal_resistance = resistance
        battery_state.current = current
        battery_state.capacity = capacity
        battery_state.power_loss = power_loss
        battery_state.max_charge_power = max_charge
        battery_state.max_discharge_power = max_discharge
        return battery_state

    @classmethod
    def sum_serial(cls, battery_states: []):
        """
        Classmethod to calculate the combined battery_state over several batteries connected in serial.

        Parameters
        ----------
        battery_states : List
            List of serial connected battery_states.

        Returns
        -------
        battery_state:
            Combined battery_state over the serial connected battery_states.
        """
        # TODO check and improvement necessary (MM)
        battery_state = LithiumIonState(0, 0)
        for bs in battery_states:
            battery_state.add(bs)
        # get non average values
        resistance = battery_state.internal_resistance
        voltage = battery_state.voltage
        nominal_voltage = battery_state.nominal_voltage
        power_loss = battery_state.power_loss
        # voltage_input = battery_state.voltage_input
        # average values
        size = len(battery_states)
        battery_state.divide_by(size)
        # set non average values
        battery_state.internal_resistance = resistance
        battery_state.voltage = voltage
        battery_state.nominal_voltage = nominal_voltage
        battery_state.power_loss = power_loss
        # battery_state.voltage_input = voltage_input
        return battery_state

    @property
    def capacity_loss_cyclic(self) -> float:
        return self.get(self.CAPACITY_LOSS_CYCLIC)

    @capacity_loss_cyclic.setter
    def capacity_loss_cyclic(self, value: float) -> None:
        self.set(self.CAPACITY_LOSS_CYCLIC, value)

    @property
    def capacity_loss_calendric(self) -> float:
        return self.get(self.CAPACITY_LOSS_CALENDRIC)

    @capacity_loss_calendric.setter
    def capacity_loss_calendric(self, value: float) -> None:
        self.set(self.CAPACITY_LOSS_CALENDRIC, value)

    @property
    def capacity_loss_other(self) -> float:
        return self.get(self.CAPACITY_LOSS_OTHER)

    @capacity_loss_other.setter
    def capacity_loss_other(self, value: float) -> None:
        self.set(self.CAPACITY_LOSS_OTHER, value)

    @property
    def resistance_increase_cyclic(self) -> float:
        return self.get(self.RESISTANCE_INCREASE_CYCLIC)

    @resistance_increase_cyclic.setter
    def resistance_increase_cyclic(self, value: float) -> None:
        self.set(self.RESISTANCE_INCREASE_CYCLIC, value)

    @property
    def resistance_increase_calendric(self) -> float:
        return self.get(self.RESISTANCE_INCREASE_CALENDRIC)

    @resistance_increase_calendric.setter
    def resistance_increase_calendric(self, value: float) -> None:
        self.set(self.RESISTANCE_INCREASE_CALENDRIC, value)

    @property
    def resistance_increase_other(self) -> float:
        return self.get(self.RESISTANCE_INCREASE_OTHER)

    @resistance_increase_other.setter
    def resistance_increase_other(self, value: float) -> None:
        self.set(self.RESISTANCE_INCREASE_OTHER, value)

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
