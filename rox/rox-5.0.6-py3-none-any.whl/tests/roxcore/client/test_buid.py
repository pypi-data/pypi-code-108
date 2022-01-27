import json
import unittest
from collections import OrderedDict

from rox.core.client.buid import BUID
from rox.core.custom_properties.custom_property import CustomProperty
from rox.core.custom_properties.custom_property_type import CustomPropertyType
from rox.core.entities.flag import Flag

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


class BUIDTests(unittest.TestCase):
    def test_will_generate_correct_md5_value(self):
        flag = Flag()
        flag.set_name('flag1')

        flag_repo = Mock()
        flag_repo.get_all_flags.return_value = OrderedDict({'flag1': flag})

        cp = CustomProperty('prop1', CustomPropertyType.STRING, '123')

        cp_repo = Mock()
        cp_repo.get_all_custom_properties.return_value = OrderedDict({'prop1': cp})

        sdk_settings = Mock()

        device_props = Mock()
        device_props.get_all_properties.return_value = {
            'app_key': '123',
            'api_version': '4.0.0',
            'platform': 'plat',
            'lib_version': '1.5.0'
        }

        buid = BUID(sdk_settings, device_props)

        device_props = Mock()
        device_props.get_all_properties.return_value = {
            'app_key': '123',
            'api_version': '4.0.0',
            'platform': 'plat2',
            'lib_version': '1.5.0'
        }

        buid2 = BUID(sdk_settings, device_props)

        device_props = Mock()
        device_props.get_all_properties.return_value = {
            'app_key': '123',
            'api_version': '4.0.0',
            'platform': 'plat2',
            'lib_version': '1.5.0',
            'nonrelevantprop': 'not effecting'
        }

        buid3 = BUID(sdk_settings, device_props)

        self.assertEqual('234A32BB4341EAFD91FC8D0395F4E66F', buid.get_value())
        self.assertNotEqual(buid.get_value(), buid2.get_value())
        self.assertEqual(buid2.get_value(), buid3.get_value())
    