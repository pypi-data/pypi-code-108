from configparser import ConfigParser
from datetime import datetime

import numpy as np
import pandas
import pytest

from simses.analysis.data.energy_management import EnergyManagementData
from simses.analysis.data.system import SystemData
from simses.analysis.evaluation.economic.revenue_stream.intraday_recharge import IntradayRechargeRevenue
from simses.commons.config.analysis.economic import EconomicAnalysisConfig
from simses.commons.config.simulation.general import GeneralSimulationConfig
# fixed input parameters
from simses.commons.state.energy_management import EnergyManagementState
from simses.commons.state.system import SystemState

idm_price = 0.3  # Euro per kWh
years = 5
timestep = 3600
unix_timestamp_start_2020 = 1577836800
n = int(years * 365 * 24 * 60 * 60 / timestep)
unix_timestamp_start_end = unix_timestamp_start_2020 + n*timestep


def create_general_config() -> GeneralSimulationConfig:
    simulation_config: ConfigParser = ConfigParser()
    simulation_config.add_section('GENERAL')
    simulation_config.set('GENERAL', 'TIME_STEP', str(timestep))
    simulation_config.set('GENERAL', 'START',
                          datetime.fromtimestamp(unix_timestamp_start_2020).strftime('%Y-%m-%d %H:%M:%S'))
    simulation_config.set('GENERAL', 'END',
                          datetime.fromtimestamp(unix_timestamp_start_end).strftime('%Y-%m-%d %H:%M:%S'))
    return GeneralSimulationConfig(simulation_config)


def create_economic_analysis_config() -> EconomicAnalysisConfig:
    analysis_config: ConfigParser = ConfigParser()
    analysis_config.add_section('ECONOMIC_ANALYSIS')
    analysis_config.set('ECONOMIC_ANALYSIS', 'IDM_PRICE', str(idm_price))
    analysis_config.set('ECONOMIC_ANALYSIS', 'IDM_USE_PRICE_TIMESERIES', 'False')
    return EconomicAnalysisConfig(analysis_config)


@pytest.mark.parametrize('idm_power_const', [-1e6, 1e6])
def test_intraday_recharge_revenue_stream(idm_power_const):
    """Performs a unit test by comparing the expected result for a generic
    time series with the actual result."""

    # set up test data
    time_test = pandas.array([unix_timestamp_start_2020 + timestep * i for i in range(n)])
    idm_power = pandas.array([idm_power_const] * n)
    battery_power = pandas.array([0] * n)

    # calculate expected result:
    expected_result = -1.0 * np.array([idm_power_const/1000 * 365 * 24 * idm_price] * years)

    # build configs for testing
    gen_sim_config = create_general_config()
    economic_config = create_economic_analysis_config()
    market_profile_config = None

    # create data for testing
    energy_management_dict = {EnergyManagementState.TIME: time_test, EnergyManagementState.IDM_POWER: idm_power}
    energy_management_data = EnergyManagementData(gen_sim_config, pandas.DataFrame(energy_management_dict))
    system_dict = {SystemState.TIME: time_test, SystemState.AC_POWER_DELIVERED: battery_power}
    system_data = SystemData(gen_sim_config, pandas.DataFrame(system_dict))

    idm_revenue_stream = IntradayRechargeRevenue(energy_management_data, system_data, economic_config,
                                                 gen_sim_config, market_profile_config)
    result1 = idm_revenue_stream.get_cashflow()
    assert list(result1.round(0)) == list(expected_result.round(0))
