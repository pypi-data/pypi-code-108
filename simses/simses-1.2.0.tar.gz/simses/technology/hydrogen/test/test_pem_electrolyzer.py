import pytest  # important to be able to use @pytest...

from simses.commons.config.data.electrolyzer import ElectrolyzerDataConfig
from simses.commons.constants import Hydrogen
from simses.commons.state.technology.electrolyzer import ElectrolyzerState
from simses.technology.hydrogen.electrolyzer.stack.pem import PemElectrolyzer

"""
Test ideas for Electrolyzers:
- hydrogen Production >=0; 
- hydrogen Production >0 bei power >0
- Pressure anode, cathode >=1


For PEM:
- Pressure anode >= pressure cathode (Differenzdruck über Membran muss >= 0 sein)



"""

'''
#1. Simple Test: Syntax, multiple asserts, import pytest, output in cmd

# def test_propertyof_product():
#     assert demo.product(5,5) == 25 #What should the result be?

#2. Test a Class using pytest's fixtures

# @pytest.fixture(scope="module")#module: gets only one instance
# def make_demo_instance():
#     print("Hey! I got instanciated :)")
#    return Demo()

def test_add(make_demo_instance):
    assert make_demo_instance.add(2, 2) == 4 #quick maths

#3. Parametrize a Test using pytest

@pytest.mark.parametrize('num1, num2, result',
                         [
                             (4, 1, 3),
                             (5, 5, 0)
                         ]
                         )
def test_subtract(num1, num2, result, make_demo_instance):
    print("For debugging reasons it is sometimes nice to print Variables. You can do this with -s", num1)
    assert make_demo_instance.subtract(num1, num2) == result

#4. Practical Example?

#Goto ACDC Example

#5. More Test Types and ressources

#60 Minute Tutorial: https://www.youtube.com/watch?v=bbp_849-RZ4
#Pytest Homepage for examples: https://docs.pytest.org/en/latest/example/index.html
'''


@pytest.fixture(scope="function") #module: gets only one instance
def uut(nominal_power) -> PemElectrolyzer:
    return PemElectrolyzer(nominal_power, ElectrolyzerDataConfig())


def create_electrolyzer_state_from(electrolyzer: PemElectrolyzer) -> ElectrolyzerState:
    state: ElectrolyzerState = ElectrolyzerState(0, 0)
    state.time = 0
    state.power = 0  # W
    state.temperature = 25  # °C
    state.power_loss = 0  # W
    state.hydrogen_production = 0  # mol/s
    state.hydrogen_outflow = 0  # mol/s
    state.oxygen_production = 0  # mol/s
    state.fulfillment = 1.0  # p.u.
    state.soh = 1.0  # p.u.
    state.convection_heat = 0  # W
    state.resistance_increase_cyclic = 0  # p.u.
    state.resistance_increase_calendar = 0  # p.u.
    state.resistance_increase = 0  # p.u.
    state.exchange_current_decrease_cyclic = 1  # p.u.
    state.exchange_current_decrease_calendar = 1  # p.u.
    state.exchange_current_decrease = 1  # p.u.
    state.pressure_anode = Hydrogen.EPS  # barg
    state.pressure_cathode = Hydrogen.EPS  # barg
    state.sat_pressure_h2o = 0.03189409713071401  # bar  h2o saturation pressure at 25°C
    state.part_pressure_h2 = (
                                         1.0 + state.pressure_cathode) - 0.03189409713071401  # bar partial pressure h2 at 25°C and cathode pressure
    state.part_pressure_o2 = (
                                         1.0 + state.pressure_anode) - 0.03189409713071401  # bar partial pressure o2 at 25°C and anode pressure
    state.total_pressure = 20
    state.water_use = 0  # mol/s#
    state.water_outflow_cathode = 0  # mol/s
    state.water_outflow_anode = 0  # mol/s
    state.water_flow = 0  # mol/s
    state.power_water_heating = 0  # W
    state.power_pump = 0  # W
    state.power_gas_drying = 0  # W
    state.power_compressor = 0  # W
    state.total_hydrogen_production = 0  # kg
    state.relative_time = 0  # start
    state.voltage = 1  # stays at 1 so that electrolyzer and fuel cell always see the power indepentently from the voltage a timestep before
    electrolyzer.calculate(state.power, state)
    state.voltage = electrolyzer.get_voltage()
    state.current = electrolyzer.get_current()
    state.current_density = electrolyzer.get_current_density()
    state.max_charge_power = electrolyzer.get_nominal_stack_power()
    state.max_discharge_power = electrolyzer.get_nominal_stack_power()
    return state


