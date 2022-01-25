from unittest import TestCase

from appyx import Result
from appyx.layers.domain.errors import BaseErrorFactory


class ResultTest(TestCase):

    def test_a_result_with_no_errors_is_successful(self):
        result = Result()

        self.assertTrue(result.is_successful())

    def test_a_new_result_has_no_errors(self):
        result = Result()

        self.assertEqual(0, len(result.errors()))
        self.assertFalse(result.has_errors())

    def test_a_result_with_errors_is_not_successful(self):
        result = Result()
        result.add_error("A sample message")

        self.assertFalse(result.is_successful())
        self.assertEqual(1, len(result.errors()))
        self.assertTrue(result.has_errors())

    def test_a_result_with_a_string_error_has_an_error_code(self):
        result = Result()
        expected_error_code = 'simple_error_code'
        result.add_error("A sample message")

        error_code = result.error_codes()[0]

        self.assertEqual(expected_error_code, error_code)
        self.assertTrue(result.has_error_with_code(expected_error_code))
        self.assertTrue(result.has_at_least_one_error_with_codes([expected_error_code]))
        self.assertTrue(result.has_at_least_one_error_with_codes([expected_error_code, 'an_unexpected_error_code']))
        self.assertFalse(result.has_at_least_one_error_with_codes(['an_unexpected_error_code']))

    def test_a_result_can_remove_identical_errors(self):
        result = Result()
        repeated_error = BaseErrorFactory().simple_error('error error!')
        result.add_error(repeated_error)
        result.add_error(repeated_error)

        result.delete_repeated_errors()

        self.assertEqual(1, len(result.errors()))

    def test_a_result_can_remove_equal_errors(self):
        result = Result()
        result.add_error(BaseErrorFactory().simple_error('A simple error'))
        result.add_error(BaseErrorFactory().simple_error('A simple error'))

        result.delete_repeated_errors()

        self.assertEqual(1, len(result.errors()))
