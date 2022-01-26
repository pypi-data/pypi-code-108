"""A helper module dedicated to the deisgn of time-varying state space model approximated by bililear state space model.

Author: stephane.ploix@grenoble-inp.fr
"""

from abc import abstractmethod
import scipy.signal
import pickle
import os
import math
import numpy
from numpy import array, dot
from itertools import product


class StateMatrix:
    """State Matrix is representing a matrix with possible variations depending on influencing variable values.

    For instance, consider the M(x1, x2, x3,...) matrix where theta contains so-called influencing variables and xi in [0, 1]. To reduce calculations, M(x1, x2, x3,...) # M(0, 0, 0,...) + D{1, 0, 0,...} x1 + D{0, 1, 0,...} x2 +D{0, 0, 1,...} x3 + D{1, 1, 0,...} x1 x2 + D{1, 0, 1,...} x1 x3 + D{0, 1, 1,...} x2 x3 + D{1, 1, 1,...} x1 x2 x3 +...
    """

    def __init__(self, name, influencing_variable_names, matrix_at_maximum_influence_dict):
        """Create a state matrix with a nominal array. Variations according influencing variables are assumed to be additive. The nominal matrix is returned when all the variable values are set to 0. The maximum variation of the matrix wrt a given variable is obtained when the specified maximum value is reached.

        :param name: name of the time-varying matrix
        :type name: str
        :param influencing_variable_names: names of the normalized variables affecting the matrix
        :type influencing_variable_names: tuple[str]
        :param matrix_at_maximum_influence_dict: a dictionary of tuples with indices of influencing variables and resulting array when the influencing variables equal to 1 (maximum value)
        :type matrix_at_maximum_influence_dict: dict[tuple[int],numpy.array]
        """
        self.name = name
        self.influencing_variable_names = influencing_variable_names
        nominal_influence = tuple([0 for _ in range(len(influencing_variable_names))])
        self._nominal_array = numpy.copy(matrix_at_maximum_influence_dict[nominal_influence])
        self.delta_matrices_dict = dict()
        for influence in matrix_at_maximum_influence_dict.keys():
            if sum(influence) > 0:
                self.delta_matrices_dict[influence] = numpy.copy(matrix_at_maximum_influence_dict[influence]) - self._nominal_array

        delta_depth = 1
        while delta_depth <= len(influencing_variable_names):
            for influence in self.delta_matrices_dict:
                if sum(influence) < delta_depth:
                    for existing_influence in self.delta_matrices_dict:
                        if StateMatrix._is_included(existing_influence, influence, True):
                            self.delta_matrices_dict[influence] -= self.delta_matrices_dict[existing_influence]
            delta_depth += 1

    @staticmethod
    def _is_included(candidate_tuple, reference_tuple, accept_equality=True):
        """Check whether a tuple in included into another one.

        For instance, (0, 1, 1, 0) is included into (0, 1, 1, 1) but the opposite is false.
        If accept_equality is True (default) (0, 1, 1, 0) is included into (0, 1, 1, 0), if not accept_equality, it's no longer True.

        :param candidate_tuple: tuple to be tested
        :type candidate_tuple: tuple
        :param reference_tuple: reference tuple
        :type reference_tuple: tuple
        :param accept_equality: allows the equality of tuples, defaults to True
        :type accept_equality: bool, optional
        :return: result of the test
        :rtype: bool
        """
        for i in range(len(candidate_tuple)):
            if candidate_tuple[i] > reference_tuple[i]:
                return False
        if not accept_equality and sum(candidate_tuple) == sum(reference_tuple):
            return False
        return True

    def nominal(self):
        """Return the nominal state matrix.

        :return: nominal state matrix i.e. the one corresponding to nul influencing variables
        :rtype: numpy.array
        """
        return self._nominal_array

    def influencing_variable_names(self):
        """List of the variables influencing the matrix.

        :return: names of the influencing variables
        :rtype: tuple[str]
        """
        return self.influencing_variable_namesi

    def get(self, influencing_variable_values):
        """Return the matrix taking into account the influencing variable values.

        :param influencing_variable_values: variable names and their current value. If a variable is not present, its value is considered equal to 0. If a variable name has not been mentioned among the infuencing variables, it's ignored. defaults to None
        :type influencing_variable_values: list[float]
        :return: the current matrix value
        :rtype: numpy.array
        """
        current_influences = tuple([int(v > 0) for v in influencing_variable_values])
        matrix = numpy.copy(self.nominal())
        for influences in self.delta_matrices_dict:
            if StateMatrix._is_included(influences, current_influences):
                coef = 1
                for i in range(len(influences)):
                    if influences[i]:
                        coef = coef * influencing_variable_values[i]
                matrix += coef*self.delta_matrices_dict[influences]
        return matrix

    def __str__(self):
        """Return a description of the state matrix.

        :return: description of the state matrix
        :rtype: str
        """
        string = '\nmatrix %s =' % self.name
        for influences in self.delta_matrices_dict:
            variables = ''
            for i in range(len(influences)):
                if influences[i]:
                    variables += self.influencing_variable_names[i] + '*'
            string += '\n' + variables + '\n' + str(self.delta_matrices_dict[influences])
        return string

