import unittest
import logging

logger = logging.getLogger()

from autoai_ts_libs.transforms.imputers import (
    AutoAITSImputer,
    IMPUTER_DISPLAY_NAMES
)

class ImputerNameTest(unittest.TestCase):
    def setUp(self):
        self.imputers = AutoAITSImputer.get_default_imputer_list()

    @unittest.skip("skip for now")
    def test_get_imputer_display_name(self):
        # All imputers should have a display name
        for i in self.imputers:
            with self.subTest(imputer=i):
                AutoAITSImputer.get_display_name(i)

    @unittest.skip("skip for now")
    def test_get_imputer_name(self):
        # All imputers should return a name
        # That name should end with "_imputer"
        for i in self.imputers:
            with self.subTest(imputer=i):
                n = AutoAITSImputer.get_imputer_name(i)
                self.assertTrue(n.endswith("_imputer"))

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
