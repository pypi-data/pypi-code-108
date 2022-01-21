"""Implementation of dynamic programming for the generation of optimal energy management strategies for the H358 office. This module can't be launch directly: it's used by h358simulator for instance."""

import h358.h358model
import buildingenergy.model
import buildingenergy.dynprog
import numpy


class DayDynamicProgramming(buildingenergy.dynprog.DayDynamicProgramming):
    """Provide a dynamic programing implementation of the optimization of actions for H358 office depicted by StateModel."""

    def __init__(self, h358model: h358.h358model.H358Model,  initial_state_vector: numpy.array, global_starting_hour_index: int, state_resolutions, preference: buildingenergy.model.Preference):
        """Intialize the dynamic programing implementation for the optimization of actions. The optimization problem is related to times from hour_index till hour_index + 24 hour steps.

        :param h358model: model of the building
        :type h358model.H358Model, subclassing Model
        :param initial_state_vector: class containing the state model
        :type initial_state_vector: numpy.array
        :param global_starting_hour_index: define the size of the state space grid for selecting best solutions in each cell.
        :type global_starting_hour_index: int
        :param state_resolutions: resolution related to the state vector to reduce the number of propagated state vectors at each time step. Same size than the state vector.
        :type state_resolutions: list[float]
        :param preference: occupant preference
        :type preference: buildingenergy.model.Preference
        """
        buildingenergy.dynprog.DayDynamicProgramming.__init__(self, h358model, initial_state_vector, global_starting_hour_index, state_resolutions, preference)

    def generate_possible_actions_at_given_hour(self, global_starting_hour_index: int):
        """Generate the possible action at hour k with 2 lists: (1) a list of action names (2) a list of tuples with the possible values corresponding to the action with the same index in the list (1).

        :param global_starting_hour_index: hour index
        :type global_starting_hour_index: int
        :return: a list of names of possible actions and a list of tuples with possible action values
        :rtype: tuple[list[str], list[tuple(float)]]
        """
        day_of_week = self.model.data('datetime')[global_starting_hour_index].isoweekday()
        hour_in_days = self.model.data('datetime')[global_starting_hour_index].hour
        heating = self.model.data('heating')[global_starting_hour_index]
        presence = self.model.data('presence')[global_starting_hour_index]
        action_names, possible_actions = list(), list()
        action_names.append('door_opening')
        action_names.append('window_opening')
        if day_of_week < 6 and presence == 1 and 7 < hour_in_days < 20:
            possible_actions.append((0, 1))
            possible_actions.append((0, 1))
        else:
            possible_actions.append((0,))
            possible_actions.append((0,))
        if heating:
            action_names.append('temperature_setpoint')
            possible_actions.append((13, 18, 19, 20, 21))
        else:
            action_names.append('heating_power')
            possible_actions.append((0,))
        return action_names, possible_actions
