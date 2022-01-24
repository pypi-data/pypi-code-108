import io
import unittest
import unittest.mock

from guide_bot.parameters.instrument_parameters import InstrumentParameter
from guide_bot.parameters.instrument_parameters import FreeInstrumentParameter
from guide_bot.parameters.instrument_parameters import FixedInstrumentParameter
from guide_bot.parameters.instrument_parameters import DependentInstrumentParameter

from guide_bot.parameters.constraints import Constraint


class TestConstraints(unittest.TestCase):

    def test_basic_constraint(self):
        """
        Test a simple constraint with one parameter works
        """

        free = FreeInstrumentParameter("par", 1, 3)

        constraint = Constraint(free, lambda x: x - 2.0)

        self.assertFalse(constraint.can_evaluate())

        free.set_value(2.5)

        self.assertTrue(constraint.can_evaluate())

        self.assertAlmostEqual(constraint.evaluate(), 0.5)

        string = constraint.__repr__()

    def test_basic_with_constants_constraint(self):
        """
        Test a simple constraint with one parameter and constant works
        """

        free = FreeInstrumentParameter("par", 1, 3)

        constraint = Constraint(free, lambda x, a: x - a,
                                constants=2.8)

        self.assertFalse(constraint.can_evaluate())

        free.set_value(2.5)

        self.assertTrue(constraint.can_evaluate())

        self.assertAlmostEqual(constraint.evaluate(), -0.3)

    def test_basic_with_several_constraint(self):
        """
        Test a simple constraint with one parameter works
        """

        free1 = FreeInstrumentParameter("par", 1, 3)
        free2 = FreeInstrumentParameter("par", 0, 1)

        constraint = Constraint([free1, free2], lambda x, y, a, b: x + 2*y - a + b,
                                constants=[2.8, 100])

        self.assertFalse(constraint.can_evaluate())

        free1.set_value(2.5)
        free2.set_value(30)

        self.assertTrue(constraint.can_evaluate())

        self.assertAlmostEqual(constraint.evaluate(), 159.7)
