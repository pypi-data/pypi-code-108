import math
from datetime import datetime, timedelta

import numpy
from pytz import timezone

from simses.analysis.data.energy_management import EnergyManagementData
from simses.analysis.data.system import SystemData
from simses.analysis.evaluation.economic.revenue_stream.abstract_revenue_stream import RevenueStream
from simses.analysis.evaluation.result import EvaluationResult, Description, Unit
from simses.analysis.utils import get_fractional_years
from simses.commons.config.analysis.economic import EconomicAnalysisConfig


class OperationAndMaintenanceRevenue(RevenueStream):

    """ Calculates the yearly costs due to maintenance and operation of the storage technology"""

    __UTC: timezone = timezone('UTC')
    __BERLIN: timezone = timezone('Europe/Berlin')

    def __init__(self, energy_management_data: EnergyManagementData, system_data: SystemData, economic_analysis_config: EconomicAnalysisConfig):
        super().__init__(energy_management_data, system_data, economic_analysis_config)
        self.__annual_relative_o_and_m_costs = economic_analysis_config.annual_realative_o_and_m_costs  # p.u.
        self.__cashflow_list = []
        self.__shorter_than_one_year = True
        #self.__annual_absolut_o_and_m_costs = self.__annual_relative_o_and_m_costs * self._investment_cost  # EUR
        # self.__investment_cost = self._investment_cost

    def get_cashflow(self) -> numpy.ndarray:
        annual_absolute_o_and_m_cost = self.__annual_relative_o_and_m_costs * self._investment_cost
        time = self._energy_management_data.time  # UTC+0

        om_cost_per_timestep = annual_absolute_o_and_m_cost / self._seconds_per_year * (time[1] - time[0])
        om_cost_time_series = [(-1) * om_cost_per_timestep] * len(time)

        # create cashflow list for each project year
        self.__cashflow_list = self.cash_time_series_to_project_years(om_cost_time_series, time)
        return numpy.array(self.__cashflow_list)

    def get_evaluation_results(self) -> [EvaluationResult]:
        key_results: [EvaluationResult] = list()
        key_results.append(EvaluationResult(Description.Economical.OperationAndMaintenance.O_AND_M_COST,
                                            Unit.EURO, [-1 * i for i in self.__cashflow_list]))
        return key_results

    def get_assumptions(self) -> [EvaluationResult]:
        assumptions: [EvaluationResult] = list()
        assumptions.append(EvaluationResult(Description.Economical.OperationAndMaintenance.ANNUAl_O_AND_M_COST,
                                            Unit.EURO, self.__annual_relative_o_and_m_costs * self._investment_cost))
        return assumptions

    def close(self):
        pass

