from configparser import ConfigParser

import numpy as np
import pandas
import pytest

from simses.analysis.data.energy_management import EnergyManagementData
from simses.analysis.data.system import SystemData
from simses.analysis.evaluation.economic.revenue_stream.energy_cost_reduction import EnergyCostReduction
from simses.commons.config.analysis.economic import EconomicAnalysisConfig
from simses.commons.config.simulation.general import GeneralSimulationConfig

# fixed input parameters
from simses.commons.state.energy_management import EnergyManagementState
from simses.commons.state.system import SystemState

years = 5
timestep = 3600
elec_price = 0.3
pv_feed = 0.1
load_const = 3000
pv_const = 2000


def create_general_config() -> GeneralSimulationConfig:
    simulation_config: ConfigParser = ConfigParser()
    simulation_config.add_section('GENERAL')
    simulation_config.set('GENERAL', 'TIME_STEP', str(timestep))
    return GeneralSimulationConfig(simulation_config)


def create_economic_analysis_config() -> EconomicAnalysisConfig:
    analysis_config: ConfigParser = ConfigParser()
    analysis_config.add_section('ECONOMIC_ANALYSIS')
    analysis_config.set('ECONOMIC_ANALYSIS', 'ELECTRICITY_PRICE', str(elec_price))
    analysis_config.set('ECONOMIC_ANALYSIS', 'PV_FEED_IN_TARIFF', str(pv_feed))
    return EconomicAnalysisConfig(analysis_config)


@pytest.mark.parametrize('batt_const', [-2000, 2000])  # load convention is used for battery in SimSES
def test_energy_cost_reduction(batt_const):
    """Performs a unit test by comparing the expected result for a generic
    time series with the actual result."""

    # set up test data
    n = int(years * 365 * 24 * 60 * 60 / timestep)
    ws_to_kwh = 1/(1000 * 3600)
    unix_timestamp_start_2020 = 1577836800
    time_test = pandas.array([unix_timestamp_start_2020 + timestep * i for i in range(n)])
    load_power = pandas.array([load_const] * n)
    pv_power = pandas.array([pv_const] * n)
    battery_power = pandas.array([batt_const] * n)

    # calculate expected result
    if load_const - pv_const > 0:
        cashflow_base_const = (-load_const + pv_const) * ws_to_kwh * timestep * elec_price
    else:
        cashflow_base_const = (-load_const + pv_const) * ws_to_kwh * timestep * pv_feed
    if load_const - pv_const + batt_const > 0:
        cashflow_battery_const = (-load_const + pv_const - batt_const) * ws_to_kwh * timestep * elec_price
    else:
        cashflow_battery_const = (-load_const + pv_const - batt_const) * ws_to_kwh * timestep * pv_feed
    cashflow_const = cashflow_battery_const - cashflow_base_const
    expected_result = np.array([cashflow_const * n/years] * years)
    # expected_result[-1] = expected_result[-1] - cashflow_const

    # build configs for testing
    gen_sim_config = create_general_config()
    economic_config = create_economic_analysis_config()

    # create data for testing
    energy_management_dict = {EnergyManagementState.TIME: time_test, EnergyManagementState.LOAD_POWER: load_power,
                              EnergyManagementState.PV_POWER: pv_power}
    energy_management_data = EnergyManagementData(gen_sim_config, pandas.DataFrame(energy_management_dict))
    system_dict = {SystemState.TIME: time_test, SystemState.AC_POWER_DELIVERED: battery_power}
    system_data = SystemData(gen_sim_config, pandas.DataFrame(system_dict))

    # get results
    self_consumption_increase_rev_stream = EnergyCostReduction(energy_management_data, system_data, economic_config)
    result1 = self_consumption_increase_rev_stream.get_cashflow()
    assert list(result1.round(0)) == list(expected_result.round(0))