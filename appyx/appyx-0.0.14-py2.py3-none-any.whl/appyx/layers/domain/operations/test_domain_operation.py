from unittest import TestCase

from appyx.layers.domain.operations.domain_operation import DomainOperation


class DomainOperationTest(TestCase):
    """

    """

    def test_operation_has_error_when_the_string_doesnt_exist_in_collection(self):
        # Given a new operation
        operation = PrefixStringWithTest(["test_hereje", "qwerty"], "sarasa")

        # When we execute it
        result = operation.execute()

        # Then we get an abort return result
        self.assertTrue(result.has_errors())
        operation_error = result.errors()[0]
        self.assertEqual('El string no está', operation_error.text())

    def test_operation_ends_successfully_when_the_string_is_in_collection_with_prefix_already_attached(self):
        # Given a new operation
        operation = PrefixStringWithTest(["test_hereje", "qwerty"], "hereje")

        # When we execute it
        result = operation.execute()

        # Then we get an early return result
        self.assertTrue(result.is_successful())
        self.assertEqual("test_hereje", result.get_object())

    def test_attaches_prefix_successfully_when_the_string_is_in_collection(self):
        # Given a new operation
        operation = PrefixStringWithTest(["test_hereje", "qwerty"], "qwerty")

        # When we execute it
        result = operation.execute()

        # Then we get a successful result
        self.assertTrue(result.is_successful())
        self.assertEqual("test_qwerty", result.get_object())


class PrefixStringWithTest(DomainOperation):
    def __init__(self, a_string_collection, a_string_to_check):
        super().__init__()
        self._prefix = 'test_'
        self._string_collection = a_string_collection
        self._string_to_check = a_string_to_check

    def _execute_logic(self):

        matched_string = None
        for a_string in self._string_collection:
            if a_string.endswith(self._string_to_check):
                matched_string = a_string

        if matched_string is None:
            self._result.add_error('El string no está')
        else:
            self._result.set_object(self._add_test_prefix(matched_string))

    def _add_test_prefix(self, a_string):
        if a_string.startswith(self._prefix):
            return a_string
        return f'{self._prefix}{a_string}'
