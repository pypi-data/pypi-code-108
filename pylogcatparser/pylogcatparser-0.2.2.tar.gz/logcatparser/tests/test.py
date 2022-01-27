from unittest import TestCase
import os
from ..logCatParser import *

this_test_file_path = os.path.dirname(os.path.abspath(__file__))






class SimpleTest(TestCase):
	def test_nr_exception_in_sample(self):
		test_file_path = os.path.join(this_test_file_path, "log_samples", "metaLog.log")
		parser = LogCatParser("threadtime", test_file_path)
		parser.parse_file()
		self.assertEqual(len(parser.get_logs_of_error("JavaException")), parser.stats.know_errors["JavaException"])

