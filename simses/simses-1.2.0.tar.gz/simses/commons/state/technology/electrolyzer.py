from simses.commons.state.technology.storage import StorageTechnologyState


class ElectrolyzerState(StorageTechnologyState):
    """
    Current physical state of the electrolyzer components with the main electrical parameters.
    """

    SYSTEM_AC_ID = 'StorageSystemAC'
    SYSTEM_DC_ID = 'StorageSystemDC'
    VOLTAGE = 'voltage of electrolyzer in V'
    CURRENT = 'current of electrolyzer in A'
    CURRENT_DENSITY = 'current density of electrolyzer in A'
    POWER = 'power in W'
    TEMPERATURE = 'temperature of electrolyzer stack in K'
    POWER_LOSS = 'Power loss in W'
    HYDROGEN_PRODUCTION = 'hydrogen production in mol/s'  # hydrogen production of electrolyzerstack
    HYDROGEN_OUTFLOW = 'hydrogen outlfow in mol/s'  # hydrogen outflow after pressure controll valve
    OXYGEN_PRODUCTION = 'oxygen production in mol/s'  # oxygen production of electrolyzer
    OXYGEN_OUTFLOW = 'oxygen outflow in mol/s'  # oxygen outflow out of the electrolyzer after pressure control
    FULFILLMENT = 'fulfillment in p.u.'  # ??
    CONVECTION_HEAT = 'convection heat in W'
    PRESSURE_ANODE = 'relative anode pressure of electrolyzer in barg'
    PRESSURE_CATHODE = 'relative cathode pressure or electrolyzer in barg'
    PART_PRESSURE_H2 = 'partial pressure H2 in bar'
    PART_PRESSURE_O2 = 'partial pressure O2 in bar'
    SAT_PRESSURE_H2O = 'saturation pressure H2O in bar'
    WATER_USE = 'wateruse in mol/s'  # water the electrolyzer splits into hydrogen and oxygen
    WATER_OUTFLOW_CATHODE = 'watersteam outflow cathode electrolyzer in mol/s'
    WATER_OUTFLOW_ANODE = 'watersteam outflow anode electrolyzer in mol/s'
    WATER_FLOW = 'waterflow electrolyzer in mol/s'  # water the is circulated through the EL stack in order to tempering
    POWER_WATER_HEATING  = 'power water heating electrolyzer in W'  # power that is transported by the water stream through the electrolyzer stack
                                                                        # if Ph20 > 0: heating  if Ph2o < 0: heat is transported out of the stack and realeased to the ambient atmosphere (no electrical power needed)
    POWER_PUMP = 'power water circulation electrolyzer in W'  # power the pump consumes for circulation of water through electrolyzer
    POWER_GAS_DRYING = 'power for drying of hydrogen in W'
    POWER_COMPRESSOR = 'power for compression of hydrogen in W'
    TOTAL_HYDROGEN_PRODUCTION = 'total amount of produced hydrogen in kg'
    RESISTANCE_INCREASE_CYCLIC = 'increase resistance cyclic in p.u.'
    RESISTANCE_INCREASE_CALENDAR = 'increase reisistance calendric in p.u.'
    RESISTANCE_INCREASE = 'increase R total in p.u.'
    REFERENCE_VOLTAGE = 'reverence voltage in V'
    EXCHANGE_CURRENT_DENS_DECREASE_CYCLIC = 'decrease j0 cyclic in p.u.'
    EXCHANGE_CURRENT_DENS_DECREASE_CALENDAR = 'decrease j0 calendric in p.u.'
    EXCHANGE_CURRENT_DENS_DECREASE = 'decrease j0 in p.u.'
    SOH = 'SOH electrolyzer in p.u.'
    MAX_CHARGE_POWER = 'Maximum charging power in W'
    MAX_DISCHARGE_POWER = 'Maximum discharging power in W'

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

    @property
    def power(self) -> float:
        return self.get(self.POWER)

    @power.setter
    def power(self, value: float) -> None:
        self.set(self.POWER, value)

    @property
    def hydrogen_production(self) -> float:
        return self.get(self.HYDROGEN_PRODUCTION)

    @hydrogen_production.setter
    def hydrogen_production(self, value: float) -> None:
        self.set(self.HYDROGEN_PRODUCTION, value)

    @property
    def hydrogen_outflow(self) -> float:
        return self.get(self.HYDROGEN_OUTFLOW)

    @hydrogen_outflow.setter
    def hydrogen_outflow(self, value: float) -> None:
        self.set(self.HYDROGEN_OUTFLOW, value)

    @property
    def oxygen_production(self) -> float:
        return self.get(self.OXYGEN_PRODUCTION)

    @oxygen_production.setter
    def oxygen_production(self, value: float) -> None:
        self.set(self.OXYGEN_PRODUCTION, value)

    @property
    def oxygen_outflow(self) -> float:
        return self.get(self.OXYGEN_OUTFLOW)

    @oxygen_outflow.setter
    def oxygen_outflow(self, value: float) -> None:
        self.set(self.OXYGEN_OUTFLOW, value)

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
    def part_pressure_h2(self) -> float:
        return self.get(self.PART_PRESSURE_H2)

    @part_pressure_h2.setter
    def part_pressure_h2(self, value: float):
        self.set(self.PART_PRESSURE_H2, value)

    @property
    def part_pressure_o2(self) -> float:
        return self.get(self.PART_PRESSURE_O2)

    @part_pressure_o2.setter
    def part_pressure_o2(self, value: float):
        self.set(self.PART_PRESSURE_O2, value)

    @property
    def sat_pressure_h2o(self) -> float:
        return self.get(self.SAT_PRESSURE_H2O)

    @sat_pressure_h2o.setter
    def sat_pressure_h2o(self, value: float):
        self.set(self.SAT_PRESSURE_H2O, value)

    @property
    def water_use(self) -> float:
        return self.get(self.WATER_USE)

    @water_use.setter
    def water_use(self, value: float):
        self.set(self.WATER_USE, value)

    @property
    def water_outflow_cathode(self) -> float:
        return self.get(self.WATER_OUTFLOW_CATHODE)

    @water_outflow_cathode.setter
    def water_outflow_cathode(self, value: float):
        self.set(self.WATER_OUTFLOW_CATHODE, value)

    @property
    def water_outflow_anode(self) -> float:
        return self.get(self.WATER_OUTFLOW_ANODE)

    @water_outflow_anode.setter
    def water_outflow_anode(self, value: float):
        self.set(self.WATER_OUTFLOW_ANODE, value)

    @property
    def water_flow(self) -> float:
        return self.get(self.WATER_FLOW)

    @water_flow.setter
    def water_flow(self, value: float):
        self.set(self.WATER_FLOW, value)

    @property
    def power_water_heating(self) -> float:
        return self.get(self.POWER_WATER_HEATING)

    @power_water_heating.setter
    def power_water_heating(self, value: float):
        self.set(self.POWER_WATER_HEATING, value)

    @property
    def power_pump(self) -> float:
        return self.get(self.POWER_PUMP)

    @power_pump.setter
    def power_pump(self, value: float):
        self.set(self.POWER_PUMP, value)

    @property
    def power_gas_drying(self) -> float:
        return self.get(self.POWER_GAS_DRYING)

    @power_gas_drying.setter
    def power_gas_drying(self, value: float):
        self.set(self.POWER_GAS_DRYING, value)

    @property
    def power_compressor(self) -> float:
        return self.get(self.POWER_COMPRESSOR)

    @power_compressor.setter
    def power_compressor(self, value: float):
        self.set(self.POWER_COMPRESSOR, value)

    @property
    def total_hydrogen_production(self) -> float:
        return self.get(self.TOTAL_HYDROGEN_PRODUCTION)

    @total_hydrogen_production.setter
    def total_hydrogen_production(self, value: float):
        self.set(self.TOTAL_HYDROGEN_PRODUCTION, value)

    @property
    def resistance_increase_cyclic(self) -> float:
        return self.get(self.RESISTANCE_INCREASE_CYCLIC)

    @resistance_increase_cyclic.setter
    def resistance_increase_cyclic(self, value: float):
        self.set(self.RESISTANCE_INCREASE_CYCLIC, value)

    @property
    def resistance_increase_calendar(self) -> float:
        return self.get(self.RESISTANCE_INCREASE_CALENDAR)

    @resistance_increase_calendar.setter
    def resistance_increase_calendar(self, value: float):
        self.set(self.RESISTANCE_INCREASE_CALENDAR, value)

    @property
    def resistance_increase(self) -> float:
        return self.get(self.RESISTANCE_INCREASE)

    @resistance_increase.setter
    def resistance_increase(self, value: float):
        self.set(self.RESISTANCE_INCREASE, value)

    @property
    def reference_voltage(self) -> float:
        return self.get(self.REFERENCE_VOLTAGE)

    @reference_voltage.setter
    def reference_voltage(self, value: float):
        self.set(self.REFERENCE_VOLTAGE, value)

    @property
    def exchange_current_decrease_cyclic(self) -> float:
        return self.get(self.EXCHANGE_CURRENT_DENS_DECREASE_CYCLIC)

    @exchange_current_decrease_cyclic.setter
    def exchange_current_decrease_cyclic(self, value: float):
        self.set(self.EXCHANGE_CURRENT_DENS_DECREASE_CYCLIC, value)

    @property
    def exchange_current_decrease_calendar(self) -> float:
        return self.get(self.EXCHANGE_CURRENT_DENS_DECREASE_CALENDAR)

    @exchange_current_decrease_calendar.setter
    def exchange_current_decrease_calendar(self, value: float):
        self.set(self.EXCHANGE_CURRENT_DENS_DECREASE_CALENDAR, value)

    @property
    def exchange_current_decrease(self) -> float:
        return self.get(self.EXCHANGE_CURRENT_DENS_DECREASE)

    @exchange_current_decrease.setter
    def exchange_current_decrease(self, value: float):
        self.set(self.EXCHANGE_CURRENT_DENS_DECREASE, value)

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

    @property
    def soh(self) -> float:
        return self.get(self.SOH)

    @soh.setter
    def soh(self, value: float):
        self.set(self.SOH, value)

    @property
    def id(self) -> str:
        return 'ELECTROLYZER' + str(self.get(self.SYSTEM_AC_ID)) + str(self.get(self.SYSTEM_DC_ID))

    @property
    def is_charge(self) -> bool:
        return self.power > 0

    @classmethod
    def sum_parallel(cls, hydrogen_states: []):
        state = ElectrolyzerState(0, 0)
        return state

    @classmethod
    def sum_serial(cls, states: []):
        pass
