import unittest2 as unittest
import os

from yangsuite.paths import set_base_path, get_path
from ysyangtree import TaskHandler


def gen_gnmi_task(*args):
    print('Make flake8 happy')


class TestGnmiTestManager(unittest.TestCase):
    """Test cases for YSGnmiTestManager class."""

    basedir = os.path.join(os.path.dirname(__file__), 'data')

    @classmethod
    def setUpClass(cls):
        """Test setup method called before each test case."""
        set_base_path(cls.basedir)
        cls.replay_dir = get_path('replays_dir', user='test')
        cls.variables = {'interface_name_1': 'TenGigabitEthernet1/0/37',
                         'interface': 'TenGigabitEthernet1/0/37'}
        cls.maxDiff = None

    @unittest.skip('Not supported.')
    def test_gen_gnmi_task_xe(self):
        """Generate a GNMI message based on an IOS-XE replay."""
        replay = TaskHandler.get_replay(self.replay_dir,
                                        'testcategory',
                                        'Native interface var',
                                        self.variables)

        gnmi_message_list = gen_gnmi_task({'task': replay})
        op, gnmi_message = gnmi_message_list[0]
        self.assertEqual(op, 'set_request')
        self.assertIn('Cisco-IOS-XE-native', gnmi_message)
        self.assertIn('entries', gnmi_message['Cisco-IOS-XE-native'])
        self.assertIn('namespace_modules', gnmi_message['Cisco-IOS-XE-native'])
        entries = gnmi_message['Cisco-IOS-XE-native']['entries']
        self.assertEqual(entries[0]['value'], 'my test variable')
        modules = gnmi_message['Cisco-IOS-XE-native']['namespace_modules']
        self.assertEqual(modules, {'ios': 'Cisco-IOS-XE-native'})

    @unittest.skip('Not supported.')
    def test_gen_gnmi_task_xr(self):
        """Generate a GNMI message based on an IOS-XR replay."""
        replay = TaskHandler.get_replay(
            self.replay_dir,
            'testcategory',
            '00002 - .../ipv4/addresses/address/address - basic merge',
            self.variables)
        gnmi_message_list = gen_gnmi_task({'task': replay})
        op, gnmi_message = gnmi_message_list[0]
        self.assertEqual(op, 'set_request')
        self.assertIn('Cisco-IOS-XR-um-interface-cfg', gnmi_message)
        self.assertIn('entries', gnmi_message['Cisco-IOS-XR-um-interface-cfg'])
        self.assertIn('namespace_modules',
                      gnmi_message['Cisco-IOS-XR-um-interface-cfg'])
        entries = gnmi_message['Cisco-IOS-XR-um-interface-cfg']['entries']
        self.assertEqual(entries[0]['value'], '10.1.1.1')
        self.assertEqual(entries[1]['value'], '255.0.0.0')
        modules = gnmi_message[
            'Cisco-IOS-XR-um-interface-cfg'
            ]['namespace_modules']
        self.assertEqual(
            modules,
            {'um-if-ip-address-cfg': 'Cisco-IOS-XR-um-if-ip-address-cfg',
             'um-interface-cfg': 'Cisco-IOS-XR-um-interface-cfg'}
        )

    @unittest.skip('Not supported.')
    def test_gen_gnmi_task_openconfig(self):
        """Generate a GNMI message based on an OpenConfig replay."""
        replay = TaskHandler.get_replay(
            self.replay_dir,
            'testcategory',
            '00001 - /interfaces/interface/config/type - basic merge',
            self.variables
        )
        gnmi_message_list = gen_gnmi_task({'task': replay,
                                           'origin': 'openconfig'})
        op, gnmi_message = gnmi_message_list[0]
        self.assertEqual(op, 'set_request')
        self.assertIn('openconfig-interfaces', gnmi_message)
        self.assertIn('entries', gnmi_message['openconfig-interfaces'])
        self.assertIn('namespace_modules',
                      gnmi_message['openconfig-interfaces'])
        entries = gnmi_message['openconfig-interfaces']['entries']
        self.assertEqual(entries[0]['value'], 'TenGigabitEthernet1/0/37')
        self.assertEqual(entries[1]['value'], 'TenGigabitEthernet1/0/37')
        self.assertEqual(entries[2]['value'], 'iana-if-type:ethernetCsmacd')
        modules = gnmi_message['openconfig-interfaces']['namespace_modules']
        self.assertEqual(
            modules,
            {'ianaift': 'iana-if-type',
             'if': 'ietf-interfaces',
             'ift': 'iana-if-type',
             'oc-if': 'openconfig-interfaces'}
        )

    @unittest.skip('Not supported.')
    def test_construct_replay(self):
        """Construct replay method."""
        replay = TaskHandler.get_replay(
            self.replay_dir,
            'testcategory',
            '00001 - /interfaces/interface/config/type - basic merge',
            self.variables
        )
        print(replay)
        # TODO: find appropriate check
