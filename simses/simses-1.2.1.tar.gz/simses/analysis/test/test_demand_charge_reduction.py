import datetime
from configparser import ConfigParser

import numpy as np
import pandas
import pytest
import pytz

from simses.analysis.data.energy_management import EnergyManagementData
from simses.analysis.data.system import SystemData
from simses.analysis.evaluation.economic.revenue_stream.demand_charge_reduction import DemandChargeReduction
from simses.commons.config.analysis.economic import EconomicAnalysisConfig
from simses.commons.config.simulation.general import GeneralSimulationConfig

# fixed input parameters
from simses.commons.state.energy_management import EnergyManagementState
from simses.commons.state.system import SystemState

yearstart = 2020
yearend = 2025
timestep = 900
demand_charge_price = 120
demand_charge_intervall = 900
load_const = 4000
pv_const = 2000


def create_general_config() -> GeneralSimulationConfig:
    simulation_config: ConfigParser = ConfigParser()
    simulation_config.add_section('GENERAL')
    simulation_config.set('GENERAL', 'TIME_STEP', str(timestep))
    return GeneralSimulationConfig(simulation_config)


def create_economic_analysis_config(billing_cycle) -> EconomicAnalysisConfig:
    analysis_config: ConfigParser = ConfigParser()
    analysis_config.add_section('ECONOMIC_ANALYSIS')
    analysis_config.set('ECONOMIC_ANALYSIS', 'DEMAND_CHARGE_BILLING_PERIOD', str(billing_cycle))
    analysis_config.set('ECONOMIC_ANALYSIS', 'DEMAND_CHARGE_AVERAGE_INTERVAL', str(demand_charge_intervall))
    analysis_config.set('ECONOMIC_ANALYSIS', 'DEMAND_CHARGE_PRICE', str(demand_charge_price))
    return EconomicAnalysisConfig(analysis_config)


@pytest.mark.parametrize('billing_cycle, batt_const',
                          [
                              (DemandChargeReduction.BillingPeriod.MONTHLY, -2000),
                              (DemandChargeReduction.BillingPeriod.MONTHLY, 2000),
                              (DemandChargeReduction.BillingPeriod.YEARLY, -2000),
                              (DemandChargeReduction.BillingPeriod.YEARLY, 2000)
                          ]
                         )  # load convention is used for battery in SimSES
def test_demand_charge_reduction(billing_cycle, batt_const):
    """Performs a unit test by comparing the expected result for a generic
    time series with the actual result."""

    # set up test data
    years = yearend - yearstart
    dstart = datetime.datetime(yearstart, 1, 1, tzinfo=pytz.UTC).timestamp()
    dend = datetime.datetime(yearend, 1, 1, tzinfo=pytz.UTC).timestamp()
    n = int((dend - dstart) / timestep)
    time_test = pandas.array([dstart + timestep * i for i in range(n)])
    load_power = pandas.array([load_const] * n)
    pv_power = pandas.array([pv_const] * n)
    battery_power = pandas.array([batt_const] * n)

    # handle fractional years (leap years -> 1 project year + 1 day)
    years_actual = (dend - dstart) / (365 * 24 * 3600)
    years_fractional = years_actual - years

    # calculate expected result
    demand_charge_base = abs(load_const - pv_const) * demand_charge_price / 1000
    demand_charge_battery = abs(load_const - pv_const + batt_const) * demand_charge_price / 1000
    if billing_cycle == DemandChargeReduction.BillingPeriod.MONTHLY:
        demand_charge_base *= 12
        demand_charge_battery *= 12
    expected_result = np.array([demand_charge_base - demand_charge_battery] * years)
    if years_fractional > 0:
        expected_result = np.append(expected_result, (years_fractional * (demand_charge_base - demand_charge_battery)))

    # build configs for testing
    gen_sim_config = create_general_config()
    economic_config = create_economic_analysis_config(billing_cycle)

    # create data for testing
    energy_management_dict = {EnergyManagementState.TIME: time_test, EnergyManagementState.LOAD_POWER: load_power,
                              EnergyManagementState.PV_POWER: pv_power}
    energy_management_data = EnergyManagementData(gen_sim_config, pandas.DataFrame(energy_management_dict))
    system_dict = {SystemState.TIME: time_test, SystemState.AC_POWER_DELIVERED: battery_power}
    system_data = SystemData(gen_sim_config, pandas.DataFrame(system_dict))

    # get results
    self_demand_charge_rev_stream = DemandChargeReduction(energy_management_data, system_data, economic_config)
    result1 = self_demand_charge_rev_stream.get_cashflow()

    # Note: in leap years, the demand chargers calculated to project years will be lower
    # In that case, demand charges are spread over 366 days, but each project year only considers 365 days
    # Therefore this tests only checks if results is within +-5 of the exepected result
    expected_upper = expected_result * 1.05
    expected_lower = expected_result * 0.95
    assert list(abs(expected_upper.round(0))) >= list(abs(result1.round(0))) >= list(abs(expected_lower.round(0)))