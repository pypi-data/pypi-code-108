# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
import platform
import os
import re
import subprocess
import netmiko
import pexpect
import traceback
import json
from collections import OrderedDict
from netmiko.ssh_dispatcher import CLASS_MAPPER_BASE
from yangsuite import get_logger, get_path
from .devprofile import YSDeviceProfile
from .utilities import encrypt_plaintext, decrypt_ciphertext

log = get_logger(__name__)


class OSVersionError(Exception):
    pass


class YSDeviceProtocolPlugin(object):
    """Abstract class - subclasses extend YSDeviceProfile for various protocols.

    A concrete subclass must provide values for :attr:`label` and :attr:`key`
    and must at minimum implement :meth:`data_format`. It may optionally
    implement :meth:`check_reachability` as well.

    A subclass must override :meth:`update` and :meth:`dict` if any special
    data transformation is required in these methods. A very common case is
    where the plugin is storing a password - in this case, :meth:`dict` must
    ensure that no plaintext password is exposed, and :meth:`update` must
    be able to accept an encrypted password as input.

    If any properties are inheritable from :class:`BasePlugin`, use the
    :meth:`inheritable_property` property constructor as appropriate.
    """

    label = ""
    """Short name of this protocol/plugin, e.g. "NETCONF"."""

    key = ""
    """Key where data belonging to this protocol is stored, e.g. "netconf"."""

    @classmethod
    def data_format(cls):
        """Dictionary of data key to type / description / constraints.

        Returns:
          OrderedDict

        For example::

          {
            'username': {
              'type': 'string',
              'description': 'Username used to access the device via NETCONF',
              'minLength': 1,
              'maxLength': 50,
            },
            'port': {
              'label': 'NETCONF port',
              'type': 'int',
              'description': 'Port number NETCONF listens on',
              'min': 0,
              'max': 65535,
              'default': 830,
            },
          }

        Data dict keys that are currently understood:

        label
          Human-readable short label (if unspecified, will use the data key)
        type
          One of 'string', 'password', 'int', 'enum', 'boolean', 'float', or
          'dict'
        description
          Verbose description of this item
        default
          Initial default value of this item
        required
          If True, this item is mandatory
        choices
          For an 'enum', a list of (value, label) tuples
        min
          Minimum value of an 'int' or 'float'
        max
          Maximum value of an 'int' or 'float'
        step
          Suggested increment value of an 'int' or 'float'
        minLength
          Minimum length of a 'string' or 'password'
        maxLength
          Maximum length of a 'string' or 'password'
        keyLabel
          Label for keys of a 'dict'
        valueLabel
          Label for values of a 'dict'
        """
        return OrderedDict()

    def __init__(self, profile, data=None):
        """Instantiate this plugin.

        Args:
          profile (YSDeviceProfile): instance owning this plugin instance.
          data (dict): Data to initialize with.
        """
        self.profile = profile
        if not data:
            data = {}
        # Don't report errors here, as the usual workflow from YSDeviceProfile
        # is to init with empty data, then immediately call update() with the
        # actual plugin data to be used.
        self.update(data)

    def update(self, data):
        """Update this plugin's properties from the given data dictionary.

        Returns:
          dict: ``{key: 'error for this key', key2: 'another error', ...}``
        """
        errors = {}
        for key, fmt in self.data_format().items():
            if key in data:
                # Value needs to be updated
                value = data[key]
            elif not hasattr(self, key):
                # Value needs to be initialized to default
                if fmt.get('required', False) and 'default' not in fmt:
                    errors[key] = "This is a required field"
                value = fmt.get('default', '')
                if fmt.get('type') == 'dict' and not value:
                    value = {}
                setattr(self, key, value)
                continue
            else:
                value = getattr(self, key)

            if value == "" or value is None:
                if fmt.get('required', False):
                    errors[key] = "This is a required field"
                else:
                    setattr(self, key, value)
                continue
            if hasattr(self, key) and value == getattr(self, key):
                # Unchanged, presume to still be valid
                continue

            error = None

            # Validate the proposed value
            if fmt.get('type') == 'int':
                try:
                    value = int(value)
                    if 'min' in fmt and value < fmt['min']:
                        error = 'Value must be at least {0}'.format(fmt['min'])
                    if 'max' in fmt and value > fmt['max']:
                        error = 'Value must be at most {0}'.format(fmt['max'])
                except ValueError:
                    error = 'Value must be an integer'
            elif fmt.get('type') == 'float':
                try:
                    value = float(value)
                    if 'min' in fmt and value < fmt['min']:
                        error = 'Value must be at least {0}'.format(fmt['min'])
                    if 'max' in fmt and value > fmt['max']:
                        error = 'Value must be at most {0}'.format(fmt['max'])
                except ValueError:
                    error = 'Value must be a number'
            elif fmt.get('type') == 'boolean':
                if value in [True, 'true', 'True', '1', 1]:
                    value = True
                elif value in [False, 'false', 'False', '0', 0]:
                    value = False
                else:
                    error = 'Value must be a boolean value'
            elif fmt.get('type') == 'enum':
                valid_values = [x[0] for x in fmt['choices']]
                if value not in valid_values:
                    error = 'Value must be one of {0}'.format(valid_values)
            elif fmt.get('type') == 'dict':
                result = OrderedDict()
                try:
                    for value_key in sorted(value.keys()):
                        result[value_key] = value.get(value_key)
                    value = result
                except AttributeError:
                    error = 'Value must be a dictionary'
            elif fmt.get('type') == 'upload':
                # Stores filename here but file may not exist yet
                pass
            else:  # string / password
                if 'minLength' in fmt and len(value) < fmt['minLength']:
                    error = ("Value must be at least {0} characters long"
                             .format(fmt['minLength']))
                if 'maxLength' in fmt and len(value) > fmt['maxLength']:
                    error = ("Value must be no more than {0} characters long"
                             .format(fmt['maxLength']))

            if error:
                errors[key] = error
            else:
                setattr(self, key, value)

        return errors

    @staticmethod
    def inheritable_property(base_name, docstring=None):
        """Create a property which can be set or uses a base value if unset.

        Helper method for setting up subclasses.

        .. warning::

          The property name this is assigned to **MUST** match the base_name::

            username = inheritable_property('username')  # correct
            user = inheritable_property('username')      # INCORRECT

        Args:
          base_name (str): Name of property to inherit from profile.base if
            this property is not explicitly set otherwise.
          docstring (str): Docstring to attach to this property

        Examples::

          username = inheritable_property('username')

          username = inheritable_property('username',
            docstring="Login user. If unset, default to profile.base.username")
        """
        def _getter(self):
            if not hasattr(self, '_' + base_name):
                setattr(self, '_' + base_name, '')
            value = getattr(self, "_" + base_name)
            if value == '' or value is None:
                value = getattr(self.profile.base, base_name)
            return value

        def _setter(self, value):
            setattr(self, "_" + base_name, value)

        return property(_getter, _setter, doc=docstring)

    def dict(self):
        """Dictionary representation of this data, suitable for saving.

        Note that any passwords must be encrypted!

        At a minimum, any protocol plugin must provide key 'enabled',
        a boolean indicating whether this protocol is enabled for this profile.
        """
        data = {}
        for key in self.data_format().keys():
            # Report actual values, not inheritable_property values
            value = getattr(self, key)
            if hasattr(self, '_' + key):
                value = getattr(self, '_' + key)
            data[key] = value

        return data

    @classmethod
    def check_reachability(cls, devprofile):
        """Check whether the given device is reachable using this protocol.

        Args:
          devprofile (YSDeviceProfile): Device to check
        Returns:
          tuple: (str label, bool success/failure, str message)
        """
        raise NotImplementedError(
            'check_reachability() is not implemented for plugin "{0}"'
            .format(cls.label))


