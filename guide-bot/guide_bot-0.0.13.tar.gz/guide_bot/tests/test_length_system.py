import io
import unittest
import unittest.mock
import random

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

from guide_bot.parameters.instrument_parameters import InstrumentParameter
from guide_bot.parameters.instrument_parameters import FreeInstrumentParameter
from guide_bot.parameters.instrument_parameters import RelativeFreeInstrumentParameter
from guide_bot.parameters.instrument_parameters import FixedInstrumentParameter
from guide_bot.parameters.instrument_parameters import DependentInstrumentParameter


from guide_bot.parameters.instrument_parameter_container import InstrumentParameterContainer

from guide_bot.base_elements.guide_elements import Element

from guide_bot.logic.length_system import length_system
from guide_bot.logic.length_system import process_section
from guide_bot.logic.length_system import propagate_fixed_lengths_to_start_points
from guide_bot.logic.length_system import sum_min_or_length
from guide_bot.logic.length_system import sum_max_or_length
from guide_bot.logic.length_system import is_free_parameter


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


def setup_complex_guide():
    guide = [Element("0"),
             Element("1"),
             Element("2", start_point=6.0),
             Element("3", length=0.5),
             Element("4", length=[None, 3.0]),
             Element("5", start_point=[11.0, 20]),
             Element("6"),
             Element("7", start_point=30, length=[2.0, 8.0]),
             Element("8")]

    return guide


def setup_classic_balistic_guide():
    guide = [Element("Moderator_gap"),
             Element("Feeder", start_point=[2, None]),
             Element("Chopper_gap", start_point=6.5, length=0.1),
             Element("Defocusing", length=[2, 10]),
             Element("Straight"),
             Element("Focusing", length=[2, 10]),
             Element("Sample_gap", length=0.5)]

    return guide

def setup_bug_example_1():
    guide = [Element("Feeder"),
             Element("Chopper_gap", start_point=6.5, length=0.1),
             Element("defocusing1", length=[2, 5]),
             Element("defocusing2", length=[2, 10]),
             Element("straight_section"),
             Element("focusing1", length=[2, 10]),
             Element("focusing2", length=[2, 5]),
             Element("Sample_gap", length=0.5)]

    return guide

