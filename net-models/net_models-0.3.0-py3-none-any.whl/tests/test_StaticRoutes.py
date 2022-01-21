import unittest
import ipaddress
from net_models.models import (
    StaticRouteV4,
    StaticRouteV6
)
from tests.BaseTestClass import TestVendorIndependentBase


class TestStaticRouteV4(TestVendorIndependentBase):

    TEST_CLASS = StaticRouteV4

    def test_valid_routes(self):
        test_cases = [
            {
                "test_name": "Test-Default-01",
                "data": {
                    "network": "0.0.0.0/0",
                    "next_hop": "1.2.3.4"
                },
                "result": {
                    "network": ipaddress.IPv4Network("0.0.0.0/0"),
                    "next_hop": ipaddress.IPv4Address("1.2.3.4")
                }
            },
            {
                "test_name": "Test-Default-02",
                "data": {
                    "network": "0.0.0.0/0.0.0.0",
                    "next_hop": "1.2.3.4"
                },
                "result": {
                    "network": ipaddress.IPv4Network("0.0.0.0/0"),
                    "next_hop": ipaddress.IPv4Address("1.2.3.4")
                }
            },
            {
                "test_name": "Test-Default-03",
                "data": {
                    "network": "0.0.0.0/0",
                    "interface": "Serial1/2/3",
                    "vrf": "TEST-VRF"
                },
                "result": {
                    "network": ipaddress.IPv4Network("0.0.0.0/0"),
                    "interface": "Serial1/2/3",
                    "vrf": "TEST-VRF"
                }
            },
            {
                "test_name": "Test-VRF-01",
                "data": {
                    "network": "192.168.0.0/255.255.255.0",
                    "next_hop": "1.2.3.4",
                    "vrf": "TEST-VRF"
                },
                "result": {
                    "network": ipaddress.IPv4Network("192.168.0.0/24"),
                    "next_hop": ipaddress.IPv4Address("1.2.3.4"),
                    "vrf": "TEST-VRF"
                }
            },
        ]
        for test_case in test_cases:
            with self.subTest(msg=test_case["test_name"]):
                want = test_case["result"]
                have = self.TEST_CLASS(**test_case["data"]).dict(exclude_none=True)
                self.assertDictEqual(want, have)



class TestStaticRouteV6(TestVendorIndependentBase):

    TEST_CLASS = StaticRouteV6


if __name__ == '__main__':
    unittest.main()