class BasePlugin(YSDeviceProtocolPlugin):
    """Base shared config of a device profile, plus ping connectivity check."""

    label = "General Info"
    key = "base"
    enabled = True

    @classmethod
    def data_format(cls):
        result = OrderedDict()
        result['profile_name'] = {
            'label': 'Profile Name',
            'type': 'string',
            'description': 'Name of this device profile',
            'minLength': 1,
            'required': True,
        }
        result['description'] = {
            'type': 'string',
            'description': 'Verbose description',
        }
        result['address'] = {
            'type': 'string',
            'description':
            'Address or hostname to use as default for all protocols',
            'required': True,
        }
        result['username'] = {
            'type': 'string',
            'description': 'Username used as default for all protocols',
            'maxLength': 50,
        }
        result['password'] = {
            'type': 'password',
            'description': 'Password used as default for all protocols',
            'maxLength': 50,
        }
        result['timeout'] = {
            'type': 'int',
            'description':
            'Timeout (in seconds) as default for all protocols',
            'default': 30,
            'required': True,
        }
        result['variables'] = {
            'type': 'dict',
            'description': 'Key/value pairs of data associated with device',
            'keyLabel': 'Variable Name',
            'valueLabel': 'Value',
        }
        result['certificate'] = {
            'label': 'TLS Authority Certificate',
            'type': 'upload',
            'description': 'Certificate authority.',
            'default': '',
        }
        result['clientcert'] = {
            'label': 'TLS Client Certificate',
            'type': 'upload',
            'description': 'Client certificate or chain of certificates',
            'default': '',
        }
        result['clientkey'] = {
            'label': 'TLS Client Key',
            'type': 'upload',
            'description': 'Client private key',
            'default': '',
        }
        result['servercert'] = {
            'label': 'TLS Server Certificate',
            'type': 'upload',
            'description': 'Server certificate or chain of certificates',
            'default': '',
        }
        result['serverkey'] = {
            'label': 'TLS Server Key',
            'type': 'upload',
            'description': 'Server private key',
            'default': '',
        }
        return result

    def update(self, data):
        extra_errors = {}
        if 'password' not in data or not data['password']:
            if 'encrypted_password' in data and data['encrypted_password']:
                try:
                    data['password'] = decrypt_ciphertext(
                        data['encrypted_password'],
                        (data.get('username') or self.username))
                except ValueError as exc:
                    extra_errors['password'] = str(exc)
        errors = super(BasePlugin, self).update(data)
        errors.update(extra_errors)
        return errors

    def dict(self):
        data = super(BasePlugin, self).dict()
        data['encrypted_password'] = encrypt_plaintext(self.password,
                                                       self.username)
        del data['password']
        return data

    @classmethod
    def check_reachability(cls, devprofile):
        """Check whether the described device is pingable.

        Loosely based on https://stackoverflow.com/a/35625078/1281083

        Returns:
          tuple: ('ping', pingable, reason) where pingable is True or False,
          and reason may be a string explaining any False result.
        """
        # Ping parameters vary by OS
        if platform.system().lower() == "windows":
            ping_str = "-n 3"
            need_shell = False
        else:
            ping_str = "-c 3"
            need_shell = True

        args = 'ping ' + ping_str + ' ' + devprofile.base.address
        log.debug('Calling "%s"', args)
        subp = subprocess.Popen(args,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                shell=need_shell)
        (output, _) = subp.communicate()
        log.debug(output)
        if subp.returncode == 0:
            return ('ping', True, '')
        else:
            # TODO - parse output for cleaner detail?
            return ('ping', False, output.decode())