class Model:
    """Describe a linear time-varying model based on state space representation."""

    def __init__(self, sampling_time_in_secs, input_variable_names, influencing_variable_names, possible_action_variable_names, output_variable_names, power_gain_variable_name, display):
        """Create a linear time-varying dynamic model described by one or several alternative state space representation sharing the same linear inputs, the same inluencing variables affacting the state matrices and the same output. Parameter can be modified within bounds and a kind of filter is also recorded to transform measurement csv file and weather file into data.

        :param sampling_time_in_secs: the sampling time in seconds for the model to operate
        :type sampling_time_in_secs: int
        :param input_variable_names: list of the input variables intervening in a linear way
        :type input_variable_names: list[str]
        :param influencing_variable_names: list of the input variables influencing the state matrices i.e. corresponding to nonlinearities
        :type influencing_variable_names: list[str]
        :param influencing_variable_max_values: maximum values, respecting the order of the listed influencing variables. It corresponds to the maximum matrix deviations
        :typr influencing_variable_max_values: list[float]
        :param state_variable_names: list of the state space variables
        :type state_variable_names: list[str]
        :param output_variable_names: list of the output variables
        :type output_variable_names: list[str]
        :param power_gain_variable_name: name of the variable standing for the power gain. It must be part of the input variables
        :type power_gain_variable_name: str
        """
        self.sampling_time_in_secs = sampling_time_in_secs
        self._parameters_dict = dict()
        self.input_variable_names = input_variable_names
        self.influencing_variable_names = influencing_variable_names
        self.possible_action_variable_names = possible_action_variable_names
        self.output_variable_names = output_variable_names
        self.power_gain_index = input_variable_names.index(power_gain_variable_name)
        self.representation_state_variables = dict()
        self.state_variable_names: list[str] = None
        self.state_matrice_generator: function = None
        self.parameter_calculations(display)

    @abstractmethod
    def register_data(self, data_container, openweather_file_name):
        """Store measurement data and weather data read respectively from a DataContainer and an OpenWeather objects.

        The DataContainer should be saved as self.data_container to get the plotting capabilities. The useful data must be stored into a [str, list[float]] dictionnary: self._data. Weather data from the provided file name will be added to the data container if dates match measurements data

        :param data_container: data container containing measurement and weather data to work with the model
        :type data_container: measurements.DataContainer
        :param openweather_file_name: name of the open weather json file containing weather data
        :type openweather_file_name: str
        """
        raise NotImplemented

    def data(self, measurement_name):
        """Return measurements corresponding to a name.

        :param measurement_name: name of the measurement
        :type measurement_name: str
        :return: measurement data
        :rtype: list[float]
        """
        return self._data[measurement_name]

    @abstractmethod
    def parameter_calculations(self, display):
        """Abstract method that must be implemented to calculate model parameters and possibly record them with self.param and self.set_bound for parameter adjustement."""
        raise NotImplemented

    def register_state_space_representation(self, state_variables, state_matrice_generator):
        """Inherited method that register state space representations matching the specified input, influence and output variables.

        :param state_variables: list of the state variable names
        :type: tuple[str]
        :param matrice_generator: a function generating 4 continuous time state matrices A, B, C and D, each one represented by a StateMatrix
        :type matrice_generator: function
        """
        self.state_variable_names = state_variables
        self.state_matrice_generator = state_matrice_generator

    def initialize(self, use_state_observer=False):
        """Update the calculation of state matrices.

        Useful if parameters have been updated. It calls the init method of the subclass for specific calculation that returns an initial state vector.

        :param use_state_observer: True if a state observer should be used, default to False.
        :type use_state_observer: bool
        """
        self.Ad_state_matrix, self.Bd_state_matrix, self.Cd_state_matrix, self.Dd_state_matrix = self.discrete_state_matrices()
        if use_state_observer:
            self.K = self.matrix_K_state_observer()
        return self.init()

    @abstractmethod
    def matrix_K_state_observer(self):
        """Return the gain matrix K for the state observer. (abstract method)

        :return: the gain matrix
        :rtype: numpy.array"""
        raise NotImplemented

    @abstractmethod
    def init(self):
        """Use to initialize a simulation (intial state vector,...).

        :return: initial state vactor
        :rtype: numpy.array
        """
        pass

    @abstractmethod
    def register_data(self, measurement_file_name, weather_file_name, skiprows=0, nrows=None):
        """Store measurement data and weather data read respectively from a DataContainer and an OpenWeather objects. The DataContainer should be saved as self.data_container to get the plotting capabilities. The useful data must be stored into a [str, list[float]] dictionnary: self._data.

        :param measurement_file_name: csv file name containing measurement data from office
        :type measurement_file_name: str
        :param weather_file_name: json file name coming from openweather
        :type weather_file_name: str
        :param skiprows: list-like or integer Row numbers to skip (0-indexed) or number of rows to skip (int) at the start of the file
        :type skiprows: int, default is 0
        :param nrows: Number of rows of file to read. Useful for reading pieces of large files. Default is None
        :type nrows: int
        """
        raise NotImplemented

    def save_parameters(self, pickle_file_name):
        """Save current parameter values into a pickle file.

        :param pickle_file_name: name of the pickle file
        :type pickle_file_name: str
        """
        name_value_bounds_dict = dict()
        for name in self._parameters_dict:
            name_value_bounds_dict[name] = [self._parameters_dict[name].val, self._parameters_dict[name].bounds]
        with open(pickle_file_name, "wb") as file:
            pickle.dump(name_value_bounds_dict, file)

    def load_parameters(self, parameters_filename):
        """Load parameter values from a pickle file: these values will replace the nominal ones.

        :param parameters_filename: name of the file, defaults to 'best_parameters.p'
        :type parameters_filename: str, optional
        """
        if os.path.exists(parameters_filename):
            self._parameters_dict.clear()
            with open(parameters_filename, 'rb') as file:
                name_value_bounds_dict = pickle.load(file)
            for name in name_value_bounds_dict:
                self.param(name, name_value_bounds_dict[name][0], name_value_bounds_dict[name][1])

    class _Parameter:
        """Inner class containing data about a parameter."""

        def __init__(self, _name_parameter_dict, name, value=None, bounds=None):
            """Create a parameter and register it into the dictionary of all registered parameters.

            :param _name_parameter_dict: dictionary of existing parameters
            :type _name_parameter_dict: dict[str, buildingenergy.Model._Parameter]
            :param name: name of the parameter
            :type name: str
            :param value: current value for the parameter, defaults to None
            :type value: float, optional
            :param bounds: extrement possible values for the parameter, defaults to None
            :type bounds: tuple[float], optional
            """
            self._name_parameter_dict = _name_parameter_dict
            self._name = name
            self._value = value
            self._initial_value = value
            self._bounds = bounds
            self._name_parameter_dict[name] = self

        @property
        def name(self):
            """Return the name of the parameter.

            :return: name of the parameter
            :rtype: str
            """
            return self._name

        def __call__(self, inf, sup):
            self._bounds = (inf, sup)

        @property
        def val(self):
            """Return the current parameter value.

            :return: the current parameter value
            :rtype: float
            """
            return self._value

        @val.setter
        def val(self, value):
            """Set parameter value.

            :param value: value
            :type value: float
            """
            self._value = value

        @property
        def bounds(self):
            """Return bounds for possible parameter values.

            :return: tuple with inferior and superior bounds
            :rtype: tuple[float]
            """
            return self._bounds

        @bounds.setter
        def bounds(self, bounds):
            """Set bounds for possible parameter values.

            :param bounds: [description]
            :type bounds: [type]
            """
            self._bounds = bounds

        @property
        def all(self):
            """Return the names of the parameters.

            :return: list of names
            :rtype: list[st]
            """
            return self._name_parameter_dict

        @all.setter
        def all(self, parameters_dict):
            """Set all the parameters at once.

            :param parameters_dict: dictionary with parameter names as keys and Parameter object as values
            :type parameters_dict: dict[str, Parameter]
            """
            self._name_parameter_dict = parameters_dict

        def __str__(self):
            """Return a description of a parameter.

            :return: a descriptive string.
            :rtype: str
            """
            if self.bounds:
                if self._initial_value is None:
                    return '%s=%f in (%f,%f)' % (self._name, self._value, self._bounds[0], self._bounds[1])
                else:
                    return '%s=%f (init. %f) in (%f,%f)' % (self._name, self._value, self._initial_value, self._bounds[0], self._bounds[1])
            else:
                if self._initial_value is None:
                    return '%s=%f' % (self._name, self._value)
                else:
                    return '%s=%f (%f)' % (self._name, self._value, self._initial_value)

    def param(self, parameter_name, value=None, bounds=None):
        """Create a constant potentially ajustable parameter whose value can be invariant or can vary within bounds.

        :param parameter_name: name of the parameter
        :type parameter_name: str
        :param value: nominal value of the parameter
        :type value: float
        :param bounds: interval for the possible parameter values. If None, it's value will not be adjusted. Defaults to None.
        :type bounds: tuple[float], optional
        """
        return Model._Parameter(self._parameters_dict, parameter_name, value, bounds)

    def pval(self, parameter_names):
        """Return requested parameter values.

        :param parameter_names: name of the requested parameter values
        :type parameter_names: str or list[str]
        :return: the requested parameter values as a float or a list of float, depending on how the parameter names have been specified
        :rtype: float or list[float]
        """
        if type(parameter_names) == str:
            return self._parameters_dict[parameter_names].val
        else:
            pvals = list()
            for parameter_name in parameter_names:
                pvals.append(self._parameters_dict[parameter_name].val)
            return pvals

    def pbound(self, parameter_names):
        """Return requested parameter bounds.

        :param parameter_names: name(s) of the requested parameter bounds
        :type parameter_names: str or list[str]
        :return: parameter bounds as tuples or None value if the parameter cannot be adjusted
        :rtype: tuple[float] or list[tuple[float]]
        """
        if type(parameter_names) == str:
            return self._parameters_dict[parameter_names].bounds
        else:
            _pbounds = list()
            for parameter_name in parameter_names:
                _pbounds.append(self._parameters_dict[parameter_name].bounds)
            return _pbounds

    @property
    def parameters(self):
        """Return the list of recorded parameter names.

        :return: list of recorded parameter names
        :rtype: list[str]
        """
        return list(self._parameters_dict.keys())

    @property
    def adjustables(self):
        """List of adjustable parameter names i.e. the one whose bounds are not None.

        :return: list of adjustable parameter names
        :rtype: list[str]
        """
        _adjustable_parameters = list()
        for parameter in self._parameters_dict:
            if self._parameters_dict[parameter].bounds is not None:
                _adjustable_parameters.append(parameter)
        return _adjustable_parameters

    @adjustables.setter
    def adjustables(self, values):
        """Set all the values of adjustable parameters at once.

        :param values: list of values ordered according to the list of names returned by the methods 'self.parameters'.
        :type values: list[float]
        """
        _adjustables = self.adjustables
        for i in range(len(_adjustables)):
            self._parameters_dict[_adjustables[i]].val = values[i]

    def discrete_state_matrices(self):
        """Discretized registered state matrices (with method self.register_state_space_representation()).

        It's a function whose prototype must comply with compute_matrices(model: Model, influencing_variable_values: list[float]). It receives a model where registered parameters recorded by param can be obtained by model.pval('parameter_name'). The influencing variable values are provided according to the order given at the initialisation of the Model object. It returns the state space matrices obtained for the specified values of influencing variables: it must return the time continuous matrices A, B, C, D as a list[list[float]]].

        :return: matrices of the discrete time state space model taking into account linearized influence of influencing variables
        :rtype: tuple[StateMatrix]
        """
        list_of_influences =  list(product(range(0, 2), repeat=len(self.influencing_variable_names)))
        influenced_Ad_dict = dict()
        influenced_Bd_dict = dict()
        influenced_Cd_dict = dict()
        influenced_Dd_dict = dict()
        for influences in list_of_influences:
            A_tab, B_tab, C_tab, D_tab = self.state_matrice_generator(influences)
            Ad, Bd, Cd, Dd, _ = scipy.signal.cont2discrete((array(A_tab), array(B_tab), array(C_tab), array(D_tab)), self.sampling_time_in_secs, method='zoh')
            influenced_Ad_dict[influences] = Ad
            influenced_Bd_dict[influences] = Bd
            influenced_Cd_dict[influences] = Cd
            influenced_Dd_dict[influences] = Dd
        Ad_state_matrix = StateMatrix('Ad', self.influencing_variable_names, influenced_Ad_dict)
        Bd_state_matrix = StateMatrix('Bd', self.influencing_variable_names, influenced_Bd_dict)
        Cd_state_matrix = StateMatrix('Cd', self.influencing_variable_names, influenced_Cd_dict)
        Dd_state_matrix = StateMatrix('Dd', self.influencing_variable_names, influenced_Dd_dict)

        return Ad_state_matrix, Bd_state_matrix, Cd_state_matrix, Dd_state_matrix

    @abstractmethod
    def computeU(self, k: int, state_vector, influencing_variable_values, actions={}):
        """Compute the vector U of the state space representation together with the heating power, that can be the one that has been recorded or deduced from the temperature setpoint (assuming a perfect controller, with a one hour perspective).

        :param k: hour index
        :type k: int
        :param state_vector: current state vector used to determine the heating power in case a setpoint is specified in the actions
        :type state_vector: numpy.array
        :param influencing_variable_values: list of values for influencing variable ordered according to the order given at initialization
        :type influencing_variable_values: list[float]
        :param actions: list of current actions performaed on the system. It might contains in particular here 'heating_power' in case it's directly controlled, and 'temperature_setpoint' in case of an indirect control of the heating power by specifying the temperature setpoint
        :type: dict[str, float]
        :return: the vector U of the state space representation together with the heating power and an array with current output values
        :rtype: tuple[array, float]
        """
        raise NotImplemented

    def stepX(self, k: int, state_vector, observer_state_vector, influencing_variable_values, input_variables):
        """Compute the next state variables according to the U vector and the specified actions.

        :param k: step number
        :type k: int
        :param state_vector: the current state vector usually denoted by X
        :type state_vector: numpy.array
        :param observer_state_vector: the current state vector of state observer, None if there is no state observer.
        :type observer_state_vector: numpy.array
        :param influencing_variable_values: list of the current influencing variable values ordered according to the list provided at Model creation.
        :type influencing_variable_values: list[float]
        :return: the next step state vector X (X_{k+1})
        :param input_variables: values of the U vector in state space model.
        :rtype: numpy.array
        """
        state_vector = dot(self.Ad_state_matrix.get(influencing_variable_values), state_vector) + dot(self.Bd_state_matrix.get(influencing_variable_values), input_variables)
        if observer_state_vector is not None:
            Ymeasured = array([[self.data(name)[k]] for name in self.output_variable_names])
            observer_state_vector = dot(self.Ad_state_matrix.get(influencing_variable_values) - dot(self.K, self.Cd_state_matrix.get(influencing_variable_values)), observer_state_vector) + dot(self.Bd_state_matrix.get(influencing_variable_values) - dot(self.K, self.Dd_state_matrix.get(influencing_variable_values)), input_variables) + dot(self.K, Ymeasured)
        return state_vector, observer_state_vector

    def computeY(self, k, state_vector, U, influencing_variables):
        """Compute the output vector Y of the state space representation.

        :param k: step number
        :type k: int
        :param state_vector: the current state vector usually named X
        :type state_vector: numpy.array
        :param U: the vector U of the state space representation
        :type U: numpy.array
        :param influencing_variables: list of the current influencing variables affecting the state matrices.
        :type influencing_variables: list[float]
        :return: the output vector Y
        :rtype: numpy.array
        """
        if influencing_variables is None:
            influencing_variables = tuple([0 for _ in range(len(self.influencing_variable_names))])
        return dot(self.Cd_state_matrix.get(influencing_variables), state_vector) + dot(self.Dd_state_matrix.get(influencing_variables), U)

    def __str__(self):
        """Return a description of the model.

        :return: A desciption as a string.
        :rtype: str
        """

        string = '* input variables: '
        for input_variable_name in self.input_variable_names:
            string += '%s,' % input_variable_name
        string += '\n* influencing variables: '
        for influencing_variable_name in self.influencing_variable_names:
            string += '%s,' % influencing_variable_name
        if self.state_variable_names is None:
            string
        string += '\n* state variables: '
        if self.state_variable_names is None:
            string += 'Not defined'
        else:
            for state_variable_name in self.state_variable_names:
                string += '%s,' % state_variable_name
        string += '\n* output variables: '
        for output_variable_name in self.output_variable_names:
            string += '%s,' % output_variable_name
        string += '\n* parameters: '
        for parameter_name in self._parameters_dict:
            string += '%s=%f' % (parameter_name, self._parameters_dict[parameter_name].val)
            if self._parameters_dict[parameter_name].bounds is not None:
                string += '(%f,%f)' % (self._parameters_dict[parameter_name].bounds[0], self._parameters_dict[parameter_name].bounds[1])
            string += "\n"
        return string


