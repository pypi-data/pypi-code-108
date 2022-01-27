import unittest
import AutoFeedback.variable_error_messages as vc


class UnitTests(unittest.TestCase):
    def test_print(self):
        assert(vc.output_check("this\\nand that",
                               executable="test/printtest.py"))

    def test_notprint(self):
        assert(not vc.output_check("this and that",
                                   executable="test/printtest.py"))
