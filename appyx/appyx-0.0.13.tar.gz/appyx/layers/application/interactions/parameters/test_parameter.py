import unittest

from appyx.layers.application.interactions.parameters.parameter import Parameter
from appyx.layers.application.interactions.validators.generic import NotNone, MinimumValue, IsADateString


class ParameterTest(unittest.TestCase):
    def test_a_parameter_with_no_validators_is_valid(self):
        parameter = Parameter('nombre', [])

        result = parameter.validate('Pedro')

        self.assertTrue(result.is_successful())
        self.assertEqual('nombre', parameter.name())

    def test_a_parameter_with_validators_and_invalid_argument_is_not_valid(self):
        parameter = Parameter('edad', [NotNone(), MinimumValue(0)])

        result = parameter.validate(-1)

        self.assertTrue(result.has_errors())

    def test_a_parameter_can_have_a_description(self):
        parameter = Parameter('inicio', [NotNone(), IsADateString('2021-08-04'), 'Fecha de inicio del trámite'])

        description = parameter.description()

        self.assertTrue('Fecha de inicio del trámite', description)