class SshPlugin(YSDeviceProtocolPlugin):
    """SSH (Netmiko) params of a device profile plus SSH connectivity check."""

    label = "SSH"
    key = "ssh"

    @classmethod
    def data_format(cls):
        result = OrderedDict()
        choices = sorted(
            [('cisco_enxr', 'cisco_enxr'),
             ('cisco_sdwan', 'cisco_sdwan')] +
            [(key, key) for key in CLASS_MAPPER_BASE.keys()]
        )
        result['enabled'] = {
            'label': 'Device allows SSH login',
            'type': 'boolean',
            'default': False,
        }
        result['device_variant'] = {
            'label': 'Device variant',
            'type': 'enum',
            'description':
            'Value specifying platform-dependent behavior of netmiko',
            'choices': choices,
            'default': 'generic_termserver',
            'required': True,
        }
        result['address'] = {
            'type': 'string',
            'description': 'Address or hostname to access via SSH',
        }
        result['port'] = {
            'label': 'SSH Port',
            'type': 'int',
            'description': 'Port number for SSH connection to device console',
            'min': 1,
            'max': 65535,
            'default': 22,
            'required': True,
        }
        result['delay_factor'] = {
            'label': 'Delay Factor',
            'type': 'float',
            'description': (
                'Multiplier for acceptable delays from the device. '
                'Set to lower value for faster performance. '
                'Set to higher value if timeout errors are seen.'
            ),
            'min': 0,
            'default': 1.0,
            'step': 0.1,
        }
        result['username'] = {
            'type': 'string',
            'description': 'Username to access the device via SSH',
            'minLength': 1,
        }
        result['password'] = {
            'type': 'password',
            'description': 'Password to access the device via SSH',
            'minLength': 1,
        }
        result['timeout'] = {
            'type': 'int',
            'description': 'Timeout, in seconds, for SSH requests',
            'min': 0,
        }
        result['secure'] = {
            'label': 'Use SSL Certificate',
            'type': 'boolean',
            'default': False,
        }
        return result

    # Inherit the following
    address = YSDeviceProtocolPlugin.inheritable_property(
        'address',
        docstring="Address for SSH access, if different from base address")
    username = YSDeviceProtocolPlugin.inheritable_property(
        'username',
        docstring="SSH login username, if different from base username")
    password = YSDeviceProtocolPlugin.inheritable_property(
        'password',
        docstring="SSH login password, if different from base password")
    timeout = YSDeviceProtocolPlugin.inheritable_property(
        'timeout',
        docstring="SSH connection timeout in seconds, "
        "if different from base timeout")

    def update(self, data):
        if 'password' not in data or not data['password']:
            if 'encrypted_password' in data and data['encrypted_password']:
                data['password'] = decrypt_ciphertext(
                    data['encrypted_password'],
                    (data.get('username') or self.username))
        return super(SshPlugin, self).update(data)

    def dict(self):
        data = super(SshPlugin, self).dict()
        data['encrypted_password'] = encrypt_plaintext(self._password,
                                                       self.username)
        del data['password']
        return data

    @classmethod
    def check_reachability(cls, devprofile):
        try:
            msg = ''
            os_type = ''
            os_ver = ''
            profile_name = devprofile.base.profile_name
            ssh = SshSession.get(devprofile)
            is_connected = ssh.connect()
            if is_connected:
                msg = "Connected successfully"
                # To check OS type and OS version for analytics
                device_path = get_path('devices_dir')
                try:
                    response = ssh.send_exec("show version")
                    if not response:
                        raise OSVersionError('No response to show version')
                    if 'IOS XE' in response:
                        os_type = 'iosxe'
                        resp = response.splitlines()
                        os_ver = resp[1][:resp[1].rfind('[')]
                        if 'Version' not in os_ver:
                            raise OSVersionError("Invalid response to IOS-XE" +
                                                 "show version")
                        os_ver = os_ver.split('Version')[1]
                        os_ver = os_ver[:os_ver.rfind('.')].strip()
                        os_ver = 'XE-' + os_ver

                    elif 'IOS XR' in response:
                        os_type = 'iosxr'
                        resp = response.splitlines()
                        if 'Version' not in resp:
                            raise OSVersionError("Invalid response to IOS-XR" +
                                                 "show version")
                        os_ver = resp[1].split('Version')[1].strip()
                        os_ver = 'XR-' + os_ver

                    elif '(NX-OS)' in response:
                        os_type = 'iosnx'
                        # Filter out the version details from show version
                        resp = [line for line in response.splitlines()
                                if 'NXOS: version' in line]
                        if not resp or 'version' not in resp[0]:
                            raise OSVersionError("Invalid response to NX-OS" +
                                                 "show version")
                        os_ver = resp[0].split('version')[1].strip()
                        os_ver = 'NX-' + os_ver
                    # Create a dictionary with device type and version
                    data = {
                             profile_name:
                             {
                               "os_type": os_type,
                               "os_ver": os_ver
                             }
                           }
                    # Create a generic json file under data/devices to
                    # document the device details
                    device_stats = os.path.join(device_path,
                                                'device_stats.json')
                    if not os.path.exists(device_stats):
                        with open(device_stats, 'w') as fd:
                            json_data = json.dumps(data)
                            fd.write(json_data)
                    # If the file exists, read the content
                    # of the device, and update the version if changed.
                    else:
                        with open(device_stats, 'r') as fd:
                            json_data = json.load(fd)
                        if not json_data.get(profile_name, ''):
                            with open(device_stats, 'w') as fd:
                                json_data = json.dumps(data)
                                fd.write(json_data)
                        else:
                            version = json_data[profile_name]['os_ver']
                            if version != os_ver:
                                json_data[profile_name]['os_ver'] = os_ver
                                with open(device_stats, 'w') as fd:
                                    json.dump(json_data, fd)
                except Exception as e:
                    log.debug("OS version check failed: %s", str(e))
            else:
                msg = 'Not reachable'
            ssh.disconnect()
            return ('SSH', is_connected, msg)
        except Exception as e:
            log.debug('SSH check failed: %s', e)
            log.debug(traceback.format_exc())
            msg = str(e)
            if devprofile.ssh.device_variant == 'generic_termserver':
                msg += ("\nYou may need to properly specify the device variant"
                        " rather than treating this as a generic device.")
            return ('SSH', False, msg)
        finally:
            SshSession.destroy(devprofile)


