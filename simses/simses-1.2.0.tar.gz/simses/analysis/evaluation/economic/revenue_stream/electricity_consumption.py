from datetime import datetime

import numpy
from pytz import timezone

from simses.analysis.data.energy_management import EnergyManagementData
from simses.analysis.data.system import SystemData
from simses.analysis.evaluation.economic.revenue_stream.abstract_revenue_stream import RevenueStream
from simses.analysis.evaluation.result import EvaluationResult, Description, Unit
from simses.commons.config.analysis.economic import EconomicAnalysisConfig


class ElectricityConsumptionRevenueStream(RevenueStream):

    """" Calculates the yearly costs for electrictiy consumption for electrolyzer"""

    __UTC: timezone = timezone('UTC')
    __BERLIN: timezone = timezone('Europe/Berlin')

    def __init__(self, energy_management_data: EnergyManagementData, system_data: SystemData, economic_analysis_config: EconomicAnalysisConfig):
        super().__init__(energy_management_data, system_data, economic_analysis_config)
        self.__electricity_price_grid = economic_analysis_config.electricity_price
        self.__electricity_price_renewable = economic_analysis_config.renewable_electricity_price
        self.__cashflow_list = []
        self.__gird_cost_list = []
        self.__renewable_cost_list = []
        self.__Ws_to_kWh = 1/1000 * 1/3600
        self.__shorter_than_one_year = True

    def get_cashflow(self) -> numpy.ndarray:
        time: numpy.ndarray = self._energy_management_data.time
        timestep = time[1] - time[0]
        total_power_system: numpy.ndarray = self._system_data.power
        renewable_power_total: numpy.ndarray = self._energy_management_data.pv_power
        grid_power = total_power_system - renewable_power_total
        renewable_power_used = numpy.add(renewable_power_total, grid_power.clip(max=0))

        cost_renewable_energy_per_timestep = numpy.asarray([power * self.__electricity_price_renewable if power >= 0
                                                            else 0 for power in renewable_power_used]) * timestep * self.__Ws_to_kWh
        cost_grid_power_per_timestep = numpy.asarray([power * self.__electricity_price_grid if power >= 0 else 0 for
                                                      power in grid_power]) * timestep * self.__Ws_to_kWh

        start: float = time[0]  # UTC
        billing_year_date = datetime.fromtimestamp(start, tz=self.__BERLIN)
        billing_year_date = self.__get_next_billing_year(billing_year_date)
        billing_year_end: float = billing_year_date.timestamp()  # UTC
        start_year_idx = int(numpy.where(time == start)[0])
        if time[-1] < billing_year_end:
            billing_year_end = time[-1]
            self.__shorter_than_one_year = True
        else:
            self.__shorter_than_one_year = False
        end_year_idx = int(numpy.where(time == billing_year_end)[0])
        # iterate through whole simulationtime and add annual costs to array
        if self.__shorter_than_one_year == False:
            for t in time: # UTC + 0
                if t >= billing_year_end:
                    self.__gird_cost_list.append(- sum(cost_grid_power_per_timestep[start_year_idx:end_year_idx+1]))
                    self.__renewable_cost_list.append(- sum(cost_renewable_energy_per_timestep[start_year_idx:end_year_idx+1]))
                    self.__cashflow_list.append(- sum(cost_renewable_energy_per_timestep[start_year_idx:end_year_idx+1])
                                                - sum(cost_grid_power_per_timestep[start_year_idx:end_year_idx+1]))
                    billing_year_start = billing_year_end
                    start_year_idx = int(end_year_idx)
                    billing_year_date = self.__get_next_billing_year(billing_year_date)
                    billing_year_end = billing_year_date.timestamp()
                    if time[-1] < billing_year_end:
                        billing_year_end = time[-1]
                    end_year_idx = int(numpy.where(time == billing_year_end)[0])
        # add remaining costs for the last billing year
        else:
            self.__gird_cost_list.append(- sum(cost_grid_power_per_timestep[start_year_idx:-1]))
            self.__renewable_cost_list.append(- sum(cost_renewable_energy_per_timestep[start_year_idx:-1]))
            self.__cashflow_list.append(- sum(cost_renewable_energy_per_timestep[start_year_idx:-1]) -
                                        sum(cost_grid_power_per_timestep[start_year_idx:-1]))
        return numpy.array(self.__cashflow_list)

    def __get_next_billing_year(self, date: datetime) -> datetime:
        """Returns begin of following year 20xx-01-01 00:00:00"""
        return date.replace(year=date.year+1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

    def get_evaluation_results(self) -> [EvaluationResult]:
        key_results: [EvaluationResult] = list()
        key_results.append(EvaluationResult(Description.Economical.ElectricityConsumption.ELECTRICITY_COST_GRID,
                                            Unit.EURO, sum(self.__gird_cost_list)))
        key_results.append(EvaluationResult(Description.Economical.ElectricityConsumption.ELECTRICITY_COST_RENEWABLE,
                                            Unit.EURO, sum(self.__renewable_cost_list)))
        key_results.append(EvaluationResult(Description.Economical.ElectricityConsumption.TOTAL_ELECTRICITY_COST,
                                            Unit.EURO, sum(self.__cashflow_list)))
        return key_results

    def get_assumptions(self) -> [EvaluationResult]:
        assumptions: [EvaluationResult] = list()
        assumptions.append(EvaluationResult(Description.Economical.ElectricityConsumption.ELECTRICITY_COST_RENEWABLE,
                                            Unit.EURO_PER_KWH, self.__electricity_price_renewable))
        assumptions.append(EvaluationResult(Description.Economical.ElectricityConsumption.ELECTRICITY_COST_GRID,
                                            Unit.EURO_PER_KWH, self.__electricity_price_grid))
        return assumptions


    def close(self):
        pass