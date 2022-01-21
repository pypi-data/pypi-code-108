"""Different simulatations of the H358 office: CONTROL.NONE re-simulated recorded inputs, CONTROL.RULE simulates taking into account action rules defined in  rules(), and CONTROL.DYNPROG computes optimate actions resulting from a "home-made" dynamic programing algorithm and simulates them. Action are discrete and not always allowed. For instance, door and window openings can be done in case of absence.

Author: stephane.ploix@grenoble-inp.fr
"""
from datetime import datetime
import numpy
import h358model
import buildingenergy
import h358measurements
from buildingenergy.model import Preference
import h358dynprog
from enum import Enum
from numpy import array, dot


class CONTROL(Enum):
    """Use to specified the type of simulation requested.

    CONTROL.NONE means pure simulation
    CONTROL.RULE means use control rules
    CONTROL.DYNPROG means use dynamic programming optimization algorithm
    """

    NONE = 1
    RULE = 2
    DYNPROG = 3


def rules(current_datetime: datetime, office_temperature: float, corridor_temperature: float, outdoor_temperature: float, office_CO2_concentration: float, corridor_CO2_concentration: float, occupancy: float, heating: bool = False):
    """Use to define rules used for rule based control. It receives variable values depicting the current context and must return set-points for control variables.

    :param datetime: current date
    :type datetime: date as a datetime.datetime
    :param office_temperature: office indoor temperature
    :type office_temperature: float
    :param corridor_temperature: corridor temperature
    :type corridor_temperature: float
    :param outdoor_temperature: outdoor temperature
    :type outdoor_temperature: float
    :param office_CO2_concentration: office CO2 concentration
    :type office_CO2_concentration: float
    :param corridor_CO2_concentration: corridor CO2 concentration
    :type corridor_CO2_concentration: float
    :param occupancy: occupancy
    :type occupancy: float
    :param heating: True if the heating system is on during the current day, False otherwise
    :type heating: bool
    :return: window opening, door opening, temperature setpoint
    :rtype: tuple[float]
    """
    current_hour, _ = current_datetime.hour, current_datetime.minute
    if occupancy > 0:
        temperature_setpoint = 21
    else:
        temperature_setpoint = 13
    window_opening = 1
    door_opening = 1
    # if heating:
    #     if occupancy and current_hour <= 18 or current_hour >= 5:
    #         temperature_setpoint = 21
    #     else:
    #         temperature_setpoint = 13
    # if occupancy >= 0:
    #     if office_CO2_concentration > 1700:
    #         window_opening = 1
    #         if corridor_CO2_concentration < 1000:
    #             door_opening = 1
    #     if office_CO2_concentration > 1200:
    #         window_opening = .5
    #         if corridor_CO2_concentration < 1000:
    #             door_opening = 1
    #     elif office_CO2_concentration > 1000:
    #         window_opening = 0
    #         if corridor_CO2_concentration < 1000:
    #             door_opening = 1
    #     else:  # office_CO2_concentration <= 1000
    #         if heating == 1:
    #             if outdoor_temperature >= 21 and office_temperature <= 21:
    #                 window_opening = 1
    #                 temperature_setpoint = 16
    #     if heating == 0 and office_temperature >= 21 and outdoor_temperature <= office_temperature:
    #         window_opening = 1
    #     if heating == 0 and office_temperature >= 21 and corridor_temperature <= office_temperature and corridor_CO2_concentration < office_CO2_concentration:
    #         door_opening = 1
    #     door_opening = 1
    #     window_opening = 1
    #     if current_datetime.weekday() < 5:
    #         temperature_setpoint = 25
    #     else:
    #         temperature_setpoint = 13
    return window_opening, door_opening, temperature_setpoint