class SshSession:
    """Session handling for SSH connections."""

    instances = {}

    @classmethod
    def get(cls, key):
        """Retrieve or create an SSH session instance.

        The key can be a string or a device profile.

        Args:
          key (str): Device name or uses the base.profile_name as key.
        Returns:
          SshSession
        """
        # accept device name or profile
        if not isinstance(key, YSDeviceProfile):
            dev_profile = YSDeviceProfile.get(key)
        else:
            dev_profile = key
            key = dev_profile.base.profile_name

        if key not in cls.instances:
            if dev_profile.ssh.device_variant == 'cisco_enxr':
                cls.instances[key] = SshEnxrSession(key)
            else:
                cls.instances[key] = SshNetmikoSession(key)

        return cls.instances[key]

    @classmethod
    def destroy(cls, key):
        """Remove the session instance from the cache.

        The key can be a string or a device profile.

        Args:
          key (str): Device name or uses the base.profile_name as key.
        """
        if isinstance(key, YSDeviceProfile):
            key = key.base.profile_name

        if key in cls.instances:
            session = cls.instances[key]
            if session.connected:
                session.disconnect()
            del cls.instances[key]

    def __init__(self, key):
        self.key = key
        self.dev_profile = YSDeviceProfile.get(key)

    @property
    def connected(self):
        """Return True if session is connected.

        ** Override this property in subclass. **

        """
        pass

    def send_config(self, cmd):
        """Send any CLI configuration command.

        ** Override this function in subclass. **

        Args:
          cmd (str): Configuration CLI command.
        Returns:
          (str): CLI response
        """
        pass

    def send_exec(self, cmd):
        """Send any CLI exec commmand.

        ** Override this function in subclass. **

        Args:
          cmd (str): Configuration CLI command.
        Returns:
          (str): CLI response
        """
        pass

    def connect(self):
        """Connect to SSH device.

        ** Override this function in subclass. **

        """
        pass

    def disconnect(self):
        """Disconnect from SSH device.

        ** Override this function in subclass. **

        """
        pass

    def __enter__(self):
        """Establish a session using a Context Manager."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Gracefully close connection on Context Manager exit."""
        self.disconnect()


