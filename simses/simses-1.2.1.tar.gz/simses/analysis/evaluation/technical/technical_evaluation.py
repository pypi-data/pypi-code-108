import math
from datetime import datetime

import numpy
import numpy as np

from simses.analysis.data.abstract_data import Data
from simses.analysis.evaluation.abstract_evaluation import Evaluation
from simses.analysis.evaluation.result import EvaluationResult, Description, Unit
from simses.commons.config.analysis.general import GeneralAnalysisConfig
from simses.commons.log import Logger
from simses.commons.utils.utilities import format_float


class TechnicalEvaluation(Evaluation):

    """
    TechnicalEvaluation is a special evaluation class for calculating technical KPIs, e.g. efficiency.
    """

    def __init__(self, data: Data, config: GeneralAnalysisConfig):
        super().__init__(data, config, config.technical_analysis)
        self.__log: Logger = Logger(type(self).__name__)

    def evaluate(self) -> None:
        self.append_result(EvaluationResult(Description.Technical.ROUND_TRIP_EFFICIENCY, Unit.PERCENTAGE, self.round_trip_efficiency))
        self.append_result(EvaluationResult(Description.Technical.MEAN_SOC, Unit.PERCENTAGE, self.mean_soc))
        self.append_result(EvaluationResult(Description.Technical.MAX_SOC, Unit.PERCENTAGE, self.max_soc))
        self.append_result(EvaluationResult(Description.Technical.MIN_SOC, Unit.PERCENTAGE, self.min_soc))
        self.append_result(EvaluationResult(Description.Technical.NUMBER_CHANGES_SIGNS, Unit.NONE, self.changes_of_sign))
        self.append_result(EvaluationResult(Description.Technical.RESTING_TIME_AVG, Unit.MINUTES, self.resting_times))
        self.append_result(EvaluationResult(Description.Technical.ENERGY_CHANGES_SIGN, Unit.PERCENTAGE, self.energy_swapsign))
        self.append_result(EvaluationResult(Description.Technical.FULFILLMENT_AVG, Unit.PERCENTAGE, self.average_fulfillment))
        self.append_result(EvaluationResult(Description.Technical.REMAINING_CAPACITY, Unit.PERCENTAGE, self.capacity_remaining))
        self.append_result(EvaluationResult(Description.Technical.ENERGY_THROUGHPUT, Unit.KWH, self.energy_throughput))

    def plot(self) -> None:
        pass

    @property
    def round_trip_efficiency(self) -> float:

        """
        Calculates the round trip efficiency of the system/battery

        Parameters
        ----------
            data : simulation results

        Returns
        -------
        float:
            round trip efficiency
        """
        data: Data = self.get_data()
        discharged = data.discharge_energy
        charged = data.charge_energy
        difference = data.energy_difference

        # eta_ohne_anpassung = 100 * (data.discharge_energy + data.energy_difference) / data.charge_energy
        # eta_formel_genau = 100 * 0.5*((b*math.sqrt(4*a*c+b**2))/c**2 + 2*a/c + (b/c)**2)

        if charged > 0.0 and discharged > 0.0:
            # return 100 * (data.discharge_energy + data.energy_difference) / data.charge_energy
            efficiency = 100 * 0.5 * ((difference * math.sqrt(
                4 * discharged * charged + difference ** 2)) / charged ** 2 + 2 * discharged / charged + (
                                                  difference / charged) ** 2)
        elif charged > 0.0:
            efficiency = 100 * difference / charged
            self.__log.warn('The storage was only charged. Thus, only a one-way efficiency could be calculated')
        elif discharged > 0.0:
            efficiency = 100 * -difference / discharged
            self.__log.warn('The storage was only discharged. Thus, only a one-way efficiency could be calculated')
        else:
            efficiency = numpy.nan
            self.__log.warn('Storage was neither charged nor discharged. Efficiency could not be calculated.')
        if not 0.0 < efficiency <= 100.0:
            self.__log.warn(Description.Technical.ROUND_TRIP_EFFICIENCY + ' should be between 0 % and 100 %, but is ' +
                             format_float(efficiency) + ' %. Perhaps your simulation time range is too short for '
                                                             'calculating an accurate round trip efficiency.')
        return efficiency

    @property
    def capacity_remaining(self) -> float:
        data: Data = self.get_data()
        return data.state_of_health[-1] * 100.0

    @property
    def energy_throughput(self) -> float:
        data: Data = self.get_data()
        return data.charge_energy + data.discharge_energy

    @property
    def max_soc(self) -> [float]:
        """
        Calculates the max SOC of the system/battery

        Parameters
        ----------
            data : simulation results

        Returns
        -------
        float:
            average soc
        """
        data: Data = self.get_data()
        return data.max_soc * 100.

    @property
    def mean_soc(self) -> [float]:
        """
        Calculates the mean SOC of the system/battery

        Parameters
        ----------
            data : simulation results

        Returns
        -------
        float:
            average soc
        """
        data: Data = self.get_data()
        return 100 * data.average_soc

    @property
    def min_soc(self) -> [float]:
        """
        Calculates the min SOC of the system/battery

        Parameters
        ----------
            data : simulation results

        Returns
        -------
        float:
            average soc
        """
        data: Data = self.get_data()
        return data.min_soc * 100.0

    @property
    def equivalent_full_cycles(self) -> float:
        """
        Calculates the number of full-equivalent cycles by dividing the amount of charged energy through the initial capacity

        Parameters
        ----------
            data : simulation results

        Returns
        -------
        float:
            number of full-equivalent cycles
        """
        data: Data = self.get_data()
        return data.charge_energy / data.initial_capacity

    @property
    def depth_of_discharges(self) -> float:
        """
        Calculates the average depth of cycles in discharge direction

        Parameters
        ----------
            data : simulation results

        Returns
        -------
        float:
            average depth of cycles in discharge direction
        """
        data: Data = self.get_data()
        delta_soc = np.diff(data.soc)[abs(np.diff(data.soc)) > 1e-8]
        delta_soc_sign = np.sign(delta_soc)
        delta_soc_sign_diff = np.diff(delta_soc_sign)
        cycle_end = np.asarray(np.where(delta_soc_sign_diff != 0))
        cycle_start = cycle_end + 1
        cycle_start = np.insert(cycle_start, 0, 0)
        cycle_end = np.append(cycle_end, len(delta_soc) - 1)
        doc = np.asarray(
            [sum(delta_soc[cycle_start[counter]:cycle_end[counter] + 1]) for counter in range(0, len(cycle_start))])
        if len(doc) == 0:
            return 0
        if len(doc[doc < 0]) == 0:
            return 0
        doc_dis = abs(100 * doc[doc < 0].mean())
        return doc_dis

    @property
    def changes_of_sign(self) -> float:
        """
        Calculates the average number of changes of sign per day

        Parameters
        ----------
            data : simulation results

        Returns
        -------
        float:
            average number of changes of sign per day
        """
        data: Data = self.get_data()
        days_in_data = round(
            (datetime.fromtimestamp(data.time[-1]) - datetime.fromtimestamp(data.time[0])).total_seconds() / 86400)
        power_sign = np.sign(data.power)
        power_sign_nozero = power_sign[power_sign != 0]
        total_changes_of_sign = np.nansum(abs(np.diff(power_sign_nozero))) / 2
        if days_in_data > 0:
            daily_changes_of_sign = total_changes_of_sign / days_in_data
        else:
            daily_changes_of_sign = 'Less than one day simulated.'
        return daily_changes_of_sign

    @property
    def resting_times(self) -> float:
        """
        Calculates the average length of resting time of the system/battery

        Parameters
        ----------
            data : simulation results

        Returns
        -------
        float:
            average length of resting time in min
        """
        data: Data = self.get_data()
        resting_data = 1 * (abs(data.power) == 0)

        idx_begin = (np.diff(resting_data) > 0)
        idx_end = np.diff(resting_data) < 0
        if resting_data[0] == 1:
            idx_begin = np.insert(idx_begin, 0, True)
            idx_end = np.insert(idx_end, 0, False)
        if resting_data[-1] == True:
            idx_begin = np.append(idx_begin, False)
            idx_end = np.append(idx_end, True)
        times_length = np.where(idx_end)[0] - np.where(idx_begin)[0]
        timestep = data.time[1] - data.time[0]  # in seconds

        if len(times_length):
            resting_times_length = times_length.mean() * timestep / 60
        else:
            resting_times_length = 'Never in resting mode'

        return resting_times_length

    @property
    def energy_swapsign(self) -> float:
        """
        Calculates the average positive (charged) energy between changes of sign

        Parameters
        ----------
            data : simulation results

        Returns
        -------
        float:
            average charged energy between between changes of sign
        """
        data: Data = self.get_data()
        power_sign = np.sign(data.power)
        power = data.power
        timestep = data.time[1] - data.time[0]  # in seconds
        nom_capacity = data.initial_capacity

        pos_or_zero_value = np.where(power_sign >= 0)

        difference_greater_one = np.diff(pos_or_zero_value) !=1
        difference_greater_one = np.append(difference_greater_one[0], True) # append last pos. value
        last_pos_indexes = pos_or_zero_value[0][difference_greater_one]
        first_pos_indexes = pos_or_zero_value[0][np.roll(difference_greater_one,1)]

        sums_list = []

        for i in range(len(first_pos_indexes)):
            summed_energy = sum(power[first_pos_indexes[i]:last_pos_indexes[i] + 1]) * \
                            timestep / 3600 / 1000

            if summed_energy != 0:
                sums_list.append(summed_energy)

        if sums_list:
            pos_energy_swapsign_norm = np.mean(sums_list) / nom_capacity * 100  # in %
        else:
            pos_energy_swapsign_norm = 'No energy was charged'

        return pos_energy_swapsign_norm

    @property
    def average_fulfillment(self) -> float:
        """
        Calculates the average fulfillment factor of the system/battery. How often can the battery/system charge/discharge the desired amount of power.

        Parameters
        ----------
            data : simulation results

        Returns
        -------
        float:
            average fulfillment factor
        """
        data: Data = self.get_data()
        return 100 * np.mean(data.storage_fulfillment)

    def close(self) -> None:
        self.__log.close()
