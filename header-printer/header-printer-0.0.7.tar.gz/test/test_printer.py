import io
from unittest import TestCase, mock

from header_printer import print_header


class TestPrinter(TestCase):
    @mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_print_correct_header_text(self, mock_stdout):
        # GIVEN the text to be displayed on the header.
        header_text = "Some header text."
        # WHEN we use the function for displaying formatted header with text.
        print_header(header_text)
        # THEN the passed text should appear on the terminal.
        self.assertIn(header_text, mock_stdout.getvalue())