class TestLengthSystem(unittest.TestCase):
    def test_length_system_one_element_simple_guide(self):

        guide = setup_guide_one_element_simple()
        instr_parameters = InstrumentParameterContainer()

        length_system(guide, 20, instr_parameters)

        self.assertIsInstance(guide[0].start_point, FixedInstrumentParameter)
        self.assertEqual(guide[0].start_point.get_value(), 0.0)

        self.assertIsInstance(guide[0].start_point_parameter, FixedInstrumentParameter)
        self.assertEqual(guide[0].start_point_parameter.get_value(), 0.0)

        self.assertIsInstance(guide[0].next_start_point_parameter, FixedInstrumentParameter)
        self.assertEqual(guide[0].next_start_point_parameter.get_value(), 20.0)

    def test_length_system_two_element_simple_guide(self):

        guide = setup_guide_two_element_simple()
        instr_parameters = InstrumentParameterContainer()

        length_system(guide, 20, instr_parameters)

        self.assertEqual(guide[0].start_point.get_value(), 0.0)
        self.assertIsInstance(guide[0].start_point, FixedInstrumentParameter)

        self.assertIsInstance(guide[0].start_point_parameter, FixedInstrumentParameter)
        self.assertEqual(guide[0].start_point_parameter.get_value(), 0.0)

        self.assertIsInstance(guide[1].start_point_parameter, FreeInstrumentParameter)
        self.assertEqual(guide[1].start_point_parameter.get_lower_static_bound(), 0.0)
        self.assertEqual(guide[1].start_point_parameter.get_upper_static_bound(), 20.0)

        self.assertIsInstance(guide[1].next_start_point_parameter, FixedInstrumentParameter)
        self.assertEqual(guide[1].next_start_point_parameter.get_value(), 20.0)

    def test_length_system_two_element_max_length_guide(self):

        guide = setup_guide_two_element_max_length()
        instr_parameters = InstrumentParameterContainer()

        length_system(guide, 20, instr_parameters)

        self.assertEqual(guide[0].start_point.get_value(), 0.0)
        self.assertIsInstance(guide[0].start_point, FixedInstrumentParameter)

        self.assertIsInstance(guide[0].start_point_parameter, FixedInstrumentParameter)
        self.assertEqual(guide[0].start_point_parameter.get_value(), 0.0)

        self.assertIsInstance(guide[1].start_point_parameter, FreeInstrumentParameter)
        self.assertEqual(guide[1].start_point_parameter.get_lower_static_bound(), 0.0)
        self.assertEqual(guide[1].start_point_parameter.get_upper_static_bound(), 5.0)

        self.assertIsInstance(guide[1].next_start_point_parameter, FixedInstrumentParameter)
        self.assertEqual(guide[1].next_start_point_parameter.get_value(), 20.0)

    def test_length_system_two_element_max_length_last_guide(self):

        guide = setup_guide_two_element_max_length_last()
        instr_parameters = InstrumentParameterContainer()

        length_system(guide, 20, instr_parameters)

        self.assertEqual(guide[0].start_point.get_value(), 0.0)
        self.assertIsInstance(guide[0].start_point, FixedInstrumentParameter)

        self.assertIsInstance(guide[0].start_point_parameter, FixedInstrumentParameter)
        self.assertEqual(guide[0].start_point_parameter.get_value(), 0.0)

        self.assertIsInstance(guide[1].start_point_parameter, FreeInstrumentParameter)
        self.assertEqual(guide[1].start_point_parameter.get_lower_static_bound(), 13.0)
        self.assertEqual(guide[1].start_point_parameter.get_upper_static_bound(), 20.0)

        self.assertIsInstance(guide[1].next_start_point_parameter, FixedInstrumentParameter)
        self.assertEqual(guide[1].next_start_point_parameter.get_value(), 20.0)

    def test_length_system_complex_guide(self):
        guide = setup_complex_guide()
        instr_parameters = InstrumentParameterContainer()

        length_system(guide, 80.0, instr_parameters)

        self.assertEqual(guide[0].start_point.get_value(), 0.0)
        self.assertIsInstance(guide[0].start_point, FixedInstrumentParameter)

        self.assertIsInstance(guide[0].start_point_parameter, FixedInstrumentParameter)
        self.assertEqual(guide[0].start_point_parameter.get_value(), 0.0)

        self.assertIsInstance(guide[0].next_start_point_parameter, FreeInstrumentParameter)
        self.assertEqual(guide[0].next_start_point_parameter.get_lower_static_bound(), 0.0)
        self.assertEqual(guide[0].next_start_point_parameter.get_upper_static_bound(), 6.0)

        self.assertIsInstance(guide[1].start_point_parameter, FreeInstrumentParameter)
        self.assertEqual(guide[1].start_point_parameter.get_lower_static_bound(), 0.0)
        self.assertEqual(guide[1].start_point_parameter.get_upper_static_bound(), 6.0)

        self.assertIsInstance(guide[1].next_start_point_parameter, FixedInstrumentParameter)
        self.assertEqual(guide[1].next_start_point_parameter.get_value(), 6.0)

        self.assertIsInstance(guide[2].start_point_parameter, FixedInstrumentParameter)
        self.assertEqual(guide[2].start_point_parameter.get_value(), 6.0)

        self.assertIsInstance(guide[2].next_start_point_parameter, FreeInstrumentParameter)
        self.assertEqual(guide[2].next_start_point_parameter.get_lower_static_bound(), 11.0 - 3.0 - 0.5)
        self.assertEqual(guide[2].next_start_point_parameter.get_upper_static_bound(), 20.0 - 0.5)

        self.assertIsInstance(guide[3].start_point_parameter, FreeInstrumentParameter)
        self.assertEqual(guide[3].start_point_parameter.get_lower_static_bound(), 11.0 - 3.0 - 0.5)
        self.assertEqual(guide[3].start_point_parameter.get_upper_static_bound(), 20.0 - 0.5)

        self.assertIsInstance(guide[3].next_start_point_parameter, DependentInstrumentParameter)
        self.assertEqual(guide[3].next_start_point_parameter.constants[0], 0.5)
        self.assertEqual(guide[3].next_start_point_parameter.dependent_on[0], guide[3].start_point_parameter)
        self.assertEqual(guide[3].next_start_point_parameter.dependent_function(10, 0.5), 10.5)

        self.assertIsInstance(guide[4].start_point_parameter, DependentInstrumentParameter)
        self.assertEqual(guide[4].start_point_parameter.constants[0], 0.5)
        self.assertEqual(guide[4].start_point_parameter.dependent_on[0], guide[3].start_point_parameter)
        self.assertEqual(guide[4].start_point_parameter.dependent_function(10, 0.5), 10.5)

        self.assertIsInstance(guide[4].next_start_point_parameter, RelativeFreeInstrumentParameter)
        self.assertEqual(guide[4].next_start_point_parameter.static_lower, 11.0)
        self.assertEqual(guide[4].next_start_point_parameter.static_upper, 20.0)
        lower_dynamic = guide[4].next_start_point_parameter.dynamic_lower[0]
        self.assertEqual(lower_dynamic.dependent_on[0], guide[4].start_point_parameter)
        self.assertEqual(lower_dynamic.constants[0], 0.0)
        self.assertEqual(lower_dynamic.function(10.0, 0.0), 10.0)
        upper_dynamic = guide[4].next_start_point_parameter.dynamic_upper[0]
        self.assertEqual(upper_dynamic.dependent_on[0], guide[4].start_point_parameter)
        self.assertEqual(upper_dynamic.constants[0], 3.0)
        self.assertEqual(upper_dynamic.function(10.0, 3.0), 13.0)
        self.assertEqual(len(guide[4].next_start_point_parameter.dynamic_lower), 1)
        self.assertEqual(len(guide[4].next_start_point_parameter.dynamic_upper), 1)

        self.assertIsInstance(guide[5].start_point_parameter, RelativeFreeInstrumentParameter)
        self.assertEqual(guide[5].start_point_parameter.static_lower, 11.0)
        self.assertEqual(guide[5].start_point_parameter.static_upper, 20.0)
        lower_dynamic = guide[5].start_point_parameter.dynamic_lower[0]
        self.assertEqual(lower_dynamic.dependent_on[0], guide[4].start_point_parameter)
        self.assertEqual(lower_dynamic.constants[0], 0.0)
        self.assertEqual(lower_dynamic.function(10.0, 0.0), 10.0)
        upper_dynamic = guide[5].start_point_parameter.dynamic_upper[0]
        self.assertEqual(upper_dynamic.dependent_on[0], guide[4].start_point_parameter)
        self.assertEqual(upper_dynamic.constants[0], 3.0)
        self.assertEqual(upper_dynamic.function(10.0, 3.0), 13.0)
        self.assertEqual(len(guide[5].start_point_parameter.dynamic_lower), 1)
        self.assertEqual(len(guide[5].start_point_parameter.dynamic_upper), 1)

        self.assertIsInstance(guide[5].next_start_point_parameter, RelativeFreeInstrumentParameter)
        self.assertEqual(guide[5].next_start_point_parameter.static_lower, 11.0)
        self.assertEqual(guide[5].next_start_point_parameter.static_upper, 30.0)
        lower_dynamic = guide[5].next_start_point_parameter.dynamic_lower[0]
        self.assertEqual(lower_dynamic.dependent_on[0], guide[5].start_point_parameter)
        self.assertEqual(lower_dynamic.constants[0], 0.0)
        self.assertEqual(lower_dynamic.function(10.0, 0.0), 10.0)
        self.assertEqual(len(guide[5].next_start_point_parameter.dynamic_lower), 1)
        self.assertEqual(len(guide[5].next_start_point_parameter.dynamic_upper), 0)

        self.assertIsInstance(guide[6].start_point_parameter, RelativeFreeInstrumentParameter)
        self.assertEqual(guide[6].start_point_parameter.static_lower, 11.0)
        self.assertEqual(guide[6].start_point_parameter.static_upper, 30.0)
        lower_dynamic = guide[6].start_point_parameter.dynamic_lower[0]
        self.assertEqual(lower_dynamic.dependent_on[0], guide[5].start_point_parameter)
        self.assertEqual(lower_dynamic.constants[0], 0.0)
        self.assertEqual(lower_dynamic.function(10.0, 0.0), 10.0)
        self.assertEqual(len(guide[6].start_point_parameter.dynamic_lower), 1)
        self.assertEqual(len(guide[6].start_point_parameter.dynamic_upper), 0)

        self.assertIsInstance(guide[6].next_start_point_parameter, FixedInstrumentParameter)
        self.assertEqual(guide[6].next_start_point_parameter.get_value(), 30.0)

        self.assertIsInstance(guide[7].start_point_parameter, FixedInstrumentParameter)
        self.assertEqual(guide[7].start_point_parameter.get_value(), 30.0)

        self.assertIsInstance(guide[7].next_start_point_parameter, FreeInstrumentParameter)
        self.assertEqual(guide[7].next_start_point_parameter.get_lower_static_bound(), 30.0 + 2.0)
        self.assertEqual(guide[7].next_start_point_parameter.get_upper_static_bound(), 30.0 + 8.0)

        self.assertIsInstance(guide[8].start_point_parameter, FreeInstrumentParameter)
        self.assertEqual(guide[8].start_point_parameter.get_lower_static_bound(), 30.0 + 2.0)
        self.assertEqual(guide[8].start_point_parameter.get_upper_static_bound(), 30.0 + 8.0)

        self.assertIsInstance(guide[8].next_start_point_parameter, FixedInstrumentParameter)
        self.assertEqual(guide[8].next_start_point_parameter.get_value(), 80.0)

    def test_length_system_complex_guide_cases(self):
        """
        Ensures a complex guide with random input provides legal state

        A large number of random configurations that fall within the limits
        of each parameter is tested on a complex guide. For each configuration
        it is checked that start point and length of each element falls within
        the range given by the user. It is checked no element starts before 0
        or after the end of the guide, and that no element has a negative
        length. It is also indirectly tested that each element is after the
        proceeding one.
        """
        guide = setup_complex_guide()
        instr_parameters = InstrumentParameterContainer()

        total_length = 80.0
        length_system(guide, total_length, instr_parameters)

        test_guide_configurations(self, guide, total_length)

    def test_length_system_classic_ballistic_guide(self):
        guide = setup_classic_balistic_guide()
        instr_parameters = InstrumentParameterContainer()

        length_system(guide, 80.0, instr_parameters)

        self.assertEqual(guide[0].start_point.get_value(), 0.0)
        self.assertIsInstance(guide[0].start_point, FixedInstrumentParameter)

        self.assertIsInstance(guide[0].start_point_parameter, FixedInstrumentParameter)
        self.assertEqual(guide[0].start_point_parameter.get_value(), 0.0)

        self.assertIsInstance(guide[0].next_start_point_parameter, FreeInstrumentParameter)
        self.assertEqual(guide[0].next_start_point_parameter.get_lower_static_bound(), 2.0)
        self.assertEqual(guide[0].next_start_point_parameter.get_upper_static_bound(), 6.5)

        self.assertIsInstance(guide[1].start_point_parameter, FreeInstrumentParameter)
        self.assertEqual(guide[1].start_point_parameter.get_lower_static_bound(), 2.0)
        self.assertEqual(guide[1].start_point_parameter.get_upper_static_bound(), 6.5)

        self.assertIsInstance(guide[1].next_start_point_parameter, FixedInstrumentParameter)
        self.assertEqual(guide[1].next_start_point_parameter.get_value(), 6.5)

        self.assertIsInstance(guide[2].start_point_parameter, FixedInstrumentParameter)
        self.assertEqual(guide[2].start_point_parameter.get_value(), 6.5)

        self.assertIsInstance(guide[2].next_start_point_parameter, FixedInstrumentParameter)
        self.assertEqual(guide[2].next_start_point_parameter.get_value(), 6.6)

        self.assertIsInstance(guide[3].start_point_parameter, FixedInstrumentParameter)
        self.assertEqual(guide[3].start_point_parameter.get_value(), 6.6)

        self.assertIsInstance(guide[3].next_start_point_parameter, FreeInstrumentParameter)
        self.assertEqual(guide[3].next_start_point_parameter.get_lower_static_bound(), 6.5 + 0.1 + 2.0)
        self.assertEqual(guide[3].next_start_point_parameter.get_upper_static_bound(), 6.5 + 0.1 + 10.0)

        self.assertIsInstance(guide[4].start_point_parameter, FreeInstrumentParameter)
        self.assertEqual(guide[4].start_point_parameter.get_lower_static_bound(), 6.5 + 0.1 + 2.0)
        self.assertEqual(guide[4].start_point_parameter.get_upper_static_bound(), 6.5 + 0.1 + 10.0)

        self.assertIsInstance(guide[4].next_start_point_parameter, RelativeFreeInstrumentParameter)
        self.assertEqual(guide[4].next_start_point_parameter.static_lower, 80.0 - 0.5 - 10.0)
        self.assertEqual(guide[4].next_start_point_parameter.static_upper, 80.0 - 0.5 - 2.0)
        lower_dynamic = guide[4].next_start_point_parameter.dynamic_lower[0]
        self.assertEqual(lower_dynamic.dependent_on[0], guide[4].start_point_parameter)
        self.assertEqual(lower_dynamic.constants[0], 0.0)
        self.assertEqual(lower_dynamic.function(10.0, 1.0), 11.00)
        self.assertEqual(len(guide[4].next_start_point_parameter.dynamic_lower), 1)
        self.assertEqual(len(guide[4].next_start_point_parameter.dynamic_upper), 0)

        self.assertIsInstance(guide[5].start_point_parameter, RelativeFreeInstrumentParameter)
        self.assertEqual(guide[5].start_point_parameter.static_lower, 80.0 - 0.5 - 10.0)
        self.assertEqual(guide[5].start_point_parameter.static_upper, 80.0 - 0.5 - 2.0)
        lower_dynamic = guide[5].start_point_parameter.dynamic_lower[0]
        self.assertEqual(lower_dynamic.dependent_on[0], guide[4].start_point_parameter)
        self.assertEqual(lower_dynamic.constants[0], 0.0)
        self.assertEqual(lower_dynamic.function(10.0, 1.0), 11.00)
        self.assertEqual(len(guide[5].start_point_parameter.dynamic_lower), 1)
        self.assertEqual(len(guide[5].start_point_parameter.dynamic_upper), 0)

        self.assertIsInstance(guide[5].next_start_point_parameter, FixedInstrumentParameter)
        self.assertEqual(guide[5].next_start_point_parameter.get_value(), 80.0 - 0.5)

        self.assertIsInstance(guide[6].start_point_parameter, FixedInstrumentParameter)
        self.assertEqual(guide[6].start_point_parameter.get_value(), 80.0 - 0.5)

        self.assertIsInstance(guide[6].next_start_point_parameter, FixedInstrumentParameter)
        self.assertEqual(guide[6].next_start_point_parameter.get_value(), 80.0)

    def test_length_system_classic_balistic_guide_cases(self):
        """
        Ensures a ballistic guide with random input provides legal state

        A large number of random configurations that fall within the limits
        of each parameter is tested on a complex guide. For each configuration
        it is checked that start point and length of each element falls within
        the range given by the user. It is checked no element starts before 0
        or after the end of the guide, and that no element has a negative
        length. It is also indirectly tested that each element is after the
        proceeding one.
        """
        guide = setup_classic_balistic_guide()
        instr_parameters = InstrumentParameterContainer()

        total_length = 80.0
        length_system(guide, total_length, instr_parameters)

        test_guide_configurations(self, guide, total_length, plot=False)

    def test_length_system_bug_guide_1(self):
        guide = setup_bug_example_1()
        instr_parameters = InstrumentParameterContainer()

        length_system(guide, 60.0, instr_parameters)
        print(instr_parameters)


