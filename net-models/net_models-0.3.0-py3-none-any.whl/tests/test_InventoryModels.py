import unittest

from net_models.exceptions import *
from net_models.inventory import *

from tests import TestBaseNetModel


class TestGroupConfig(TestBaseNetModel):

    def test_vlan_definitions(self):
        config = GroupConfig(
            vlan_definitions=[
                VLANHostMapping(
                    vlan_id=10,
                    name="TestVlan-10",
                    hosts=[
                        VlanHost(
                            name="SW-01"
                        )
                    ]
                )
            ]
        )
        self.assertIsInstance(config, GroupConfig)

class TestGroup(TestBaseNetModel):

    def test_get_all_groups(self):
        group = Group(
            name="A",
            children={
                "B": Group(
                    name="B",
                    children={
                        "C": Group(name="C"),
                        "D": Group(name="D")
                    }
                )
            }
        )
        group_dict = group.get_flat_children()
        self.assertEqual(group_dict, {"B": Group(name="B"), "C": Group(name="C"), "D": Group(name="D")})


class TestHostConfig(TestBaseNetModel):


    def test_get_interface_01(self):
        existing_interface = InterfaceModel(
            name="Loopback0",
            description="Test"
        )
        model = HostConfig(
            interfaces={
                existing_interface.name: existing_interface
            }
        )
        with self.subTest(msg="Get existing interface"):
            candidate = model._get_interface(existing_interface.name)
            self.assertEqual(existing_interface, candidate)

        with self.subTest(msg="Get non-existing interface"):
            candidate = model._get_interface("Loopback1000")
            self.assertTrue(candidate is None)

    def test_create_interface_01(self):
        # Create Empty Model
        model = HostConfig()

        with self.subTest(msg="Create interface on empty model"):
            interface = InterfaceModel(name="Loopback0")
            model._create_interface(interface=interface)
            self.assertEqual(model.interfaces[interface.name], interface)

        with self.subTest(msg="Try creating existing interface again - without force"):
            interface = InterfaceModel(name="Loopback0")
            with self.assertRaises(expected_exception=InterfaceAlreadyExists):
                model._create_interface(interface=interface)


        with self.subTest(msg="Try creating existing interface again - with force"):
            interface = InterfaceModel(name="Loopback0", description="New Interface")
            model._create_interface(interface=interface, force_create=True)
            self.assertEqual(model.interfaces[interface.name], interface)

    def test_get_or_create_interface_01(self):
        # Create Empty Model
        model = HostConfig()

        with self.subTest(msg="Create interface on empty model"):
            interface = InterfaceModel(name="Loopback0")
            model._get_or_create_interface(interface=interface)
            self.assertEqual(model.interfaces[interface.name], interface)

class TestHost(TestBaseNetModel):

    def test_get_or_create_interface_01(self):

        model = Host(name="Test-Host")

        with self.subTest(msg="Test invalid parameters - parameters"):
            with self.assertRaises(expected_exception=ValueError):
                model.get_or_create_interface()

        with self.subTest(msg="Test invalid parameters - missing name"):
            with self.assertRaises(expected_exception=ValueError):
                model.get_or_create_interface(interface={"description": "Test Description"})

        with self.subTest(msg="Test creating interface - 01 - Dict"):
            interface = {
                "name": "Loopback0",
                "l3_port": {
                    "ipv4": {
                        "addresses": [
                            {"address": "192.168.0.2"}
                        ]
                    }
                }
            }
            model.get_or_create_interface(
                interface=interface
            )
            interface = InterfaceModel.parse_obj(interface)
            self.assertEqual(model.config.interfaces[interface.name], interface)

        with self.subTest(msg="Test getting interface - 01 - Dict"):
            interface = {
                "name": "Loopback0",
                "l3_port": {
                    "ipv4": {
                        "addresses": [
                            {"address": "192.168.0.2"}
                        ]
                    }
                }
            }
            model.get_or_create_interface(
                interface=interface
            )
            interface = InterfaceModel.parse_obj(interface)
            self.assertEqual(model.config.interfaces[interface.name], interface)


class TestInventory(TestBaseNetModel):

    def test_get_group_01(self):

        model = Inventory(
            groups={
                "A": Group(name="A"),
                "B": Group(
                    name="B",
                    children={
                        "C": Group(
                            name="C",
                            children={
                                "D": Group(name="D")
                            }
                        )
                    }
                ),
            },
            hosts={}
        )

        with self.subTest(msg="Get Existing Group"):
            self.assertEqual(
                model.get_group(group_name="C", create_if_missing=False),
                Group(
                    name="C",
                    children={
                        "D": Group(name="D")
                    }
                )
            )

        with self.subTest(msg="Get Existing Group with Existing Parent"):
            self.assertEqual(
                model.get_group(group_name="C", parent_name="B", create_if_missing=False),
                Group(
                    name="C",
                    children={
                        "D": Group(name="D")
                    }
                )
            )

        with self.subTest(msg="Get Non-existing Group"):
            self.assertTrue(model.get_group(group_name="E", create_if_missing=False) is None)

        with self.subTest(msg="Get Group from Non-existing Parent"):
            with self.assertRaises(AssertionError):
                model.get_group(group_name="C", parent_name="E", create_if_missing=False)

        with self.subTest(msg="Create New Top-level Group"):
            self.assertEqual(model.get_group(group_name="E"), Group(name="E"))

        with self.subTest(msg="Create New Group Under Parent"):
            self.assertEqual(model.get_group(group_name="F", parent_name="E"), Group(name="F"))

    def test_get_host_01(self):

        model = Inventory(
            groups={
                "A": Group(name="A"),
                "B": Group(
                    name="B",
                    children={
                        "C": Group(
                            name="C",
                            children={
                                "D": Group(name="D")
                            },
                            hosts={
                                "Host-01": None
                            }
                        )
                    }
                ),
            },
            hosts={
                "Host-01": Host(name="Host-01")
            }
        )

        with self.subTest(msg="Get Existing Host"):
            self.assertEqual(
                model.get_host(host_name="Host-01", create_if_missing=False),
                Host(name="Host-01")
            )

        with self.subTest(msg="Get Non-existing Host"):
            self.assertTrue(
                model.get_host(host_name="Host-02", create_if_missing=False) is None
            )

        with self.subTest(msg="Create New Host"):
            self.assertEqual(
                model.get_host(host_name="Host-02", create_if_missing=True),
                Host(name="Host-02")
            )

        with self.subTest(msg="Get Newly Created Host"):
            self.assertEqual(
                model.get_host(host_name="Host-02", create_if_missing=False),
                Host(name="Host-02")
            )

    def test_assign_host_to_group(self):

        model = Inventory(
            groups={
                "A": Group(name="A"),
            },
            hosts={
                "Host-01": Host(name="Host-01")
            }
        )

        with self.subTest(msg="Assign Existing Host to Existing Group"):
            self.assertTrue(model.assign_host_to_group(host_name="Host-01", group_name="A"))

        with self.subTest(msg="Assign Existing Host to Existing Group - Again"):
            self.assertTrue(model.assign_host_to_group(host_name="Host-01", group_name="A"))

        with self.subTest(msg="Assign Existing Host to Non-existing Group"):
            with self.assertRaises(expected_exception=GroupNotFound):
                model.assign_host_to_group(host_name="Host-01", group_name="B"),

        with self.subTest(msg="Assign Non-existing Host to Existing Group"):
            with self.assertRaises(expected_exception=HostNotFound):
                model.assign_host_to_group(host_name="Host-02", group_name="A")


if __name__ == '__main__':
    unittest.main()