@pytest.mark.parametrize('nominal_power, power, temperature, pressure_anode, pressure_cathode, current_result',
                         [
                             (5, 0, 0, 0, 0, 0)
                         ]
                         )
def test_calculate_current(uut: PemElectrolyzer, power, temperature, pressure_anode, pressure_cathode, current_result):
    state: ElectrolyzerState = create_electrolyzer_state_from(uut)
    state.temperature = temperature
    state.pressure_anode = pressure_anode
    state.pressure_cathode = pressure_cathode
    uut.calculate(power, state)
    assert uut.get_current() == current_result


@pytest.mark.parametrize('nominal_power, power, temperature, pressure_anode, pressure_cathode, current_result',
                         [
                             (5, 5, 20, 1, 1, 0)
                         ]
                         )
def test_calculate_geq_current(uut: PemElectrolyzer, power, temperature, pressure_anode, pressure_cathode, current_result):
    state: ElectrolyzerState = create_electrolyzer_state_from(uut)
    state.temperature = temperature
    state.pressure_anode = pressure_anode
    state.pressure_cathode = pressure_cathode
    uut.calculate(power, state)
    assert uut.get_current() > current_result


@pytest.mark.parametrize('nominal_power, power, temperature, pressure_anode, pressure_cathode, voltage_result',
                         [
                             (10, 10, 25, 1, 1, 0),
                             (10, 0, 25, 0, 0, 0)
                         ]
                         )
def test_calculate_voltage(uut: PemElectrolyzer, power, temperature, pressure_anode, pressure_cathode, voltage_result):
    state: ElectrolyzerState = create_electrolyzer_state_from(uut)
    state.temperature = temperature
    state.pressure_anode = pressure_anode
    state.pressure_cathode = pressure_cathode
    uut.calculate(power, state)
    assert uut.get_voltage() > voltage_result


@pytest.mark.parametrize('nominal_power, power, temperature, pressure_anode, pressure_cathode, h2_flow_result',
                         [
                             (10, 10, 25, 1, 1, 0)
                         ]
                         )
def test_calculate_hydrogen_flow_geq(uut: PemElectrolyzer, power, temperature, pressure_anode, pressure_cathode, h2_flow_result):
    state: ElectrolyzerState = create_electrolyzer_state_from(uut)
    state.temperature = temperature
    state.pressure_anode = pressure_anode
    state.pressure_cathode = pressure_cathode
    uut.calculate(power, state)
    assert uut.get_hydrogen_production() > h2_flow_result


@pytest.mark.parametrize('nominal_power, power, temperature, pressure_anode, pressure_cathode, h2_flow_result',
                         [
                             (10, 0, 25, 0, 0, 0)
                         ]
                         )
def test_calculate_hydrogen_flow(uut: PemElectrolyzer, power, temperature, pressure_anode, pressure_cathode, h2_flow_result):
    state: ElectrolyzerState = create_electrolyzer_state_from(uut)
    state.temperature = temperature
    state.pressure_anode = pressure_anode
    state.pressure_cathode = pressure_cathode
    uut.calculate(power, state)
    assert uut.get_hydrogen_production() == h2_flow_result


@pytest.mark.parametrize('nominal_power, power, temperature, pressure_anode, pressure_cathode, get_water_use_result',
                         [
                             (10, 10, 25, 1, 1, 0)
                         ]
                         )
def test_calculate_water_use(uut: PemElectrolyzer, power, temperature, pressure_anode, pressure_cathode, get_water_use_result):
    state: ElectrolyzerState = create_electrolyzer_state_from(uut)
    state.temperature = temperature
    state.pressure_anode = pressure_anode
    state.pressure_cathode = pressure_cathode
    uut.calculate(power, state)
    assert uut.get_water_use() > get_water_use_result