def test_guide_configurations(test_object, guide, total_length, plot=False):
    """
    Tests random configurations within allowed range of parameters

    Ensures each configuration is legal in terms of start points and lengths
    satisfying the user input and being meaningful.

    test_object: unittest object

    guide: list of Element objects

    total_length: float
        Total length of the guide

    plot: bool
        If true, plots change points and element lengths
    """
    cp_list = []
    for element in guide:
        cp_list.append(element.start_point_parameter)

    n_tests = 1000

    cp_data = np.zeros((len(cp_list), n_tests))
    length_data = np.zeros((len(cp_list), n_tests))

    for run_index in range(n_tests):
        # Start random test that can be repeated
        for cp in cp_list:
            cp.clear()

        for cp in cp_list:
            if isinstance(cp, RelativeFreeInstrumentParameter):
                lb = cp.get_lower_bound()
                ub = cp.get_upper_bound()

                cp.set_value(random.uniform(lb, ub))

        cp_values = []
        for cp in cp_list:
            cp.calculate()
            cp_values.append(cp.get_value())

        for index in range(len(cp_values)):
            cp = cp_values[index]
            if index < len(cp_values) - 1:
                next_cp = cp_values[index + 1]
            else:
                next_cp = guide[-1].next_start_point_parameter.get_value()

            element = guide[index]

            # Check start point satisfy specified requirements
            cp_data[index, run_index] = cp
            test_object.assertGreaterEqual(cp, 0.0)
            test_object.assertLess(cp, total_length)
            if is_free_parameter(element.start_point):
                min_start_point = element.start_point.get_lower_static_bound()
                if min_start_point is not None:
                    test_object.assertGreater(cp, min_start_point)

                max_start_point = element.start_point.get_upper_static_bound()
                if max_start_point is not None:
                    test_object.assertLess(cp, max_start_point)

            else:
                test_object.assertEqual(element.start_point.get_value(), cp)

            # Check length satisfy specified requirements
            element_length = next_cp - cp
            length_data[index, run_index] = element_length
            test_object.assertGreater(element_length, 0) # legal length

            if is_free_parameter(element.length):
                min_length = element.length.get_lower_static_bound()
                if min_length is None:
                    min_length = 0

                test_object.assertGreater(element_length, min_length)

                max_length = element.length.get_upper_static_bound()
                if max_length is not None:
                    test_object.assertLess(element_length, max_length)

            else:
                # May need to change this to approximately equal
                test_object.assertAlmostEqual(element.length.get_value(), element_length)

    if plot:
        fig, ax = plt.subplots()

        colors = cm.rainbow(np.linspace(0, 1, len(cp_list)))
        for index, color in zip(range(len(cp_list)), colors):
            ax.scatter(cp_data[index, :], length_data[index, :], marker=".", color=color)

        ax.set_xlabel("Change point [m]")
        ax.set_ylabel("Length [m]")

        plt.show()


