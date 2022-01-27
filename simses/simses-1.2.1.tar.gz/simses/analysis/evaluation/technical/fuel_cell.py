from simses.analysis.data.fuel_cell import FuelCellData
from simses.analysis.evaluation.plotting.axis import Axis
from simses.analysis.evaluation.plotting.plotly_plotting import PlotlyPlotting
from simses.analysis.evaluation.plotting.plotter import Plotting
from simses.analysis.evaluation.technical.technical_evaluation import TechnicalEvaluation
from simses.commons.config.analysis.general import GeneralAnalysisConfig
from simses.commons.state.technology.fuel_cell import FuelCellState


class FuelCellTechnicalEvaluation(TechnicalEvaluation):

    title = 'Fuel cell results'

    def __init__(self, data: FuelCellData, config: GeneralAnalysisConfig, path: str):
        super().__init__(data, config)
        title_extension: str = ' for system ' + self.get_data().id
        self.title += title_extension
        self.__result_path = path

    def evaluate(self) -> None:
        # super().evaluate()
        # data: FuelCellData = self.get_data()
        # self.append_result(EvaluationResult(Description.Technical.H2_PRODUCTION_EFFICIENCY_LHV, Unit.PERCENTAGE, self.h2_production_efficiency_lhv()))
        self.print_results()

    def plot(self) -> None:
        self.current_plotting()
        self.current_dens_plotting()
        self.pressures_plotting()
        self.temperature_plotting()
        self.power_plotting()
        self.hydrogen_consumption_plotting()

    def current_plotting(self):
        data: FuelCellData = self.get_data()
        plot: Plotting = PlotlyPlotting(title=FuelCellState.CURRENT, path=self.__result_path)
        xaxis: Axis = Axis(data=Plotting.format_time(data.time), label=FuelCellState.TIME)
        yaxis: [Axis] = [Axis(data=data.current, label=FuelCellState.CURRENT)]
        plot.lines(xaxis, yaxis)
        self.extend_figures(plot.get_figures())

    def current_dens_plotting(self):
        data: FuelCellData = self.get_data()
        plot: Plotting = PlotlyPlotting(title=FuelCellState.CURRENT_DENSITY, path=self.__result_path)
        xaxis: Axis = Axis(data=Plotting.format_time(data.time), label=FuelCellState.TIME)
        yaxis: [Axis] = [Axis(data=data.current_density, label=FuelCellState.CURRENT_DENSITY)]
        plot.lines(xaxis, yaxis)
        self.extend_figures(plot.get_figures())

    def pressures_plotting(self):
        data: FuelCellData = self.get_data()
        plot: Plotting = PlotlyPlotting(title='Pressures Cathode', path=self.__result_path)
        xaxis: Axis = Axis(data=Plotting.format_time(data.time), label=FuelCellState.TIME)
        yaxis: [Axis] = list()
        yaxis.append(Axis(data=data.pressure_cathode, label=FuelCellState.PRESSURE_CATHODE,
                          color=PlotlyPlotting.Color.CATHODE_PINK, linestyle=PlotlyPlotting.Linestyle.SOLID))
        yaxis.append(Axis(data=data.pressure_anode, label=FuelCellState.PRESSURE_ANODE,
                          color=PlotlyPlotting.Color.ANODE_GREEN, linestyle=PlotlyPlotting.Linestyle.SOLID))
        plot.lines(xaxis, yaxis)
        self.extend_figures(plot.get_figures())

    def temperature_plotting(self):
        data: FuelCellData = self.get_data()
        plot: Plotting = PlotlyPlotting(title=FuelCellState.TEMPERATURE, path=self.__result_path)
        xaxis: Axis = Axis(data=Plotting.format_time(data.time), label=FuelCellState.TIME)
        yaxis: [Axis] = list()
        yaxis.append(Axis(data=data.temperature, label=FuelCellState.TEMPERATURE, color=PlotlyPlotting.Color.TEMPERATURE_RED))
        plot.lines(xaxis, yaxis, [1])
        self.extend_figures(plot.get_figures())

    def power_plotting(self):
        data: FuelCellData = self.get_data()
        plot: Plotting = PlotlyPlotting(title=FuelCellState.POWER, path=self.__result_path)
        xaxis: Axis = Axis(data=Plotting.format_time(data.time), label=FuelCellState.TIME)
        yaxis: [Axis] = [Axis(data=data.power, label=FuelCellState.POWER)]
        plot.lines(xaxis, yaxis)
        self.extend_figures(plot.get_figures())

    def hydrogen_consumption_plotting(self):
        data: FuelCellData = self.get_data()
        plot: Plotting = PlotlyPlotting(title=FuelCellState.HYDROGEN_USE, path=self.__result_path)
        xaxis: Axis = Axis(data=Plotting.format_time(data.time), label=FuelCellState.TIME)
        yaxis: [Axis] = [Axis(data=data.hydrogen_use, label=FuelCellState.HYDROGEN_USE)]
        plot.lines(xaxis, yaxis)
        self.extend_figures(plot.get_figures())

