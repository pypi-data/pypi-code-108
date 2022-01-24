import io
import unittest
import unittest.mock

from guide_bot.parameters.instrument_parameters import InstrumentParameter
from guide_bot.parameters.instrument_parameters import FreeInstrumentParameter
from guide_bot.parameters.instrument_parameters import FixedInstrumentParameter
from guide_bot.parameters.instrument_parameters import DependentInstrumentParameter

from guide_bot.parameters.instrument_parameter_container import InstrumentParameterContainer

from guide_bot.base_elements.guide_elements import Element

from guide_bot.logic.length_system import length_system
from guide_bot.logic.length_system import process_section
from guide_bot.logic.length_system import propagate_fixed_lengths_to_start_points
from guide_bot.logic.length_system import sum_min_or_length
from guide_bot.logic.length_system import sum_max_or_length


def setup_guide_one_element_simple():
    guide = [Element("one_element_guide")]
    return guide


def setup_guide_two_element_simple():
    guide = [Element("first_element"), Element("second_element")]
    return guide


def setup_guide_two_element_max_length():
    guide = [Element("first_element", length=[None, 5]), Element("second_element")]
    return guide


def setup_guide_two_element_max_length_last():
    guide = [Element("first_element"), Element("second_element", length=[None, 7.0])]
    return guide


def setup_propagate_forward_test():
    guide = [Element("0", length=3),
             Element("1", length=5),
             Element("2"),
             Element("3", start_point=12)]
    return guide


def setup_propagate_backwards_test():
    guide = [Element("0"),
             Element("1"),
             Element("2", length=3.0),
             Element("3", length=4.0)]
    return guide


def setup_propagate_middle_fix_test():
    guide = [Element("0"),
             Element("1", length=3.0),
             Element("2", start_point=11.0, length=4.0),
             Element("3", length=1.0),
             Element("4")]
    return guide


class TestPropagateFixedLengths(unittest.TestCase):
    def test_simple_case_forward(self):
        guide = setup_propagate_forward_test()

        propagate_fixed_lengths_to_start_points(guide, 20.0)

        self.assertIsInstance(guide[0].start_point, FixedInstrumentParameter)
        self.assertEqual(guide[0].start_point.get_value(), 0.0)

        self.assertIsInstance(guide[1].start_point, FixedInstrumentParameter)
        self.assertEqual(guide[1].start_point.get_value(), 3.0)

        self.assertIsInstance(guide[2].start_point, FixedInstrumentParameter)
        self.assertEqual(guide[2].start_point.get_value(), 3.0+5.0)

        self.assertIsInstance(guide[3].start_point, FixedInstrumentParameter)
        self.assertEqual(guide[3].start_point.get_value(), 12.0)

    def test_simple_case_backwards(self):
        guide = setup_propagate_backwards_test()

        propagate_fixed_lengths_to_start_points(guide, 20.0)

        self.assertIsInstance(guide[0].start_point, FixedInstrumentParameter)
        self.assertEqual(guide[0].start_point.get_value(), 0.0)

        self.assertIsInstance(guide[1].start_point, FreeInstrumentParameter)

        self.assertIsInstance(guide[2].start_point, FixedInstrumentParameter)
        self.assertEqual(guide[2].start_point.get_value(), 20.0-4.0-3.0)

        self.assertIsInstance(guide[3].start_point, FixedInstrumentParameter)
        self.assertEqual(guide[3].start_point.get_value(), 20.0-4.0)

    def test_simple_case_middle(self):
        guide = setup_propagate_middle_fix_test()

        propagate_fixed_lengths_to_start_points(guide, 20.0)

        self.assertIsInstance(guide[0].start_point, FixedInstrumentParameter)
        self.assertEqual(guide[0].start_point.get_value(), 0.0)

        self.assertIsInstance(guide[1].start_point, FixedInstrumentParameter)
        self.assertEqual(guide[1].start_point.get_value(), 11.0-3.0)

        self.assertIsInstance(guide[2].start_point, FixedInstrumentParameter)
        self.assertEqual(guide[2].start_point.get_value(), 11.0)

        self.assertIsInstance(guide[3].start_point, FixedInstrumentParameter)
        self.assertEqual(guide[3].start_point.get_value(), 11.0+4.0)

        self.assertIsInstance(guide[4].start_point, FixedInstrumentParameter)
        self.assertEqual(guide[4].start_point.get_value(), 11.0 + 4.0 + 1.0)


def setup_min():
    guide = [Element("0", length=[None, 4]),
             Element("1", length=[3, 4]),
             Element("2"),
             Element("3", length=4.0)]
    return guide


def setup_max_broken():
    guide = [Element("0", length=[None, 5]),
             Element("1", length=[3, 5]),
             Element("2"),
             Element("3", length=4.0)]
    return guide


def setup_max_unbroken():
    guide = [Element("0", length=[None, 5]),
             Element("1", length=[3, 5]),
             Element("2", length=[None, 1.0]),
             Element("3", length=4.0)]
    return guide


class TestMinAndMaxFunctions(unittest.TestCase):
    def test_min_sum(self):
        guide = setup_min()

        self.assertEqual(sum_min_or_length(guide), 0+3+0+4.0)

    def test_max_sum_broken(self):
        guide = setup_max_broken()

        sum, unbroken = sum_max_or_length(guide)

        self.assertEqual(sum, 5.0 + 5.0 + 0.0 + 4.0)
        self.assertFalse(unbroken)

    def test_max_sum_unbroken(self):
        guide = setup_max_unbroken()

        sum, unbroken = sum_max_or_length(guide)

        self.assertEqual(sum, 5.0 + 5.0 + 1.0 + 4.0)
        self.assertTrue(unbroken)

