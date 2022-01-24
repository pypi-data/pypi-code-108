import io
import unittest
import unittest.mock

from guide_bot.parameters.instrument_parameters import InstrumentParameter
from guide_bot.parameters.instrument_parameters import FreeInstrumentParameter
from guide_bot.parameters.instrument_parameters import FixedInstrumentParameter
from guide_bot.parameters.instrument_parameters import DependentInstrumentParameter

from guide_bot.parameters.constraints import Constraint

from guide_bot.parameters.instrument_parameter_container import InstrumentParameterContainer

def setup_basic_container():


    container = InstrumentParameterContainer()

    free = FreeInstrumentParameter("test_free", 0.1, 2.3)
    fixed = FixedInstrumentParameter("test_fixed", 0.5)

    container.add_parameter(free)
    container.add_parameter(fixed)

    return container


class TestInstrumentParameterContainer(unittest.TestCase):

    def test_basic_container(self):
        """
        Basic test of InstrumentParameterContainer

        """

        container = InstrumentParameterContainer()

        self.assertEqual(container.get_N_free_parameters(), 0)

        container.clear() # Check clear doesn't fail

        container.set_current_category("testing_time")
        self.assertEqual(container.current_category, "testing_time")

        string = container.__repr__() # test __repr__() doesnt fail

    def test_occupied_container(self):

        container = setup_basic_container()

        self.assertEqual(container.get_N_free_parameters(), 1)
        self.assertEqual(container.get_lower_bounds(), [0.1])
        self.assertEqual(container.get_upper_bounds(), [2.3])

        # Test setting a value for free
        container.set_values([0.8])

        output = container.extract_instrument_parameters()

        self.assertEqual(output["test_free"], 0.8)
        self.assertEqual(output["test_fixed"], 0.5)

        # Test clear removes value
        container.clear()

        output = container.extract_instrument_parameters()

        self.assertEqual(output["test_free"], None)
        self.assertEqual(output["test_fixed"], 0.5)