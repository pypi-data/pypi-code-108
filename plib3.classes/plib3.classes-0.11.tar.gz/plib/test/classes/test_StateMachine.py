#!/usr/bin/env python3
"""
TEST.CLASSES.TEST_STATEMACHINE.PY -- test script for state machine class
Copyright (C) 2008-2015 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script contains unit tests for the StateMachine class.
"""

import unittest

from plib.classes import StateMachine, InvalidState, InvalidInput, RecursiveTransition


class TestMachine(StateMachine):
    
    states = {
        'ONE': {
            "TWO": ('TWO', "State two."),
            "THREE": ('THREE', "State three."),
            "": ('', "Still in state one.")
        },
        'TWO': {
            "ONE": ('ONE', "State one."),
            "THREE": ('THREE', "State three.")
        },
        'THREE': {
            "TWO": ('TWO', "State two."),
            "THREE": ('', ""),
            "FOUR": ('FOUR', "State four.")
        },
        'FOUR': {
            "ONE": ('ONE', "output_method")
        }
    }
    
    initial_state = 'ONE'
    default_output = "Default output."
    
    def __init__(self):
        StateMachine.__init__(self, self.states, self.initial_state, self.default_output)
    
    def output_method(self, old_state, new_state, input_data):
        return "Method output: from {} to {} on input {}.".format(old_state, new_state, input_data)


class StateMachineTest(unittest.TestCase):
    
    def test_machine(self):
        machine = TestMachine()
        self.assertEqual(machine.current_state, "ONE")
        self.assertEqual(machine.send_input("TWO"), "State two.")
        self.assertEqual(machine.current_state, "TWO")
        self.assertEqual(machine.in_transition, False)
        self.assertEqual(machine.send_input("ONE"), "State one.")
        self.assertEqual(machine.current_state, "ONE")
        self.assertEqual(machine.send_input("FOUR"), "Still in state one.")
        self.assertEqual(machine.current_state, "ONE")
        self.assertEqual(machine.send_input("INVALID"), "Still in state one.")
        self.assertEqual(machine.current_state, "ONE")
        self.assertEqual(machine.send_input("THREE"), "State three.")
        self.assertEqual(machine.current_state, "THREE")
        self.assertEqual(machine.send_input("TWO"), "State two.")
        self.assertEqual(machine.current_state, "TWO")
        self.assertRaises(InvalidInput, machine.send_input, "TWO")
        self.assertEqual(machine.in_transition, False)
        self.assertEqual(machine.current_state, "TWO")
        self.assertRaises(InvalidInput, machine.send_input, "FOUR")
        self.assertEqual(machine.current_state, "TWO")
        self.assertRaises(InvalidInput, machine.send_input, "INVALID")
        self.assertEqual(machine.current_state, "TWO")
        self.assertEqual(machine.send_input("THREE"), "State three.")
        self.assertEqual(machine.current_state, "THREE")
        self.assertEqual(machine.send_input("THREE"), "Default output.")
        self.assertEqual(machine.current_state, "THREE")
        self.assertRaises(InvalidInput, machine.send_input, "ONE")
        self.assertEqual(machine.current_state, "THREE")
        self.assertRaises(InvalidInput, machine.send_input, "INVALID")
        self.assertEqual(machine.current_state, "THREE")
        self.assertEqual(machine.send_input("FOUR"), "State four.")
        self.assertEqual(machine.current_state, "FOUR")
        self.assertRaises(InvalidInput, machine.send_input, "TWO")
        self.assertEqual(machine.current_state, "FOUR")
        self.assertRaises(InvalidInput, machine.send_input, "THREE")
        self.assertEqual(machine.current_state, "FOUR")
        self.assertRaises(InvalidInput, machine.send_input, "FOUR")
        self.assertEqual(machine.current_state, "FOUR")
        self.assertRaises(InvalidInput, machine.send_input, "INVALID")
        self.assertEqual(machine.current_state, "FOUR")
        self.assertEqual(machine.send_input("ONE"), "Method output: from FOUR to ONE on input ONE.")
        self.assertEqual(machine.current_state, "ONE")


class BadTestMachine(TestMachine):
    
    initial_state = "INVALID"


class StateMachineTestBad(unittest.TestCase):
    
    def test_machine(self):
        #machine = BadTestMachine()
        self.assertRaises(InvalidState, BadTestMachine)


class NoDefaultTestMachine(TestMachine):
    
    default_output = ""


class StateMachineTestNoDefault(unittest.TestCase):
    
    def test_machine(self):
        machine = NoDefaultTestMachine()
        self.assertEqual(machine.current_state, "ONE")
        self.assertEqual(machine.send_input("THREE"), "State three.")
        self.assertEqual(machine.current_state, "THREE")
        self.assertEqual(machine.send_input("THREE"), "THREE")
        self.assertEqual(machine.current_state, "THREE")


class MethodDefaultTestMachine(TestMachine):
    
    default_output = "output_method"


class StateMachineTestMethodDefault(unittest.TestCase):
    
    def test_machine(self):
        machine = MethodDefaultTestMachine()
        self.assertEqual(machine.current_state, "ONE")
        self.assertEqual(machine.send_input("THREE"), "State three.")
        self.assertEqual(machine.current_state, "THREE")
        self.assertEqual(machine.send_input("THREE"), "Method output: from THREE to THREE on input THREE.")
        self.assertEqual(machine.current_state, "THREE")


class OverlapTransitionTestMachine(TestMachine):
    
    initial_state = 'TWO'
    
    def enter_THREE(self, old_state, new_state, input_data):
        self.send_input("THREE")


class StateMachineTestOverlapTransition(unittest.TestCase):
    
    def test_machine(self):
        machine = OverlapTransitionTestMachine()
        self.assertEqual(machine.current_state, "TWO")
        self.assertRaises(RecursiveTransition, machine.send_input, "THREE")


if __name__ == '__main__':
    unittest.main()