class SshNetmikoSession(SshSession):
    """Basic wrapper class around Netmiko library.

    https://github.com/ktbyers/netmiko
    """
    def __init__(self, key, user=''):
        super().__init__(key)
        if self.dev_profile.ssh.device_variant == "cisco_sdwan":
            self.netmiko_device = {
                'device_type': 'cisco_xe',  # Using IOS-XE netmiko class
                'ip': self.dev_profile.ssh.address,
                'username': self.dev_profile.ssh.username,
                'password': self.dev_profile.ssh.password,
                'port': self.dev_profile.ssh.port,
                'timeout': self.dev_profile.ssh.timeout,
                'global_delay_factor': self.dev_profile.ssh.delay_factor
            }
        else:
            self.netmiko_device = {
                'device_type': self.dev_profile.ssh.device_variant,
                'ip': self.dev_profile.ssh.address,
                'username': self.dev_profile.ssh.username,
                'password': self.dev_profile.ssh.password,
                'port': self.dev_profile.ssh.port,
                'timeout': self.dev_profile.ssh.timeout,
                'global_delay_factor': self.dev_profile.ssh.delay_factor
            }
        if user and self.dev_profile.ssh.secure:
            user_device_path = get_path('user_device_dir', user=user)
            cert_path = os.path.join(
                user_device_path,
                self.dev_profile.base.profile_name,
                self.dev_profile.base.certificate
            )
            if os.path.isfile(cert_path):
                self.netmiko_device["use_keys"] = True
                self.netmiko_device["key_file"] = cert_path
            else:
                log.error('SSH: Certificate "{0}" not found'.format(
                    self.dev_profile.base.certificate
                ))

        # Need both global_delay_factor set plus pass in delay_factor for send
        self.delay_factor = self.dev_profile.ssh.delay_factor
        self.ssh = None

    @property
    def connected(self):
        """ Return True if session is connected."""
        return (self.ssh is not None)

    def send_config(self, cmd, **kwargs):
        """Send any CLI configuration command.

        Args:
          cmd (str): Configuration CLI command.
          kwargs (dict): Optional Netmiko arguments.
        Returns:
          (str): CLI response
        """
        if not cmd or not self.connected:
            return

        try:
            if self.dev_profile.ssh.device_variant == "cisco_sdwan":
                result = self.ssh.send_config_set(
                    cmd, exit_config_mode=False,
                    delay_factor=self.delay_factor,
                    config_mode_command='config-transaction')

            else:
                result = self.ssh.send_config_set(
                    cmd, delay_factor=self.delay_factor)
        except ValueError as exc:
            if re.search("Failed.*config.*mode",
                         exc.args[0]) and self.delay_factor < 1:
                # Can happen if the delay_factor is too small for a slow device
                exc.args = (exc.args[0] +
                            '\nYou might need to increase the SSH ' +
                            '"delay factor" configured for this ' +
                            'device profile.',)
            raise
        if (self.dev_profile.ssh.device_variant == "cisco_sdwan"):
            # SDWAN - need to send commit then explicitly exit config mode
            command_string = "commit"
            error_marker = "Failed to"
            alt_error_marker = "One or more commits have occurred from other"
            output = self.ssh.config_mode(config_command='config-transaction')
            output += self.ssh.send_command_expect(
                command_string,
                strip_prompt=False,
                strip_command=False,
                delay_factor=1,
            )
            if error_marker in output:
                raise ValueError(
                    "Commit failed with the " +
                    "following errors:\n\n{0}".format(output)
                )
            if alt_error_marker in output:
                # Other commits occurred, don't proceed with commit
                output += self.ssh.send_command_timing(
                    "no", strip_prompt=False, strip_command=False,
                    delay_factor=self.delay_factor
                )
                raise ValueError(
                    "Commit failed with the " +
                    "following errors:\n\n{}".format(output)
                )
            result += output
            result += self.ssh.exit_config_mode(exit_config="end")

        elif (self.dev_profile.ssh.device_variant == "cisco_xr"):
            # IOS XR - need to send commit then explicitly exit config mode
            result += self.ssh.commit()
            result += self.ssh.exit_config_mode()

        return result

    def send_exec(self, cmd, **kwargs):
        """Send any CLI exec commmand.

        Args:
          cmd (str): Configuration CLI command.
          kwargs (dict): Optional Netmiko arguments.
        Returns:
          (str): CLI response
        """
        if not cmd or not self.connected:
            return
        return self.ssh.send_command(cmd, delay_factor=self.delay_factor)

    def connect(self):
        """Connect to Netmiko."""
        log.debug(
            "SSH CONNECTION:\n{0}: {1}:{2}\nuser: {3} ".format(
                self.dev_profile.base.profile_name,
                self.dev_profile.ssh.address,
                self.dev_profile.ssh.port,
                self.dev_profile.ssh.username
            )
        )
        if not self.connected:
            self.ssh = netmiko.ConnectHandler(**self.netmiko_device)
        return self.connected

    def disconnect(self):
        """Disconnect from Netmiko device."""
        if self.connected:
            self.ssh.disconnect()
        self.ssh = None


