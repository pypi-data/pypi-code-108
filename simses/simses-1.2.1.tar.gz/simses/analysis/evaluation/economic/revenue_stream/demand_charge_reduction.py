from datetime import datetime

import numpy
import pytz

from simses.analysis.data.energy_management import EnergyManagementData
from simses.analysis.data.system import SystemData
from simses.analysis.evaluation.economic.revenue_stream.abstract_revenue_stream import RevenueStream
from simses.analysis.evaluation.result import EvaluationResult, Unit, Description
from simses.analysis.utils import get_fractional_years
from simses.commons.config.analysis.economic import EconomicAnalysisConfig
from simses.commons.log import Logger
from simses.commons.utils.utilities import add_month_to, add_year_to, get_average_from, get_maximum_from


class DemandChargeReduction(RevenueStream):

    class BillingPeriod:
        MONTHLY: str = 'monthly'
        YEARLY: str = 'yearly'
        OPTIONS: [str] = [MONTHLY, YEARLY]

    def __init__(self, energy_management_data: EnergyManagementData, system_data: SystemData,
                 economic_analysis_config: EconomicAnalysisConfig):
        super().__init__(energy_management_data, system_data, economic_analysis_config)
        self.__log: Logger = Logger(type(self).__name__)
        self.__billing_period = economic_analysis_config.demand_charge_billing_period
        self.__demand_charge = economic_analysis_config.demand_charge_price
        self.__demand_charge_average_interval = economic_analysis_config.demand_charge_average_interval
        self.__key_results: [EvaluationResult] = list()
        self.__seconds_per_year = 24 * 60 * 60 * 365
        if self.__billing_period not in self.BillingPeriod.OPTIONS:
            raise Exception('Please configure demand charge billing period to one of the following options: ' +
                            str(self.BillingPeriod.OPTIONS) + '. The current billing cycle is set to ' +
                            str(self.__billing_period) + '.')

    def __get_demand_charge_in_billing_period_for(self, time: numpy.ndarray, power: numpy.ndarray) \
            -> ([float], [datetime]):
        """
         Calculate demand charge based on absolute power values in each billing periods and detemrine billing periods.
         Here, demand charges are not scaled yet:
         If only one day is in the billing period, the full demand charge will apply

        Parameters
        ----------
        time :
            series of unix time stamps as numpy array
        power:
            series of site power values as numpy array

        Returns
        -------
        list of float
            List of float, representing demand charges in each billing period
        list of datetime
            List of datetime, representing beginning and end of each billing period
        """
        power_time_series: numpy.ndarray = numpy.column_stack([time, abs(power)])
        billing_periods: list = list()
        # determine start and end of first billing period in unix timestamps
        billing_period_start: float = self.__get_initial_billing_period_for(time[0]).timestamp()
        billing_periods.append(datetime.fromtimestamp(billing_period_start, tz=pytz.UTC))
        billing_period_end: float = self.__get_next_billing_period(billing_period_start).timestamp()

        # determine interval end of first interval for averging power values (e.g. 15min in Germany)
        interval_end = time[0] - time[0] % self.__demand_charge_average_interval + self.__demand_charge_average_interval

        # initialise lists
        power_interval: list = list()
        power_avg_in_interval: list = list()
        power_max_for_billing_period: list = list()
        for tstmp, value in power_time_series:
            power_interval.append(value)
            if tstmp >= interval_end:  # get average power values for demand charge interval
                power_avg_in_interval.append(get_average_from(power_interval))
                power_interval.clear()
                interval_end += self.__demand_charge_average_interval
            if tstmp >= billing_period_end:  # get maximum power values for billing period
                # scale values accordingly to days that have passed in the respective billing period
                power_max_for_billing_period.append(get_maximum_from(power_avg_in_interval))
                power_avg_in_interval.clear()
                billing_periods.append(datetime.fromtimestamp(billing_period_end, tz=pytz.UTC))
                billing_period_start = billing_period_end
                billing_period_end = self.__get_next_billing_period(billing_period_start).timestamp()
        # add remaining values
        power_avg_in_interval.append(get_average_from(power_interval))
        power_max_for_billing_period.append(get_maximum_from(power_avg_in_interval))
        # add end of last billing period
        billing_periods.append(datetime.fromtimestamp(billing_period_end, tz=pytz.UTC))
        # convert maximum power values into demand charge
        return list(numpy.array(power_max_for_billing_period) * self.__demand_charge / 1000.0), billing_periods

    @staticmethod
    def __get_cashflow_time_series(time: [float], demand_charges: [float], billing_periods: [datetime]) -> [float]:
        """
         Turns list of billing periods and demand charges for each billing period into a
         list of cashflow values for each timestep.

        Parameters
        ----------
        time :
            series of unix time stamps as list of float
        demand_charges:
            series of demand_charges as list of float
        billing_periods:
            series of billing periods as list of datetime

        Returns
        -------
        list of float
            List of float, representing demand charges for each timestep
        """
        cashflow_list = list()
        i = 0  # counter for current billing period
        delta_t = time[1] - time[0]
        start_period = billing_periods[i].timestamp()
        end_period = billing_periods[i+1].timestamp()
        for t in time:
            if t > end_period:
                i += 1
                start_period = billing_periods[i].timestamp()
                end_period = billing_periods[i + 1].timestamp()
            cashflow = delta_t / (end_period - start_period) * demand_charges[i]
            cashflow_list.append(cashflow)
        return cashflow_list

    def __get_initial_billing_period_for(self, tstmp: float) -> datetime:
        date = datetime.fromtimestamp(tstmp, tz=pytz.UTC)
        # start of month
        date = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if self.__billing_period == self.BillingPeriod.YEARLY:
            # start of year
            date = date.replace(month=1)
        return date

    def __get_next_billing_period(self, tstmp: float) -> datetime:
        date = datetime.fromtimestamp(tstmp, tz=pytz.UTC)
        if self.__billing_period == self.BillingPeriod.MONTHLY:
            date = add_month_to(date)
        else:  # self.__billing_period == self.BillingPeriod.YEARLY
            date = add_year_to(date)
        return date

    def __print_warning(self):
        time = self._energy_management_data.time
        if time[1] - time[0] > self.__demand_charge_average_interval:
            self.__log.warn('Simulation timestep is larger than DEMAND_CHARGE_AVERAGE_INTERVAL (' +
                             str(self.__demand_charge_average_interval) + ' sec). Economic evaluation for peak shaving '
                                                                          'may not be representative.')

    def get_cashflow(self) -> numpy.ndarray:
        self.__print_warning()
        # get data for calculation
        time: numpy.ndarray = self._energy_management_data.time
        load_power: numpy.ndarray = self._energy_management_data.load_power
        pv_power: numpy.ndarray = self._energy_management_data.pv_power
        storage_power: numpy.ndarray = self._system_data.power
        # calculate power arrays
        grid_power_base: numpy.ndarray = load_power - pv_power
        grid_power_storage: numpy.ndarray = load_power - pv_power + storage_power

        # calculate demand charge in each billing period
        demand_charge_base, billing_periods = self.__get_demand_charge_in_billing_period_for(time, grid_power_base)
        demand_charge_storage, billing_periods = self.__get_demand_charge_in_billing_period_for(time, grid_power_storage)

        # turn into time series
        demand_charge_base_ts = self.__get_cashflow_time_series(list(time), demand_charge_base, billing_periods)
        demand_charge_storage_ts = self.__get_cashflow_time_series(list(time), demand_charge_storage, billing_periods)

        # calculate in project years
        demand_charge_per_year_base = self.cash_time_series_to_project_years(demand_charge_base_ts, time)
        demand_charge_per_year_storage = self.cash_time_series_to_project_years(demand_charge_storage_ts, time)

        # append demand charges to key results
        self.__key_results.append(EvaluationResult(Description.Economical.DemandCharges.COST_WITHOUT_STORAGE,
                                                   Unit.EURO, demand_charge_per_year_base))
        self.__key_results.append(EvaluationResult(Description.Economical.DemandCharges.COST_WITH_STORAGE,
                                                   Unit.EURO, demand_charge_per_year_storage))
        # self.__key_results.append(
        #     EvaluationResult('Demand charges each billing period without storage', Unit.EURO, demand_charge_base))
        #  self.__key_results.append(
        #     EvaluationResult('Demand charges each billing period with storage', Unit.EURO, demand_charge_storage))
        revenue_nondiscounted = numpy.array(demand_charge_per_year_base) - numpy.array(demand_charge_per_year_storage)
        return revenue_nondiscounted

    def get_evaluation_results(self):
        return self.__key_results

    def get_assumptions(self):
        assumptions: [EvaluationResult] = list()
        assumptions.append(EvaluationResult(Description.Economical.DemandCharges.CYCLE, Unit.NONE,
                                            self.__billing_period))
        assumptions.append(EvaluationResult(Description.Economical.DemandCharges.PRICE, Unit.EURO_PER_KW,
                                            self.__demand_charge))
        assumptions.append(EvaluationResult(Description.Economical.DemandCharges.INTERVAL, Unit.MINUTES,
                                            self.__demand_charge_average_interval / 60.0))
        return assumptions

    def close(self):
        self.__log.close()
