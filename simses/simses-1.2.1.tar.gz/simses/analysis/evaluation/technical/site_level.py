import numpy
import time as calctime

from simses.analysis.data.energy_management import EnergyManagementData
from simses.analysis.data.system import SystemData
from simses.analysis.evaluation.plotting.axis import Axis
from simses.analysis.evaluation.plotting.plotly_plotting import PlotlyPlotting
from simses.analysis.evaluation.plotting.plotter import Plotting
from simses.analysis.evaluation.result import EvaluationResult, Description, Unit
from simses.analysis.evaluation.technical.technical_evaluation import TechnicalEvaluation
from simses.analysis.utils import get_max_for
from simses.commons.config.analysis.general import GeneralAnalysisConfig
from simses.commons.config.simulation.energy_management import EnergyManagementConfig
from simses.commons.state.energy_management import EnergyManagementState
from simses.commons.state.system import SystemState


class SiteLevelEvaluation(TechnicalEvaluation):

    title_power = 'Site Level Power'
    title_idm = 'Intraday Power'

    def __init__(self, data: SystemData, energy_management_data: EnergyManagementData, config: GeneralAnalysisConfig,
                 energy_management_config: EnergyManagementConfig, path: str):
        super().__init__(energy_management_data, config)
        self.__system_data: SystemData = data
        self.__max_power: float = energy_management_config.max_power
        title_extension: str = ' for system ' + self.get_data().id
        self.title_power += title_extension
        self.title_idm += title_extension
        self.__result_path = path
        self.__max_power_timeseries = energy_management_data.peakshaving_limit

    def evaluate(self):
        power_above_peak = self.power_above_peak
        energy_events_above_peak = self.energy_events_above_peak(power_above_peak)
        self.append_result(EvaluationResult(Description.Technical.MAX_GRID_POWER, Unit.WATT, self.max_grid_power))
        self.append_result(EvaluationResult(Description.Technical.POWER_ABOVE_PEAK_MAX, Unit.WATT, self.max_power_above_peak(power_above_peak)))
        self.append_result(EvaluationResult(Description.Technical.POWER_ABOVE_PEAK_AVG, Unit.WATT, self.get_average_power_above_peak_from(power_above_peak)))
        self.append_result(EvaluationResult(Description.Technical.ENERGY_ABOVE_PEAK_MAX, Unit.KWH, self.get_max_energy_event_above_peak_from(energy_events_above_peak)))
        self.append_result(EvaluationResult(Description.Technical.ENERGY_ABOVE_PEAK_AVG, Unit.KWH, self.get_average_energy_event_above_peak_from(energy_events_above_peak)))
        self.append_result(EvaluationResult(Description.Technical.SELF_CONSUMPTION_RATE, Unit.PERCENTAGE, self.self_consumption_rate))
        self.append_result(EvaluationResult(Description.Technical.SELF_SUFFICIENCY, Unit.PERCENTAGE, self.self_sufficiency))
        self.append_result(EvaluationResult(Description.Technical.NUMBER_ENERGY_EVENTS, Unit.NONE, len(energy_events_above_peak)))
        self.append_result(EvaluationResult(Description.Technical.ENERGY_IDM_BOUGHT, Unit.KWH, self.intraday_energy_bought))
        self.append_result(EvaluationResult(Description.Technical.ENERGY_IDM_SOLD, Unit.KWH, self.intraday_energy_sold))
        self.print_results()

    def plot(self) -> None:
        self.site_level_power_plotting()
        self.intraday_power_plotting()

    def site_level_power_plotting(self) -> None:
        ems_data: EnergyManagementData = self.get_data()
        system_data: SystemData = self.__system_data
        plot: Plotting = PlotlyPlotting(title=self.title_power, path=self.__result_path)
        time = Plotting.format_time(system_data.time)
        xaxis: Axis = Axis(data=time, label=SystemState.TIME)
        yaxis: [Axis] = list()
        yaxis.append(Axis(system_data.power, label=SystemState.AC_POWER_DELIVERED, color=PlotlyPlotting.Color.AC_POWER_BLUE,
                          linestyle=PlotlyPlotting.Linestyle.SOLID))
        yaxis.append(Axis(ems_data.load_power, label=EnergyManagementState.LOAD_POWER,
                          color=PlotlyPlotting.Color.DC_POWER_GREEN,
                          linestyle=PlotlyPlotting.Linestyle.DASHED))
        # yaxis.append(Axis(self.__energy_management_data.pv_power, label=EnergyManagementState.PV_POWER, color=Plotting.Color.BLUE,
        #                  linestyle=Plotting.Linestyle.DASH_DOT))
        # grid_power = [load + battery - pv for load, battery, pv in zip(data.power, self.__energy_management_data.load_power, self.__energy_management_data.pv_power)]
        grid_power = system_data.power + ems_data.load_power - ems_data.pv_power
        yaxis.append(Axis(grid_power, label='Total Site Power in W', color=PlotlyPlotting.Color.POWER_YELLOW,
                          linestyle=PlotlyPlotting.Linestyle.DOTTED))
        yaxis.append(Axis(system_data.soc, label=SystemState.SOC, color=PlotlyPlotting.Color.SOC_BLUE,
                          linestyle=PlotlyPlotting.Linestyle.SOLID))
        yaxis.append(
            Axis(self.__max_power_timeseries, label='Peak power allowed in W', color=PlotlyPlotting.Color.MAGENTA,
                 linestyle=PlotlyPlotting.Linestyle.DASHED))
        plot.lines(xaxis, yaxis, [3])
        self.extend_figures(plot.get_figures())

    def intraday_power_plotting(self) -> None:
        try:
            ems_data: EnergyManagementData = self.get_data()
            if sum(abs(ems_data.idm_power)) > 0.0:
                plot: Plotting = PlotlyPlotting(title=self.title_idm, path=self.__result_path)
                time = Plotting.format_time(ems_data.time)
                xaxis: Axis = Axis(data=time, label=SystemState.TIME)
                yaxis: [Axis] = [Axis(ems_data.idm_power, label=EnergyManagementState.IDM_POWER)]
                plot.lines(xaxis, yaxis)
                self.extend_figures(plot.get_figures())
        except KeyError as err:
            self.__log.warn(err)

    @property
    def intraday_energy_bought(self) -> float:
        ems_data: EnergyManagementData = self.get_data()
        charge_energy = ems_data.idm_power[:].copy() * ems_data.convert_watt_to_kWh
        return abs(sum(charge_energy[charge_energy > 0.0]))

    @property
    def intraday_energy_sold(self) -> float:
        ems_data: EnergyManagementData = self.get_data()
        discharge_energy = ems_data.idm_power[:].copy() * ems_data.convert_watt_to_kWh
        return abs(sum(discharge_energy[discharge_energy < 0.0]))

    @property
    def grid_power(self) -> numpy.ndarray:
        data: EnergyManagementData = self.get_data()
        grid_power = self.__system_data.power + data.load_power - data.pv_power
        return grid_power

    @property
    def max_grid_power(self) -> float:
        return max(0.0, get_max_for(self.grid_power))

    @property
    def power_above_peak(self) -> numpy.ndarray:
        grid_power = self.grid_power
        power_above_peak = grid_power - self.__max_power_timeseries
        power_above_peak[power_above_peak < 0.0] = 0.0
        return power_above_peak

    @staticmethod
    def max_power_above_peak(power_above_peak) -> float:
        return max(0.0, get_max_for(power_above_peak))

    @staticmethod
    def get_average_power_above_peak_from(power_above_peak) -> float:
        power = power_above_peak[power_above_peak > 0.0]
        if len(power) == 0:
            return 0.0
        return sum(power) / len(power)

    def energy_events_above_peak(self, power_above_peak) -> [float]:
        energy_above_peak = power_above_peak * self.get_data().convert_watt_to_kWh
        energy_events: [float] = list()
        energy_event: float = 0.0
        for energy in energy_above_peak:
            if energy_event > 1e-5 and energy == 0.0:
                energy_events.append(energy_event)
                energy_event = 0.0
            else:
                energy_event += energy
        return energy_events

    @staticmethod
    def get_max_energy_event_above_peak_from(energy_events: [float]) -> float:
        if not energy_events:
            return 0.0
        return max(energy_events)

    @staticmethod
    def get_average_energy_event_above_peak_from(energy_events: [float]) -> float:
        if not energy_events:
            return 0.0
        return sum(energy_events) / len(energy_events)

    @property
    def self_consumption_rate(self) -> float:
        ems_data: EnergyManagementData = self.get_data()
        system_data: SystemData = self.__system_data
        grid_exchange: numpy.ndarray = ems_data.pv_power - system_data.power - ems_data.load_power
        grid_feed_in: float = sum(grid_exchange[grid_exchange > 0.0])
        pv_generation: float = sum(ems_data.pv_power)
        if pv_generation > 0.0:
            self_consumption: float = 100.0 * (1.0 - grid_feed_in / pv_generation)
        else:
            self_consumption: str = '-No PV- 0'
        return self_consumption

    @property
    def self_sufficiency(self) -> float:
        ems_data: EnergyManagementData = self.get_data()
        system_data: SystemData = self.__system_data
        grid_exchange: numpy.ndarray = ems_data.pv_power - system_data.power - ems_data.load_power
        grid_purchase: float = sum(-grid_exchange[grid_exchange < 0.0])
        load: float = sum(ems_data.load_power)
        pv_generation: float = sum(ems_data.pv_power)
        if pv_generation > 0.0:
            self_sufficiency_value: float = 100.0 * (1.0 - grid_purchase / load)
        else:
            self_sufficiency_value: str = '-No PV- 0'
        return self_sufficiency_value
