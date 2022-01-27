from configparser import ConfigParser

import pytest

from simses.commons.config.simulation.battery import BatteryConfig
from simses.commons.state.technology.lithium_ion import LithiumIonState
from simses.technology.lithium_ion.battery_management_system.management_system import BatteryManagementSystem
from simses.technology.lithium_ion.cell.generic import GenericCell
from simses.technology.lithium_ion.cell.type import CellType

THRESHOLD: float = 1e-10

voltage: float = 600  # V
capacity: float = 60e3  # Wh
soh: float = 1.0  # p.u.

start_soc: float = 0.5  # p.u.
start_temperature: float = 300  # K

max_current: float = 205  # A (for Generic Cell in current setup)

time_step: float = 60  # s


battery_config: ConfigParser = ConfigParser()
battery_config.add_section('BATTERY')
battery_config.set('BATTERY', 'START_SOC', str(start_soc))
battery_config.set('BATTERY', 'MIN_SOC', str(0.0))
battery_config.set('BATTERY', 'MAX_SOC', str(1.0))
battery_config.set('BATTERY', 'EOL', str(0.6))
battery_config.set('BATTERY', 'START_SOH', str(soh))


@pytest.fixture()
def uut() -> BatteryManagementSystem:
    cell_type: CellType = GenericCell(voltage, capacity, soh, BatteryConfig(battery_config))
    return BatteryManagementSystem(cell_type, BatteryConfig(battery_config))


def create_battery_state() -> LithiumIonState:
    cell_type: CellType = GenericCell(voltage, capacity, soh, BatteryConfig(battery_config))
    bs = LithiumIonState(0, 0)
    bs.time = 0
    bs.soc = start_soc
    bs.temperature = start_temperature
    bs.voltage = cell_type.get_open_circuit_voltage(bs)
    bs.voltage_open_circuit = cell_type.get_open_circuit_voltage(bs)
    bs.nominal_voltage = cell_type.get_nominal_voltage()
    bs.internal_resistance = cell_type.get_internal_resistance(bs)
    bs.capacity = cell_type.get_capacity(bs) * cell_type.get_nominal_voltage() * cell_type.get_soh_start()
    bs.soh = cell_type.get_soh_start()
    bs.soe = bs.soc * bs.capacity
    bs.fulfillment = 1.0
    bs.max_charge_power = cell_type.get_max_current(bs) * bs.voltage
    bs.max_discharge_power = cell_type.get_min_current(bs) * bs.voltage
    return bs


@pytest.mark.parametrize('temperature, current, result',
                         [
                            (0, 100, 0),
                            (300, 100, 100),
                            (400, 100, 0)
                         ]
                         )
def test_temperature(uut: BatteryManagementSystem, temperature: float, current: float, result: float):
    battery_state: LithiumIonState = create_battery_state()
    battery_state.temperature = temperature
    battery_state.current = current
    uut.update(time_step, battery_state, current * battery_state.voltage)
    uut.close()
    assert abs(battery_state.current - result) <= THRESHOLD


@pytest.mark.parametrize('current, result',
                         [
                            (-400, -max_current),
                            (-100, -100),
                            (0, 0),
                            (100, 100),
                            (400, max_current)
                         ]
                         )
def test_current(uut: BatteryManagementSystem, current: float, result: float):
    battery_state: LithiumIonState = create_battery_state()
    battery_state.current = current
    uut.update(time_step, battery_state, current * battery_state.voltage)
    uut.close()
    assert abs(battery_state.current - result) <= THRESHOLD


@pytest.mark.parametrize('soc, current, result',
                         [
                            (-1, -100, 0),
                            (1, 100, 0),
                            (0.5, 200, 200)
                         ]
                         )
def test_soc(uut: BatteryManagementSystem, soc: float, current: float, result: float):
    battery_state: LithiumIonState = create_battery_state()
    battery_state.soc = soc
    battery_state.soe = soc * battery_state.capacity
    battery_state.current = current
    uut.update(time_step, battery_state, current * battery_state.voltage)
    uut.close()
    assert abs(battery_state.current - result) <= THRESHOLD


@pytest.mark.parametrize('current, result',
                         [
                            (-400, max_current/400.0),
                            (-100, 1.0),
                            (0, 1.0),
                            (100, 1.0),
                            (400, max_current/400.0)
                         ]
                         )
def test_fulfillment(uut: BatteryManagementSystem, current: float, result: float):
    battery_state: LithiumIonState = create_battery_state()
    battery_state.current = current
    uut.update(time_step, battery_state, current * battery_state.voltage)
    uut.close()
    assert abs(battery_state.fulfillment - result) <= THRESHOLD
