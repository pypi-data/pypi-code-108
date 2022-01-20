# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
"""Unit tests for the ysdevices.devprofile module."""

import os.path
import unittest2 as unittest
import shutil
import tempfile

from yangsuite.paths import get_path, set_base_path

from ..devprofile import YSDeviceProfile, YSDeviceProfileValidationError
from ..plugin import YSDeviceProtocolPlugin


class TestYSDeviceProfile(unittest.TestCase):
    """Test YSDeviceProfile functions."""

    base_dir = os.path.join(os.path.dirname(__file__), 'data')

    def setUp(self):
        """Pre-test setup function, called automatically."""
        set_base_path(self.base_dir)
        self.temp_path = tempfile.mkdtemp()

    def tearDown(self):
        """Post-test cleanup function, called automatically."""
        if os.path.exists(self.temp_path):
            shutil.rmtree(self.temp_path)

    def test_get_profile_basic(self):
        """Test loading of JSON data into a device profile."""
        profile = YSDeviceProfile.get("Basic Device")
        self.assertEqual("Basic Device", profile.base.profile_name)
        self.assertEqual("127.0.0.1", profile.base.address)
        self.assertEqual("admin", profile.base.username)
        self.assertEqual(30, profile.base.timeout)
        # Stored in encrypted form, decrypted in memory
        self.assertEqual("admin", profile.base.password)

    def test_get_profile_extra_data(self):
        """Test loading of JSON data including extra data we don't know."""
        # Note that due to slugify, the profile name is not case-sensitive
        profile = YSDeviceProfile.get("Device with netconf")
        self.assertEqual("Device with NETCONF", profile.base.profile_name)
        self.assertEqual(profile.extra_data, {'protocolX': {
            'enabled': True,
            'device_variant': 'default',
            'port': 830,
            'ignore_keys': False,
            'address': '',
            'username': '',
            'timeout': '',
            'encrypted_password': '',
        }})

        # Make sure the dict representation includes the extra data
        self.assertEqual(profile.dict()['protocolX'], {
            'enabled': True,
            'device_variant': 'default',
            'port': 830,
            'ignore_keys': False,
            'address': '',
            'username': '',
            'timeout': '',
            'encrypted_password': '',
        })

    def test_get_profile_legacy_2_1(self):
        """Test loading of legacy XML 'format 2.1' data."""
        profile = YSDeviceProfile.get("n9kv")
        self.assertEqual("n9kv", profile.base.profile_name)
        self.assertEqual("n9kv vagrant", profile.base.description)
        self.assertEqual("127.0.0.1", profile.base.address)
        self.assertEqual("vagrant", profile.base.username)
        # Not present in legacy XML, hence initialized to default
        self.assertEqual(30, profile.base.timeout)
        # Stored in encrypted form, decrypted in memory
        self.assertEqual("vagrant", profile.base.password)

    def test_get_profile_legacy_2_0(self):
        """Test loading of legacy XML 'format 2.0' data."""
        profile = YSDeviceProfile.get("iosxrv_vagrant")
        self.assertEqual("iosxrv_vagrant", profile.base.profile_name)
        self.assertEqual("IOS XRv (x86_64) Vagrant VM",
                         profile.base.description)
        self.assertEqual("127.0.0.1", profile.base.address)
        self.assertEqual("vagrant", profile.base.username)
        # Not present in legacy XML, hence initialized to default
        self.assertEqual(30, profile.base.timeout)
        # Stored in encrypted form, decrypted in memory
        self.assertEqual("vagrant", profile.base.password)

    def test_get_profile_negative(self):
        """Test failures when loading a profile."""
        self.assertRaises(OSError, YSDeviceProfile.get, "nonexistent")
        self.assertRaises(ValueError, YSDeviceProfile.get, "malformed")

    def test_list_profiles(self):
        """Test the YSDeviceProfile.list() method."""
        self.assertEqual(YSDeviceProfile.list(), [
            {'description': 'Basic device profile, with no extensions',
             'key': 'basic-device',
             'name': 'Basic Device'},
            {'description': 'Nexus 9k device with NETCONF support',
             'key': 'device-with-netconf',
             'name': 'Device with NETCONF'},
            {'description': 'Device with netmiko SSH',
             'key': 'netmiko',
             'name': 'Netmiko'},
            {'description': 'Basic device profile, with certificate',
             'key': 'certificate',
             'name': 'certificate'},
            {'description': 'Cisco IOS-XR ENxR simulator',
             'key': 'enxr',
             'name': 'enxr'},
            {'description': 'IOS XRv (x86_64) Vagrant VM',
             'key': 'iosxrv_vagrant',
             'name': 'iosxrv_vagrant'},
            {'description': '(an error occurred while reading this profile)',
             'key': 'malformed',
             'name': 'malformed'},
            {'description': 'n9kv vagrant', 'key': 'n9kv', 'name': 'n9kv'}
        ])

        self.assertEqual(YSDeviceProfile.list(require_feature='netconf'), [
            {'key': 'device-with-netconf',
             'name': 'Device with NETCONF',
             'description': 'Nexus 9k device with NETCONF support'},
            {'description': 'Device with netmiko SSH',
             'key': 'netmiko',
             'name': 'Netmiko'},
            {'description': 'Cisco IOS-XR ENxR simulator',
             'key': 'enxr',
             'name': 'enxr'},
            {'key': 'iosxrv_vagrant',   # legacy 2.0 XML profile
             'name': 'iosxrv_vagrant',
             'description': 'IOS XRv (x86_64) Vagrant VM'},
            {'key': 'malformed',
             'name': 'malformed',
             'description': '(an error occurred while reading this profile)'},
            {'key': 'n9kv',    # legacy 2.1 XML profile
             'name': 'n9kv',
             'description': 'n9kv vagrant'}])

    def test_defaults(self):
        """Test default values in a new profile instance."""
        profile = YSDeviceProfile({"base": {
            "profile_name": "test",
            "address": "127.0.0.1",
        }})
        self.assertEqual("test", profile.base.profile_name)
        self.assertEqual("", profile.base.description)
        self.assertEqual("127.0.0.1", profile.base.address)
        self.assertEqual("", profile.base.username)
        self.assertEqual("", profile.base.password)
        self.assertEqual(30, profile.base.timeout)
        self.assertEqual({}, profile.base.variables)

    def test_create_write_delete(self):
        """Test profile creation and deletion."""
        profile = YSDeviceProfile({'base': {
            'profile_name': 'MyProfile',
            'description': 'some description goes here',
            'username': 'user',
            'password': 'some_password',
            'address': '127.0.0.1',
            'timeout': '22',
            'variables': {
                'interface_type': 'GigabitEthernet',
                'interface_id_1': '2',
                'interface_id_2': '3',
            },
        }})

        set_base_path(self.temp_path)

        result, message = profile.write()
        self.assertTrue(result)
        self.assertEqual('Profile "MyProfile" saved', message)

        # Make sure password is not stored as plaintext
        with open(get_path('device', device='myprofile')) as fd:
            jsontext = fd.read()
        self.assertIn('127.0.0.1', jsontext)
        self.assertNotIn('some_password', jsontext)

        my_profile = YSDeviceProfile.get('MyProfile')
        self.assertEqual('MyProfile', my_profile.base.profile_name)
        self.assertEqual('user', my_profile.base.username)
        self.assertEqual('some_password', my_profile.base.password)
        self.assertEqual('127.0.0.1', my_profile.base.address)
        self.assertEqual(22, my_profile.base.timeout)
        self.assertEqual({
            'interface_type': 'GigabitEthernet',
            'interface_id_1': '2',
            'interface_id_2': '3',
        }, my_profile.base.variables)

        result, message = YSDeviceProfile.delete('MyProfile')

        self.assertTrue(result)
        self.assertEqual('Profile "MyProfile" deleted', message)

        self.assertRaises(OSError, YSDeviceProfile.get, 'MyProfile')

        result, message = YSDeviceProfile.delete('MyProfile')
        self.assertFalse(result)
        self.assertEqual('No such profile "MyProfile" found', message)

    def test_write_negative(self):
        """Failure to write profile to disk."""
        result, message = YSDeviceProfile().write()
        self.assertFalse(result)
        self.assertEqual(message, "Profile has no defined name")

    def test_check_reachability_succeed(self):
        """Test success of check_reachability() method."""
        profile = YSDeviceProfile({'base': {
            'profile_name': 'MyProfile',
            'username': 'user',
            'password': 'password',
            'address': '127.0.0.1',
        }})

        # Ping to 127.0.0.1 (localhost) should always succeed
        result = profile.check_reachability()
        self.assertTrue(result['status'])
        self.assertTrue(result['base']['status'])
        self.assertEqual('ping', result['base']['label'])

    def test_update_success(self):
        """Test success of update() method."""
        profile = YSDeviceProfile.get('Basic Device')
        profile.update({'base': {
            'address': '169.254.1.1',
            'timeout': 22,
        }})
        self.assertEqual('169.254.1.1', profile.base.address)
        self.assertEqual(22, profile.base.timeout)
        # Unspecified properties are unchanged
        self.assertEqual('Basic Device', profile.base.profile_name)
        self.assertEqual('admin', profile.base.username)

    def test_update_negative(self):
        """Confirm that various invalid updates are rejected."""
        profile = YSDeviceProfile.get('Basic Device')
        with self.assertRaises(YSDeviceProfileValidationError) as cm:
            profile.update({'base': {
                'username': 'x' * 51,
                'timeout': 'foo',
                'variables': 'python',
            }})
        self.assertEqual(cm.exception.errors, {'base': {
            'username': 'Value must be no more than 50 characters long',
            'timeout': 'Value must be an integer',
            'variables': 'Value must be a dictionary',
        }})

    def test_upload_no_replace(self):
        """Test success of upload() with no replacement file."""
        profile = YSDeviceProfile.get('Certificate')
        set_base_path(self.temp_path)
        os.makedirs(os.path.join(self.temp_path, 'users', 'tester'))
        profile.write()
        file_info = {'user': 'tester',
                     'file_name': 'grpc_new.pem',
                     'file_replace': '',
                     'file_data': open(os.path.join(
                        os.path.dirname(__file__),
                        'data', 'grpc_new.pem')).read()}
        profile.upload(profile.base.profile_name, file_info)
        self.assertEqual('127.0.0.1', profile.base.address)
        self.assertEqual(30, profile.base.timeout)
        self.assertEqual('certificate', profile.base.profile_name)
        self.assertEqual('admin', profile.base.username)
        self.assertEqual('grpc_new.pem', profile.base.certificate)

    def test_upload_replace(self):
        """Confirm that certificate gets replaced."""
        profile = YSDeviceProfile.get('Certificate')
        set_base_path(self.temp_path)
        os.makedirs(os.path.join(self.temp_path, 'users', 'tester'))
        profile.write()
        device_path = get_path('user_devices_dir', user='tester')
        os.makedirs(os.path.join(device_path, profile.base.profile_name))
        shutil.copyfile(
            os.path.join(os.path.dirname(__file__),
                         'data', 'grpc_new.pem'),
            os.path.join(
                device_path, profile.base.profile_name, 'replace_me.pem'
            )
        )
        file_info = {'user': 'tester',
                     'file_name': 'grpc_new.pem',
                     'file_replace': 'replace_me.pem',
                     'file_data': open(os.path.join(
                        os.path.dirname(__file__),
                        'data', 'grpc_new.pem')).read()}
        profile.upload(profile.base.profile_name, file_info)
        self.assertEqual('127.0.0.1', profile.base.address)
        self.assertEqual(30, profile.base.timeout)
        self.assertEqual('certificate', profile.base.profile_name)
        self.assertEqual('admin', profile.base.username)
        self.assertEqual('grpc_new.pem', profile.base.certificate)
        self.assertFalse(os.path.exists(os.path.join(
                device_path, profile.base.profile_name, 'replace_me.pem'
            )
        ))

    def test_upload_no_certificate_name(self):
        """Test failure of upload() with no certificate name."""
        profile = YSDeviceProfile.get('Certificate')
        set_base_path(self.temp_path)
        os.makedirs(os.path.join(self.temp_path, 'users', 'tester'))
        profile.write()
        file_info = {'user': 'tester',
                     'file_name': '',
                     'file_replace': '',
                     'file_data': open(os.path.join(
                        os.path.dirname(__file__),
                        'data', 'grpc_new.pem')).read()}
        with self.assertRaises(YSDeviceProfileValidationError):
            profile.upload(profile.base.profile_name, file_info)

    def test_upload_no_file_data(self):
        """Test failure of upload() with no certificate data."""
        profile = YSDeviceProfile.get('Certificate')
        set_base_path(self.temp_path)
        os.makedirs(os.path.join(self.temp_path, 'users', 'tester'))
        profile.write()
        file_info = {'user': 'tester',
                     'file_name': 'grpc_new.pem',
                     'file_replace': '',
                     'file_data': ''}
        with self.assertRaises(YSDeviceProfileValidationError):
            profile.upload(profile.base.profile_name, file_info)

    def test_extra_plugin(self):
        """Test with an extra, not-fully-implemented plugin."""
        YSDeviceProfile._plugins['myplugin'] = YSDeviceProtocolPlugin
        try:
            profile = YSDeviceProfile.get('Basic Device')
            self.assertEqual(sorted(profile.dict().keys()),
                             ['base', 'myplugin', 'netconf', 'ssh'])

            result = profile.check_reachability()
            self.assertTrue(result['status'])
            self.assertTrue(result['base']['status'])
            self.assertEqual('ping', result['base']['label'])
            self.assertNotIn('myplugin', result)

            self.assertEqual({'data': {}, 'label': ''},
                             profile.data_format()['myplugin'])
        finally:
            del YSDeviceProfile._plugins['myplugin']
