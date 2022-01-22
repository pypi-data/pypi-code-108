#!/usr/bin/env python3
"""
Module StateMachine
Sub-Package STDLIB.CLASSES of Package PLIB3
Copyright (C) 2008-2015 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the ``StateMachine`` class, which takes
a simple state table and instantiates a state machine
based on it. The state machine takes input strings and
returns output objects (which do not need to be strings),
possibly with side effects defined by methods on the
state machine instance.
"""

from plib.stdlib.builtins import first

from ._defs import InvalidState, InvalidInput, RecursiveTransition


class StateMachine(object):
    """Generic state machine class.
    
    This takes a state table dictionary and implements
    the code to instantiate a state machine based on it.
    
    State table format: a mapping of state names to mappings;
    each value maps input strings to 2-tuples containing:
    (<new state name>, <output>). One of the input string keys
    may be the empty string; if so, this entry will be the
    default if an input string is not in the mapping. If there
    is no default entry present, sending an input string that
    isn't in the mapping for the current state will raise an
    InvalidInput exception.
    
    The new state may be empty; if so, this is equivalent
    to remaining in the current state for that input.
    
    The output may be anything, and if none of the special cases
    below apply, it will be returned unchanged. The special
    cases are:
    
    - If the output is a string and the name of a valid method,
      that method will be called with the old and new states and
      the input to the send_input function as parameters; i.e.,
      its signature must be:
    
          def output_method(self, old_state, new_state, input_data)
    
      The result of the method call will be the output.
    
    - If the output is empty, but the default_output parameter
      was passed to the constructor, default_output will be
      treated as the output (including the possible call of a
      method by the rule just above). Note that "empty" output
      includes *anything* that is considered empty (false) by
      Python; it is not limited to None or an empty string.
    
    - If the output is empty, and there is no default output per
      the above, the new state will be returned as the output.
    
    By default, the machine starts in the first state returned
    from state_table.keys(); however, this is usually not very
    useful since the key ordering depends on the hash table
    implementation. The initial_state parameter to the constructor
    can be used to set a specific state at startup.
    
    Once the machine is instantiated, the send_input method sends
    an input string to the machine and returns the corresponding
    output (see above). When the method returns, the machine will
    be in the new state per the table.
    
    For each named state, two methods can be defined that allow
    arbitrary code to be executed during state transitions:
    
    - enter_<state> will be called when the machine transitions
      into the state;
    
    - exit_<state> will be called when the machine transitions
      out of the state.
    
    The enter method on the initial state is called from the
    constructor. On state transition, the outgoing exit method
    is called first, then the incoming enter method. Each method
    takes the old and new states and the current input as
    parameters.
    
    One other thing to note about all methods called during state
    transitions (state exit, state enter, and output) is that they
    must *not* trigger any further state transitions; thus, they
    must not call the send_input method, either directly or indirectly
    by calling some other function that may do so. If transitions
    overlap, a RecursiveTransition exception will be raised. This must
    be carefully considered when state transitions trigger side effects;
    if any of the side effects could result in a state change (for
    example, starting an I/O process whose result might trigger
    another state transition), those side effects *must* be delayed
    until the current state transition has been completed and the
    send_input method has returned. (Often this can be accomplished
    by posting the desired side effect to an event queue which will
    not be processed again until after send_input returns.)
    """
    
    def __init__(self, state_table, initial_state='', default_output=""):
        self.state_table = state_table
        self.default_output = default_output
        if initial_state:
            if initial_state not in state_table:
                raise InvalidState(
                    "Initial state {} is not valid.".format(initial_state))
        else:
            initial_state = first(state_table.keys())
        self.current_state = ''
        self.in_transition = False
        self.transition(initial_state)
    
    def state_method(self, state, change):
        try:
            return getattr(self, '{}_{}'.format(change, state))
        except AttributeError:
            return None
        except TypeError:
            raise InvalidState("States must be strings.")
    
    def exit_state(self, old_state, new_state, input_data=""):
        exit_method = self.state_method(old_state, 'exit')
        if exit_method:
            exit_method(old_state, new_state, input_data)
    
    def enter_state(self, old_state, new_state, input_data=""):
        enter_method = self.state_method(new_state, 'enter')
        if enter_method:
            enter_method(old_state, new_state, input_data)
    
    def transition(self, state, input_data=""):
        curr = self.current_state
        if curr != state:
            if curr:
                self.exit_state(curr, state, input_data)
            self.enter_state(curr, state, input_data)
            self.current_state = state
    
    def send_input(self, input_data):
        if self.in_transition:
            raise RecursiveTransition(
                "Overlapping state transitions not allowed.")
        self.in_transition = True
        try:  # this ensures that in_transition is cleared on exceptions
            curr = self.current_state
            try:
                entry = self.state_table[curr]
            except KeyError:
                raise InvalidState(
                    "Current state not in state table.")
            try:
                state, output = entry[input_data]
            except KeyError:
                try:
                    state, output = entry[""]
                except KeyError:
                    raise InvalidInput(
                        "Input not in state table entry for current state.")
            if not state:
                state = curr
            self.transition(state, input_data)
            if (not output) and self.default_output:
                output = self.default_output
            if output:
                try:
                    meth = getattr(self, output)
                    result = meth(curr, state, input_data)
                except (AttributeError, TypeError):
                    result = output
            else:
                result = state
        finally:
            self.in_transition = False
        return result
