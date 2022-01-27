import math
import numpy

from simses.analysis.data.redox_flow import RedoxFlowData
from simses.analysis.evaluation.plotting.axis import Axis
from simses.analysis.evaluation.plotting.plotly_plotting import PlotlyPlotting
from simses.analysis.evaluation.plotting.plotter import Plotting
from simses.analysis.evaluation.result import EvaluationResult, Description, Unit
from simses.analysis.evaluation.technical.technical_evaluation import TechnicalEvaluation
from simses.commons.config.analysis.general import GeneralAnalysisConfig
from simses.commons.log import Logger
from simses.commons.state.technology.redox_flow import RedoxFlowState
from simses.commons.utils.utilities import format_float


class RedoxFlowTechnicalEvaluation(TechnicalEvaluation):

    title_overview = 'Redox flow results'
    title_soc = 'Redox flow SOC difference'
    title_temperature = 'Redox flow temperature'

    def __init__(self, data: RedoxFlowData, config: GeneralAnalysisConfig, path: str):
        super().__init__(data, config)
        self.__log: Logger = Logger(type(self).__name__)
        title_extension: str = ' for system ' + self.get_data().id
        self.title_overview += title_extension
        self.__result_path = path

    def evaluate(self):
        super().evaluate()
        self.append_result(EvaluationResult(Description.Technical.EQUIVALENT_FULL_CYCLES, Unit.NONE,
                                            self.equivalent_full_cycles))
        self.append_result(EvaluationResult(Description.Technical.DEPTH_OF_DISCHARGE, Unit.PERCENTAGE,
                                            self.depth_of_discharges))
        self.append_result(EvaluationResult(Description.Technical.COULOMB_EFFICIENCY, Unit.PERCENTAGE,
                                            self.coulomb_efficiency))
        self.print_results()

    def plot(self) -> None:
        self.overview_plotting()
        self.soc_comparison_plotting()
        self.temperature_plotting()

    def overview_plotting(self) -> None:
        data: RedoxFlowData = self.get_data()
        plot: Plotting = PlotlyPlotting(title=self.title_overview, path=self.__result_path)
        xaxis: Axis = Axis(data=Plotting.format_time(data.time), label=RedoxFlowState.TIME)
        yaxis: [Axis] = list()
        yaxis.append(Axis(data=data.resistance, label=RedoxFlowState.INTERNAL_RESISTANCE,
                          color=PlotlyPlotting.Color.RESISTANCE_BLACK))
        yaxis.append(Axis(data=data.capacity, label='C in kWh', color=PlotlyPlotting.Color.SOH_GREEN))
        yaxis.append(Axis(data=data.pump_power, label=RedoxFlowState.PUMP_POWER,
                          color=PlotlyPlotting.Color.AC_POWER_BLUE, linestyle=PlotlyPlotting.Linestyle.DASH_DOT))
        yaxis.append(Axis(data=data.power, label=RedoxFlowState.POWER, color=PlotlyPlotting.Color.DC_POWER_GREEN))
        plot.subplots(xaxis=xaxis, yaxis=yaxis)
        self.extend_figures(plot.get_figures())

    def soc_comparison_plotting(self) -> None:
        data: RedoxFlowData = self.get_data()
        plot: Plotting = PlotlyPlotting(title=self.title_soc, path=self.__result_path)
        xaxis: Axis = Axis(data=Plotting.format_time(data.time), label=RedoxFlowState.TIME)
        yaxis: [Axis] = list()
        yaxis.append(Axis(data=data.soc, label=RedoxFlowState.SOC, color=PlotlyPlotting.Color.SOC_BLUE,
                          linestyle=PlotlyPlotting.Linestyle.SOLID))
        yaxis.append(Axis(data=data.soc_stack, label=RedoxFlowState.SOC_STACK, color=PlotlyPlotting.Color.STACK_PURPLE,
                          linestyle=PlotlyPlotting.Linestyle.DOTTED))
        plot.lines(xaxis, yaxis)
        self.extend_figures(plot.get_figures())

    def temperature_plotting(self) -> None:
        data: RedoxFlowData = self.get_data()
        plot: Plotting = PlotlyPlotting(title=self.title_temperature, path=self.__result_path)
        xaxis: Axis = Axis(data=Plotting.format_time(data.time), label=RedoxFlowState.TIME)
        yaxis: [Axis] = list()
        yaxis.append(Axis(data=data.temperature, label=RedoxFlowState.TEMPERATURE,
                          color=PlotlyPlotting.Color.TEMPERATURE_RED, linestyle=PlotlyPlotting.Linestyle.SOLID))
        plot.lines(xaxis, yaxis)
        self.extend_figures(plot.get_figures())

    @property
    def coulomb_efficiency(self):
        data: RedoxFlowData = self.get_data()
        discharge = data.discharge_current_sec
        difference = data.charge_difference
        charge = data.charge_current_sec
        # efficiency_coulomb = (data.discharge_current_sec + data.charge_difference) / data.charge_current_sec * 100
        if charge > 0.0 and discharge > 0.0:
            efficiency_coulomb = 100 * 0.5 * ((difference * math.sqrt(4 * discharge * charge + difference ** 2)) /
                                              charge ** 2 + 2 * discharge / charge + (difference / charge) ** 2)
        elif charge > 0.0:
            efficiency_coulomb = 100 * difference / charge
            self.__log.warn('The storage was only charged. Thus, only a one-way efficiency could be calculated')
        elif discharge > 0.0:
            efficiency_coulomb = 100 * -difference / discharge
            self.__log.warn('The storage was only discharged. Thus, only a one-way efficiency could be calculated')
        else:
            efficiency_coulomb = numpy.nan
            self.__log.warn('Storage was neither charged nor discharged. Efficiency could not be calculated.')
        if not 0.0 < efficiency_coulomb < 100.0:
            self.__log.warn('Coulombic Efficiency should be between 0 % and 100 %, but is ' +
                            format_float(efficiency_coulomb) + ' %. Perhaps your simulation time range is too short '
                            'for calculating an accurate round trip efficiency.')
        return efficiency_coulomb
