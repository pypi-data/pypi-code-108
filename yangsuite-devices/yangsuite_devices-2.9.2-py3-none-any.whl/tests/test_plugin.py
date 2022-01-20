# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
"""Unit tests for the ysdevices.plugin module."""

import unittest2 as unittest
from ..devprofile import YSDeviceProfile
from ..plugin import (
    YSDeviceProtocolPlugin,
    BasePlugin,
    SshPlugin,
    SshSession,
    SshEnxrSession,
    SshNetmikoSession,
)


class TestYSDeviceProtocolPlugin(unittest.TestCase):
    """Test semi-abstract YSDeviceProtocolPlugin functions."""

    def test_api(self):
        """Check default API implementations."""
        self.assertEqual({}, YSDeviceProtocolPlugin.data_format())
        self.assertRaises(NotImplementedError,
                          YSDeviceProtocolPlugin.check_reachability, None)

        plugin = YSDeviceProtocolPlugin(None)
        self.assertEqual({}, plugin.dict())

        # update() / dict() ignores keys not in data_format():
        plugin.update({'foo': 'bar', 'baz': False})
        self.assertEqual({}, plugin.dict())


class TestBasePlugin(unittest.TestCase):
    """Test 'base' plugin implementation."""

    def test_data_format(self):
        """Check the data format reported by this plugin."""
        # We could do a whole 'self.assertEqual({......}' for the entire
        # dict copy-and-pasted from plugin.py, but spot checks are arguably
        # MORE likely to catch unintended behavior changes
        fmt = BasePlugin.data_format()
        self.assertEqual(['address', 'certificate', 'clientcert', 'clientkey',
                          'description', 'password', 'profile_name',
                          'servercert', 'serverkey', 'timeout', 'username',
                          'variables'],
                         sorted(fmt.keys()))
        self.assertTrue(fmt['profile_name']['required'])
        self.assertEqual('string', fmt['profile_name']['type'])
        self.assertEqual('password', fmt['password']['type'])
        self.assertEqual('int', fmt['timeout']['type'])
        self.assertEqual('dict', fmt['variables']['type'])

    def test_dict(self):
        plugin = BasePlugin(None, data={"profile_name": "test"})
        self.assertEqual(plugin.dict(), {
            'profile_name': 'test',
            'description': '',
            'address': '',
            'certificate': '',
            'clientkey': '',
            'clientcert': '',
            'username': '',
            'encrypted_password': '',
            'servercert': '',
            'serverkey': '',
            'timeout': 30,
            'variables': {},
        })

    def test_update_success(self):
        plugin = BasePlugin(None, data={"profile_name": "test"})
        errors = plugin.update({
            'profile_name': 'a new test',
            'description': 'describe myself here',
            'address': '127.0.0.1',
            'username': 'x' * 50,
            'timeout': 22,
            'variables': {'interface_name': 'GigabitEthernet2'},
        })
        self.assertEqual(errors, {})
        self.assertEqual(plugin.dict(), {
            'profile_name': 'a new test',
            'description': 'describe myself here',
            'address': '127.0.0.1',
            'certificate': '',
            'clientkey': '',
            'clientcert': '',
            'username': 'x' * 50,
            'encrypted_password': '',
            'servercert': '',
            'serverkey': '',
            'timeout': 22,
            'variables': {'interface_name': 'GigabitEthernet2'},
        })

    def test_update_invalid(self):
        plugin = BasePlugin(None, data={"profile_name": "test"})
        errors = plugin.update({
            'profile_name': '',
            'username': 'x' * 51,
            'encrypted_password': 'foobar',
            'timeout': 'hello',
            'variables': 0,
        })
        self.assertEqual(
            ['address', 'password', 'profile_name', 'timeout', 'username',
             'variables'],
            sorted(errors.keys()))
        self.assertEqual('This is a required field', errors['profile_name'])
        self.assertEqual('This is a required field', errors['address'])
        self.assertEqual('Value must be no more than 50 characters long',
                         errors['username'])
        self.assertEqual('String is not in the form "salt$ciphertext"',
                         errors['password'])
        self.assertEqual('Value must be an integer', errors['timeout'])
        self.assertEqual('Value must be a dictionary', errors['variables'])

    def test_check_reachability(self):
        profile = YSDeviceProfile({'base': {
            'profile_name': 'MyProfile',
            'username': 'user',
            'password': 'password',
            'address': '127.0.0.1',
        }})
        label, result, message = BasePlugin.check_reachability(profile)

        # Ping to 127.0.0.1 (localhost) should always succeed
        self.assertEqual('ping', label)
        self.assertTrue(result)
        self.assertEqual('', message)

        # 198.51.100.0/24 is reserved for documentation and shouldn't be used
        profile.base.update({"address": "198.51.100.122"})
        label, result, message = BasePlugin.check_reachability(profile)
        self.assertEqual('ping', label)
        self.assertFalse(result)
        self.assertNotEqual('', message)


