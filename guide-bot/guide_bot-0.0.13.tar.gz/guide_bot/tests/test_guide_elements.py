import io
import unittest
import unittest.mock

from guide_bot.parameters.instrument_parameters import InstrumentParameter
from guide_bot.parameters.instrument_parameters import FreeInstrumentParameter
from guide_bot.parameters.instrument_parameters import RelativeFreeInstrumentParameter
from guide_bot.parameters.instrument_parameters import FixedInstrumentParameter
from guide_bot.parameters.instrument_parameters import DependentInstrumentParameter

from guide_bot.parameters.constraints import Constraint

from guide_bot.parameters.instrument_parameter_container import InstrumentParameterContainer

from guide_bot.base_elements.guide_elements import handle_input_parameter
from guide_bot.base_elements.guide_elements import Element
from guide_bot.base_elements.guide_elements import GuideElement


class Test_handle_input_parameter(unittest.TestCase):

    def test_simple_fixed_parameter(self):
        """
        Basic test of handle_input_parameter, fixed value given
        """

        par = handle_input_parameter("test_par", 0.1)

        self.assertIsInstance(par, FixedInstrumentParameter)
        self.assertEqual(par.get_value(), 0.1)

    def test_simple_free_parameter(self):
        """
        Basic test of handle_input_parameter, range given
        """

        par = handle_input_parameter("test_par", [-3.2, 4.2])

        self.assertIsInstance(par, RelativeFreeInstrumentParameter)
        self.assertEqual(par.static_lower, -3.2)
        self.assertEqual(par.static_upper, 4.2)

    def test_simple_empty_free_parameter(self):
        """
        Basic test of handle_input_parameter, None given
        """

        par = handle_input_parameter("test_par", None)

        self.assertIsInstance(par, RelativeFreeInstrumentParameter)
        self.assertEqual(par.static_lower, None)
        self.assertEqual(par.static_upper, None)

    def test_simple_empty_with_defaults_free_parameter(self):
        """
        Basic test of handle_input_parameter, None given
        """

        par = handle_input_parameter("test_par", None,
                                     default_min=-0.2, default_max=0.8)

        self.assertIsInstance(par, RelativeFreeInstrumentParameter)
        self.assertEqual(par.static_lower, -0.2)
        self.assertEqual(par.static_upper, 0.8)

    def test_defined_free_parameter(self):
        """
        Basic test of handle_input_parameter, free parameter given
        """

        input = FreeInstrumentParameter("free", 0.1, 0.8)

        par = handle_input_parameter("test_par", input)

        self.assertIsInstance(par, FreeInstrumentParameter)
        self.assertEqual(par.get_lower_bound(), 0.1)
        self.assertEqual(par.get_upper_bound(), 0.8)

    def test_defined_fixed_parameter(self):
        """
        Basic test of handle_input_parameter, fixed parameter given
        """

        input = FixedInstrumentParameter("fixed", 0.5)

        par = handle_input_parameter("test_par", input)

        self.assertIsInstance(par, FixedInstrumentParameter)
        self.assertEqual(par.get_value(), 0.5)

    def test_defined_dependent_on_free_parameter(self):
        """
        Basic test of handle_input_parameter, fixed
        """

        free = FreeInstrumentParameter("free", -0.5, 1.0)
        fixed = FixedInstrumentParameter("fixed", 0.5)
        input = DependentInstrumentParameter("dep", [free, fixed], lambda x,y: x + 2*y)

        par = handle_input_parameter("test_par", input)

        self.assertIsInstance(par, DependentInstrumentParameter)

        free.set_value(0.8)
        par.calculate()

        self.assertEqual(par.get_value(), 1.8)

    def test_defined_dependent_on_fixed_parameters(self):
        """
        Basic test of handle_input_parameter, fixed
        """

        fixed1 = FixedInstrumentParameter("fixed1", 1.0)
        fixed2 = FixedInstrumentParameter("fixed2", 0.5)
        input = DependentInstrumentParameter("dep", [fixed1, fixed2], lambda x,y: x + 2*y)

        par = handle_input_parameter("test_par", input)

        self.assertIsInstance(par, FixedInstrumentParameter)

        self.assertEqual(par.get_value(), 2.0)


class TestGuideElement(unittest.TestCase):
    def test_basic_element(self):
        """
        Testing basic Element with fixed length and start point
        """

        element = Element("test", length=0.5, start_point=40)

        self.assertIsInstance(element.length, FixedInstrumentParameter)
        self.assertEqual(element.length.get_value(), 0.5)

        self.assertIsInstance(element.start_point, FixedInstrumentParameter)
        self.assertEqual(element.start_point.get_value(), 40)

        string = element.__repr__() # check __repr__ doesn't fail

    def test_basic_empty_element(self):
        """
        Testing basic Element with no info
        """

        element = Element("test")

        self.assertIsInstance(element.length, FreeInstrumentParameter)
        self.assertEqual(element.length.get_lower_static_bound(), None)
        self.assertEqual(element.length.get_upper_static_bound(), None)

        self.assertIsInstance(element.start_point, FreeInstrumentParameter)
        self.assertEqual(element.start_point.get_lower_static_bound(), None)
        self.assertEqual(element.start_point.get_upper_static_bound(), None)

        string = element.__repr__()  # check __repr__ doesn't fail

    def test_basic_element_owner(self):
        """
        Testing basic Element with fixed length and start point
        """

        element = Element("test", length=0.5, start_point=40)

        self.assertIsInstance(element.length, FixedInstrumentParameter)
        self.assertEqual(element.length.get_value(), 0.5)

        self.assertIsInstance(element.start_point, FixedInstrumentParameter)
        self.assertEqual(element.start_point.get_value(), 40)

        element.set_owner("test")
        self.assertEqual(element.owner, "test")

        string = element.__repr__() # check __repr__ doesn't fail


