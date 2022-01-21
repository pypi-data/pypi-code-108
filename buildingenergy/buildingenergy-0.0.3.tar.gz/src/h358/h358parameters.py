__author__ = 'stephane.ploix@g-scop.grenoble-inp.fr'

import pickle
from numpy import array
import scipy.optimize
from buildingenergy.model import Preference  # for differential_evolution
import h358model
import h358simulator
import time
import matplotlib
from prettytable import PrettyTable, MSWORD_FRIENDLY
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import SALib.sample.morris
import SALib.analyze.morris
import warnings
import buildingenergy
warnings.filterwarnings("ignore")


class ModelFitter:
    """Dedicated to the adjustment of physical model parameters: it can do a Morris parameter sensitivity analysis to get an idea of the parameter identifiability, but also a non-linear adjustments in order to get optimal parameters among their bounds specified in the provided model. The optimization method uses differential evolution algorithm."""

    def __init__(self, simulator: h358simulator, data_container: buildingenergy.measurements.DataContainer, pickle_file_name_suffix: str='best_parameters.p', use_state_observer=False) -> None:
        """Initialize a model fitter.

        :param simulator: a simulator
        :type simulator: h358simulator.Simulator
        :param measurements_csv_file_name: the name of the csv file containing measurement data, defaults to 'h358data_winter2015-2016.csv'
        :type measurements_csv_file_name: str, optional
        :param weather_file_name: the name of the json file containing openweather weather data, defaults to 'grenoble_weather2015-2019.json'
        :type weather_file_name: str, optional
        :param pickle_file_name_suffix: pickle file name suffix. The name of the state space representation used will be added as a prefix.
        :type pickle_file_name_suffix: str
        """
        self.simulator = simulator
        self.model = simulator.model
        self.state_observer = False
        self.data_container = data_container
        self.use_state_observer = use_state_observer
        self.pickle_file_name = pickle_file_name_suffix

    def sensitivity(self, number_of_trajectories: int=100, number_of_levels: int=4, state_observer: bool=False, plot_results: bool = False):
        """Perform a Morris sensitivity analysis for everage simulation error both for indoor temperature and CO2 concentration. It returns 2 plots related to each output variable. mu_star axis deals with the simulation variation bias, and sigma for standard deviation of the simulation variations wrt to each parameter.

        :param skiprows: starting row from the measurement csv file to use, defaults to 0
        :type skiprows: int, optional
        :param nrows: endding row from the measurement csv file to use, defaults to 60*24
        :type nrows: int, optional
        :param number_of_trajectories: [description], defaults to 100
        :type number_of_trajectories: int, optional
        :param number_of_levels: [description], defaults to 4
        :type number_of_levels: int, optional
        :param stete_observer: use or not a state observer to estimate the state a the beginning of each day, default is False
        :type state_observer: bool
        :param plot_results: True if results should be plotted, default is False
        :type plot_results: bool
        :return: a dictionnary with the output variables as key and another dictionnary as values. It admits 'names', 'mu', 'mu_star', 'sigma', 'mu_star_conf' as keys and corresponding values as lists
        :rtype: dict[str,dict[str,list[float|str]]]
        """
        self.model.register_data(self.data_container)
        h358_simulator = h358simulator.Simulator(self.model)
        self.state_observer = state_observer
        print(self.model)
        problem = dict()
        adjustable_parameters = self.model.adjustables
        problem['num_vars'] = len(adjustable_parameters)
        problem['names'] = []
        problem['bounds'] = []
        for parameter_name in adjustable_parameters:
            problem['names'].append(parameter_name)
            problem['bounds'].append(self.model.pbound(parameter_name))

        print('# Generating parameter values')
        parameter_value_sets = SALib.sample.morris.sample(problem, number_of_trajectories, num_levels=number_of_levels)
        Tins_value_sets, Cins_value_sets = [], []
        for parameter_set in parameter_value_sets:
            print('.', end='')
            self.model.adjustables = parameter_set
            Tins, Cins, Tin_setpoints, heating_powers, door_openings, window_openings, estimated_outputs = h358_simulator.simulate(h358simulator.CONTROL.NONE, self.state_observer)
            Tins_value_sets.append(ModelFitter.avg_error(Tins, self.model.data('Toffice_reference')))
            Cins_value_sets.append(ModelFitter.avg_error(Cins, self.model.data('office_CO2_concentration')))
        print()
        print('Analyzing simulation results')
        results = dict()
        print('\n* Tin sensitivty')
        results['Tins'] = SALib.analyze.morris.analyze(problem, parameter_value_sets, array(Tins_value_sets), conf_level=0.95, print_to_console=True, num_levels=number_of_levels)
        print('\n* Cins sensitivity')
        results['Cins'] = SALib.analyze.morris.analyze(problem, parameter_value_sets, array(Cins_value_sets), conf_level=0.95, print_to_console=True, num_levels=number_of_levels)

        if plot_results:
            _, ax = plt.subplots(2)
            j=0
            for output_variable_name in results:
                ax[j].scatter(results[output_variable_name]['mu_star'], results[output_variable_name]['sigma'])
                for i in range(problem['num_vars']):
                    ax[j].annotate(problem['names'][i], (results[output_variable_name]['mu_star'][i], results[output_variable_name]['sigma'][i]))
                    ax[j].set(xlabel='mu_star ' + output_variable_name, ylabel='sigma ' + output_variable_name)
                j += 1
            plt.ion()
            plt.show()
            input('Close figure and press enter to continue:')
        return results

    def adjust_parameters(self, validation_data_container, strategy: int='best1bin', maxiter: int=100, popsize: int=50, tol: float=0.01, mutation=(0.5, 1), recombination: float=0.7, seed: int=None, callback: float=None, disp=True, updating='deferred', polish=True, init='latinhypercube', workers=-1, perform_sensitivity_analysis: bool=False, plot_results: bool = True) -> dict:
        """Search for best parameter values taking into account parameter bounds specified in the model.

        :param learning_skiprows: starting row from the measurement csv file to use for best parameter search, defaults to 0
        :type learning_skiprows: int, optional
        :param learning_nrows: endding row from the measurement csv file to use for best parameter search, defaults to 60*24
        :type learning_nrows: int, optional
        :param strategy: see https://docs.scipy.org/doc/scipy-0.15.1/reference/generated/scipy.optimize.differential_evolution.html, defaults to 'best1bin'
        :type strategy: int, optional
        :param maxiter: see https://docs.scipy.org/doc/scipy-0.15.1/reference/generated/scipy.optimize.differential_evolution.html, defaults to 100
        :type maxiter: int, optional
        :param popsize: see https://docs.scipy.org/doc/scipy-0.15.1/reference/generated/scipy.optimize.differential_evolution.html, defaults to 50
        :type popsize: int, optional
        :param tol: see https://docs.scipy.org/doc/scipy-0.15.1/reference/generated/scipy.optimize.differential_evolution.html, defaults to 0.01
        :type tol: float, optional
        :param mutation: see https://docs.scipy.org/doc/scipy-0.15.1/reference/generated/scipy.optimize.differential_evolution.html, defaults to (0.5, 1)
        :type mutation: tuple[float], optional
        :param recombination: see https://docs.scipy.org/doc/scipy-0.15.1/reference/generated/scipy.optimize.differential_evolution.html, defaults to 0.7
        :type recombination: float, optional
        :param seed: see https://docs.scipy.org/doc/scipy-0.15.1/reference/generated/scipy.optimize.differential_evolution.html, defaults to None
        :type seed: int, optional
        :param callback: see https://docs.scipy.org/doc/scipy-0.15.1/reference/generated/scipy.optimize.differential_evolution.html, defaults to None
        :type callback: float, optional
        :param disp: see https://docs.scipy.org/doc/scipy-0.15.1/reference/generated/scipy.optimize.differential_evolution.html, defaults to True
        :type disp: bool, optional
        :param updating: see https://docs.scipy.org/doc/scipy-0.15.1/reference/generated/scipy.optimize.differential_evolution.html, defaults to 'deferred'
        :type updating: str, optional
        :param polish: see https://docs.scipy.org/doc/scipy-0.15.1/reference/generated/scipy.optimize.differential_evolution.html, defaults to True
        :type polish: bool, optional
        :param init: see https://docs.scipy.org/doc/scipy-0.15.1/reference/generated/scipy.optimize.differential_evolution.html, defaults to 'latinhypercube'
        :type init: str, optional
        :param workers: see https://docs.scipy.org/doc/scipy-0.15.1/reference/generated/scipy.optimize.differential_evolution.html, defaults to -1
        :type workers: int, optional
        :param stete_observer: use or not a state observer to estimate the state a the beginning of each day, default is False
        :type state_observer: bool
        :param plot_results: True if results should be plotted, default is True
        :type plot_results: bool
        :return: result with 'name', 'bounds', 'initial', 'initial error', 'final', 'final error', 'duration' (and 'Tins_mu/sigma', 'Cins_mu/sigma' if sensitivity analysis is performed) as keys and values according to parameter names
        :rtype: dict[str,float|dict[str,list[str|float]]]
        """
        self.model.register_data(self.data_container)
        results = dict()
        adjustables = self.model.adjustables
        results['name'] = adjustables
        adjustables_bounds = self.model.pbound(adjustables)
        adjustables_bounds_str = ['(%.5f,%.5f)' % t for t in self.model.pbound(adjustables)]

        results['bounds'] = adjustables_bounds
        initial_parameter_values = list(self.model.pval(self.model.adjustables))
        results['initial'] = initial_parameter_values
        results['initial error'] = self.cost_function(initial_parameter_values)
        if perform_sensitivity_analysis:
            sa_results = self.sensitivity(number_of_trajectories=maxiter, number_of_levels=4, state_observer=False, plot_results=False)
            results['Tins_mu/sigma'] = list()
            results['Cins_mu/sigma'] = list()
            for parameter_name in adjustables:
                i = sa_results['Tins']['names'].index(parameter_name)
                results['Tins_mu/sigma'].append('%.5f / %.5f' % (sa_results['Tins']['mu'][i], sa_results['Tins']['sigma'][i]))
                i = sa_results['Cins']['names'].index(parameter_name)
                results['Cins_mu/sigma'].append('%.5f / %.5f' % (sa_results['Cins']['mu'][i], sa_results['Cins']['sigma'][i]))

        init_time = time.time()
        # see https://docs.scipy.org/doc/scipy-0.15.1/reference/generated/scipy.optimize.differential_evolution.html
        result = scipy.optimize.differential_evolution(self.cost_function, adjustables_bounds,
                                                       strategy=strategy, maxiter=maxiter, popsize=popsize, tol=tol, mutation=mutation, recombination=recombination, seed=seed, callback=callback, disp=disp, updating=updating, polish=polish, init=init, workers=workers)
        results['duration'] = time.time() - init_time
        better_parameter_values = tuple(result.x)
        results['final'] = better_parameter_values
        self.model.adjustables = better_parameter_values
        results['final error'] = self.cost_function(better_parameter_values)
        contact = []
        for pname in adjustables:
            if abs(self.model.pval(pname)-self.model.pbound(pname)[0]) < 1e-2 * abs(self.model.pbound(pname)[0]):
                contact.append('<')
            elif abs(self.model.pval(pname)-self.model.pbound(pname)[1]) < 1e-2 * abs(self.model.pbound(pname)[1]):
                contact.append('>')
            else:
                contact.append('-')
        self.model.save_parameters(self.pickle_file_name)
        if perform_sensitivity_analysis:
            column_names = ['name', 'initial', 'final', 'bounds', 'contact', 'Tins_mu/sigma', 'Cins_mu/sigma']
        else:
            column_names = ['name', 'initial', 'final', 'bounds', 'contact']
        ptable = PrettyTable()
        ptable.set_style(MSWORD_FRIENDLY)
        for column_name in column_names:
            if column_name == "bounds":
                ptable.add_column('bounds', adjustables_bounds_str)
            elif column_name == 'contact':
                ptable.add_column('contact', contact)
            else:
                ptable.add_column(column_name, [results[column_name][i] for i in range(len(adjustables))])
            ptable.float_format[column_name] = ".4"
        print(ptable)
        print('Error from %f to %f (duration %s seconds)' % (results['initial error'], results['final error'], results['duration']))

        if plot_results:
            print('* Validation starts')
            self.model.register_data(validation_data_container)
            office_temperatures, office_CO2s, office_temperature_setpoints, heater_powers, door_openings, window_openings, estimated_outputs = self.simulator.simulate(h358simulator.CONTROL.NONE, use_state_observer=self.use_state_observer)
            validation_data_container.add_external_variable('Tin_better', office_temperatures)
            validation_data_container.add_external_variable('Cin_better', office_CO2s)
            validation_data_container.add_external_variable('heater_powers', heater_powers)
            validation_data_container.plot()
        return results

    def cost_function(self, pvals) -> float:
        """Compute cost function to combine average absolute simulation errors dealing with simulated indoor temperature and CO2 concentration.

        :param pvals: parameter values corresponding to adjustable parameters
        :type pvals: list[float]
        :return: simulation error
        :rtype: float
        """
        self.simulator.model.adjustables =  pvals
        Tins, Cins, Tin_setpoints, heating_powers, door_openings, window_openings, estimated_outputs = self.simulator.simulate(h358simulator.CONTROL.NONE, )
        temperature_error = ModelFitter.avg_error(self.simulator.model.data('Toffice_reference'), Tins)
        CO2_error = ModelFitter.avg_error(self.simulator.model.data('office_CO2_concentration'), Cins)
        return (temperature_error + CO2_error / 200) / 2

    @staticmethod
    def avg_error(values, ref_values) -> float:
        """Compute average error computed as the sum of the absolute differences between 2 vectors of the same length.

        :param values: the 1st vector
        :type values: list[float]
        :param ref_values: the 2nd vector
        :type ref_values: list[float]
        :return: the error
        :rtype: float
        """
        return sum([abs(values[i]-ref_values[i]) for i in range(len(values))]) / len(values)

