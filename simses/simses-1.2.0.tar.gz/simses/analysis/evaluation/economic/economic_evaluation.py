from datetime import datetime

import numpy
import numpy_financial

from simses.analysis.data.system import SystemData
from simses.analysis.evaluation.abstract_evaluation import Evaluation
from simses.analysis.evaluation.economic.revenue_stream.abstract_revenue_stream import RevenueStream
from simses.analysis.evaluation.result import EvaluationResult, Description, Unit
from simses.commons.config.analysis.economic import EconomicAnalysisConfig
from simses.commons.config.analysis.general import GeneralAnalysisConfig
from simses.commons.config.simulation.system import StorageSystemConfig
from simses.commons.log import Logger
from simses.commons.utils.utilities import format_float


class EconomicEvaluation(Evaluation):
    """
    Performs an economic evaluation by iterating through the respective RevenueStreams. Calculates key KPIs such as
     internal rate of return (IRR), net present value (NPV), etc..
    """

    def __init__(self, system_data: SystemData, economic_analysis_config: EconomicAnalysisConfig,
                 revenue_streams: [RevenueStream], config: GeneralAnalysisConfig,
                 storage_system_config: StorageSystemConfig):
        super().__init__(system_data, config, config.economical_analysis)
        self.__log: Logger = Logger(type(self).__name__)
        self.__config: GeneralAnalysisConfig = config
        self.__revenue_streams = revenue_streams
        self.__discount_rate = economic_analysis_config.discount_rate
        if economic_analysis_config.use_specific_costs:
            energy_costs: float = economic_analysis_config.specific_investment_costs_energy
            power_costs: float = economic_analysis_config.specific_investment_costs_power
            energy: float = system_data.initial_capacity / system_data.initial_state_of_health
            # TODO Review: Remove interdependence with StorageSystemConfig
            power: float = sum([float(storage_system_ac[StorageSystemConfig.AC_SYSTEM_POWER])
                                for storage_system_ac in storage_system_config.storage_systems_ac]) * 1e-3
            self.__investment_costs = energy_costs * energy + power_costs * power
        else:
            self.__investment_costs = economic_analysis_config.investment_costs
        # TODO clarify if this is the right way for coping with investment costs
        for stream in self.__revenue_streams:
            stream.set_investment_cost(self.__investment_costs)

    def evaluate(self):
        if self.__revenue_streams:
            # Calculate cashflow
            future_cashflow: numpy.ndarray = numpy.array([])
            for revenue_stream in self.__revenue_streams:
                cashflow: numpy.ndarray = revenue_stream.get_cashflow()
                self.extend_results(revenue_stream.get_evaluation_results())
                # get the right array size based on first incoming cash flow
                if not future_cashflow.size:
                    future_cashflow.resize(cashflow.shape, refcheck=False)
                # add cashflow and correct potential size issues for leap years
                if len(future_cashflow) < len(cashflow):
                    self.__log.warn('Cashflow arrays have different lengths.')
                future_cashflow[:len(cashflow)] += cashflow
            # Compile list of results
            self.append_result(EvaluationResult(Description.Economical.INVESTMENT_COSTS, Unit.EURO,
                                                self.__investment_costs))
            self.append_result(EvaluationResult(Description.Economical.CASHFLOW, Unit.EURO, future_cashflow))
            self.append_result(EvaluationResult(Description.Economical.NET_PRESENT_VALUE, Unit.EURO,
                                                self.__net_present_value(future_cashflow)))
            self.append_result(EvaluationResult(Description.Economical.INTERNAL_RATE_OF_RETURN, Unit.PERCENTAGE,
                                                self.__internal_rate_of_return(future_cashflow) * 100))
            self.append_result(EvaluationResult(Description.Economical.PROFITABILITY_INDEX, Unit.NONE,
                                                self.__profitability_index(future_cashflow)))
            self.append_result(EvaluationResult(Description.Economical.RETURN_ON_INVEST, Unit.NONE,
                                                self.__return_on_investment(future_cashflow)))
            self.append_result(EvaluationResult(Description.Economical.LEVELIZED_COST_OF_STORAGE, Unit.EURO_PER_MWH,
                                                self.__levelized_cost_of_storage_energy()))
            self.print_results()

    def plot(self) -> None:
        pass

    def __internal_rate_of_return(self, cashflow: numpy.ndarray) -> float:
        cashflow = numpy.append(numpy.array([-self.__investment_costs]), cashflow)
        if numpy.any(numpy.isnan(cashflow)) or numpy.any(numpy.isinf(cashflow)):
            self.__log.error('NaN in cashflow, IRR calculation cannot be performed: ' + str(cashflow))
            return 0
        return numpy_financial.irr(cashflow)

    def __net_present_value(self, revenue: numpy.ndarray) -> float:
        return self.__npv(self.__investment_costs, revenue, self.__discount_rate)

    def __profitability_index(self, revenue: numpy.ndarray) -> float:
        return self.__npv(0, revenue, self.__discount_rate) / self.__investment_costs

    def __return_on_investment(self, revenue: numpy.ndarray) -> float:
        return self.__net_present_value(revenue) / self.__investment_costs

    def __levelized_cost_of_storage_energy(self) -> float:
        energy: numpy.ndarray = self.get_data().discharge_energy_per_year / 1000.0  # conversion to MWh
        energy_per_year: float = self.__npv(0, energy, self.__discount_rate)
        if energy_per_year:
            # TODO include further (discounted) costs for LCOS
            return self.__investment_costs / energy_per_year
        else:
            return numpy.nan

    @staticmethod
    def __npv(invest: float, cashflow: numpy.ndarray, discount_rate: float) -> float:
        cashflow = numpy.append(numpy.array([-invest]), cashflow)
        return numpy_financial.npv(discount_rate, cashflow)

    def __get_assumptions(self) -> list:
        assumptions: list = list()
        assumptions.append(EvaluationResult(Description.Economical.INVESTMENT_COSTS, Unit.EURO, self.__investment_costs))
        assumptions.append(EvaluationResult(Description.Economical.DISCOUNT_RATE, Unit.PERCENTAGE, self.__discount_rate * 100))
        for revenue_stream in self.__revenue_streams:
            assumptions.extend(revenue_stream.get_assumptions())
        return assumptions

    def print_results(self):
        if not self._print_to_console:
            return
        print('\n\n[ECONOMIC ANALYSIS]:')
        print('ASSUMPTIONS:')
        for assumption in self.__get_assumptions():
            print(assumption.to_console())
        print('\nRESULTS:')
        for evaluation_result in self.evaluation_results:
            print(evaluation_result.to_console())
        self.__print_warning()

    def __print_warning(self):
        time: numpy.ndarray = self.get_data().time
        start: float = time[0]
        end: float = time[-1]
        duration: float = end - start
        date = datetime.fromtimestamp(start)
        year_end: float = date.replace(year=date.year + 1).timestamp()
        year: float = year_end - start
        if duration < year:
            print('Note: Simuation time is less than one year (' + format_float(duration / year) +
                  ' a). Results only cover the simulation time.')

    def close(self) -> None:
        self.__log.close()
        for revenue_stream in self.__revenue_streams:
            revenue_stream.close()