class Simulator:
    """A simulator to estimate the outputs (indoor temperature and CO2 concentration) in the H358 office.

    It's based on a time-varying state space representation depicted in the provided Model and it simulates days one by one to make day anticipative control possible.
    """

    def __init__(self, model: buildingenergy.model.Model, preference=Preference()):
        """Initialize a simulator.

        :param model: a model containing parameterized state matrices and also offers an access to data
        :type model: buildingenergy.model.Model
        :param preference: assessment of inhabitant comfort and cost preference
        :type preference: buildingenergy.model.Preference
        """
        self.model = model
        self.day_step = int(24 * 3600 / model.sampling_time_in_secs)
        self.opening_bounds = (0, 1)
        self.temperature_setpoint_bounds = (13, 30)
        self.preference = preference

    def _simulate_day(self, control: CONTROL, day_index: int, state_vector: array, observer_state_vector: array, **day_actions):
        """Simulate a single day.

        :param control: type of control requested (CONTROL.NONE, CONTROL.RULE, CONTROL.DYNPROG)
        :type: int (or h358model.CONTROL)
        :param k: hour index for the beginning of the current day
        :type k: int
        :param state_vector: the state vector at the beginning of the current day
        :type state_vector: numpy.array
        :param observer_state_vector: the state vector at the state observer beginning of the current day
        :type observer_state_vector: numpy.array
        :param day_actions: list of the possible day actions (door_opening, window_opening, heating_power, temperature_setpoint
        :type day_actions: dict[str,list[float]]
        :return: state_vector at the end of the day, day_Tins for the whole day, day_Cins for the whole day, resulting_day_Tin_setpoints for the whole day, resulting_day_heating_powers for the whole day, resulting_day_door_openings for the whole day, resulting_day_window_openings  for the whole day
        :rtype: tuple[array]
        """
        day_Tins, day_Cins= [], []
        resulting_day_window_openings, resulting_day_door_openings, resulting_day_heating_powers, resulting_day_Tin_setpoints = [], [], [], []


        # determine weather the heating system is on during this day
        heating = False
        for k in range(day_index, day_index + self.day_step):
            if k < len(self.model.data('datetime')) and self.model.data('dT_heat')[k] > 2:
                    heating = True
        requested_actions = dict()
        requested_actions['window_opening'] = 0
        requested_actions['door_opening'] = 0
        requested_actions['heating_power'] = 0
        requested_actions['temperature_setpoint'] = None
        for k in range(day_index, day_index + self.day_step):
            if k < len(self.model.data('datetime')):
                if control == CONTROL.NONE:
                    requested_actions['window_opening'] = self.model.data('window_opening')[k]
                    requested_actions['door_opening'] = self.model.data('door_opening')[k]
                    requested_actions['heating_power'] = self.model.data('dT_heat')[k] * self.model.pval('heater_power_per_degree')
                    requested_actions['temperature_setpoint'] = None
                elif control == CONTROL.RULE:
                    influencing_variables = (0, 0)
                    U, requested_actions = self.model.computeU(k, state_vector, influencing_variables, requested_actions)
                    Y = self.model.computeY(k, state_vector, U, influencing_variables)
                    requested_actions['window_opening'], requested_actions['door_opening'], requested_actions['temperature_setpoint'] = rules(self.model.data('datetime')[k], Y[0, 0], self.model.data('Tcorridor')[k], self.model.data('Tout')[k], Y[1, 0], self.model.data('corridor_CO2_concentration')[k], self.model.data('occupancy')[k], heating)
                elif control == CONTROL.DYNPROG:
                    for day_action in day_actions:
                        requested_actions[day_action] = day_actions[day_action][k - day_index]

                influencing_variables = (requested_actions['door_opening'], requested_actions['window_opening'])
                U, requested_actions = self.model.computeU(k, state_vector, influencing_variables, requested_actions)
                Y = self.model.computeY(k, state_vector, U, influencing_variables)

                day_Tins.append(Y[0,0])
                day_Cins.append(Y[1,0])
                state_vector, observer_state_vector = self.model.stepX(k, state_vector, observer_state_vector, influencing_variables, U)
                resulting_day_window_openings.append(requested_actions['window_opening'])
                resulting_day_door_openings.append(requested_actions['door_opening'])
                resulting_day_heating_powers.append(requested_actions['heating_power'])
                resulting_day_Tin_setpoints.append(requested_actions['temperature_setpoint'])

        return state_vector, day_Tins, day_Cins, resulting_day_Tin_setpoints, resulting_day_heating_powers, resulting_day_door_openings, resulting_day_window_openings, observer_state_vector

    def simulate(self, control: CONTROL, use_state_observer: bool=False, state_resolutions=[.1, .1, 1]):
        """Simulate the whole period accordingly to the requested control type (NONE, RULE, DYNPROG).

        :param control: the type of control for the simulation
        :type control: CONTROL.NONE for pur simulation, CONTROL.RULE for rule-bassed control or CONTROL.DYNPROG for dynamic programming
        :param stete_observer: use or not a state observer to estimate the state a the beginning of each day, default is False
        :type state_observer: bool
        :return: whole period variable values for Tins, Cins, Tin_setpoints, heating_powers, door_openings, window_openings
        :rtype: tuple[list[float]]
        """
        state_vector = self.model.initialize(use_state_observer)
        if use_state_observer:
            observer_state_vector = numpy.copy(state_vector)
        else:
            observer_state_vector = None
        Tins, Cins, Tin_setpoints, heating_powers, door_openings, window_openings = [], [], [], [], [], []
        estimated_outputs = None
        for day_index in range(0, len(self.model.data('datetime')), self.day_step):
            day_window_openings = None
            day_door_openings = None
            day_temperature_setpoints = None

            if control == CONTROL.DYNPROG:
                dynamic_programming = h358dynprog.DayDynamicProgramming(self.model, state_vector, day_index, state_resolutions = state_resolutions, preference=self.preference)
                results = dynamic_programming.results

                day_door_openings = results['door_opening']
                day_window_openings = results['window_opening']
                day_temperature_setpoints = results['temperature_setpoint']
                if estimated_outputs is None:
                    estimated_outputs = results['estimated_outputs']
                else:
                    estimated_outputs = numpy.concatenate((estimated_outputs, results['estimated_outputs']), axis=1)

            state_vector, day_Tins, day_Cins, resulting_day_temperature_setpoints, resulting_day_heating_powers, resulting_day_door_openings, resulting_day_window_openings, observer_state_vector = self._simulate_day(control, day_index, state_vector, observer_state_vector, window_opening=day_window_openings, door_opening=day_door_openings, temperature_setpoint=day_temperature_setpoints)
            if use_state_observer and control == CONTROL.NONE:
                state_vector = numpy.copy(observer_state_vector)
            Tins.extend(day_Tins)
            Cins.extend(day_Cins)
            Tin_setpoints.extend(resulting_day_temperature_setpoints)
            heating_powers.extend(resulting_day_heating_powers)
            door_openings.extend(resulting_day_door_openings)
            window_openings.extend(resulting_day_window_openings)
            if estimated_outputs is not None:
                estimated_outputs = estimated_outputs.tolist()
        return Tins, Cins, Tin_setpoints, heating_powers, door_openings, window_openings, estimated_outputs


