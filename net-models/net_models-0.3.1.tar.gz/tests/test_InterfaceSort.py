import unittest
from net_models.config import CONFIG, update_loggers
from net_models.utils import *
from net_models.fields.InterfaceNames import InterfaceName

import random

class TestInterfaceSort(unittest.TestCase):

    def test_split_interface_01(self):

        test_data = {
            "Loopback0": ["Loopback", "0"],
            "Port-channel1": ["Port-channel", "1"],
            "GigabitEthernet1/0/1": ["GigabitEthernet", "1/0/1"],
            "Serial0/0/1:2.3": ["Serial", "0/0/1:2.3"],
            "ThisIsNotAnInteface": (None, None),
            None: (None, None)
        }

        for interface, want in test_data.items():
            with self.subTest(msg=interface):
                have = split_interface(interface_name=interface)
                self.assertEqual(want, have)

    def test_extract_numbers_01(self):

        test_data = {
            "0": ([0, 0, 0, 0, 0, 0], 1),
            "1": ([0, 0, 0, 1, 0, 0], 1),
            "1/0/1": ([0, 1, 0, 1, 0, 0], 3),
            "0/0/1:2.3": ([0, 0, 0, 1, 2, 3], 3),
            "NoNumbersHere": None
        }
        for text, want in test_data.items():
            with self.subTest(msg=text):
                have = extract_numbers(text=text)
                self.assertEqual(want, have)

    def test_extract_numbers_too_long(self):

        with self.assertRaisesRegex(ValueError, expected_regex="Cannot unpack 6 slots with max_length == 6"):
            extract_numbers(text="1/2/3/4/5/6")

    def test_get_weight_by_type(self):

        test_data = {
            "Loopback": 100,
            "Vlan": 95,
            "FastEthernet": 50
        }
        for interface_type, want in test_data.items():
            with self.subTest(msg=interface_type):
                have = get_weight_by_type(interface_type=interface_type)
                self.assertEqual(want, have)

    def test_get_interface_index_01(self):

        test_data = {
            "Loopback1": 196565071197889821569586835750912,
            "TenGigabitEthernet1/9/1/1.100": 260185286905935925249970165252196,
            "TenGigabitEthernet1/9/1/1.101": 260185286905935925249970165252197

        }
        for text, want in test_data.items():
            with self.subTest(msg=text):
                have = get_interface_index(interface_name=text)
                self.assertEqual(want, have)

    def test_interface_sort(self):
        CONFIG.INTERFACE_UTILS_LOG_LEVEL = 5
        update_loggers()
        interfaces = ["Loopback0", "Loopback1", "Vlan100", "Vlan1000", "BDI11", "Tunnel1", "Tunnel1000", "pseudowire1", "pseudowire2",
                      "pseudowire3", "pseudowire4", "pseudowire5", "pseudowire6", "pseudowire7", "pseudowire8",
                      "pseudowire9", "pseudowire10", "pseudowire11", "pseudowire12", "pseudowire13", "pseudowire15",
                      "pseudowire16", "pseudowire17", "pseudowire18", "pseudowire19", "pseudowire20", "pseudowire21",
                      "pseudowire22", "pseudowire23", "pseudowire24", "pseudowire25", "pseudowire26", "pseudowire27",
                      "pseudowire28", "pseudowire29", "pseudowire30", "pseudowire31", "pseudowire32", "pseudowire33",
                      "pseudowire34", "pseudowire35", "pseudowire36", "pseudowire37", "pseudowire38", "pseudowire39",
                      "pseudowire40", "pseudowire41", "pseudowire42", "pseudowire43", "pseudowire44", "pseudowire45",
                      "pseudowire46", "pseudowire47", "pseudowire48", "pseudowire49", "pseudowire50", "pseudowire51",
                      "pseudowire52", "pseudowire53", "pseudowire54", "pseudowire55", "pseudowire56", "pseudowire57",
                      "pseudowire58", "pseudowire59", "pseudowire60", "pseudowire61", "pseudowire62", "pseudowire63",
                      "pseudowire64", "pseudowire65", "pseudowire66", "pseudowire67", "pseudowire68", "pseudowire69",
                      "pseudowire70", "pseudowire71", "pseudowire72", "pseudowire73", "pseudowire74", "pseudowire75",
                      "pseudowire83", "pseudowire84", "pseudowire85", "pseudowire86", "pseudowire87", "pseudowire88",
                      "pseudowire89", "pseudowire90", "pseudowire91", "pseudowire92", "pseudowire93", "pseudowire94",
                      "pseudowire95", "pseudowire96", "pseudowire97", "pseudowire98", "pseudowire99", "pseudowire100",
                      "pseudowire101", "pseudowire102", "pseudowire103", "pseudowire104", "pseudowire105",
                      "pseudowire106", "pseudowire107", "pseudowire108", "pseudowire109", "pseudowire110",
                      "pseudowire111", "pseudowire112", "pseudowire30000", "GigabitEthernet0", "GigabitEthernet0/0/0",
                      "GigabitEthernet0/0/1", "GigabitEthernet0/0/2", "GigabitEthernet0/0/3", "GigabitEthernet0/0/4",
                      "GigabitEthernet0/0/5", "GigabitEthernet0/0/6", "GigabitEthernet0/0/7", "TenGigabitEthernet0/0/8",
                      "GigabitEthernet0/1/0", "GigabitEthernet0/1/1", "GigabitEthernet0/1/2", "GigabitEthernet0/1/3",
                      "GigabitEthernet0/1/4", "GigabitEthernet0/1/5", "GigabitEthernet0/1/6", "GigabitEthernet0/1/7",
                      "TenGigabitEthernet0/1/8", "CEM0/5/0", "CEM0/5/1"]
        scrambled_interfaces = list(interfaces)
        random.shuffle(scrambled_interfaces)
        sorted_interfaces = sorted(scrambled_interfaces, key=lambda x: get_interface_index(x))
        self.assertListEqual(sorted_interfaces, interfaces)

    def test_interface_sort_models(self):
        CONFIG.INTERFACE_UTILS_LOG_LEVEL = 5
        update_loggers()
        interfaces = [InterfaceName(x) for x in ["Loopback0", "Loopback1", "Vlan100", "Vlan1000", "BDI11", "Tunnel1", "Tunnel1000", "pseudowire1", "pseudowire2",
                      "pseudowire3", "pseudowire4", "pseudowire5", "pseudowire6", "pseudowire7", "pseudowire8",
                      "pseudowire9", "pseudowire10", "pseudowire11", "pseudowire12", "pseudowire13", "pseudowire15",
                      "pseudowire16", "pseudowire17", "pseudowire18", "pseudowire19", "pseudowire20", "pseudowire21",
                      "pseudowire22", "pseudowire23", "pseudowire24", "pseudowire25", "pseudowire26", "pseudowire27",
                      "pseudowire28", "pseudowire29", "pseudowire30", "pseudowire31", "pseudowire32", "pseudowire33",
                      "pseudowire34", "pseudowire35", "pseudowire36", "pseudowire37", "pseudowire38", "pseudowire39",
                      "pseudowire40", "pseudowire41", "pseudowire42", "pseudowire43", "pseudowire44", "pseudowire45",
                      "pseudowire46", "pseudowire47", "pseudowire48", "pseudowire49", "pseudowire50", "pseudowire51",
                      "pseudowire52", "pseudowire53", "pseudowire54", "pseudowire55", "pseudowire56", "pseudowire57",
                      "pseudowire58", "pseudowire59", "pseudowire60", "pseudowire61", "pseudowire62", "pseudowire63",
                      "pseudowire64", "pseudowire65", "pseudowire66", "pseudowire67", "pseudowire68", "pseudowire69",
                      "pseudowire70", "pseudowire71", "pseudowire72", "pseudowire73", "pseudowire74", "pseudowire75",
                      "pseudowire83", "pseudowire84", "pseudowire85", "pseudowire86", "pseudowire87", "pseudowire88",
                      "pseudowire89", "pseudowire90", "pseudowire91", "pseudowire92", "pseudowire93", "pseudowire94",
                      "pseudowire95", "pseudowire96", "pseudowire97", "pseudowire98", "pseudowire99", "pseudowire100",
                      "pseudowire101", "pseudowire102", "pseudowire103", "pseudowire104", "pseudowire105",
                      "pseudowire106", "pseudowire107", "pseudowire108", "pseudowire109", "pseudowire110",
                      "pseudowire111", "pseudowire112", "pseudowire30000", "GigabitEthernet0", "GigabitEthernet0/0/0",
                      "GigabitEthernet0/0/1", "GigabitEthernet0/0/2", "GigabitEthernet0/0/3", "GigabitEthernet0/0/4",
                      "GigabitEthernet0/0/5", "GigabitEthernet0/0/6", "GigabitEthernet0/0/7", "TenGigabitEthernet0/0/8",
                      "GigabitEthernet0/1/0", "GigabitEthernet0/1/1", "GigabitEthernet0/1/2", "GigabitEthernet0/1/3",
                      "GigabitEthernet0/1/4", "GigabitEthernet0/1/5", "GigabitEthernet0/1/6", "GigabitEthernet0/1/7",
                      "TenGigabitEthernet0/1/8", "CEM0/5/0", "CEM0/5/1"]]
        scrambled_interfaces = list(interfaces)
        random.shuffle(scrambled_interfaces)
        sorted_interfaces = sorted(scrambled_interfaces, key=lambda x: x.get_index())
        self.assertListEqual(sorted_interfaces, interfaces)


if __name__ == '__main__':
    unittest.main()
