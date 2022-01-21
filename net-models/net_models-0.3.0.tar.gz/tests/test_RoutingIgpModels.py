
from pydantic.error_wrappers import ValidationError

from net_models.models.routing import *

from tests.BaseTestClass import TestVendorIndependentBase




class TestRoutingIsisLspGenInterval(TestVendorIndependentBase):

    TEST_CLASS = RoutingIsisLspGenInterval

    def test_valid(self):

        with self.subTest(msg="Valid 01"):
            test_obj = self.TEST_CLASS(interval=5)
        with self.subTest(msg="Valid 02"):
            test_obj = self.TEST_CLASS(interval=5, init_wait=5)
        with self.subTest(msg="Valid 03"):
            test_obj = self.TEST_CLASS(interval=5, init_wait=5, wait=200)


    def test_invalid(self):

        with self.subTest(msg="Missing 'interval'"):
            with self.assertRaises(expected_exception=ValidationError):
                test_obj = self.TEST_CLASS(init_wait=5)
        with self.subTest(msg="Missing 'init_wait'"):
            with self.assertRaisesRegex(expected_exception=ValidationError,
                                        expected_regex="Field 'wait' can only be specified together with 'interval' and 'init_wait'."
                                        ):
                test_obj = self.TEST_CLASS(interval=5, wait=200)
