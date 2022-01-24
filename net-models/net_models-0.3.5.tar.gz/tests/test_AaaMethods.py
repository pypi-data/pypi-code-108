from pydantic import ValidationError

from net_models.models import (
    IosAaaAction,
    IosAaaAuthenticationMethod,
    IosAaaAuthentication,
    IosAaaAuthorizationMethod,
    IosAaaAuthorization,
    IosAaaAccountingMethod,
    IosAaaAccountingAction,
    IosAaaAccounting,
    IosAaaConfig

)

from tests.BaseTestClass import TestVendorIndependentBase

class TestIosAaaAction(TestVendorIndependentBase):

    TEST_CLASS = IosAaaAction

    def test_valid_01(self):
        test_cases = [
            {
                "test_name": "Test-Valid-Local-01",
                "data": {
                    "action": "local"
                }
            },
            {
                "test_name": "Test-Valid-Group-01",
                "data": {
                    "action": "group",
                    "group": "tacacs+"
                }
            },
            {
                "test_name": "Test-Valid-Group-02",
                "data": {
                    "action": "group",
                    "group": "TACACS-GROUP"
                }
            },
            {
                "test_name": "Test-Valid-Group-02",
                "data": {
                    "action": "none"
                }
            }
        ]
        for test_case in test_cases:
            with self.subTest(msg=test_case["test_name"]):
                test_obj = self.TEST_CLASS(**test_case["data"])

    def test_missing_group(self):

        test_cases = [
            {
                "test_name": "Test-Missing-Group-01",
                "data": {
                    "action": "group",
                    # "group": "TACACS-GROUP"
                }
            }
        ]
        for test_case in test_cases:
            with self.subTest(msg=test_case["test_name"]):
                with self.assertRaisesRegex(expected_exception=ValidationError, expected_regex=r"When action == 'group', group is required\."):
                    test_obj = self.TEST_CLASS(**test_case["data"])

    def test_extra_group(self):

        test_cases = [
            {
                "test_name": "Test-Extra-Group-01",
                "data": {
                    "action": "local",
                    "group": "TACACS-GROUP"
                }
            }
        ]
        for test_case in test_cases:
            with self.subTest(msg=test_case["test_name"]):
                with self.assertRaisesRegex(expected_exception=ValidationError, expected_regex=r"Unless action == 'group', group must be None\."):
                    test_obj = self.TEST_CLASS(**test_case["data"])





class TestIosAaaAuthentication(TestVendorIndependentBase):

    TEST_CLASS = IosAaaAuthentication
    RESOURCE_DIR = TestVendorIndependentBase.RESOURCE_DIR.joinpath("aaa_methods").joinpath("cisco_ios")


class TestIosAaaAuthorization(TestVendorIndependentBase):

    TEST_CLASS = IosAaaAuthorization
    RESOURCE_DIR = TestVendorIndependentBase.RESOURCE_DIR.joinpath("aaa_methods").joinpath("cisco_ios")


class TestIosAaaAccountingAction(TestVendorIndependentBase):

    TEST_CLASS = IosAaaAccountingAction

    def test_valid_01(self):
        test_cases = [
            {
                "test_name": "Test-Valid-01",
                "data": {
                    "action": "group",
                    "group": "TACACS-GROUP",
                    "broadcast": True
                }
            },
            {
                "test_name": "Test-Valid-02",
                "data": {
                    "action": "none"
                }
            }
        ]
        for test_case in test_cases:
            with self.subTest(msg=test_case["test_name"]):
                test_obj = self.TEST_CLASS(**test_case["data"])




    def test_raises_01(self):
        data = {
            "action": "none",
            "broadcast": True
        }
        with self.assertRaisesRegex(expected_exception=ValidationError, expected_regex=r"If action == 'none', broadcast can only be in \[None, False\]\."):
            test_obj = self.TEST_CLASS(**data)


class TestIosAaaAccountingMethod(TestVendorIndependentBase):

    TEST_CLASS = IosAaaAccountingMethod

    def test_raises_01(self):
        data = {
            "record": "none",
            "action_list": [
                {
                    "action": "group",
                    "group": "TACACS-GROUP"
                }
            ]
        }
        with self.assertRaisesRegex(expected_exception=ValidationError, expected_regex=r"If record == 'none', action_list must be None\."):
            test_obj = self.TEST_CLASS(**data)

    def test_raises_02(self):
        data = {
            "record": "start-stop"
        }
        with self.assertRaisesRegex(expected_exception=ValidationError, expected_regex=r"Unless record == 'none', action_list cannot be None\."):
            test_obj = self.TEST_CLASS(**data)


class TestIosAaaAccounting(TestVendorIndependentBase):

    TEST_CLASS = IosAaaAccounting
    RESOURCE_DIR = TestVendorIndependentBase.RESOURCE_DIR.joinpath("aaa_methods").joinpath("cisco_ios")


class TestIosAaaConfig(TestVendorIndependentBase):

    TEST_CLASS = IosAaaConfig
    RESOURCE_DIR = TestVendorIndependentBase.RESOURCE_DIR.joinpath("aaa_methods").joinpath("cisco_ios")




if __name__ == '__main__':
    unittest.main()


