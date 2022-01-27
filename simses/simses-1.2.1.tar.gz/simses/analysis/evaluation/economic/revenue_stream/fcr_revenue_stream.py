import numpy

from simses.analysis.data.energy_management import EnergyManagementData
from simses.analysis.data.system import SystemData
from simses.analysis.evaluation.economic.revenue_stream.abstract_revenue_stream import RevenueStream
from simses.analysis.evaluation.result import EvaluationResult, Unit, Description
from simses.commons.config.analysis.economic import EconomicAnalysisConfig
from simses.commons.config.analysis.market import MarketProfileConfig
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.log import Logger
from simses.commons.profile.economic.constant import ConstantPrice
from simses.commons.profile.economic.fcr import FcrMarketProfile
from simses.commons.profile.economic.market import MarketProfile


class FCRRevenue(RevenueStream):

    def __init__(self, energy_management_data: EnergyManagementData, system_data: SystemData,
                 economic_analysis_config: EconomicAnalysisConfig, general_config: GeneralSimulationConfig,
                 market_profile_config: MarketProfileConfig):
        super().__init__(energy_management_data, system_data, economic_analysis_config)
        self.__log: Logger = Logger(type(self).__name__)
        if economic_analysis_config.fcr_use_price_timeseries:
            self.__fcr_price_profile: MarketProfile = FcrMarketProfile(general_config, market_profile_config)
        else:
            self.__fcr_price_profile: MarketProfile = ConstantPrice(economic_analysis_config.fcr_price)
        self._energy_management_data: EnergyManagementData = energy_management_data
        self.__system_data: SystemData = system_data
        self.__fcr_power_avg = numpy.array([])
        self.__fcr_price_avg = numpy.array([])
        self.__fcr_revenue = numpy.array([])
        self.day_to_sec = 60 * 60 * 24
        self.year_to_sec = self.day_to_sec * 365

        self.__simulation_start = general_config.start
        self.__simulation_end = general_config.end

    def get_cashflow(self) -> numpy.ndarray:
        time = self._energy_management_data.time
        fcr_power = abs(self._energy_management_data.fcr_max_power)
        t = 0
        t_year_start = 0
        cashflow_fcr = 0
        fcr_power_annual_avg = []
        fcr_price_annual_avg = []
        fcr_price_list = []
        cashflow_list_fcr = []
        fcr_price_scaling_factor_day_to_second = 1 / 1e3 * 1 / self.day_to_sec
        delta_ts = time[1] - time[0]
        start = self.__simulation_start
        end = self.__simulation_end
        loop = 0
        t_loop = 0

        while t < len(time):
            # calculate adapted time for looped simulations
            if (time[t] - start) // (end - start) > loop:
                loop += 1
                t_loop = t
                self.__fcr_price_profile.initialize_profile()
            adapted_time = time[t] - (time[t_loop] - time[0])
            price = self.__fcr_price_profile.next(adapted_time)
            fcr_price_list.append(price)
            if time[t] - time[t_year_start] >= self.year_to_sec:
                fcr_power_annual_avg.append(sum(fcr_power[t_year_start:t]) / (t - t_year_start + 1))
                fcr_price_annual_avg.append(sum(fcr_price_list[t_year_start:t]) / (t - t_year_start + 1))
                cashflow_list_fcr.append(cashflow_fcr)
                t_year_start = t
                cashflow_fcr = 0
            cashflow_fcr += delta_ts * fcr_power[t] * price * fcr_price_scaling_factor_day_to_second
            t += 1
                
        # Adding non-full year
        year_length: float = t - t_year_start - 1
        if year_length > 0.0:
            fcr_power_annual_avg.append(sum(fcr_power[t_year_start:t]) / year_length)
            fcr_price_annual_avg.append(sum(fcr_price_list[t_year_start:t]) / year_length)
        cashflow_list_fcr.append(cashflow_fcr)

        self.__fcr_power_avg = numpy.array(fcr_power_annual_avg)
        self.__fcr_price_avg = numpy.array(fcr_price_annual_avg)
        self.__fcr_revenue = numpy.array(cashflow_list_fcr)
        return numpy.array(cashflow_list_fcr)

    def get_evaluation_results(self) -> [EvaluationResult]:
        key_results: [EvaluationResult] = list()
        key_results.append(EvaluationResult(Description.Economical.FCR.REVENUE_YEARLY, Unit.EURO, self.__fcr_revenue))
        return key_results

    def get_assumptions(self) -> [EvaluationResult]:
        assumptions: [EvaluationResult] = list()
        assumptions.append(EvaluationResult(Description.Economical.FCR.PRICE_AVERAGE, Unit.EURO_PER_KW_DAY, self.__fcr_price_avg))
        assumptions.append(EvaluationResult(Description.Economical.FCR.POWER_BID_AVERAGE, Unit.KILOWATT, self.__fcr_power_avg / 1000.0))
        return assumptions

    def close(self):
        self.__log.close()
