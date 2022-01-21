from unittest import TestCase

from canvas_workflow_kit.builtin_cqms.helper_population import Population


class TestPopulation(TestCase):

    def test___init__(self):
        tested = Population()
        self.assertIsNone(tested.in_initial_population)
        self.assertIsNone(tested.in_denominator)
        self.assertIsNone(tested.in_numerator)

    def test_set_initial_population(self):
        tested = Population()

        tested.set_initial_population(True)
        self.assertTrue(tested.in_initial_population)
        self.assertTrue(tested.in_denominator)
        self.assertTrue(tested.in_numerator)

        tested.set_initial_population(False)
        self.assertFalse(tested.in_initial_population)
        self.assertFalse(tested.in_denominator)
        self.assertFalse(tested.in_numerator)

    def test_set_denominator(self):
        tested = Population()

        tested.set_denominator(True)
        self.assertIsNone(tested.in_initial_population)
        self.assertTrue(tested.in_denominator)
        self.assertTrue(tested.in_numerator)

        tested.set_denominator(False)
        self.assertIsNone(tested.in_initial_population)
        self.assertFalse(tested.in_denominator)
        self.assertFalse(tested.in_numerator)

    def test_set_numerator(self):
        tested = Population()

        tested.set_numerator(True)
        self.assertIsNone(tested.in_initial_population)
        self.assertIsNone(tested.in_denominator)
        self.assertTrue(tested.in_numerator)

        tested.set_numerator(False)
        self.assertIsNone(tested.in_initial_population)
        self.assertIsNone(tested.in_denominator)
        self.assertFalse(tested.in_numerator)