class TestElement(unittest.TestCase):
    def test_basic_element(self):
        """
        Testing basic Element with fixed length and start point, and start dimensions fixed
        """

        element = GuideElement("test", length=0.5, start_point=40,
                               start_width=0.04, start_height=0.08)

        self.assertIsInstance(element.length, FixedInstrumentParameter)
        self.assertEqual(element.length.get_value(), 0.5)

        self.assertIsInstance(element.start_point, FixedInstrumentParameter)
        self.assertEqual(element.start_point.get_value(), 40)

        self.assertIsInstance(element.start_width, FixedInstrumentParameter)
        self.assertEqual(element.start_width.get_value(), 0.04)

        self.assertIsInstance(element.start_height, FixedInstrumentParameter)
        self.assertEqual(element.start_height.get_value(), 0.08)

        string = element.__repr__() # check __repr__ doesn't fail

    def test_basic_element_with_end(self):
        """
        Testing basic Element with all parameters fixed
        """

        element = GuideElement("test", length=0.5, start_point=40,
                               start_width=0.04, start_height=0.08,
                               end_width=0.01, end_height=0.2)

        self.assertIsInstance(element.length, FixedInstrumentParameter)
        self.assertEqual(element.length.get_value(), 0.5)

        self.assertIsInstance(element.start_point, FixedInstrumentParameter)
        self.assertEqual(element.start_point.get_value(), 40)

        self.assertIsInstance(element.start_width, FixedInstrumentParameter)
        self.assertEqual(element.start_width.get_value(), 0.04)

        self.assertIsInstance(element.start_height, FixedInstrumentParameter)
        self.assertEqual(element.start_height.get_value(), 0.08)

        self.assertIsInstance(element.end_width, FixedInstrumentParameter)
        self.assertEqual(element.end_width.get_value(), 0.01)

        self.assertIsInstance(element.end_height, FixedInstrumentParameter)
        self.assertEqual(element.end_height.get_value(), 0.2)

        string = element.__repr__() # check __repr__ doesn't fail

    def test_basic_empty_element(self):
        """
        Testing basic Element with no info
        """

        element = GuideElement("test")

        self.assertIsInstance(element.length, FreeInstrumentParameter)
        self.assertEqual(element.length.get_lower_static_bound(), None)
        self.assertEqual(element.length.get_upper_static_bound(), None)

        self.assertIsInstance(element.start_point, FreeInstrumentParameter)
        self.assertEqual(element.start_point.get_lower_static_bound(), None)
        self.assertEqual(element.start_point.get_upper_static_bound(), None)

        self.assertIsInstance(element.start_width, RelativeFreeInstrumentParameter)
        self.assertEqual(element.start_width.static_lower, 0.005)
        self.assertEqual(element.start_width.static_upper, 0.15)

        self.assertIsInstance(element.start_height, RelativeFreeInstrumentParameter)
        self.assertEqual(element.start_height.static_lower, 0.005)
        self.assertEqual(element.start_height.static_upper, 0.15)

        string = element.__repr__()  # check __repr__ doesn't fail

    def test_basic_element_owner(self):
        """
        Testing basic Element with fixed length and start point
        """

        element = GuideElement("test_element")

        element.set_owner("test")
        self.assertEqual(element.owner, "test")

        string = element.__repr__() # check __repr__ doesn't fail

    def test_setup_instr_and_pars_element(self):
        """
        Testing basic Element with no info
        """

        element = GuideElement("test")

        self.assertIsInstance(element.length, FreeInstrumentParameter)
        self.assertEqual(element.length.get_lower_static_bound(), None)
        self.assertEqual(element.length.get_upper_static_bound(), None)

        self.assertIsInstance(element.start_point, FreeInstrumentParameter)
        self.assertEqual(element.start_point.get_lower_static_bound(), None)
        self.assertEqual(element.start_point.get_upper_static_bound(), None)

        test_container = InstrumentParameterContainer()
        dummy_instrument = 5.0

        element.setup_instrument_and_parameters(dummy_instrument, test_container)

        start_width = None
        start_height = None
        for par in element.current_parameters.all_parameters:
            if par.name == "test_start_width":
                start_width = par
            if par.name == "test_start_height":
                start_height = par

        self.assertIsInstance(element.start_width, RelativeFreeInstrumentParameter)
        self.assertEqual(start_width.static_lower, 0.005)
        self.assertEqual(start_width.static_upper, 0.15)

        self.assertIsInstance(element.start_height, RelativeFreeInstrumentParameter)
        self.assertEqual(start_height.static_lower, 0.005)
        self.assertEqual(start_height.static_upper, 0.15)

        string = element.__repr__()  # check __repr__ doesn't fail


