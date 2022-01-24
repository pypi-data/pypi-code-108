from pydantic import ValidationError

from net_models.models.BaseModels.SharedModels import *
from tests.BaseTestClass import TestBaseNetModel, TestVendorIndependentBase



class TestKeyBase(TestVendorIndependentBase):

    TEST_CLASS = KeyBase

    def test_valid_01(self):
        test_cases = [
            {
                "test_name": "Test-xyz",
                "data": {
                    "encryption_type": 0,
                    "value": "SuperSecret"
                }
            }
        ]
        for test_case in test_cases:
            with self.subTest(msg=test_case["test_name"]):
                test_obj = self.TEST_CLASS(**test_case["data"])


class TestKeyChain(TestVendorIndependentBase):

    TEST_CLASS = KeyChain

    def test_valid_01(self):
        test_cases = [
            {
                "test_name": "Test-xyz",
                "data": {
                    "name": "KC-01",
                    "keys_list": [
                        {
                            "encryption_type": 0,
                            "value": "SuperSecret"
                        }
                    ]
                }
            }
        ]
        for test_case in test_cases:
            with self.subTest(msg=test_case["test_name"]):
                test_obj = self.TEST_CLASS(**test_case["data"])



class TestVLANModel(TestVendorIndependentBase):
    TEST_CLASS = VLANModel

    def test_valid_01(self):
        test_payload = {
            "vlan_id": "100",
            "name": "Vlan-100"
        }
        test_obj = self.TEST_CLASS(**test_payload)
        self.assertTrue(
            all([hasattr(test_obj, x) for x in test_payload.keys()])
        )


class TestRouteTarget(TestVendorIndependentBase):

    TEST_CLASS = RouteTarget


    def test_valid_01(self):
        test_cases = [
            {
                "test_name": "Test-01",
                "data": {
                    "rt": "1:1",
                    "action": "both"

                }
            },
            {
                "test_name": "Test-01",
                "data": {
                    "rt": "1:1",
                    "action": "both",
                    "rt_type": "stitching"
                }
            }
        ]
        for test_case in test_cases:
            with self.subTest(msg=test_case["test_name"]):
                test_obj = self.TEST_CLASS(**test_case["data"])

class TestVRFAddressFamily(TestVendorIndependentBase):

    TEST_CLASS = VRFAddressFamily


class TestVRFModel(TestVendorIndependentBase):

    TEST_CLASS = VRFModel

    def test_valid_01(self):
        test_cases = [
            {
                "test_name": "Test-01",
                "data": {
                    "name": "MGMT-VRF"
                }
            },
            {
                "test_name": "Test-02",
                "data": {
                    "name": "MGMT-VRF",
                    "rd": "1:1"
                }
            },
            {
                "test_name": "Test-03",
                "data": {
                    "name": "MGMT-VRF",
                    "rd": "1:1",
                    "address_families": [
                        {
                            "afi": "ipv4",
                            "route_targets": [
                                {
                                    "rt": "1:1",
                                    "action": "both"
                                },
                                {
                                    "rt": "1:1",
                                    "action": "both",
                                    "rt_type": "stitching"
                                }
                            ]
                        }
                    ]
                }
            }
        ]
        for test_case in test_cases:
            with self.subTest(msg=test_case["test_name"]):
                test_obj = self.TEST_CLASS(**test_case["data"])



class TestAclStandardIPv4(TestVendorIndependentBase):

    TEST_CLASS = AclStandardIPv4

    def test_01(self):
        test_cases = [
            {
                "test_name": "Test-01",
                "data": {
                    "name": 1,
                    "entries": [
                        {
                            "action": "permit",
                            "src_address": "192.168.0.0/24"
                        },
                        {
                            "action": "deny",
                            "src_address": "10.0.0.0",
                            "src_wildcard": "0.0.0.255"
                        }
                    ]
                },
                "result": ()
            }
        ]
        for test_case in test_cases:
            with self.subTest(msg=test_case["test_name"]):
                test_obj = self.TEST_CLASS(**test_case["data"])
                # print(test_obj.yaml(exclude_none=True))

if __name__ == '__main__':
    unittest.main()
