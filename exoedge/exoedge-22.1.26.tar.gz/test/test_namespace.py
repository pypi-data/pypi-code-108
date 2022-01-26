# pylint: disable=C0103,W0602,C0325,C0301,C0111
import os
import unittest
import json
import pureyaml
from exoedge import namespaces

test_dir = os.path.dirname(os.path.abspath(__file__))


class TestChannelNamespace(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass
    @classmethod
    def tearDownClass(cls):
        pass
    def setUp(self):
        print("setup for test: {}".format(self.id().split('.')[-1]))
    def tearDown(self):
        print("teardown for test: {}".format(self.id().split('.')[-1]))

    def test_001_constructor(self):
        d = {}
        n = namespaces.ChannelNamespace(**d)
        self.assertIsInstance(n, namespaces.ChannelNamespace)

    def test_002_simple_namespace(self):
        d = {'a': 'b'}
        n = namespaces.ChannelNamespace(**d)
        self.assertTrue(hasattr(n, 'a'))

    def test_003_ns_no_defaults(self):
        d = {'a': 'b', '__ns_no_defaults__': True}
        n = namespaces.ChannelNamespace(**d)
        self.assertTrue(hasattr(n, 'a'))
        self.assertFalse(hasattr(n, 'protocol_config'))
        self.assertFalse(hasattr(n, 'report_rate'))

    def test_004_print_json(self):
        chconf = json.loads(open(os.path.join(test_dir, 'assets/complete-channel-config.json')).read())
        n = namespaces.ChannelNamespace(**chconf)
        tojson = n.to_json(indent=2)
        print(tojson)
        self.assertIsInstance(json.loads(tojson), dict)

    def test_005_print_yaml(self):
        chconf = json.loads(open(os.path.join(test_dir, 'assets/complete-channel-config.json')).read())
        print(chconf)
        n = namespaces.ChannelNamespace(**chconf)
        toyaml = n.to_yaml()
        print(toyaml)
        print("type: {}".format(type(toyaml)))
        self.assertIsInstance(pureyaml.loads(toyaml), dict)

    def test_006_walk_namespace(self):
        chconf = json.loads(open(os.path.join(test_dir, 'assets/complete-channel-config.json')).read())
        n = namespaces.ChannelNamespace(**chconf)
        self.assertIsInstance(dict(n), dict)
        self.assertTrue(hasattr(n.protocol_config, 'report_rate'))

    def test_007_config_with_missing_display_name_elem_no_defaults(self):
        chconf = json.loads(open(os.path.join(test_dir, 'assets/missing-display-name.json')).read())
        chconf['__ns_no_defaults__'] = True
        n = namespaces.ChannelNamespace(**chconf)
        self.assertTrue(not hasattr(n, 'display_name'))

    def test_008_config_with_missing_display_name_elem_add_defaults(self):
        chconf = json.loads(open(os.path.join(test_dir, 'assets/missing-display-name.json')).read())
        n = namespaces.ChannelNamespace(**chconf)
        self.assertTrue(hasattr(n, 'display_name'))

    def test_009_config_with_missing_properties_data_type_elem_no_defaults(self):
        chconf = json.loads(open(os.path.join(test_dir, 'assets/missing-properties-data_type.json')).read())
        chconf['__ns_no_defaults__'] = True
        n = namespaces.ChannelNamespace(**chconf)
        self.assertTrue(hasattr(n, 'properties'))
        self.assertTrue(not hasattr(n.properties, 'data_type'))

    def test_010_config_with_missing_properties_data_type_elem_add_defaults(self):
        chconf = json.loads(open(os.path.join(test_dir, 'assets/missing-properties-data_type.json')).read())
        # chconf['__ns_no_defaults__'] = True
        n = namespaces.ChannelNamespace(**chconf)
        self.assertTrue(hasattr(n, 'properties'))
        self.assertTrue(hasattr(n.properties, 'data_type'))


def main():
    unittest.main()

if __name__ == "__main__":
    main()
