import unittest

from appyx import Result
from appyx.layers.application.interactions.validators.generic import IsAPositiveInteger, IsString
from appyx.layers.interface.validators.dict_validator import DictValidator


class DictValidatorTest(unittest.TestCase):
    def test_empty_dict_has_keys_included(self):
        dictionary = {}
        validator = DictValidator()

        result = validator.validate_keys_included_in(dictionary, [])

        self.assertTrue(result.is_successful())

    def test_dict_has_keys_included(self):
        dictionary = {'key1': 'value1'}
        validator = DictValidator()

        result = validator.validate_keys_included_in(dictionary, ['key1', 'key2'])

        self.assertTrue(result.is_successful())

    def test_when_dict_has_keys_not_included_an_error_is_answered(self):
        dictionary = {'key3': 'value1'}
        validator = DictValidator()

        result = validator.validate_keys_included_in(dictionary, ['key1', 'key2'])

        self.assertTrue(result.has_errors())
        self.assertTrue(result.has_error_with_code('simple_error_code'))
        self.assertEqual(result.errors()[0].text(), 'Key key3 is not included in [\'key1\', \'key2\']')

    def test_we_can_validate_the_dictionary_keys(self):
        dictionary = {1: 'un valor', 2: 3, 'key invalida': 'una string'}
        validator = DictValidator()

        result = validator.validate_keys_with_result(dictionary, [IsAPositiveInteger()], Result())

        self.assertTrue(result.has_errors())
        self.assertEqual(1, len(result.errors()))

    def test_we_can_validate_the_dictionary_values(self):
        dictionary = {1: 'un valor', 2: 3, 'key invalida': 'una string'}
        validator = DictValidator()

        result = validator.validate_values_with_result(dictionary, [IsString()], Result())

        self.assertTrue(result.has_errors())
        self.assertEqual(1, len(result.errors()))

    def test_we_can_validate_the_dictionary_has_at_least_some_keys(self):
        dictionary = {1: 'un valor', 2: 3, 'key textual': 'una string'}
        validator = DictValidator()

        result = validator.validate_keys_defined(dictionary, [1, 'key textual'], Result())

        self.assertTrue(result.is_successful())

    def test_we_can_validate_the_dictionary_doesnt_have_at_least_some_keys(self):
        dictionary = {1: 'un valor', 2: 3, 'key textual': 'una string'}
        validator = DictValidator()

        result = validator.validate_keys_defined(dictionary, [1, 2, 3], Result())

        self.assertTrue(result.has_errors())

    def test_we_can_validate_the_dictionary_has_exactly_some_keys(self):
        dictionary = {1: 'un valor', 2: 3, 'key textual': 'una string'}
        validator = DictValidator()

        result = validator.validate_has_exact_keys(dictionary, [1, 2, 'key textual'], Result())

        self.assertTrue(result.is_successful())

    def test_we_can_validate_the_dictionary_doesnt_have_exactly_some_keys(self):
        dictionary = {1: 'un valor', 2: 3, 'key textual': 'una string'}
        validator = DictValidator()

        result = validator.validate_has_exact_keys(dictionary, [1, 2], Result())

        self.assertTrue(result.has_errors())

    def test_we_can_validate_the_dictionary_has_a_key_and_its_value_is_valid(self):
        dictionary = {1: 'un valor', 2: 3, 'key textual': 'una string'}
        validator = DictValidator()

        result = validator.validate_key_defined(dictionary, 2, Result(), [IsAPositiveInteger()])

        self.assertTrue(result.is_successful())

    def test_sadly_a_dict_validator_cannot_validate_a_dictionary(self):
        dictionary = {1: 'un valor', 2: 3, 'key textual': 'una string'}
        validator = DictValidator()
        not_implemented_error_raised = False

        try:
            result = validator.validate(dictionary)
        except NotImplementedError:
            not_implemented_error_raised = True

        self.assertTrue(not_implemented_error_raised)
