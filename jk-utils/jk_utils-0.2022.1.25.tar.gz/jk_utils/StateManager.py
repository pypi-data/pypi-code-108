#!/usr/bin/python3

import inspect
from typing import List, Union
import collections

import jk_logging





# ----------------------------------------------------------------

_ActionRecord = collections.namedtuple("__ActionRecord", [ "f", "priority", "name" ])


def _listOfActionRecordsToStr(records:list):
	ret = "[ "
	for r in records:
		if len(ret) > 2:
			ret += ", "
		ret += "(" + str(r.name if r.name else "callable") + ", " + str(r.priority) + ")"
	return ret + " ]"
#


# ----------------------------------------------------------------







class _State(object):

	def __init__(self, state):
		self.__state = state
		self.__fromStates = {}			# preconditions: int -> __ActionRecord[]
		self.__general = []				# __ActionRecord[]
	#

	def registerAction(self, fromStateOrListOfStates, action:callable, priority:int, name:str):
		assert action != None

		if fromStateOrListOfStates is None:
			self.__general.append(_ActionRecord(action, priority, name))
		else:
			if isinstance(fromStateOrListOfStates, (list, tuple)):
				for s in fromStateOrListOfStates:
					s = int(s)
					if s in self.__fromStates:
						actions = self.__fromStates[s]
					else:
						actions = []
						self.__fromStates[s] = actions
					actions.append(_ActionRecord(action, priority, name))
			else:
				s = int(fromStateOrListOfStates)
				if s in self.__fromStates:
					actions = self.__fromStates[s]
				else:
					actions = []
					self.__fromStates[s] = actions
				actions.append(_ActionRecord(action, priority, name))
	#

	def getActions(self, fromState) -> List[_ActionRecord]:
		fromState = int(fromState)
		ret = []
		ret.extend(self.__general)
		if fromState in self.__fromStates:
			ret.extend(self.__fromStates[fromState])
		return ret
	#

	def __str__(self):
		return str(self.__state)
	#

	def __repr__(self):
		return str(self.__state)
	#

	def dump(self, stateMap, prefix, outputFunction):
		outputFunction(prefix + str(self.__state) + ":")
		prefix += "\t"
		for precond in self.__fromStates:
			outputFunction(prefix + str(stateMap[precond]) + " -> " + str(self.__state) + " : " + _listOfActionRecordsToStr(self.__fromStates[precond]))
		if len(self.__general) > 0:
			outputFunction(prefix + "* -> " + str(self.__state) + " : " + _listOfActionRecordsToStr(self.__general))
	#

#

# ----------------------------------------------------------------



#
# This class manages actions on state transitions. The basic concept follows this principle:
#
# * initialization phase
#	* instantiate a state manager object; specify all possible states and the initial state;
#	* register actions with all transitions as necessary; you can choose from
#		* actions performed if a state is left
#		* actions performed if a state is reached
#		* actions performed on specific state transitions
# * runtime phase
#	* specify state transitions using <c>switchState()</c> and get actions performed automatically in sorted order: priorities of actions are considered accordingly
#
class StateManager(object):

	def __init__(self, states, startingState):
		self.__states = {}
		for state in states:
			self.__states[int(state)] = _State(state)
		self.__currentState = startingState
		self.__general = []				# __ActionRecord[]
	#

	@property
	def currentState(self) -> int:
		return self.__currentState
	#

	def registerActionFromTo(self, fromStateOrListOfStates, toStateOrListOfStates, action:callable, priority:int, name:str = None):
		assert fromStateOrListOfStates != None
		assert toStateOrListOfStates != None
		assert action != None

		if isinstance(toStateOrListOfStates, (list, tuple)):
			for s in toStateOrListOfStates:
				self.__states[int(s)].registerAction(fromStateOrListOfStates, action, priority, name)
		else:
			self.__states[int(toStateOrListOfStates)].registerAction(fromStateOrListOfStates, action, priority, name)
	#

	def registerActionTo(self, toStateOrListOfStates, action:callable, priority:int, name:str = None):
		assert toStateOrListOfStates != None
		assert action != None

		if isinstance(toStateOrListOfStates, (list, tuple)):
			for s in toStateOrListOfStates:
				self.__states[int(s)].registerAction(None, action, priority, name)
		else:
			self.__states[int(toStateOrListOfStates)].registerAction(None, action, priority, name)
	#

	def registerActionFrom(self, fromStateOrListOfStates, action:callable, priority:int, name:str = None):
		assert fromStateOrListOfStates != None
		assert action != None

		for state in self.__states.values():
			state.registerAction(fromStateOrListOfStates, action, priority, name)
	#

	def registerAction(self, action:callable, priority:int, name:str = None):
		assert action != None

		self.__general.append(_ActionRecord(action, priority, name))
	#

	#
	# Switch to a state without performaing any actions.
	#
	def switchStateWithoutActions(self, toState, logger:jk_logging.AbstractLogger = None):
		if logger != None:
			logger.debug("Setting state: " + str(toState))

		self.__currentState = toState
	#

	#
	# Switch the current state to the specified state and perform all actions defined for this transition.
	#
	def switchState(self, toState, logger:jk_logging.AbstractLogger = None):
		if self.__currentState == toState:
			return None

		if logger != None:
			logger.debug("Switching from state " + str(self.__currentState) + " to " + str(toState))

		allActions = self.__states[int(toState)].getActions(self.__currentState)
		allActions.extend(self.__general)

		# sort all actions so that actions with the highest priority come first
		allActions.sort(key=lambda a: a.priority, reverse=True)

		# remember state
		self.__currentState = toState

		# process all actions
		for a in allActions:
			if logger != None:
				logger.debug("Executing: " + str(a.f))
			a.f()
	#

	def dump(self, prefix="", outputFunction=print):
		outputFunction(prefix + "Current state: " + str(self.__currentState))
		outputFunction(prefix + "States:")
		prefix += "\t"
		for state in self.__states.values():
			state.dump(self.__states, prefix, outputFunction)
			if len(self.__general) > 0:
				outputFunction(prefix + "\t*" + " : " + _listOfActionRecordsToStr(self.__general))
	#

#