if __name__ == '__main__':
    learning_data_container = buildingenergy.measurements.DataContainer('h358data_winter2015-2016.csv', skiprows=0, nrows=24*60)
    validation_data_container = buildingenergy.measurements.DataContainer('h358data_winter2015-2016.csv')

    h358_model = h358model.H358Model(sampling_time_in_secs=3600, input_variable_names = ('Tcorridor', 'Tout', 'free_gain_power', 'corridorCCO2', 'outCCO2', 'occupancy'), influencing_variable_names = ('door_opening', 'window_opening'), possible_action_variable_names = ('door_opening', 'window_opening', 'heating_power', 'temperature_setpoint'), output_variable_names = ('Toffice_reference', 'office_CO2_concentration'), power_gain_variable_name='free_gain_power')
    h358_model.register_data(learning_data_container)

    #h358_model.register_state_space_representation(('tau2', 'Cin'), h358_model.compute_physical_matrices_order1_fast)
    h358_model.register_state_space_representation(('tau1', 'Cin'), h358_model.compute_physical_matrices_order1_slow)
    #h358_model.register_state_space_representation(('tau1', 'tau2', 'Cin'), h358_model.compute_physical_matrices_order2)
    simulator = h358simulator.Simulator(h358_model)

    model_fitter = ModelFitter(simulator, learning_data_container, pickle_file_name_suffix='best_parameters.p')
    model_fitter.adjust_parameters(validation_data_container, strategy='best1bin', maxiter=50, popsize=50, tol=0.01, mutation=(0.5, 1), recombination=0.7, seed=None, callback=None, disp=True, updating='deferred', polish=True, init='latinhypercube', workers=-1, perform_sensitivity_analysis=True)