class Preference:
    """Provide de a model of the occupants'preferences. It deals with thermal comfort, air quality, number of home configuration changes, energy cost, icone,..."""

    def __init__(self, preferred_temperatures=(21, 23), extreme_temperatures=(18, 26), preferred_CO2_concentration=(500, 1500), temperature_weight_wrt_CO2: float = 0.5, power_weight_wrt_comfort: float = 0.5e-3):
        """Definition of comfort regarding  number of required actions by accupants, temperature and CO2 concentration, but also weights between cost and comfort, and between thermal and air quality comfort.

        :param preferred_temperatures: preferred temperature range, defaults to (21, 23)
        :type preferred_temperatures: tuple, optional
        :param extreme_temperatures: limits of acceptable temperatures, defaults to (18, 26)
        :type extreme_temperatures: tuple, optional
        :param preferred_CO2_concentration: preferred CO2 concentration range, defaults to (500, 1500)
        :type preferred_CO2_concentration: tuple, optional
        :param temperature_weight_wrt_CO2: relative importance of thermal comfort wrt air quality (1 means only temperature is considered), defaults to 0.5
        :type temperature_weight_wrt_CO2: float, optional
        :param power_weight_wrt_comfort: relative importance of energy cost wrt comfort (1 means only energy cost is considered), defaults to 0.5e-3
        :type power_weight_wrt_comfort: float, optional
        """
        self.preferred_temperatures = preferred_temperatures
        self.extreme_temperatures = extreme_temperatures
        self.preferred_CO2_concentration = preferred_CO2_concentration
        self.temperature_weight_wrt_CO2 = temperature_weight_wrt_CO2
        self.power_weight_wrt_comfort = power_weight_wrt_comfort

    def change_dissatisfaction(self, occupancy, action_set):
        """Compute the ratio of the number of hours where occupants have to change their home configuration divided by the number of hours with presence.

        :param occupancy: a vector of occupancies
        :type occupancy: list[float]
        :param action_set: different vectors of actions
        :type action_set: tuple[list[float]]
        :return: the number of hours where occupants have to change their home configuration divided by the number of hours with presence
        :rtype: float
        """
        number_of_changes = 0
        number_of_presences = 0
        previous_actions = [actions[0] for actions in action_set]
        for k in range(len(occupancy)):
            if occupancy[k] > 0:
                number_of_presences += 1
                for i in range(len(action_set)):
                    actions = action_set[i]
                    if actions[k] != previous_actions[i]:
                        number_of_changes += 1
                        previous_actions[i] = actions[k]
        return number_of_changes / number_of_presences if number_of_presences > 0 else 0

    def thermal_comfort_dissatisfaction(self, temperatures, occupancies):
        """Compute average dissatisfaction regarding thermal comfort: 0 means perfect and greater than 1 means not acceptable. Note that thermal comfort is only taken into account if occupancy > 0, i.e. in case of presence.

        :param temperatures: vector of temperatures
        :type temperatures: list[float]
        :param occupancies: vector of occupancies (number of people per time slot)
        :type occupancies: list[float]
        :return: average dissatisfaction regarding thermal comfort
        :rtype: float
        """
        if type(temperatures) is not list:
            temperatures = [temperatures]
            occupancies = [occupancies]
        dissatisfaction = 0
        for i in range(len(temperatures)):
            if occupancies[i] != 0:
                if temperatures[i] < self.preferred_temperatures[0]:
                    dissatisfaction += (self.preferred_temperatures[0] - temperatures[i]) / (self.preferred_temperatures[0] - self.extreme_temperatures[0])
                elif temperatures[i] > self.preferred_temperatures[1]:
                    dissatisfaction += (temperatures[i] - self.preferred_temperatures[1]) / (self.extreme_temperatures[1] - self.preferred_temperatures[1])
        return dissatisfaction / len(temperatures)

    def air_quality_dissatisfaction(self, CO2_concentrations, occupancies):
        """Compute average dissatisfaction regarding air quality comfort: 0 means perfect and greater than 1 means not acceptable. Note that air quality comfort is only taken into account if occupancy > 0, i.e. in case of presence.

        :param CO2_concentrations: vector of CO2 concentrations
        :type CO2_concentrations: list[float]
        :param occupancies: vector of occupancies (number of people per time slot)
        :type occupancies: list[float]
        :return: average dissatisfaction regarding air quality comfort
        :rtype: float
        """
        if type(CO2_concentrations) is not list:
            CO2_concentrations = [CO2_concentrations]
            occupancies = [occupancies]
        dissatisfaction = 0
        for i in range(len(CO2_concentrations)):
            if occupancies[i] != 0:
                dissatisfaction += max(0., (CO2_concentrations[i] - self.preferred_CO2_concentration[0]) / (self.preferred_CO2_concentration[1] - self.preferred_CO2_concentration[0]))
        return dissatisfaction / len(CO2_concentrations)

    def comfort_dissatisfaction(self, temperatures, CO2_concentrations, occupancies):
        """Compute the comfort weighted dissatisfaction that combines thermal and air quality dissatisfactions: it uses the thermal_dissatisfaction and air_quality_dissatisfaction methods.

        :param temperatures: list of temperatures
        :type temperatures: list[float]
        :param CO2_concentrations: list of CO2 concentrations
        :type CO2_concentrations: list[float]
        :param occupancies: list of occupancies
        :type occupancies: list[float]
        :return: the global comfort dissatisfaction
        :rtype: float
        """
        return self.temperature_weight_wrt_CO2 * self.thermal_comfort_dissatisfaction(temperatures, occupancies) + (1 - self.temperature_weight_wrt_CO2) * self.air_quality_dissatisfaction(CO2_concentrations, occupancies)

    def cost(self, Pheat, kWh_price=.13):
        """Compute the heating cost.

        :param Pheat: list of heating power consumptions
        :type Pheat: list[float]
        :param kWh_price: tariff per kWh, defaults to .13
        :type kWh_price: float, optional
        :return: energy cost
        :rtype: float
        """
        if type(Pheat) is not list:
            Pheat = [Pheat]
        return sum(Pheat) / 1000 * kWh_price

    def icone(self, CO2_concentration, occupancy):
        """Compute the ICONE indicator dealing with confinement regarding air quality.

        :param CO2_concentration: list of CO2 conncentrations
        :type CO2_concentration: list[float]
        :param occupancy: list of occupancies
        :type occupancy: list[float]
        :return: value between 0 and 5
        :rtype: float
        """
        n_presence = 0
        n1_medium_containment = 0
        n2_high_containment = 0
        for k in range(len(occupancy)):
            if occupancy[k] > 0:
                n_presence += 1
                if 1000 <= CO2_concentration[k] < 1700:
                    n1_medium_containment += 1
                elif CO2_concentration[k] >= 1700:
                    n2_high_containment += 1
        f1 = n1_medium_containment / n_presence if n_presence > 0 else 0
        f2 = n2_high_containment / n_presence if n_presence > 0 else 0
        return 8.3 * math.log10(1 + f1 + 3 * f2)

    def assess(self, Pheater, temperatures, CO2_concentrations, occupancies) -> float:
        """Compute the global objective to minimise including both comforts and energy cost for heating.

        :param Pheater: list of heating powers
        :type Pheater: list[float]
        :param temperatures: list of temperatures
        :type temperatures: list[float]
        :param CO2_concentrations: list of CO2 concentrations
        :type CO2_concentrations: list[float]
        :param occupancies: list of occupancies
        :type occupancies: list[float]
        :return: objective value
        :rtype: float
        """
        return self.cost(Pheater) * self.power_weight_wrt_comfort + (1 - self.power_weight_wrt_comfort) * self.comfort_dissatisfaction(temperatures, CO2_concentrations, occupancies)

    def print_assessment(self, Pheat, temperatures, CO2_concentrations, occupancies, action_sets):
        """Print different indicateurs to appreciate the impact of a series of actions.

        :param Pheat: list of heating powers
        :type Pheat: list[float]
        :param temperatures: list of temperatures
        :type temperatures: list[float]
        :param CO2_concentrations: list of CO2 concentrations
        :type CO2_concentrations: list[float]
        :param occupancies: list of occupancies
        :type occupancies: list[float]
        :param actions: list of actions
        :type actions: tuple[list[float]]
        """
        print('- global objective: %s' % self.assess(Pheat, temperatures, CO2_concentrations, occupancies))
        print('- average thermal dissatisfaction: %.2f%%' % (self.thermal_comfort_dissatisfaction(temperatures, occupancies) * 100))
        print('- average CO2 dissatisfaction: %.2f%%' % (self.air_quality_dissatisfaction(CO2_concentrations, occupancies) * 100))
        print('- ICONE: %.2f' % (self.icone(CO2_concentrations, occupancies)))
        print('- average comfort dissatisfaction: %.2f%%' % (self.comfort_dissatisfaction(temperatures, CO2_concentrations, occupancies) * 100))
        print('- change dissatisfaction (number of changes / number of time slots with presence): %.2f%%' % (self.change_dissatisfaction(occupancies, action_sets) * 100))
        print('- heating cost: %s' % self.cost(Pheat))

        temperatures_when_presence = list()
        CO2_concentrations_when_presence = list()
        for i in range(len(occupancies)):
            if occupancies[i] > 0:
                temperatures_when_presence.append(temperatures[i])
                CO2_concentrations_when_presence.append(CO2_concentrations[i])
        if len(temperatures_when_presence) > 0:
            temperatures_when_presence.sort()
            CO2_concentrations_when_presence.sort()
            office_temperatures_estimated_presence_lowest = temperatures_when_presence[:math.ceil(len(temperatures_when_presence) * 0.1)]
            office_temperatures_estimated_presence_highest = temperatures_when_presence[math.floor(len(temperatures_when_presence) * 0.9):]
            office_co2_concentrations_estimated_presence_lowest = CO2_concentrations_when_presence[:math.ceil(len(CO2_concentrations_when_presence) * 0.1)]
            office_co2_concentrations_estimated_presence_highest = CO2_concentrations_when_presence[math.floor(len(CO2_concentrations_when_presence) * 0.9):]
            print('- average temperature during presence:', sum(temperatures_when_presence) / len(temperatures_when_presence))
            print('- average 10% lowest temperature during presence:', sum(office_temperatures_estimated_presence_lowest) / len(office_temperatures_estimated_presence_lowest))
            print('- average 10% highest temperature during presence:', sum(office_temperatures_estimated_presence_highest) / len(office_temperatures_estimated_presence_highest))
            print('- average CO2 concentration during presence:', sum(CO2_concentrations_when_presence) / len(CO2_concentrations_when_presence))
            print('- average 10% lowest CO2 concentration during presence:', sum(office_co2_concentrations_estimated_presence_lowest) / len(office_co2_concentrations_estimated_presence_lowest))
            print('- average 10% highest CO2 concentration during presence:', sum(office_co2_concentrations_estimated_presence_highest) / len(office_co2_concentrations_estimated_presence_highest))

    def __str__(self):
        """Return a description of the defined preferences.

        :return: a descriptive string of characters.
        :rtype: str
        """
        string = 'preference: temperature in %f<%f-%f>%f, concentrationCO2 %f>%f\n' % (self.extreme_temperatures[0], self.preferred_temperatures[0], self.preferred_temperatures[1], self.extreme_temperatures[1], self.preferred_CO2_concentration[0], self.preferred_CO2_concentration[1])
        string += '%.3f * cost + %.3f disT + %.3f disCO2' % (self.power_weight_wrt_comfort, (1-self.power_weight_wrt_comfort) * self.temperature_weight_wrt_CO2, (1-self.power_weight_wrt_comfort) * (1-self.temperature_weight_wrt_CO2))
        return string