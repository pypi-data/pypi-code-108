import unittest
from net_models.models import BaseNetModel
from net_models.fields.InterfaceNames import *

class ModelWithInterface(BaseNetModel):

    interface: InterfaceName


class TestBaseInterfaceName(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.test_interfaces = {
            "GigabitEthernet1/0/1": IosInterfaceName,
            "Vlan10": IosInterfaceName,
            "Loopback0": IosInterfaceName,
            "MPLS-SR-Tunnel1": IosInterfaceName,
            "xe-1/0/1": JuniperInterfaceName,
            'br0': GenericInterfaceName
        }


    def test_direct_new(self):
        for interface_name, wanted_type in self.test_interfaces.items():
            with self.subTest(msg=interface_name):
                model = wanted_type(interface_name)
                self.assertEqual(model, interface_name)
                self.assertIsInstance(model, wanted_type)

    def test_direct_validate(self):
        for interface_name, wanted_type in self.test_interfaces.items():
            with self.subTest(msg=interface_name):
                model = wanted_type.validate(interface_name)
                self.assertEqual(model, interface_name)
                self.assertIsInstance(model, wanted_type)

    def test_baseclass_new(self):
        for interface_name, wanted_type in self.test_interfaces.items():
            with self.subTest(msg=interface_name):
                model = InterfaceName(interface_name)
                self.assertEqual(model, interface_name)
                self.assertIsInstance(model, wanted_type)

    def test_pydantic_validate(self):
        for interface_name, wanted_type in self.test_interfaces.items():
            with self.subTest(msg=interface_name):
                model = ModelWithInterface.parse_obj({'interface': interface_name})
                self.assertEqual(model.interface, interface_name)
                self.assertIsInstance(model.interface, wanted_type)

    def test_pydantic_dumps(self):
        for interface_name, wanted_type in self.test_interfaces.items():
            with self.subTest(msg=interface_name):
                model = ModelWithInterface.parse_obj({'interface': interface_name})
                yaml_dump = model.yaml()
                print(yaml_dump)
                json_dump = model.json()
                print(json_dump)

    def test_long(self):
        for interface_name, wanted_type in self.test_interfaces.items():
            with self.subTest(msg=interface_name):
                model = InterfaceName(interface_name).long
                self.assertEqual(model.long, interface_name)

    # TODO: Make it a proper test
    def test_short(self):
        for interface_name, wanted_type in self.test_interfaces.items():
            with self.subTest(msg=interface_name):
                model = InterfaceName(interface_name).long
                print(model.short)


if __name__ == '__main__':
    unittest.main()