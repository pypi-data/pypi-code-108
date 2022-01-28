from unittest import TestCase

from aejuice_base_logger import Logger


class SomeTestCases(TestCase):

    @classmethod
    def setUpClass(cls):
        cls._logger = Logger("Package", "Test scope")

    def test_message_should_be_a_string(self):
        formatted_string = self._logger.get_log_message("This is logger message")

        assert isinstance(formatted_string, str), 'should be a string'

    def test_message_should_have_suggested_message(self):
        formatted_string, message = self.get_gets_message()

        self.assertRegex(formatted_string, message)

    def test_message_should_have_suggested_context(self):
        formatted_string, _ = self.get_gets_message()

        self.assertRegex(formatted_string, self._logger.context)

    def test_message_should_have_suggested_service_name(self):
        formatted_string, _ = self.get_gets_message()

        self.assertRegex(formatted_string, self._logger.service_name)

    def get_gets_message(self):
        message = "This is logger message"
        return self._logger.get_log_message(message), message
