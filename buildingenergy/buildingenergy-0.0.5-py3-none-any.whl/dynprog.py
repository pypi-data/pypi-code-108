"""Dynamic programming for the generation of optimal energy management strategies."""

import buildingenergy.model
import numpy


class Possibilities:
    """Represent a node in digraph representing a set of possible actions at a given timestep."""

    def __init__(self, value_lists, ancestor=None, value: float=None):
        """Initialize a node.

        :param value_lists: tuples of possible values respectively related to the possible controls
        :type value_lists: list[tuple[float]]
        :param ancestor: a node of possibilities at the previous sample time, which led to this node, defaults to None
        :type ancestor: Possibilities, optional
        :param value: values in term of optimization objective to be minimized, defaults to None
        :type value: float, optional
        :raises ValueError: raise an error if one of the 3 tuples of possible values is empty i.e. no one action is possible
        """
        if ancestor is None:
            Possibilities.root_node = self
            Possibilities.terminal_nodes = list()
            for i in range(len(value_lists)):
                if len(value_lists[i]) == 0:
                    raise ValueError('Generation of possibilities is impossible because of the empty set in position %i', i)
            self._rank = len(value_lists)
            Possibilities.full_rank = len(value_lists)
        else:
            self._rank = ancestor._rank - 1
            self._value =  value
        self._ancestor = ancestor
        self._descendants = list()
        self._value_lists = value_lists
        if len(self._value_lists) > 0:
            for value in value_lists[0]:
                self._descendants.append(Possibilities(value_lists[1:], self, value))
        else:
            Possibilities.terminal_nodes.append(self)

    def _val(self):
        """Return the sum of the objective values of the Possibilities bloodline leading to this node.

        :return: the objective value of the bloodline leading to this node
        :rtype: float
        """
        ancestor = self
        _values = list()
        while ancestor._ancestor is not None:
            _values.append(ancestor._value)
            ancestor = ancestor._ancestor
        _values.reverse()
        return _values

    def values(self):
        """Return all the lastest hour nodes.

        :return: latest hour nodes
        :rtype: list[float]
        """
        _all = list()
        for terminal_node in Possibilities.terminal_nodes:
            _all.append(terminal_node._val())
        return _all


