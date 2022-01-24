import unittest
import pathlib
import shutil
from net_models.models.interfaces import *


from net_models.inventory import Host, Group, Inventory
from net_models.loaders import BaseLoader, ExcelLoader, DirectoryLoader, AnsibleInventoryDumper, NornirInventoryDumper

VERBOSITY = 4

class TestBaseLoader(unittest.TestCase):

    TEST_CLASS = BaseLoader

    def test_init(self):

        loader = self.TEST_CLASS(verbosity=VERBOSITY)
        loader.get_host(host_name="TestHost-A")
        for i in range(1, 49):
            interface = loader.get_interface(host_name="TestHost-A", interface_name=f"Te1/0/{i}")
            interface.lag_member = InterfaceLagMemberConfig(group=10, protocol='lacp', mode='active')
        loader.get_interface(host_name="TestHost-A", interface_name="vlan1")

        loader.finish()


    def test_recursive_find_group(self):
        group_dict = {
            "Level-1": Group(
                name="Level-1",
                children={
                    "Level-2A": Group(
                        name="Level-2A",
                        children={
                            "Level-3A": Group(
                                name="Level-3A"
                            )
                        }
                    ),
                    "Level-2B": Group(
                        name="Level-2B"
                    )
                }
            )
        }
        loader = BaseLoader()
        with self.subTest(msg="Get existing group"):
            have = loader.recursive_find_group(group_name="Level-3A", group_dict=group_dict)
            want = Group(name="Level-3A")
            self.assertEqual(want, have)

        with self.subTest(msg="Get non-existent group"):
            have = loader.recursive_find_group(group_name="NonExistentGroup", group_dict=group_dict)
            self.assertTrue(have is None)

    def test_get_group(self):
        inventory = Inventory(
            hosts={},
            groups={
                "Level-1": Group(
                    name="Level-1",
                    children={
                        "Level-2A": Group(
                            name="Level-2A",
                            children={
                                "Level-3A": Group(
                                    name="Level-3A"
                                )
                            }
                        ),
                        "Level-2B": Group(
                            name="Level-2B"
                        )
                    }
                )
            }
        )
        loader = BaseLoader(
            inventory=inventory
        )
        with self.subTest(msg="Get existing group without parent_name"):
            want = Group(name="Level-3A")
            have = loader.get_group(group_name="Level-3A")
            self.assertEqual(want, have)

        with self.subTest(msg="Get existing group with parent_name"):
            want = Group(name="Level-3A")
            have = loader.get_group(group_name="Level-3A", parent_name="Level-2A")
            self.assertEqual(want, have)

        with self.subTest(msg="Get non-existing group with parent_name, without creation"):
            have = loader.get_group(group_name="Level-3B", parent_name="Level-2A", create_if_missing=False)
            self.assertTrue(have is None)

        with self.subTest(msg="Get non-existing group with parent_name, with creation"):
            have = loader.get_group(group_name="Level-3B", parent_name="Level-2A")
            # print(loader.inventory.yaml(exclude_none=True))
            want = Group(name="Level-3B")
            # print(want, have)
            self.assertEqual(want, have)


class TestExcelLoader(unittest.TestCase):

    RESOURCE_PATH = pathlib.Path(__file__).resolve().parent.joinpath("resources")

    def test_01(self):
        path = self.RESOURCE_PATH.joinpath("ExcelLoaderResource-01.xlsx")
        el = ExcelLoader(input_file=path)
        # el.load_vlan_definitions()
        el.load_physical_links()
        el.load_ospf_templates()
        el.load_l3_links()
        el.load_l3_ports()
        el.load_bgp_routers()
        el.load_bgp_neighbors()

        el.finish()



class TestDirectoryLoader(unittest.TestCase):

    RESOURCE_PATH = pathlib.Path(__file__).resolve().parent.joinpath("resources").joinpath("inventory")

    def test_load_sample_01(self):

        inventory_path = self.RESOURCE_PATH.joinpath("sample-inventory-01")
        loader = DirectoryLoader(inventory_path=inventory_path, verbosity=VERBOSITY)
        loader.load()
        loader.finish()


class TestAnsibleInventoryDumper(unittest.TestCase):

    RESOURCE_PATH = pathlib.Path(__file__).resolve().parent.joinpath("resources").joinpath("inventory")

    def test_01_dump_sample_01(self):

        inventory_path = self.RESOURCE_PATH.joinpath("sample-inventory-01")
        test_inventory_path = inventory_path.parent.joinpath("test")
        loader = DirectoryLoader(inventory_path=inventory_path, verbosity=VERBOSITY)
        loader.load()
        inventory = loader.inventory.clone()
        dumper = AnsibleInventoryDumper(inventory=inventory, directory=inventory_path)
        dumper.remove_all_backups()
        dumper.dump_inventory(path=test_inventory_path, separate_host_sections=True)
        # Cleanup
        # shutil.rmtree(test_inventory_path)

    def test_02_circle_sample_01(self):
        """
        Load sample inventory, dump it to different folder and load it again. Then compare them.
        """
        inventory_path = self.RESOURCE_PATH.joinpath("sample-inventory-01")
        test_inventory_path = inventory_path.parent.joinpath("test")
        # Load the initial inventory
        loader1 = DirectoryLoader(inventory_path=inventory_path, verbosity=VERBOSITY)
        loader1.load()
        inventory1 = loader1.inventory.clone()
        # Dump the loaded inventory
        dumper = AnsibleInventoryDumper(inventory=inventory1, directory=inventory_path)
        dumper.backup_inventory()
        dumper.dump_inventory(path=test_inventory_path, separate_host_sections=True)
        loader2 = DirectoryLoader(inventory_path=test_inventory_path, verbosity=VERBOSITY)
        loader2.load()
        inventory2 = loader2.inventory.clone()

        # Cleanup
        shutil.rmtree(test_inventory_path)
        dumper.remove_all_backups()

        self.assertEqual(inventory1.yaml(exclude_none=True), inventory2.yaml(exclude_none=True))

class TestNornirInventoryDumper(unittest.TestCase):

    RESOURCE_PATH = pathlib.Path(__file__).resolve().parent.joinpath("resources").joinpath("inventory")

    def test_dump_sample_01(self):

        inventory_path = self.RESOURCE_PATH.joinpath("sample-inventory-01")
        test_inventory_path = inventory_path.parent.joinpath("test-nr")
        loader = DirectoryLoader(inventory_path=inventory_path, verbosity=VERBOSITY)
        loader.load()
        inventory = loader.inventory.clone()

        dumper = NornirInventoryDumper(inventory=inventory, directory=inventory_path)
        dumper.remove_all_backups()
        dumper.dump_inventory(path=test_inventory_path)
        # Cleanup
        shutil.rmtree(test_inventory_path)


if __name__ == '__main__':
    unittest.main()