import unittest
from pydantic.typing import List, Dict, Callable
from net_models.validators import *
from net_models.models.interfaces import InterfaceModel

class TestValidatorBase(unittest.TestCase):


    def common_testcase(self, test_cases: List[Dict], test_func: Callable):
        for test_case in test_cases:
            with self.subTest(msg=test_case["test_name"]):
                want = test_case["result"]
                have = test_func(**test_case["data"])
                self.assertEqual(want, have)


class TestExpandVlanRange(TestValidatorBase):

    def test_common_testcase(self):
        test_cases = [
            {
                "test_name": "Test-Integer-List-No-Duplicates",
                "data": {
                    "vlan_range": [1, 2, 3, 4, 5, 10]
                },
                "result": [1, 2, 3, 4, 5, 10]
            },
            {
                "test_name": "Test-Integer-List-With-Duplicates",
                "data": {
                    "vlan_range": [1, 2, 2, 3, 4, 4, 5, 10]
                },
                "result": [1, 2, 3, 4, 5, 10]
            },
            {
                "test_name": "Test-String-Range-01",
                "data": {
                    "vlan_range": "1-5,10"
                },
                "result": [1, 2, 3, 4, 5, 10]
            },
            {
                "test_name": "Test-Mixed-List-Range-01",
                "data": {
                    "vlan_range": ["1-3", 4, 5, "10"]
                },
                "result": [1, 2, 3, 4, 5, 10]
            },
            {
                "test_name": "Test-Mixed-List-Range-02",
                "data": {
                    "vlan_range": ["1-3", 3, "4-5", "10"]
                },
                "result": [1, 2, 3, 4, 5, 10]
            },

        ]
        super().common_testcase(test_cases=test_cases, test_func=expand_vlan_range)


    def test_invalid_range_01(self):

        with self.assertRaisesRegex(expected_exception=ValueError, expected_regex=f"Invalid 'vlan_range' element: 1-x."):
            result = expand_vlan_range(vlan_range="1-x")

    def test_invalid_range_02(self):

        with self.assertRaisesRegex(expected_exception=ValueError, expected_regex=f"Invalid 'vlan_range' element: 5-4. Range beggining >= end."):
            result = expand_vlan_range(vlan_range="5-4")

    def test_invalid_range_03(self):

        with self.assertRaisesRegex(expected_exception=TypeError, expected_regex=r"Invalid 'vlan_range' element type: <class 'NoneType'>. Expected Union\[str, int\]."):
            result = expand_vlan_range(vlan_range=[1, "2", None])

    def test_invalid_range_04(self):

        with self.assertRaisesRegex(expected_exception=TypeError, expected_regex=r"Invalid type of 'vlan_range'. Expected Union\[list, str\], got <class 'NoneType'>."):
            result = expand_vlan_range(vlan_range=None)

    def test_invalid_range_05(self):

        with self.assertRaisesRegex(expected_exception=ValueError, expected_regex=r"Invalid 'vlan_range' element: 1-3-5."):
            result = expand_vlan_range(vlan_range="1-3-5")

    def test_invalid_range_06(self):

        with self.assertRaisesRegex(expected_exception=ValueError, expected_regex=r"Invalid 'vlan_range' element: Foo."):
            result = expand_vlan_range(vlan_range="Foo")



class TestNormalizeInterfaceName(TestValidatorBase):

    def test_common_testcase(self):
        test_cases = [
            {
                "test_name": "Test-Ethernet-01",
                "data": {
                    "interface_name": "ethernet0/1"
                },
                "result": "Ethernet0/1"
            },
            {
                "test_name": "Test-Vlan-01",
                "data": {
                    "interface_name": "Vl100"
                },
                "result": "Vlan100"
            }
        ]
        super().common_testcase(test_cases=test_cases, test_func=normalize_interface_name)


    def test_normalize_name_2(self):

        name = 'gigabitEtHerneT1/0/1'
        want = 'GigabitEthernet1/0/1'
        have = normalize_interface_name(interface_name=name)
        print(f"{want=}, {have=}")
        self.assertEqual(want, have)


class TestRequiredTogether(TestValidatorBase):

    def test_raises(self):
        test_cases = [
            {
                "test_name": "Test-01",
                "data": {
                    "values": {
                        "one": 1
                    },
                    "required": [
                        "one",
                        "two"
                    ]
                }
            }
        ]
        for test_case in test_cases:
            with self.subTest(test_case["test_name"]):
                with self.assertRaises(AssertionError):
                    test_result = required_together(**test_case["data"])


class TestSortInterfaceDict(TestValidatorBase):

    def test_01(self):
        data = {
            "Loopback2": {
                "name": "Loopback2"
            },
            "Lo1": {
                "name": "Lo1"
            }
        }
        model_data = {k: InterfaceModel.parse_obj(v) for k, v in data.items()}
        #print(model_data)
        sorted_data = sort_interface_dict(interfaces=model_data)
        with self.subTest(msg="Test Keys are sorted"):
            self.assertListEqual(list(sorted_data.keys()), ["Loopback1", "Loopback2"])
        with self.subTest(msg="Test Values are sorted"):
            self.assertListEqual(list(sorted_data.values()), [InterfaceModel(name="Loopback1"), InterfaceModel(name="Loopback2")])
        with self.subTest(msg="Test Repeated sort"):
            self.assertEqual(sorted_data, sort_interface_dict(interfaces=sorted_data))



del TestValidatorBase

if __name__ == '__main__':
    unittest.main()