class DayDynamicProgramming:
    """Provide a dynamic programing implementation of the optimization of actions depicted by StateModel."""

    class _HourNode:
        """Internal class for building a digraph where each node is standing for a state vector at time k and the actions that led to this node from the previous node (time k-1)."""

        NodeCounter = 0

        def __init__(self, state_vector: numpy.array, global_hour_index: int, estimated_outputs: numpy.array,ancestor_node = None, leading_actions=None, preference_value = 0):
            """Initialize a node standing for an possible state vector at a specific hour.

            :param state_vector: possible state vector
            :type state_vector: numpy.array
            :param global_hour_index: hour index
            :type global_hour_index: int
            :param ancestor_node: node of the previous hour that led to this node, defaults to None
            :type ancestor_node: _HourNode, optional
            :param leading_actions: actions (name and value) that led to this node, defaults to None
            :type leading_actions: dict[str,float], optional
            :param preference_value: assessment of the current state, defaults to 0
            :type preference_value: int, optional
            """
            self.ancestor_node = ancestor_node


            self._node_id = DayDynamicProgramming._HourNode.NodeCounter
            self.estimated_outputs = estimated_outputs
            self.global_hour_index = global_hour_index
            self.state_vector = state_vector
            self.discrete_state_vector = self._discretize_state(state_vector)
            self._preference_value_km1 = preference_value
            self.leading_actions_km1 = leading_actions
            DayDynamicProgramming._HourNode.NodeCounter += 1

        @property
        def cumulated_preference_value_km1(self) -> float:
            """Return the sum of the preference values from the first hour and according to the bloodline.

            :return: sum of preference values
            :rtype: float
            """
            _cumulated_preference_value_km1 = self._preference_value_km1
            if self.ancestor_node is not None:
                _cumulated_preference_value_km1 += self.ancestor_node.cumulated_preference_value_km1
            return _cumulated_preference_value_km1

        @property
        def node_id(self) -> int:
            """Return the id of the node.

            :return: unique identifier
            :rtype: int
            """
            return self._node_id

        def _discretize_state(self, state_vector: numpy.array):
            """Return a discrete-value representation of the state vector corresponding to the specified state space resolution.

            :param state_vector: the state vector in the continuous space
            :type state_vector: numpy.array
            :return: pair of indices referencing the cell of the virtual grid to which the state of the node belongs
            :rtype: tuple[int]
            """
            _discrete_state_vector = list()
            for state_variable_index in range(len(state_vector)):
                _discrete_state_vector.append(int(round(state_vector[state_variable_index, 0] / DayDynamicProgramming._HourNode.state_resolutions[state_variable_index])))
            return _discrete_state_vector

        def __cmp__(self, other_node: 'DayDynamicProgramming._HourNode') -> int:
            """Define comparison between nodes according to virtual state grid indices. Priority is given to first indices.

            :param other_node: other node
            :return: -1 if cell indices of current node <= other_node cell indices, 1 if greater than and 0 in case of equality
            """
            for i in range(len(self.discrete_state_vector)):
                if self.discrete_state_vector[i] < other_node.discrete_state_vector[i]:
                    return -1
                elif self.discrete_state_vector[i] > other_node.discrete_state_vector[i]:
                    return 1
            return 0

        def __lt__(self, other_node: 'DayDynamicProgramming._HourNode') -> bool:
            """Redefine 'lower than' legacy method.

            :param other_node: other node
            :return: True if node state grid cell indices < other_node state grid cell indices, False otherwise
            """
            return self.__cmp__(other_node) == -1

        def __eq__(self, other_node: 'DayDynamicProgramming._HourNode') -> bool:
            """Redefine 'equal to' legacy method.

            :param other_node: other node
            :return: True if node state grid cell indices == other_node state grid cell indices, False otherwise
            """
            return self.__cmp__(other_node) == 0

        def __gt__(self, other_node: 'DayDynamicProgramming._HourNode') -> bool:
            """Redefine 'greater than' legacy method.

            :param other_node: other node
            :return: True if node state grid cell indices > other_node state grid cell indices, False otherwise
            """
            return self.__cmp__(other_node) == 1

        def __str__(self) -> str:
            """Return a descriptive string of the node.

            :return: description of the node
            :rtype: str
            """
            string = 'N:' + str(self.node_id) + '(h:' + str(self.hour_in_day) + ', v:' + str(self.cumulated_preference_value_km1) + ', a:'
            if self.leading_actions_km1 is not None:
                for k,v in self.leading_actions_km1.items():
                    string += '%s > %i, ' % (k, v)
            if self.ancestor_node is not None:
                string += ' > ' + str(self.ancestor_node.node_id)
            return string

    def __init__(self, a_model: buildingenergy.model.Model,  initial_state_vector: numpy.array, global_starting_hour_index: int, state_resolutions, preference: buildingenergy.model.Preference):
        """Intialize the dynamic programing implementation for the optimization of actions. The optimization problem is related to times from hour_index till hour_index + 24 hour steps.

        :param model: model of the building
        :type model.H358Model, subclassing Model
        :param initial_state_vector: class containing the state model
        :type initial_state_vector: numpy.array
        :param global_starting_hour_index: define the size of the state space grid for selecting best solutions in each cell.
        :type global_starting_hour_index: int
        :param state_resolutions: resolution related to the state vector to reduce the number of propagated state vectors at each time step. Same size than the state vector.
        :type state_resolutions: list[float]
        :param preference: occupant preference
        :type preference: buildingenergy.model.Preference
        """
        print('# dynamic programming')
        print('## date: ', a_model.data('stringtime')[global_starting_hour_index])
        DayDynamicProgramming._HourNode.state_resolutions = state_resolutions
        self.model = a_model

        U0, _ = a_model.computeU(0, initial_state_vector, None, None)
        Y0 = a_model.computeY(0, initial_state_vector, U0, None)
        self.day_hour_node_lists = [[DayDynamicProgramming._HourNode(initial_state_vector, global_starting_hour_index, Y0)]]
        for k in range(global_starting_hour_index + 1, global_starting_hour_index + 25):  # k refers to the nodes under creation
            hour_nodes_list_for_hour_k = []  # contains the nodes of the current hour k
            action_names, possible_actions = self.generate_possible_actions_at_given_hour(k-1)  # generate the possible actions for hour k
            leading_action_possibilities = Possibilities(possible_actions).values()   #generate a list with combinations of possible action values, respecting the order in action_names
            for leading_action_possibility in leading_action_possibilities:
                leading_action_km1 = dict(zip(action_names, leading_action_possibility))  # create a dict with action_names as keys and corresponding values (leading_action_possibility) as values: 1 action name is related to 1 action value
                for hour_node_km1 in self.day_hour_node_lists[-1]:  # select all the nodes of the preceding hour
                    influencing_variable_km1 = (leading_action_km1['door_opening'], leading_action_km1['window_opening'])
                    Ukm1, leading_action_km1 = a_model.computeU(k-1, hour_node_km1.state_vector, influencing_variable_km1, leading_action_km1)
                    currentY_km1 = a_model.computeY(k-1, hour_node_km1.state_vector, Ukm1, influencing_variable_km1)
                    state_vector_k, _ = a_model.stepX(k-1, hour_node_km1.state_vector, None, influencing_variable_km1, Ukm1)

                    presence=self.model.data('occupancy')[k-1]
                    if k < len(self.model.data('occupancy')):
                        presence = presence + self.model.data('occupancy')[k]
                    preference_value_km1 = preference.assess(leading_action_km1['heating_power'], currentY_km1[0,0], currentY_km1[1,0], presence)
                    new_node = DayDynamicProgramming._HourNode(state_vector_k, k, currentY_km1, hour_node_km1, leading_action_km1, preference_value_km1)
                    hour_nodes_list_for_hour_k.append(new_node)
            print('hour %i: %i new nodes' % (k, len(hour_nodes_list_for_hour_k)), end=' ')
            hour_nodes_list_for_hour_k.sort()
            filtered_next_hour_node_list = list()
            current_cell, current_vals, current_nodes = [], [], []
            for k in range(len(hour_nodes_list_for_hour_k)):
                if len(current_cell) == 0 or current_cell[-1] == hour_nodes_list_for_hour_k[k].discrete_state_vector:
                    current_cell.append(hour_nodes_list_for_hour_k[k].discrete_state_vector)
                    current_vals.append(hour_nodes_list_for_hour_k[k].cumulated_preference_value_km1)
                    current_nodes.append(hour_nodes_list_for_hour_k[k])
                else:
                    i_best = current_vals.index(min(current_vals))
                    filtered_next_hour_node_list.append(current_nodes[i_best])
                    current_cell, current_vals, current_nodes = [], [], []
            if len(current_cell) > 0:
                i_best = current_vals.index(min(current_vals))
                filtered_next_hour_node_list.append(current_nodes[i_best])

            print('-> remaining %i new nodes' % (len(filtered_next_hour_node_list)))
            self.day_hour_node_lists.append(filtered_next_hour_node_list)
        terminal_nodes = self.day_hour_node_lists[-1]
        terminal_nodes_indices_values = dict()
        for i in range(len(terminal_nodes)):
            terminal_nodes_indices_values[i] = terminal_nodes[i].cumulated_preference_value_km1
        sorted_terminal_nodes_indices_values = [(i, v) for i, v in sorted(terminal_nodes_indices_values.items(), key=lambda item: item[1])]
        best_terminal_node = terminal_nodes[sorted_terminal_nodes_indices_values[0][0]]
        self._best_strategy = self._strategy(best_terminal_node)

        print("* 10 best strategies")
        counter = 0
        for i,v in sorted_terminal_nodes_indices_values:
            current_strategy = self._strategy(terminal_nodes[i])
            string = str(i) + ':'
            for k in range(len(current_strategy['door_opening'])):
                string += str(k)+'['
                for action in current_strategy:
                    if action == 'door_opening'and current_strategy[action][k]==1:
                        string += 'D'
                    elif action == 'window_opening'and current_strategy[action][k]==1:
                        string += 'W'
                    elif action == 'temperature_setpoint':
                        string += 'T' + str(current_strategy[action][k])
                    elif action == 'heating_power':
                        string += 'P%.0f' % current_strategy[action][k]
                string += ']'
            string += '>%f%%, ' % (100*v / len(current_strategy['door_opening']))
            if counter > 9:
                break
            counter += 1
            print(string + '\n')

    def _strategy(self, terminal_node):
        _results = {'door_opening': list(), 'window_opening': list(), 'heating_power': list(), 'temperature_setpoint': list()}
        estimated_outputs = None
        while terminal_node.ancestor_node is not None:
            resulting_actions = terminal_node.leading_actions_km1
            if estimated_outputs is None:
                estimated_outputs = terminal_node.estimated_outputs
            else:
                estimated_outputs = numpy.concatenate((terminal_node.estimated_outputs, estimated_outputs), axis=1)
            _results['door_opening'].insert(0, resulting_actions['door_opening'])
            _results['window_opening'].insert(0, resulting_actions['window_opening'])
            _results['heating_power'].insert(0, resulting_actions['heating_power'])
            if 'temperature_setpoint' in resulting_actions:
                _results['temperature_setpoint'].insert(0, resulting_actions['temperature_setpoint'])
            else:
                _results['temperature_setpoint'].insert(0, None)
            _results['estimated_outputs'] = estimated_outputs
            terminal_node = terminal_node.ancestor_node
        return _results

    @property
    def results(self):
        """Return results of the optimization.

        :return: list of actions with optimal values covering 24 hours
        :rtype: dict[str,list[float]]
        """
        return self._best_strategy

    def generate_possible_actions_at_given_hour(self, global_starting_hour_index: int):
        """Generate the possible action at hour k as a list of action names and a list of tuples with the possible values corresponding to the action with the same index in the list (1).

        :param global_starting_hour_index: hour index
        :type global_starting_hour_index: int
        :return: a list of names of possible actions and a list of tuples with possible action values
        :rtype: tuple[list[str], list[tuple(float)]]
        """
        raise NotImplemented