class SshEnxrSession(SshSession):
    """Handles calls to Cisco IOS XR EnXR simulator.

    http://enwiki.cisco.com/EnXR
    """
    def __init__(self, key):
        super().__init__(key)
        self.connected = False
        self.ssh = None

    @property
    def connected(self):
        """ Return True if session is connected."""
        return self._connected

    @connected.setter
    def connected(self, is_connected):
        self._connected = is_connected

    def _flush_connection(self):
        """Spawn a new pexpect between send calls.

        The NETCONF plugin on same EnXR simulator uses a proxy executable.
        When the NETCONF proxy is used, the CLI changes do not show up in
        the pexpect pty unless it is closed and a new one is spawned.
        """
        self.disconnect()
        self.connect(spawn=self.spawn, prompt=self.prompt)

    def _send(self, cmd):
        """Using pexpect for all commands."""
        if not cmd or not self.connected:
            return
        try:
            self._flush_connection()
            self.ssh.sendline(cmd)
            self.ssh.expect(self.prompt, timeout=10)
            return self.ssh.before.decode('utf-8') + self.prompt
        except pexpect.exceptions.TIMEOUT:
            log.error('EVxR CLI failed %s\n\n%s',
                      (self.dev_profile.base.profile_name,
                       cmd))
            return 'Command TIMEOUT'

    def send_config(self, cmd):
        """Send any CLI configuration command.

        If command does not start with "conf", that will be prepended.
        If command does not end in "commit end" it will be appended.

        Args:
          cmd (str): Configuration CLI command.
          kwargs (dict): Optional arguments.
        Returns:
          (str): CLI response
        """
        if not cmd.strip().startswith('conf'):
            cmd = 'conf\r\n' + cmd
        if not cmd.strip().endswith('end'):
            if not cmd.strip().endswith('commit'):
                cmd += '\r\ncommit\r\nend\r\n'
            else:
                cmd += '\r\nend\r\n'
        return self._send(cmd)

    def send_exec(self, cmd):
        """Send any CLI exec commmand.

        Args:
          cmd (str): Configuration CLI command.
          kwargs (dict): Optional arguments.
        Returns:
          (str): CLI response
        """
        return self._send(cmd)

    def connect(self, **kwargs):
        """Connect to EnXR.

        Args:
          kwargs (dict):
            spawn (str): Spawn parameter for pexpect (default "exec").
            prompt (str): Expect parameter for pexpect (default ":ios#").
        Returns:
          (bool): True if connection is successful
        """
        try:
            self.spawn = kwargs.get('spawn', 'exec')
            self.prompt = kwargs.get('prompt', ':ios#')
            if not self.connected:
                p = pexpect.spawn(self.spawn)
                p.expect(self.prompt, timeout=10)
                self.connected = True
                self.ssh = p

        except pexpect.exceptions.TIMEOUT:
            log.error('EnXR connect failed %s',
                      self.dev_profile.base.profile_name)
        except Exception:
            log.error('EnXR connect failed %s',
                      self.dev_profile.base.profile_name)
            log.error(traceback.format_exc())
        finally:
            return self.connected

    def disconnect(self):
        """Disconnect from EnXR.

        Returns:
          (bool): True if disconnect is successful
        """
        try:
            if self.connected:
                self.ssh.close()
                self.connected = False
        except Exception:
            log.error('EnXR disconnect failed %s',
                      self.dev_profile.base.profile_name)
            log.error(traceback.format_exc())
        finally:
            return self.connected
