from simses.commons.state.technology.storage import StorageTechnologyState


class FuelCellState(StorageTechnologyState):
    """
    Current physical state of the fuel cell components with the main electrical parameters.
    """

    SYSTEM_AC_ID = 'StorageSystemAC'
    SYSTEM_DC_ID = 'StorageSystemDC'
    VOLTAGE = 'voltage of fuel cell in V'
    CURRENT = 'current of fuel cell in A'
    CURRENT_DENSITY = 'current density of fuel cell in A cm-2'
    POWER = 'power in W'
    TEMPERATURE = 'temperature of fuel cell stack in K'
    POWER_LOSS = 'Power loss in W'
    HYDROGEN_USE = 'hydrogen use in mol/s'  # hydrogen use of fuel cell
    HYDROGEN_INFLOW = 'hydrogen inflow in mol/s'  # hydrogen inflow into fuelcell stack for pressure control
    OXYGEN_USE = 'oxygen use in mol/s'  # oxygen use of fuel cell
    OXYGEN_INFLOW = 'oxygen inflow in mol/s'  # oxygen inflow into fuelcell stack for pressure control of fuel cell
    FULFILLMENT = 'fulfillment in p.u.'  # ??
    CONVECTION_HEAT = 'convection heat in W'
    PRESSURE_ANODE = 'relative anode pressure of fuelcell in barg'
    PRESSURE_CATHODE = 'relative cathode pressure of fuelcell in barg'
    SOH = 'State of health in p.u.'
    SOC = 'SOC of Hydrogen Storage'
    MAX_CHARGE_POWER = 'max charge power in W'
    MAX_DISCHARGE_POWER = 'max discharge power in W'

    def __init__(self, system_id: int, storage_id: int):
        super().__init__()
        self._initialize()
        self.set(self.SYSTEM_AC_ID, system_id)
        self.set(self.SYSTEM_DC_ID, storage_id)

    @property
    def soc(self) -> float:
        pass

    @soc.setter
    def soc(self, value: float) -> None:
        pass

    @property
    def capacity(self) -> float:
        pass

    @capacity.setter
    def capacity(self, value: float):
        pass

    @property
    def voltage(self) -> float:
        return self.get(self.VOLTAGE)

    @voltage.setter
    def voltage(self, value: float) -> None:
        self.set(self.VOLTAGE, value)

    @property
    def current(self) -> float:
        return self.get(self.CURRENT)

    @current.setter
    def current(self, value: float) -> None:
        self.set(self.CURRENT, value)

    @property
    def current_density(self) -> float:
        return self.get(self.CURRENT_DENSITY)

    @current_density.setter
    def current_density(self, value: float) -> None:
        self.set(self.CURRENT_DENSITY, value)

    @property
    def temperature(self) -> float:
        return self.get(self.TEMPERATURE)

    @temperature.setter
    def temperature(self, value: float) -> None:
        self.set(self.TEMPERATURE, value)

    @property
    def power_loss(self) -> float:
        return self.get(self.POWER_LOSS)

    @power_loss.setter
    def power_loss(self, value: float) -> None:
        self.set(self.POWER_LOSS, value)

    # @property
    # def power(self) -> float:
    #     return self.get(self.POWER)
    #
    # @power.setter
    # def power(self, value: float) -> None:
    #     self.set(self.POWER, value)

    @property
    def hydrogen_use(self) -> float:
        return self.get(self.HYDROGEN_USE)

    @hydrogen_use.setter
    def hydrogen_use(self, value: float) -> None:
        self.set(self.HYDROGEN_USE, value)

    @property
    def hydrogen_inflow(self) -> float:
        return self.get(self.HYDROGEN_INFLOW)

    @hydrogen_inflow.setter
    def hydrogen_inflow(self, value: float) -> None:
        self.set(self.HYDROGEN_INFLOW, value)

    @property
    def oxygen_use(self) -> float:
        return self.get(self.OXYGEN_USE)

    @oxygen_use.setter
    def oxygen_use(self, value: float) -> None:
        self.set(self.OXYGEN_USE, value)

    @property
    def oxygen_inflow(self) -> float:
        return self.get(self.OXYGEN_INFLOW)

    @oxygen_inflow.setter
    def oxygen_inflow(self, value: float) -> None:
        self.set(self.OXYGEN_INFLOW, value)

    @property
    def convection_heat(self) -> float:
        return self.get(self.CONVECTION_HEAT)

    @convection_heat.setter
    def convection_heat(self, value: float) -> None:
        self.set(self.CONVECTION_HEAT, value)

    @property
    def fulfillment(self) -> float:
        return self.get(self.FULFILLMENT)

    @fulfillment.setter
    def fulfillment(self, value: float):
        self.set(self.FULFILLMENT, value)

    @property
    def pressure_anode(self) -> float:
        return self.get(self.PRESSURE_ANODE)

    @pressure_anode.setter
    def pressure_anode(self, value: float):
        self.set(self.PRESSURE_ANODE, value)

    @property
    def pressure_cathode(self) -> float:
        return self.get(self.PRESSURE_CATHODE)

    @pressure_cathode.setter
    def pressure_cathode(self, value: float):
        self.set(self.PRESSURE_CATHODE, value)

    @property
    def soh(self) -> float:
        return self.get(self.SOH)

    @soh.setter
    def soh(self, value: float):
        self.set(self.SOH, value)

    @property
    def max_charge_power(self) -> float:
        return self.get(self.MAX_CHARGE_POWER)

    @max_charge_power.setter
    def max_charge_power(self, value: float):
        self.set(self.MAX_CHARGE_POWER, value)

    @property
    def max_discharge_power(self) -> float:
        return self.get(self.MAX_DISCHARGE_POWER)

    @max_discharge_power.setter
    def max_discharge_power(self, value: float):
        self.set(self.MAX_DISCHARGE_POWER, value)

    @property
    def id(self) -> str:
        return 'FUELCELL' + str(self.get(self.SYSTEM_AC_ID)) + str(self.get(self.SYSTEM_DC_ID))

    @property
    def is_charge(self) -> bool:
        return self.current > 0

    @classmethod
    def sum_parallel(cls, hydrogen_states: []):
        hydrogen_state = FuelCellState(0, 0)
        return hydrogen_state

    @classmethod
    def sum_serial(cls, states: []):
        pass