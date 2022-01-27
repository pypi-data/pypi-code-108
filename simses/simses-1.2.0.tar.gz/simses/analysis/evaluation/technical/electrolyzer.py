from simses.analysis.data.electrolyzer import ElectrolyzerData
from simses.analysis.evaluation.plotting.axis import Axis
from simses.analysis.evaluation.plotting.plotly_plotting import PlotlyPlotting
from simses.analysis.evaluation.plotting.plotter import Plotting
from simses.analysis.evaluation.result import EvaluationResult, Description, Unit
from simses.analysis.evaluation.technical.technical_evaluation import TechnicalEvaluation
from simses.commons.config.analysis.general import GeneralAnalysisConfig
from simses.commons.state.technology.electrolyzer import ElectrolyzerState


class ElectrolyzerTechnicalEvaluation(TechnicalEvaluation):

    title = 'Electrolyzer results'

    def __init__(self, data: ElectrolyzerData, config: GeneralAnalysisConfig, path: str):
        super().__init__(data, config)
        title_extension: str = ' for system ' + self.get_data().id
        self.title += title_extension
        self.__result_path = path
        # self.__electrolyzer = PemElectrolyzerMultiDimAnalytic(16000, ElectrolyzerDataConfig())

    def evaluate(self):
        # super().evaluate()
        data: ElectrolyzerData = self.get_data()
        self.append_result(EvaluationResult(Description.Technical.H2_PRODUCTION_EFFICIENCY_LHV, Unit.PERCENTAGE, self.h2_production_efficiency_lhv()))
        self.append_result(EvaluationResult(Description.Technical.SOH, Unit.PERCENTAGE, self.soh()))
        self.append_result(EvaluationResult(Description.Technical.ENERGY_H2_REACTION, Unit.KWH, data.total_energy_reaction))
        self.append_result(EvaluationResult(Description.Technical.ENERGY_WATER_HEATING, Unit.KWH, data.total_energy_heating))
        self.append_result(EvaluationResult(Description.Technical.ENERGY_WATER_CIRCULATION, Unit.KWH, data.total_energy_pump))
        self.append_result(EvaluationResult(Description.Technical.ENERGY_H2_DRYING, Unit.KWH, data.total_energy_gas_drying))
        self.append_result(EvaluationResult(Description.Technical.ENERGY_H2_COMPRESSION, Unit.KWH, data.total_energy_compressor))
        self.append_result(EvaluationResult(Description.Technical.ENERGY_H2_LHV, Unit.KWH, data.total_energy_h2_lhv))
        self.append_result(EvaluationResult(Description.Technical.TOTAL_H2_PRODUCTION_KG, Unit.KG, data.total_amount_h2_kg))
        self.append_result(EvaluationResult(Description.Technical.TOTAL_H2_PRODUCTION_NM, Unit.NCM, data.total_amount_h2_nqm))
        self.print_results()

    def plot(self) -> None:
        self.fulfillment_plotting()
        self.current_plotting()
        self.current_dens_plotting()
        self.degradation_plotting()
        self.soh_plotting()
        self.hydrogen_production_plotting()
        self.pressures_plotting()
        self.hydrogen_outflow_plotting()
        #self.pressure_anode_plotting()
        self.temperature_plotting()
        # self.power_water_heating_plotting()
        self.power_auxilliaries_1_plotting()
        self.power_auxilliaries_2_plotting()
        # self.efficiency_plotting()

    def h2_production_efficiency_lhv(self) -> float:
        """
        Calculates the hydrogen production efficiency relative to its lower heating value

        Parameters
        -----------
            data: simulation results

        :return:
            float: h2 production efficiency
        """
        data: ElectrolyzerData = self.get_data()
        return data.total_energy_h2_lhv / (data.total_energy_pump + data.total_energy_compressor +
                                           data.total_energy_gas_drying + data.total_energy_heating +
                                           data.total_energy_reaction) * 100

    def soh(self, index=-1):
        data: ElectrolyzerData = self.get_data()
        return data.soh[index] * 100  #  %

    # def efficieny_curve_electrolyzer(self, index=0):
    #     data: ElectrolyzerData = self.get_data()
    #     # timestep = data.time[1] - data.time[0]
    #     # state_index = int(time / timestep)
    #     # values out of the hydrogen state are used for temperature and pressure
    #     # stack_temperature = data.temperature_el[index] - 273.15  # K -> °C
    #     # p_anode = data.pressure_anode_el[index]
    #     # p_cathode = data.pressure_cathode_el[index]
    #     # fixed values for pressure and temperature, so that the efficiency curves are only changed by the values for
    #     # degradation -> resistance increase and exchange_current_decrease
    #     eff_hydrogen_state = ElectrolyzerState(1,1)
    #     eff_hydrogen_state.temperature_el = 80  # °C
    #     eff_hydrogen_state.pressure_anode_el = 0  # barg
    #     eff_hydrogen_state.pressure_cathode_el = 25  # barg
    #     # eff_hydrogen_state.temperature_el = data.temperature_el[index]
    #     # eff_hydrogen_state.pressure_cathode_el = data.pressure_cathode_el[index]
    #     # eff_hydrogen_state.pressure_anode_el = data.pressure_anode_el[index]
    #     eff_hydrogen_state.resistance_increase_el = data.resistance_increase[index]
    #     eff_hydrogen_state.exchange_current_decrease_el = data.exchange_current_dens_decrease[index]
    #     # efficiency_df = self.__electrolyzer.calculate_efficiency_curves(eff_hydrogen_state)
    #     efficiency_df = self.__electrolyzer.get_efficiency_curve(eff_hydrogen_state)
    #     return efficiency_df

    def current_plotting(self):
        data: ElectrolyzerData = self.get_data()
        plot: Plotting = PlotlyPlotting(title=ElectrolyzerState.CURRENT, path=self.__result_path)
        xaxis: Axis = Axis(data=Plotting.format_time(data.time), label=ElectrolyzerState.TIME)
        yaxis: [Axis] = [Axis(data=data.current, label=ElectrolyzerState.CURRENT)]
        plot.lines(xaxis, yaxis)
        self.extend_figures(plot.get_figures())

    def current_dens_plotting(self):
        data: ElectrolyzerData = self.get_data()
        plot: Plotting = PlotlyPlotting(title=ElectrolyzerState.CURRENT_DENSITY, path=self.__result_path)
        xaxis: Axis = Axis(data=Plotting.format_time(data.time), label=ElectrolyzerState.TIME)
        yaxis: [Axis] = [Axis(data=data.current_density, label=ElectrolyzerState.CURRENT_DENSITY)]
        plot.lines(xaxis, yaxis)
        self.extend_figures(plot.get_figures())

    def hydrogen_production_plotting(self):
        data: ElectrolyzerData = self.get_data()
        plot: Plotting = PlotlyPlotting(title=ElectrolyzerState.HYDROGEN_PRODUCTION, path=self.__result_path)
        xaxis: Axis = Axis(data=Plotting.format_time(data.time), label=ElectrolyzerState.TIME)
        yaxis: [Axis] = [Axis(data=data.hydrogen_production, label=ElectrolyzerState.HYDROGEN_PRODUCTION)]
        plot.lines(xaxis, yaxis)
        self.extend_figures(plot.get_figures())

    def pressures_plotting(self):
        data: ElectrolyzerData = self.get_data()
        plot: Plotting = PlotlyPlotting(title='Pressures Cathode', path=self.__result_path)
        xaxis: Axis = Axis(data=Plotting.format_time(data.time), label=ElectrolyzerState.TIME)
        yaxis: [Axis] = list()
        yaxis.append(Axis(data=data.pressure_cathode, label=ElectrolyzerState.PRESSURE_CATHODE,
                          color=PlotlyPlotting.Color.CATHODE_PINK, linestyle=PlotlyPlotting.Linestyle.SOLID))
        yaxis.append(Axis(data=data.part_pressure_h2, label=ElectrolyzerState.PART_PRESSURE_H2,
                          color=PlotlyPlotting.Color.CATHODE_PINK, linestyle=PlotlyPlotting.Linestyle.DASHED))
        yaxis.append(Axis(data=data.pressure_anode, label=ElectrolyzerState.PRESSURE_ANODE,
                          color=PlotlyPlotting.Color.ANODE_GREEN, linestyle=PlotlyPlotting.Linestyle.SOLID))
        yaxis.append(Axis(data=data.part_pressure_o2, label=ElectrolyzerState.PART_PRESSURE_O2,
                          color=PlotlyPlotting.Color.ANODE_GREEN, linestyle=PlotlyPlotting.Linestyle.DASHED))
        plot.lines(xaxis, yaxis)
        self.extend_figures(plot.get_figures())

    def temperature_plotting(self):
        data: ElectrolyzerData = self.get_data()
        plot: Plotting = PlotlyPlotting(title=ElectrolyzerState.TEMPERATURE, path=self.__result_path)
        xaxis: Axis = Axis(data=Plotting.format_time(data.time), label=ElectrolyzerState.TIME)
        yaxis: [Axis] = list()
        yaxis.append(Axis(data=data.temperature, label=ElectrolyzerState.TEMPERATURE,
                          color=PlotlyPlotting.Color.TEMPERATURE_RED))
        yaxis.append(Axis(data=data.convection_heat, label=ElectrolyzerState.CONVECTION_HEAT,
                          color=PlotlyPlotting.Color.HEAT_ORANGE))
        plot.lines(xaxis, yaxis, [1])
        self.extend_figures(plot.get_figures())

    # def power_water_heating_el_plotting(self):
    #     data: HydrogenData = self.get_data()
    #     plot: Plotting = PlotlyPlotting(title='Elektrolyzer Stack Heat', path=self.__result_path)
    #     xaxis: Axis = Axis(data=Plotting.format_time(data.time), label=HydrogenState.TIME)
    #     yaxis: [Axis] = list()
    #     yaxis.append(Axis(data=data.power_water_heating_el, label=HydrogenState.POWER_WATER_HEATING_EL,
    #                       color=PlotlyPlotting.Color.BLUE))
    #     plot.lines(xaxis, yaxis, [2,3])
    #     self.extend_figures(plot.get_figures())

    def power_auxilliaries_1_plotting(self):
        data: ElectrolyzerData = self.get_data()
        plot: Plotting = PlotlyPlotting(title='Auxiliaries 1', path=self.__result_path)
        xaxis: Axis = Axis(data=Plotting.format_time(data.time), label=ElectrolyzerState.TIME)
        yaxis: [Axis] = list()
        yaxis.append(Axis(data.power_water_heating, label=ElectrolyzerState.POWER_WATER_HEATING,
                          color=PlotlyPlotting.Color.AC_POWER_BLUE, linestyle=PlotlyPlotting.Linestyle.DASHED))
        yaxis.append(Axis(data.power_pump, label=ElectrolyzerState.POWER_PUMP,
                          color=PlotlyPlotting.Color.AC_POWER_BLUE,linestyle=PlotlyPlotting.Linestyle.DASHED))
        plot.lines(xaxis, yaxis, [1])
        self.extend_figures(plot.get_figures())

    def power_auxilliaries_2_plotting(self):
        data: ElectrolyzerData = self.get_data()
        plot: Plotting = PlotlyPlotting(title='Auxiliaries 2', path=self.__result_path)
        xaxis: Axis = Axis(data=Plotting.format_time(data.time), label=ElectrolyzerState.TIME)
        yaxis: [Axis] = list()
        yaxis.append(Axis(data.power_compressor, label=ElectrolyzerState.POWER_COMPRESSOR,
                          color=PlotlyPlotting.Color.AC_POWER_BLUE, linestyle= PlotlyPlotting.Linestyle.DASHED))
        yaxis.append(Axis(data.power_gas_drying, label=ElectrolyzerState.POWER_GAS_DRYING,
                          color=PlotlyPlotting.Color.RED, linestyle=PlotlyPlotting.Linestyle.DOTTED))
        plot.lines(xaxis, yaxis, [1])
        self.extend_figures(plot.get_figures())

    def hydrogen_outflow_plotting(self):
        data: ElectrolyzerData = self.get_data()
        plot: Plotting = PlotlyPlotting(title='Hydrogen outflow and total injection', path=self.__result_path)
        xaxis: Axis = Axis(data=Plotting.format_time(data.time), label=ElectrolyzerState.TIME)
        yaxis: [Axis] = list()
        yaxis.append(Axis(data=data.hydrogen_outflow, label=ElectrolyzerState.HYDROGEN_OUTFLOW))
        yaxis.append(Axis(data=data.total_h2_production, label=ElectrolyzerState.TOTAL_HYDROGEN_PRODUCTION,
                          color=PlotlyPlotting.Color.CATHODE_PINK, linestyle=PlotlyPlotting.Linestyle.DOTTED))
        plot.lines(xaxis, yaxis, [1])
        self.extend_figures(plot.get_figures())

    def fulfillment_plotting(self):
        data: ElectrolyzerData = self.get_data()
        plot: Plotting = PlotlyPlotting(title=ElectrolyzerState.FULFILLMENT, path=self.__result_path)
        xaxis: Axis = Axis(data=Plotting.format_time(data.time), label=ElectrolyzerState.TIME)
        yaxis: [Axis] = [Axis(data=data.storage_fulfillment, label=ElectrolyzerState.FULFILLMENT)]
        plot.lines(xaxis, yaxis)
        self.extend_figures(plot.get_figures())

    def degradation_plotting(self):
        data: ElectrolyzerData = self.get_data()
        plot: Plotting = PlotlyPlotting(title='Degradation Electrolyzer', path=self.__result_path)
        xaxis: Axis = Axis(data=Plotting.format_time(data.time), label=ElectrolyzerState.TIME)
        yaxis: [Axis] = list()
        yaxis.append(Axis(data=data.resistance_increase, label=ElectrolyzerState.RESISTANCE_INCREASE, color=PlotlyPlotting.Color.RESISTANCE_BLACK, linestyle=PlotlyPlotting.Linestyle.SOLID))
        yaxis.append(Axis(data=data.resistance_increase_cyclic, label=ElectrolyzerState.RESISTANCE_INCREASE_CYCLIC, color=PlotlyPlotting.Color.RESISTANCE_BLACK, linestyle=PlotlyPlotting.Linestyle.DASHED))
        yaxis.append(Axis(data=data.resistance_increase_calendar, label=ElectrolyzerState.RESISTANCE_INCREASE_CALENDAR, color=PlotlyPlotting.Color.RESISTANCE_BLACK, linestyle=PlotlyPlotting.Linestyle.DOTTED))
        yaxis.append(Axis(data=data.exchange_current_dens_decrease, label=ElectrolyzerState.EXCHANGE_CURRENT_DENS_DECREASE, color=PlotlyPlotting.Color.CURRENT_CYAN))
        plot.lines(xaxis, yaxis, [3])
        self.extend_figures(plot.get_figures())

    def soh_plotting(self):
        data: ElectrolyzerData = self.get_data()
        plot: Plotting = PlotlyPlotting(title=ElectrolyzerState.SOH, path=self.__result_path)
        xaxis: Axis = Axis(data=Plotting.format_time(data.time), label=ElectrolyzerState.TIME)
        yaxis: [Axis] = list()
        yaxis.append(Axis(data=data.soh, label=ElectrolyzerState.SOH, color=PlotlyPlotting.Color.SOH_GREEN))
        # yaxis.append(Axis(data=data.ref_voltage_el, label=HydrogenState.REFERENCE_VOLTAGE_EL, color=PlotlyPlotting.Color.YELLOW))
        plot.lines(xaxis, yaxis, [1])
        self.extend_figures(plot.get_figures())

    # def efficiency_plotting(self):
    #     efficiency_data_begin = self.efficieny_curve_electrolyzer(0)
    #     efficiency_data_end = self.efficieny_curve_electrolyzer(-1)
    #     current_dens_array = efficiency_data_begin['current density'].to_numpy()
    #     voltage_efficiency_array_begin = efficiency_data_begin['voltage efficiency'].to_numpy()
    #     voltage_efficiency_array_end = efficiency_data_end['voltage efficiency'].to_numpy()
    #     faraday_efficiency_array_begin = efficiency_data_begin['faraday efficiency'].to_numpy()
    #     faraday_efficiency_array_end = efficiency_data_end['faraday efficiency'].to_numpy()
    #     cell_efficiency_array_begin = efficiency_data_begin['cell efficiency'].to_numpy()
    #     cell_efficiency_array_end = efficiency_data_end['cell efficiency'].to_numpy()
    #
    #     file_name: str = 'electrolyzer_efficiency.csv'
    #     file = self.__result_path + file_name
    #     # with open(file, 'w', newline=' ') as file:
    #     #     writer = csv.writer(file)
    #     dict = {'currentdensity': current_dens_array, 'voltage eff begin': voltage_efficiency_array_begin,
    #             'voltage eff end': voltage_efficiency_array_end, 'faraday eff begin': faraday_efficiency_array_begin,
    #             'faraday eff end': faraday_efficiency_array_end, 'cell eff begin': cell_efficiency_array_begin,
    #             'cell eff end': cell_efficiency_array_end}
    #     df = pd.DataFrame(dict)
    #     df.to_csv(file, index=False)
    #
    #     plot: Plotting = PlotlyPlotting(title='Efficiency', path=self.__result_path)
    #     xaxis: Axis = Axis(data=current_dens_array, label='currentdensity')
    #     yaxis: [Axis] = list()
    #     yaxis.append(Axis(data=cell_efficiency_array_begin, label='cell efficiency begin'))
    #     yaxis.append(Axis(data=cell_efficiency_array_end, label='cell efficiency end', color=PlotlyPlotting.Color.RESISTANCE_BLACK))
    #     #yaxis.append(Axis(data=voltage_efficiency_array, label='voltage efficiency', color=PlotlyPlotting.Color.RED))
    #     #yaxis.append(Axis(data=faraday_efficiency_array, label='faraday efficiency', color=PlotlyPlotting.Color.GREEN))
    #     plot.lines(xaxis, yaxis)
    #     self.extend_figures(plot.get_figures())
