import os
import sys
import importlib
import unittest
from unittest import mock
from genie.conf.base.device import Device
from genie.conf.base.api import ExtendApis, _load_function_json
from genie.tests.conf.base.mock_errored_api_data import data_loader
from genie.json.exceptions import ApiImportError


class TestApi(unittest.TestCase):

    def setUp(self):
        self.device = Device(name='aDevice', os='iosxe',
                             custom={'abstraction': {'order':['os']}})

    def test_api_success(self):
        api = self.device.api.get_api('shut_interface', self.device)
        self.assertEqual(callable(api), True)
        self.assertEqual(api.__name__, 'shut_interface')

    def test_api_exception(self):
        with self.assertRaises(AttributeError):
            self.device.api.get_api('DontExists', self.device)

    @mock.patch('genie.tests.conf.base.test_api._load_function_json', return_value=data_loader())
    def test_api_recall_error(self, mock_data):

        with self.assertRaises(NameError):
            importlib.reload(genie.libs.sdk.apis)
            self.device.api.get_api('clear_interface_counters', self.device)


class TestExtendApi(unittest.TestCase):

    def setUp(self):
        sys.path.append(os.path.dirname(__file__))

    def test_extend_api(self):
        ext = ExtendApis('dummy_api')
        ext.extend()
        summary = ext.output['extend_info']

        self.assertEqual(len(summary), 2)
        self.assertIn("api name: 'dummy_iosxe', tokens ['iosxe'], "
                      "module name: utils",
                      summary)
        self.assertIn("api name: 'dummy_common', tokens ['com'], "
                      "module name: utils",
                      summary)


class TestExtendApi_Error(unittest.TestCase):

    def setUp(self):
        sys.path.append(os.path.dirname(__file__))

    def test_extend_api_module_error(self):
        ext = ExtendApis('dummy_api_error')
        with self.assertRaises(ApiImportError):
            ext.extend()


if __name__ == '__main__':
    unittest.main()

