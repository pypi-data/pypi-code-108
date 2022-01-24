import io
import unittest
import unittest.mock

import numpy as np
import matplotlib.pyplot as plt

from guide_bot.parameters.instrument_parameters import InstrumentParameter
from guide_bot.parameters.instrument_parameters import FreeInstrumentParameter
from guide_bot.parameters.instrument_parameters import RelativeFreeInstrumentParameter
from guide_bot.parameters.instrument_parameters import FixedInstrumentParameter
from guide_bot.parameters.instrument_parameters import DependentInstrumentParameter


class TestInstrumentParameters(unittest.TestCase):

    def test_basic_InstrumentParameter(self):
        """
        Testing a InstrumentParameter can be made and manipulated
        """

        A = InstrumentParameter("test_par")
        self.assertEqual(A.name, "test_par")

        A.set_category("testing")
        self.assertEqual(A.category, "testing")

        A.value = 29
        A.clear()
        self.assertEqual(A.value, None)

        string = A.__repr__() # ensure __repr__ doesnt fail

    def test_Basic_FreeInstrumentParameter(self):
        """
        Testing basic properties of FreeInstrumentParameter class
        """

        free = FreeInstrumentParameter("test_free", -0.2, 1.2)

        self.assertEqual(free.lower_bound, -0.2)
        self.assertEqual(free.upper_bound, 1.2)
        self.assertEqual(free.value, None)

        limits = free.get_limits()
        self.assertEqual(limits[0], -0.2)
        self.assertEqual(limits[1], 1.2)

        self.assertEqual(free.get_lower_bound(), -0.2)
        self.assertEqual(free.get_upper_bound(), 1.2)

        string = free.__repr__()  # ensure __repr__ doesnt fail

    def test_Value_FreeInstrumentParameter(self):
        """
        Testing basic properties of FreeInstrumentParameter class
        """

        free = FreeInstrumentParameter("test_free", None, 1.2)

        self.assertEqual(free.lower_bound, None)
        self.assertEqual(free.upper_bound, 1.2)
        self.assertEqual(free.get_value(), None)
        self.assertEqual(free.ready_for_optimization(), False)

        free.set_value(1.1)
        self.assertEqual(free.get_value(), 1.1)

        free.clear()
        self.assertEqual(free.get_value(), None)

    def test_eq_FreeInstrumentParameter(self):
        """
        Testing basic properties of FreeInstrumentParameter class
        """

        free1 = FreeInstrumentParameter("test_free", None, 1.2)
        free2 = FreeInstrumentParameter("test_free", None, 1.2)

        self.assertEqual(free1, free2)

        free2.set_value(1.0)

        self.assertEqual(free1, free2)

        free2.upper_bound = 0.0

        self.assertNotEqual(free1, free2)

    def test_Basic_FixedInstrumentParameter(self):
        """
        Testing basic properties of FixedInstrumentParameter class
        """

        fixed = FixedInstrumentParameter("test_fixed", 3.0)

        self.assertEqual(fixed.get_value(), 3.0)

        fixed.clear()  # Fixed parameters ignores clear

        self.assertEqual(fixed.get_value(), 3.0)

        string = fixed.__repr__()  # ensure __repr__ doesnt fail

    def test_Basic_DependentInstrumentParameter(self):
        """
        Testing basic properties of DependentInstrumentParameter class

        Using a free and fixed parameter as dependents
        """

        free = FreeInstrumentParameter("test_free", -0.2, 1.2)
        free.set_value(0.5)

        fixed = FixedInstrumentParameter("test_fixed", 3.0)

        dependent = DependentInstrumentParameter("test_dependent", [free, fixed],
                                                 lambda x,y : 2*x + y)

        self.assertEqual(dependent.get_value(), None)
        self.assertTrue(dependent.depends_on_free())

        dependent.calculate()

        self.assertEqual(dependent.get_value(), 4.0)

        string = dependent.__repr__()  # ensure __repr__ doesnt fail

    def test_no_free_DependentInstrumentParameter(self):
        """
        Testing DependentInstrumentParameter with fixed dependents
        """

        fixed1 = FixedInstrumentParameter("test_fixed", 5.0)
        fixed2 = FixedInstrumentParameter("test_fixed", 3.0)

        dependent = DependentInstrumentParameter("test_dependent", [fixed1, fixed2],
                                                 lambda x, y: x - y)

        self.assertEqual(dependent.get_value(), None)
        self.assertFalse(dependent.depends_on_free())

        dependent.calculate()

        self.assertEqual(dependent.get_value(), 2.0)

    def test_Constant_DependentInstrumentParameter(self):
        """
        Testing DependentInstrumentParameter with the constants keyword argument
        """

        free = FreeInstrumentParameter("test_free", -0.2, 1.2)
        free.set_value(0.5)

        fixed = FixedInstrumentParameter("test_fixed", 3.0)

        dependent = DependentInstrumentParameter("test_dependent", [free, fixed],
                                                 lambda x, y, a, b: 2*x + y*a + b,
                                                 constants=[4.0, -1.0])

        self.assertEqual(dependent.get_value(), None)
        self.assertTrue(dependent.depends_on_free())

        dependent.calculate()

        self.assertEqual(dependent.get_value(), 12.0)

    def test_dependent_DependentInstrumentParameter(self):
        """
        Testing DependentInstrumentParameter dependent on another dependent
        """

        fixed1 = FixedInstrumentParameter("test_fixed", 5.0)
        fixed2 = FixedInstrumentParameter("test_fixed", 3.0)

        dependent = DependentInstrumentParameter("test_dependent", [fixed1, fixed2],
                                                 lambda x, y: x - y)

        free = FreeInstrumentParameter("new_free", 0.0, 1.0)
        free.set_value(100)

        dep_dep = DependentInstrumentParameter("dep_dep", [free, dependent],
                                               lambda x, y: x - 10*y)

        self.assertEqual(dep_dep.get_value(), None)
        self.assertTrue(dep_dep.depends_on_free())

        dep_dep.calculate()

        self.assertEqual(dep_dep.get_value(), 80.0)

    def test_RelativeFreeInstrumentParameter_simple(self):
        relative = RelativeFreeInstrumentParameter("test_relative", 4, 6.0)

        self.assertEqual(relative.lower_bound, 0.0)
        self.assertEqual(relative.upper_bound, 1.0)
        self.assertEqual(relative.static_lower, 4)
        self.assertEqual(relative.static_upper, 6)
        self.assertEqual(relative.get_value(), None)
        self.assertEqual(relative.ready_for_optimization(), True)

        relative.set_value(0.25)
        self.assertEqual(relative.get_value(), 4.0 + (6.0-4)*0.25)

        relative.clear()
        self.assertEqual(relative.get_value(), None)

    def test_RelativeFreeInstrumentParameter_dynamic_lower_limit(self):
        relative = RelativeFreeInstrumentParameter("test_relative", 4, 6.0)
        free_dep = FreeInstrumentParameter("dep", 3.0, 5.0)

        relative.add_lower_dynamic(free_dep, lambda x: x)

        free_dep.set_value(5.0)

        relative.set_value(0.25)
        self.assertEqual(relative.get_value(), 5.0 + (6.0-5.0)*0.25)

        relative.clear()
        self.assertEqual(relative.get_value(), None)

    def test_RelativeFreeInstrumentParameter_dynamic_upper_limit(self):
        relative = RelativeFreeInstrumentParameter("test_relative", 4, 6.0)
        free_dep = FreeInstrumentParameter("dep", 3.0, 5.0)

        relative.add_upper_dynamic(free_dep, lambda x: x)

        free_dep.set_value(5.5)

        relative.set_value(0.25)
        self.assertEqual(relative.get_value(), 4.0 + (5.5-4.0)*0.25)

        relative.clear()
        self.assertEqual(relative.get_value(), None)

    def test_RelativeFreeInstrumentParameter_illegal_interval(self):
        """
        Ensures illegal intervals can be defined without dynamic limits.

        Plotting available to ensure it is working correctly.
        """
        relative = RelativeFreeInstrumentParameter("test_relative", 10, 15)

        relative.add_dynamic_illegal_interval([], lambda a, b: a, lambda a,b: b, constants=[10.5, 11.5])
        relative.add_dynamic_illegal_interval([], lambda a, b: a, lambda a, b: b, constants=[12, 14])
        relative.add_dynamic_illegal_interval([], lambda a, b: a, lambda a, b: b, constants=[9, 10.2])
        relative.add_dynamic_illegal_interval([], lambda a, b: a, lambda a, b: b, constants=[13, 14.5])
        relative.add_dynamic_illegal_interval([], lambda a, b: a, lambda a, b: b, constants=[14.8, 15.3])

        self.assertEqual(len(relative.illegal_dynamic_intervals), 5)

        """
        n_points = 1000
        x_values = np.linspace(0.0, 1.0, n_points)
        y_values = np.zeros((n_points))

        for index in range(len(x_values)):
            relative.set_value(x_values[index])
            y_values[index] = relative.get_value()

        plt.scatter(x_values, y_values)
        plt.show()
        """

        relative.clear()
        self.assertEqual(relative.get_value(), None)

    def test_RelativeFreeInstrumentParameter_dynamic_illegal_interval(self):
        """
        Ensures illegal intervals can be defined with dynamic limits.

        Plotting available to ensure it is working correctly.
        """
        relative = RelativeFreeInstrumentParameter("test_relative", 1, 11)
        free_dep = FreeInstrumentParameter("dep", 3.0, 5.0)

        relative.add_dynamic_illegal_interval(free_dep, lambda x, a: x, lambda x, a: x+a, constants=[1.0])

        self.assertEqual(len(relative.illegal_dynamic_intervals), 1)

        free_dep.set_value(4.0)
        relative.set_value(0.25)
        self.assertEqual(relative.get_value(), 9*0.25 + 1)

        relative.set_value(0.8)
        self.assertEqual(relative.get_value(), 9*0.8 + 5.0 - 3.0)

        free_dep.set_value(5.0)
        relative.set_value(0.25)
        self.assertEqual(relative.get_value(), 9 * 0.25 + 1)

        relative.set_value(0.8)
        self.assertEqual(relative.get_value(), 9 * 0.8 + 6.0 - 4.0)

        """
        n_points = 1000
        x_values = np.linspace(0.0, 1.0, n_points)
        y_values = np.zeros((n_points))

        for index in range(len(x_values)):
            relative.set_value(x_values[index])
            y_values[index] = relative.get_value()

        plt.scatter(x_values, y_values)
        plt.show()
        """

        relative.clear()
        self.assertEqual(relative.get_value(), None)

    def test_RelativeFreeInstrumentParameter_dynamic_illegal_interval_elliptic_limit(self):
        """
        Ensures illegal intervals can be defined with dynamic limits in edge case

        Plotting available to ensure it is working correctly.
        """
        minor = RelativeFreeInstrumentParameter("minor_axis", -0.3, 0.1)
        dim = RelativeFreeInstrumentParameter("start_dimension", 0.0, 0.1)

        minor.add_dynamic_illegal_interval(dim, lambda x: -x, lambda x: x)

        self.assertEqual(len(minor.illegal_dynamic_intervals), 1)

        """
        minor.set_value(0.8)
        self.assertEqual(minor.get_value(), 9*0.8 + 5.0 - 3.0)

        dim.set_value(5.0)
        minor.set_value(0.25)
        self.assertEqual(minor.get_value(), 9 * 0.25 + 1)

        minor.set_value(0.8)
        self.assertEqual(minor.get_value(), 9 * 0.8 + 6.0 - 4.0)
        
        dim.set_value(1.0)

        n_points = 1000
        x_values = np.linspace(0.0, 1.0, n_points)
        y_values = np.zeros((n_points))

        for index in range(len(x_values)):
            minor.set_value(x_values[index])
            y_values[index] = minor.get_value()

        plt.scatter(x_values, y_values)
        plt.show()
        """

        minor.clear()
        self.assertEqual(minor.get_value(), None)

        dim.set_value(1.0)  # corresponds to 0.1 (coinciding with limit)

        minor.set_value(0.0)
        self.assertEqual(minor.get_value(), -0.3)

        minor.set_value(1.0)
        self.assertEqual(minor.get_value(), -0.1)

        minor.set_value(0.5)
        self.assertEqual(minor.get_value(), -0.2)