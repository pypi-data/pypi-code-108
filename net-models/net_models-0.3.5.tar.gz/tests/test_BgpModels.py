import unittest
from pydantic import ValidationError
from net_models.models.routing import (
    BgpTimers,
    BgpFallOver,
    BgpNeighborBase,
    BgpPeerGroup,
    BgpNeighbor,
    BgpRedistributeEntry,
    BgpAddressFamily,
    RoutingBgpProcess,

)
from tests.BaseTestClass import TestVendorIndependentBase

class TestViBgpBase(TestVendorIndependentBase):

    RESOURCE_DIR = TestVendorIndependentBase.RESOURCE_DIR.joinpath("routing").joinpath("vi")

class TestBgpTimers(TestViBgpBase):

    TEST_CLASS = BgpTimers


class TestBgpFallOver(TestViBgpBase):

    TEST_CLASS = BgpFallOver


class TestBgpNeighborBase(TestViBgpBase):

    TEST_CLASS = BgpNeighborBase


class TestBgpPeerGroup(TestViBgpBase):

    TEST_CLASS = BgpPeerGroup


class TestBgpNeighbor(TestViBgpBase):

    TEST_CLASS = BgpNeighbor

    def test_empty_neighbor(self):
        with self.assertRaisesRegex(expected_exception=ValidationError, expected_regex=r"Neighbor needs `address` specified, unless there is at least 'name'."):
            test_obj = self.TEST_CLASS.parse_obj({})


class TestBgpRedistributeEntry(TestViBgpBase):

    TEST_CLASS = BgpRedistributeEntry


class TestBgpAddressFamily(TestViBgpBase):

    TEST_CLASS = BgpAddressFamily


class TestRoutingBgpProcess(TestViBgpBase):

    TEST_CLASS = RoutingBgpProcess

    def test_existing_peer_group(self):
        data = {
            "asn": 64496,
            "neighbors": [
                {
                    "name": "Router-01",
                    "address": "192.0.2.1",
                    "peer_group": "PG-01"
                }
            ],
            "peer_groups": [
                {
                    "name": "PG-01",
                    "asn": 64496
                }
            ]
        }
        test_obj = self.TEST_CLASS.parse_obj(data)


    def test_global_missing_address(self):
        data = {
            "asn": 64496,
            "neighbors": [
                {
                    "name": "Router-01"
                }
            ]
        }
        with self.assertRaisesRegex(expected_exception=ValidationError, expected_regex=r"Global BGP Neighbors must have either 'address', or both \['name', 'dest_interface'\]"):
            test_obj = self.TEST_CLASS.parse_obj(data)

    def test_global_missing_peer_groups(self):
        data = {
            "asn": 64496,
            "neighbors": [
                {
                    "name": "Router-01",
                    "address": "192.0.2.1",
                    "peer_group": "PG-01"
                }
            ]
        }
        with self.assertRaisesRegex(expected_exception=ValidationError, expected_regex=r"'peer_groups' is undefined."):
            test_obj = self.TEST_CLASS.parse_obj(data)

    def test_global_missing_peer_group(self):
        data = {
            "asn": 64496,
            "neighbors": [
                {
                    "name": "Router-01",
                    "address": "192.0.2.1",
                    "peer_group": "PG-01"
                }
            ],
            "peer_groups": [
                {
                    "name": "PG-02"
                }
            ]
        }
        with self.assertRaisesRegex(expected_exception=ValidationError, expected_regex=r"Can not find 'peer_group' PG-01."):
            test_obj = self.TEST_CLASS.parse_obj(data)

    def test_missing_asn(self):
        data = {
            "asn": 64496,
            "neighbors": [
                {
                    "name": "Router-01",
                    "address": "192.0.2.1",
                }
            ]
        }
        with self.assertRaisesRegex(expected_exception=ValidationError, expected_regex=r"Global BGP Neighbor must have either 'asn' or 'peer_group' \(with 'asn' set\)."):
            test_obj = self.TEST_CLASS.parse_obj(data)

    def test_missing_asn_peer_group(self):
        data = {
            "asn": 64496,
            "neighbors": [
                {
                    "name": "Router-01",
                    "address": "192.0.2.1",
                    "peer_group": "PG-01"
                }
            ],
            "peer_groups": [
                {
                    "name": "PG-01"
                }
            ]
        }
        with self.assertRaisesRegex(expected_exception=ValidationError, expected_regex=r"Neither neighbor nor its 'peer_group' have 'asn' defined."):
            test_obj = self.TEST_CLASS.parse_obj(data)

    def test_duplicate_peer_groups(self):
        data = {
            "asn": 64496,
            "peer_groups": [
                {"name": "PG-01"},
                {"name": "PG-01"}
            ]
        }
        with self.assertRaisesRegex(expected_exception=ValidationError,
                                    expected_regex=r"Given models .*? contain duplicate values for the following fields: \['name'\]\."):
            test_obj = self.TEST_CLASS.parse_obj(data)






if __name__ == '__main__':
    unittest.main()
