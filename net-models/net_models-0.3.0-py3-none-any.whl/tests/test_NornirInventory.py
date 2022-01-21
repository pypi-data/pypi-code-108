
from tests import TestBaseNetModel, BASE_RESOURCE_DIR

from net_models.inventory.InventoryModels import (
    Host, Group
)

from net_models.inventory.NornirInventoryModels import (
    NornirHostModel, NornirGroupModel, NornirHostsFile, NornirGroupsFile, NornirInventory, to_nornir_model
)

from net_models.loaders import DirectoryLoader

VERBOSITY = 5



class TestNornirHostModel(TestBaseNetModel):

    TEST_CLASS = NornirHostModel

class TestNornirGroupModel(TestBaseNetModel):

    TEST_CLASS = NornirGroupModel


class TestNornirInventory(TestBaseNetModel):

    TEST_CLASS = NornirInventory
    RESOURCE_PATH = BASE_RESOURCE_DIR.joinpath("inventory")

    def test_sample_inventory_01(self):
        inventory_path = self.RESOURCE_PATH.joinpath("sample-inventory-01")
        result_path = self.RESOURCE_PATH.joinpath('results/nornir_sample_inventory_01_output.yml')
        loader = DirectoryLoader(inventory_path=inventory_path, verbosity=VERBOSITY)
        loader.load()
        loader.finish()
        inventory = loader.inventory
        nr_inventory = to_nornir_model(inventory)
        have_yml = nr_inventory.yaml(exclude_none=True)
        have = nr_inventory.serial_dict(exclude_none=True)
        want = self.load_yaml(path=result_path)
        self.assertEqual(want, have)



if __name__ == '__main__':
    unittest.main()
