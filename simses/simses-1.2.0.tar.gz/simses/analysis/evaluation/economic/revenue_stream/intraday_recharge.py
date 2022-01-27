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
from simses.commons.profile.economic.intraday import IntradayMarketProfile
from simses.commons.profile.economic.market import MarketProfile


class IntradayRechargeRevenue(RevenueStream):
    def __init__(self, energy_management_data: EnergyManagementData, system_data: SystemData,
                 economic_analysis_config: EconomicAnalysisConfig, general_config: GeneralSimulationConfig,
                 market_profile_config: MarketProfileConfig):
        super().__init__(energy_management_data, system_data, economic_analysis_config)
        self.__log: Logger = Logger(type(self).__name__)
        if economic_analysis_config.idm_use_price_timeseries:
            self.__idm_price_profile: MarketProfile = IntradayMarketProfile(general_config, market_profile_config)
        else:
            self.__idm_price_profile: MarketProfile = ConstantPrice(economic_analysis_config.idm_price)
        self.__time = energy_management_data.time
        self.__intraday_power = energy_management_data.idm_power
        self.__system_data: SystemData = system_data
        self.__intraday_power_avg = []
        self.__intraday_price_avg = []
        self.__intraday_revenue = []
        self.hour_to_sec = 60 * 60
        self.day_to_sec = self.hour_to_sec * 24
        self.year_to_sec = self.day_to_sec * 365
        self.__simulation_start = general_config.start
        self.__simulation_end = general_config.end

    def get_cashflow(self) -> numpy.ndarray:

        time = self.__time
        intraday_power = self.__intraday_power
        t = 0
        t_year_start = 0
        cashflow = 0
        intraday_power_annual_avg = []
        intraday_price_annual_avg = []
        cashflow_list_intraday = []
        intraday_price_list = []
        intraday_price_scaling_factor = 1/1e3 * 1/self.hour_to_sec
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
                self.__idm_price_profile.initialize_profile()
            adapted_time = time[t] - (time[t_loop] - time[0])
            price = self.__idm_price_profile.next(adapted_time)
            intraday_price_list.append(price)
            if time[t] - time[t_year_start] >= self.year_to_sec:
                intraday_power_annual_avg.append(sum(intraday_power[t_year_start:t]) / (t - t_year_start + 1))
                intraday_price_annual_avg.append(sum(intraday_price_list[t_year_start:t]) / (t - t_year_start + 1))
                cashflow_list_intraday.append(cashflow)
                t_year_start = t
                cashflow = 0
            cashflow -= delta_ts * intraday_power[t] * price * intraday_price_scaling_factor
            t += 1

        # Adding non-full year
        intraday_power_annual_avg.append(sum(intraday_power[t_year_start:t]) / (t - t_year_start + 1))
        intraday_price_annual_avg.append(sum(intraday_price_list[t_year_start:t]) / (t - t_year_start + 1))
        cashflow_list_intraday.append(cashflow)

        intraday_power_annual_avg_kW = [i / 1000 for i in intraday_power_annual_avg] # in kW
        self.__intraday_power_avg = intraday_power_annual_avg_kW
        self.__intraday_price_avg = intraday_price_annual_avg
        self.__intraday_revenue = cashflow_list_intraday

        return numpy.array(cashflow_list_intraday)

    def get_evaluation_results(self) -> [EvaluationResult]:
        key_results: [EvaluationResult] = list()
        key_results.append(EvaluationResult(Description.Economical.Intraday.REVENUE_YEARLY, Unit.EURO, self.__intraday_revenue))
        return key_results

    def get_assumptions(self) -> [EvaluationResult]:
        assumptions: [EvaluationResult] = list()
        assumptions.append(EvaluationResult(Description.Economical.Intraday.PRICE_AVERAGE, Unit.EURO_PER_KWH, self.__intraday_price_avg))
        assumptions.append(EvaluationResult(Description.Economical.Intraday.POWER_AVERAGE, Unit.KILOWATT, self.__intraday_power_avg))
        return assumptions

    def close(self):
        self.__log.close()