def plot_change_points(elements, instrument_parameters):
    """
    Takes calculated instrument parameters with only change points
    """
    start_point_list = []
    for element in elements:
        start_point_list.append(element.start_point_parameter)

    start_point_list.append(elements[-1].next_start_point_parameter)

    fig, ax = plt.subplots()

    cb_index = 0
    for par in start_point_list:

        if cb_index < len(elements):
            describing_string = elements[cb_index].__repr__()  # + "\n length = " + length_string
        else:
            describing_string = ""

        if isinstance(par, RelativeFreeInstrumentParameter):
            value = par.get_value()
            if value is not None:
                ax.plot(cb_index, value, marker=".", color="blue")
                ax.text(cb_index, value, describing_string, ha="left", va="bottom", rotation=45)

            interval = [par.static_lower, par.static_upper]
            ax.plot([cb_index, cb_index], interval, color="blue")
            # todo: code for dynamic limit too

        elif isinstance(par, FreeInstrumentParameter):
            value = par.get_value()
            if value is not None:
                ax.plot(cb_index, value, marker=".", color="blue")
                ax.text(cb_index, value, describing_string, ha="left", va="bottom", rotation=45)

            interval = [par.get_lower_static_bound(), par.get_upper_static_bound()]
            ax.plot([cb_index, cb_index], interval, color="blue")

        if isinstance(par, FixedInstrumentParameter):
            ax.plot(cb_index, par.get_value(), marker=".", color="red")
            ax.text(cb_index, par.get_value(), describing_string, ha="left", va="bottom", rotation=45)

        if isinstance(par, DependentInstrumentParameter):
            par.calculate()
            ax.plot(cb_index, par.get_value(), marker=".", color="purple")
            ax.text(cb_index, par.get_value(), describing_string, ha="left", va="bottom", rotation=45)

        cb_index += 1

    plt.show()