class TestDerivedPlugin(unittest.TestCase):
    """Test plugin derivation from base data using an artificial plugin."""

    class MyPlugin(YSDeviceProtocolPlugin):

        label = "My First Plugin"
        key = "myplugin"

        @classmethod
        def data_format(cls):
            return {
                'enabled': {
                    'type': 'boolean',
                    'default': False,
                },
                'little_int': {
                    'type': 'int',
                    'max': 5,
                },
                'big_int': {
                    'type': 'int',
                    'min': 1000,
                },
                'username': {
                    'type': 'string',
                    'maxLength': 3,
                },
                'address': {
                    'type': 'string',
                    'minLength': 20,
                },
                'enumeration': {
                    'type': 'enum',
                    'choices': [
                        ('foo', 'label for foo'),
                        ('bar', 'label for bar'),
                    ],
                },
            }

        username = YSDeviceProtocolPlugin.inheritable_property('username')
        address = YSDeviceProtocolPlugin.inheritable_property('address')

        @classmethod
        def check_reachability(cls, profile):
            return ('My Plugin', False, 'Always unreachable')

    def setUp(self):
        YSDeviceProfile._plugins['myplugin'] = self.MyPlugin

    def tearDown(self):
        del YSDeviceProfile._plugins['myplugin']

    def test_inheritance(self):
        """Test inheritable properties."""
        profile = YSDeviceProfile({'base': {
            'profile_name': 'test',
            'address': '127.0.0.1',
            'username': 'hello',
            'password': 'world',
        }})

        self.assertEqual(profile.myplugin.username, 'hello')
        self.assertEqual(profile.myplugin.address, '127.0.0.1')

        # Inherited properties are not repeated in the plugin's dict:
        self.assertEqual(profile.myplugin.dict(), {
            'enabled': False,
            'little_int': '',
            'big_int': '',
            'username': '',
            'address': '',
            'enumeration': '',
        })

    def test_update_positive(self):
        """Test data update / inheritance."""
        profile = YSDeviceProfile({'base': {
            'profile_name': 'test',
            'address': '127.0.0.1',
            'username': 'hello',
        }})

        profile.myplugin.update({
            'enabled': True,
            'little_int': 5,
            'big_int': 1000,
            'username': 'foo',
            'address': 'FE80:1000:2000:3000:4000:5000',
            'enumeration': 'foo',
        })

        self.assertEqual(profile.myplugin.dict(), {
            'enabled': True,
            'little_int': 5,
            'big_int': 1000,
            'username': 'foo',
            'address': 'FE80:1000:2000:3000:4000:5000',
            'enumeration': 'foo',
        })

        # Updating inherited properties does NOT change base property
        self.assertEqual(profile.base.username, 'hello')
        self.assertEqual(profile.base.address, '127.0.0.1')

    def test_update_negative(self):
        """Test update data validation."""
        profile = YSDeviceProfile({'base': {
            'profile_name': 'test',
            'address': '127.0.0.1',
        }})
        errors = profile.myplugin.update({
            'enabled': 'unknown',
            'little_int': 100,
            'big_int': 1,
            'username': 'abcdefg',
            'address': 'x',
            'enumeration': 'alpha',
        })
        self.assertEqual(errors, {
            'enabled': 'Value must be a boolean value',
            'little_int': 'Value must be at most 5',
            'big_int': 'Value must be at least 1000',
            'username': 'Value must be no more than 3 characters long',
            'address': 'Value must be at least 20 characters long',
            'enumeration': "Value must be one of ['foo', 'bar']",
        })

    def test_check_reachability(self):
        """Reachability scenarios."""
        profile = YSDeviceProfile({'base': {
            'profile_name': 'test',
            'address': '127.0.0.1',
        }})

        result = profile.check_reachability()
        # Because myplugin.enabled is False (default), we don't
        # call its connectivity check
        self.assertEqual(result, {
            'status': True,
            'base': {'label': 'ping', 'status': True},
        })

        profile.myplugin.update({'enabled': True})

        result = profile.check_reachability()
        self.assertEqual(result, {
            'status': False,
            'base': {'label': 'ping', 'status': True},
            'myplugin': {'label': 'My Plugin',
                         'status': False,
                         'reason': 'Always unreachable'}
        })


