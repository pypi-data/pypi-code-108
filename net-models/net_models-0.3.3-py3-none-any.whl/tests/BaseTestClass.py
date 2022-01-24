import sys
import pathlib
import unittest
import yaml
from net_models.models.BaseModels import BaseNetModel, VendorIndependentBaseModel
from net_models.utils import get_logger

class TestBaseNetModel(unittest.TestCase):

    LOGGER = get_logger(name="NetCm-Tests", verbosity=5)
    TEST_CLASS = BaseNetModel

    def test_subclasses_basemodel(self):
        self.assertTrue(issubclass(self.TEST_CLASS, BaseNetModel))

    def test_has_dict_method(self):
        self.assertTrue(hasattr(self.TEST_CLASS, "__dict__"))

    def test_has_validators(self):
        self.assertTrue(hasattr(self.TEST_CLASS, "__validators__"))

    def load_yaml(self, path: pathlib.Path):
        return yaml.safe_load(path.read_text())


class TestVendorIndependentBase(TestBaseNetModel):

    TEST_CLASS = VendorIndependentBaseModel
    RESOURCE_DIR = pathlib.Path(__file__).resolve().parent.joinpath("resources")

    def test_has_resource_dir(self):
        # print(f"RESOURCE_DIR for {model.__class__.__name__}: {model.RESOURCE_DIR}")
        self.assertIsInstance(self.RESOURCE_DIR, pathlib.Path)

    def get_resource_yaml(self):
        resource_files = [x for x in self.RESOURCE_DIR.joinpath("data").iterdir() if x.is_file and x.suffix in [".yml"] and x.stem.startswith(self.__class__.__name__)]
        return resource_files

    def test_load_yaml(self):
        resource_files = self.get_resource_yaml()
        for resource_file in resource_files:
            with self.subTest(msg=resource_file.stem):
                test_data = self.load_yaml(path=resource_file)
                test_obj = self.TEST_CLASS.parse_obj(test_data)
                self.assertIsInstance(test_obj, BaseNetModel)


if __name__ == '__main__':
    unittest.main()