if __name__ == '__main__':
    control_type = CONTROL.DYNPROG  # choose one among CONTROL.NONE, CONTROL.RULE or CONTROL.DYNPROG
    h358_model = h358model.H358Model(sampling_time_in_secs=3600, input_variable_names = ('Tcorridor', 'Tout', 'free_gain_power', 'corridorCCO2', 'outCCO2', 'occupancy'), influencing_variable_names = ('door_opening', 'window_opening'), possible_action_variable_names = ('door_opening', 'window_opening', 'heating_power', 'temperature_setpoint'), output_variable_names = ('Toffice_reference', 'office_CO2_concentration'), power_gain_variable_name='free_gain_power')
    #data_container = h358measurements.DataContainer('h358data_winter2015-2016.csv', skiprows=24*74, nrows=24*7)
    data_container = h358measurements.DataContainer('h358data_winter2015-2016.csv', initial_string_date='14/12/2015 00:00:00', final_string_date='21/12/2015 00:00:00')
    #data_container = h358measurements.DataContainer('h358data_winter2015-2016.csv', initial_string_date='1/09/2015 00:00:00', final_string_date='31/10/2015 23:00:00')
    h358_model.register_data(data_container)
    # h358model.register_state_space_representation(('tau2', 'Cin'), h358model.compute_physical_matrices_order1_fast)
    #h358_model.load_parameter_values('O1fast_best_parameters_ref.p')
    #h358model.register_state_space_representation(('tau1', 'Cin'), h358model.compute_physical_matrices_order1_slow)
    #h358_model.load_parameter_values('O1slow_best_parameters_ref.p')
    h358_model.register_state_space_representation(('tau1', 'tau2', 'Cin'), h358_model.compute_physical_matrices_order2)
    h358_model.load_parameters('O2_best_parameters_ref.p')

    preference = buildingenergy.model.Preference(preferred_temperatures=(21, 23), extreme_temperatures=(18, 26), preferred_CO2_concentration=(500, 1500), temperature_weight_wrt_CO2 = 0.1, power_weight_wrt_comfort = 1/3)
    simulator = Simulator(h358_model, preference=preference)
    office_temperatures, office_CO2s, office_temperature_setpoints, heater_powers, door_openings, window_openings, estimated_outputs = simulator.simulate(control_type, use_state_observer=True, state_resolutions=[.2, .2, 2])
    data_container.add_external_variable('Toffice_sim', office_temperatures)
    data_container.add_external_variable('office_CO2_sim', office_CO2s)
    data_container.add_external_variable('power_heater_sim', heater_powers)
    data_container.add_external_variable('door_opening_sim', door_openings)
    data_container.add_external_variable('window_opening_sim', window_openings)
    data_container.add_external_variable('Toffice_setpoint_sim', office_temperature_setpoints)
    if estimated_outputs is not None:
        data_container.add_external_variable('Toffice_estimated', estimated_outputs[0])
        data_container.add_external_variable('office_CO2_estimated', estimated_outputs[1])
    print(preference)
    preference.print_assessment(heater_powers, office_temperatures, office_CO2s, h358_model.data('occupancy'), (door_openings, window_openings))
    data_container.plot()