class TestSshPlugin(unittest.TestCase):
    """Test the included SSH plugin."""

    def test_data_format(self):
        """Check the data format reported by this plugin."""
        # We could do a whole 'self.assertEqual({......}' for the entire
        # dict copy-and-pasted from plugin.py, but spot checks are arguably
        # MORE likely to catch unintended behavior changes
        fmt = SshPlugin.data_format()
        self.assertEqual(['address', 'delay_factor', 'device_variant',
                          'enabled', 'password',
                          'port', 'secure', 'timeout', 'username'],
                         sorted(fmt.keys()))
        self.assertTrue(fmt['port']['required'])
        self.assertEqual('string', fmt['username']['type'])
        self.assertEqual('password', fmt['password']['type'])
        self.assertEqual('int', fmt['timeout']['type'])

    def test_check_reachability(self):
        # 198.51.100.0/24 is reserved for documentation and shouldn't be used
        profile = YSDeviceProfile({
            'base': {
                'profile_name': 'MyProfile',
                'username': 'user',
                'password': 'password',
                'address': '198.51.100.22',
            },
            'ssh': {
                'enabled': True,
                'timeout': 3,
            }
        })
        label, result, message = SshPlugin.check_reachability(profile)
        self.assertEqual('SSH', label)
        self.assertFalse(result)
        self.assertNotEqual('', message)

    def test_netmiko_session(self):
        """Test a netmiko SSH session."""
        ssh = SshSession.get('netmiko')
        self.assertTrue(isinstance(ssh, SshNetmikoSession))

    def test_ssh_session(self):
        """Test profile instance and name string get session."""
        ssh1 = SshSession.get('enxr')
        dev_profile = YSDeviceProfile.get('enxr')
        # should get the 'enxr' instance using dev_profile
        ssh2 = SshSession.get(dev_profile)
        SshSession.destroy('enxr')
        self.assertIs(ssh1, ssh2)
        # destroy should have removed the instance
        self.assertNotIn('enxr', SshSession.instances)
        self.assertTrue(isinstance(ssh1, SshEnxrSession))
        self.assertTrue(isinstance(ssh2, SshEnxrSession))

    def test_enxr_session(self):
        """Test an EnXR SSH session."""
        ssh = SshSession.get('enxr')
        self.assertTrue(isinstance(ssh, SshEnxrSession))
        # Use simple calls through pexpect to python for testing
        ssh.connect(spawn='python', prompt='>>>')
        resp = ssh.send_exec('dir()')
        self.assertIn('__builtins__', resp)
        # send_config appends "conf at start and "commit\r\nend" at end
        resp = ssh.send_config('junk')
        self.assertTrue(resp.strip().startswith('conf'))
        self.assertTrue(resp.strip().endswith('>>>'))
        SshSession.destroy('enxr')
