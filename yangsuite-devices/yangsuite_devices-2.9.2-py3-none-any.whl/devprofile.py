# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
import errno
import os
import traceback
import json
import xml.etree.ElementTree as ET
from collections import OrderedDict
from pkg_resources import iter_entry_points
from yangsuite import get_path, get_logger
from .utilities import encrypt_plaintext

log = get_logger(__name__)


class YSDeviceProfileValidationError(ValueError):
    """Exception raised when attempting to create or modify a YSDeviceProfile.

    Aggregates all errors encountered in initializing each parameter,
    similar to a Django Form.errors attribute.
    """

    def __init__(self, errors, *args):
        self.errors = errors
        super(YSDeviceProfileValidationError, self).__init__(errors, *args)


class YSDeviceProfile(object):
    """Representation of a targeted device and properties related to its usage.

    Per-protocol properties are defined by protocol-specific plugins, accessed
    as instance property ``<instance>.<protocol>``. If data is provided for
    an undefined plugin, the raw data will be accessible as
    ``<instance>.extra_data[<protocol>]``. :mod:`ysdevices.plugin` provides the
    abstract class :class:`~ysdevices.plugin.YSDeviceProtocolPlugin` and a
    "base functionality" plugin, :class:`~ysdevices.plugin.BasePlugin`,
    while all other plugins are optional.

    Properties are individually readable by name, and the entire profile
    can be converted back to a data dictionary by calling :meth:`dict`.
    Changes can be validated and applied by calling :meth:`update`.

    Examples::

      >>> data = {'base': {'profile_name': 'n9k-110',
      ... 'description': '', 'address': '10.122.84.110',
      ... 'username': 'admin', 'password': 'foo', 'timeout': '30'},
      ... 'mystery': {'port': 8080}}
      >>> profile = YSDeviceProfile(data=data)
      >>> profile.base.profile_name
      'n9k-110'
      >>> profile.base.timeout
      30
      >>> profile.extra_data
      {'mystery': {'port': 8080}}
      >>> str(profile)
      'Device profile "n9k-110"'
      >>> import pprint
      >>> pprint.pprint(profile.base.dict())  # doctest: +ELLIPSIS
      {'address': '10.122.84.110',
       'certificate': '',
       'clientcert': '',
       'clientkey': '',
       'description': '',
       'encrypted_password': ...
       'profile_name': 'n9k-110',
       'servercert': '',
       'serverkey': '',
       'timeout': 30,
       'username': 'admin',
       'variables': {}}
      >>> pprint.pprint(profile.dict())  # doctest: +ELLIPSIS
      {'base': {'address': '10.122.84.110',
                'certificate': '',
                'clientcert': '',
                'clientkey': '',
                'description': '',
                'encrypted_password': ...
                'profile_name': 'n9k-110',
                'servercert': '',
                'serverkey': '',
                'timeout': 30,
                'username': 'admin',
                'variables': {}},
       'mystery': {'port': 8080},
       'netconf': {'address': '',
                   'device_variant': 'default',
                   'enabled': False,
                   'encrypted_password': ...
                   'ignore_keys': False,
                   'port': 830,
                   'timeout': '',
                   'username': ''},
       'ssh': {'address': '',
               'delay_factor': 1.0,
               'device_variant': 'generic_termserver',
               'enabled': False,
               'encrypted_password': ...
               'port': 22,
               'secure': False,
               'timeout': '',
               'username': ''}}
      >>> profile.update({'base': {'profile_name': ''}})
      ... # doctest: +NORMALIZE_WHITESPACE
      ... # doctest: +IGNORE_EXCEPTION_DETAIL
      Traceback (most recent call last):
        ...
      YSDeviceProfileValidationError:
      {'base': {'profile_name': 'This is a required field'}}
      >>> profile2 = YSDeviceProfile(data=profile.dict())
      >>> pprint.pprint(profile2.dict())  # doctest: +ELLIPSIS
      {'base': {'address': '10.122.84.110',
                'certificate': '',
                'clientcert': '',
                'clientkey': '',
                'description': '',
                'encrypted_password': ...
                'profile_name': 'n9k-110',
                'servercert': '',
                'serverkey': '',
                'timeout': 30,
                'username': 'admin',
                'variables': {}},
       'mystery': {'port': 8080},
       'netconf': {'address': '',
                   'device_variant': 'default',
                   'enabled': False,
                   'encrypted_password': ...
                   'ignore_keys': False,
                   'port': 830,
                   'timeout': '',
                   'username': ''},
       'ssh': {'address': '',
               'delay_factor': 1.0,
               'device_variant': 'generic_termserver',
               'enabled': False,
               'encrypted_password': ...
               'port': 22,
               'secure': False,
               'timeout': '',
               'username': ''}}
    """

    @classmethod
    def list(cls, require_feature=None):
        """Get the sorted list of devices in the given directory.

        1) TODO: This should take a user or context as an optional parameter,
           and filter to only include the devices available to said user
           if given.

        Args:
          require_feature (str): If specified, only list profiles that support
            the given feature, such as "netconf".

        Returns:
          list: of dicts ``{name: name, key: key_slug, description: desc}``.
        """
        path = get_path('devices_dir')
        dev_list = []
        for f in os.listdir(path):
            (root, ext) = os.path.splitext(f)
            if ext == ".devprofile":
                try:
                    with open(os.path.join(path, f), 'r') as fp:
                        data = json.load(fp)
                    name = data['base']['profile_name']
                    if require_feature and require_feature not in data:
                        log.debug("Skipping %s; it doesn't support %s",
                                  name, require_feature)
                        continue
                    description = data['base'].get('description', '')
                    dev_list.append({'name': name, 'key': root,
                                     'description': description})
                except Exception as exc:
                    log.error(exc)
                    log.debug(traceback.format_exc())
                    dev_list.append({'name': root, 'key': root,
                                     'description': '(an error occurred while '
                                     'reading this profile)'})
            elif ext == ".xml":  # Legacy format
                tree = ET.parse(os.path.join(path, f))
                description = tree.getroot().find('desc').text
                dev_list.append({'name': root, 'key': root,
                                 'description': description})
        dev_list.sort(key=lambda x: x['name'])
        log.debug("Device profile list (filter: %s): %s",
                  require_feature, dev_list)
        return dev_list

    @classmethod
    def get(cls, name):
        """Load the given profile if it exists.

        Args:
          name (str): Device profile name or slug
        Returns:
          YSDeviceProfile
        """
        profile = get_path('device', device=name)
        legacy_profile = os.path.join(get_path('devices_dir'), name + '.xml')
        if not os.path.exists(profile) and os.path.exists(legacy_profile):
            return cls.from_xml(legacy_profile)
        return cls.from_file(profile)

    @classmethod
    def from_file(cls, file_path):
        """Open the given JSON file and read it into a YSDeviceProfile."""
        if not os.path.exists(file_path):
            raise OSError(errno.ENOENT, os.strerror(errno.ENOENT), file_path)
        with open(file_path, 'r') as fp:
            data = json.load(fp)
            if 'devicekey' in data['base']:
                data['base']['clientcert'] = data['base'].pop('devicekey')
        return cls(data)

    @classmethod
    def from_xml(cls, file_path):
        """Open the given legacy XML file and read into a YSDeviceProfile."""
        if not os.path.exists(file_path):
            raise OSError(errno.ENOENT, os.strerror(errno.ENOENT), file_path)

        tree = ET.parse(file_path)
        device_profile = tree.getroot()

        def parse_bool_str(string):
            """XML lets a boolean be 'true', 'false', '0', or '1'.

            Furthermore, Jinja2 represents a python bool as 'True' or 'False'
            when writing XML. Sigh.

            Args:
              string (str): XML value string to parse
            Returns:
              bool: True or False
            """
            if string == 'true' or string == 'True' or string == '1':
                return True
            elif string == 'false' or string == 'False' or string == '0':
                return False
            log.warning("Unexpected truth value '%s'", string)
            return False

        data = OrderedDict()
        data['base'] = OrderedDict()

        profile = device_profile.find("profile")
        data['base']['profile_name'] = profile.get('name')
        data['base']['description'] = device_profile.find('desc').text or ""

        device_info = device_profile.find("device-info")
        data['base']['address'] = device_info.find('address').text or ""
        data['base']['username'] = device_info.find('username').text or ""
        data['base']['timeout'] = 30  # not defined in XML profile, use default
        encpwd = device_info.find('encrypted_password')
        if encpwd is not None:
            data['base']['encrypted_password'] = encpwd.text or ""
        else:
            pwd = device_info.find('password')
            data['base']['encrypted_password'] = encrypt_plaintext(
                pwd.text or "", data['base']['username'])

        netconf = device_profile.find("netconf")
        data['netconf'] = OrderedDict()
        data['netconf']['enabled'] = parse_bool_str(netconf.get('enabled'))
        data['netconf']['device_variant'] = (
            device_info.find('platform').text or "")
        data['netconf']['port'] = int(netconf.find('port').text) or ""
        if device_info.find('ignore_keys') is not None:
            data['netconf']['ignore_keys'] = parse_bool_str(
                device_info.find('ignore_keys').text)
        data['netconf']['address'] = netconf.find('address').text or ""
        data['netconf']['username'] = netconf.find('username').text or ""
        encpwd = netconf.find('encrypted_password')
        if encpwd is not None:
            data['netconf']['encrypted_password'] = encpwd.text or ""
        else:
            pwd = netconf.find('password')
            data['netconf']['encrypted_password'] = encrypt_plaintext(
                pwd.text or "", data['netconf']['username'])

        return cls(data)

    @classmethod
    def delete(cls, name, user=''):
        """Delete the given profile.

        Args:
          name (str): Device name
        Returns:
          tuple: (bool success/failure, str message)
        """
        profile = get_path('device', device=name)
        legacy_profile = os.path.join(get_path('devices_dir'), name + '.xml')
        if os.path.isfile(profile):
            cert_removed = ''
            devprofile = cls.from_file(profile)
            certificate = devprofile.dict().get('certificate', '')
            clientcert = devprofile.dict().get('clientcert', '')
            clientkey = devprofile.dict().get('clientkey', '')
            servercert = devprofile.dict().get('servercert', '')
            serverkey = devprofile.dict().get('serverkey', '')
            if certificate or servercert or serverkey and user:
                user_device_path = get_path(
                    'user_devices_dir', device=name, user=user
                )
                if os.path.isfile(os.path.join(
                                      user_device_path, name, certificate)):
                    cert_removed += '\n {0} "{1}" deleted\n'.format(
                        'Certificate Authority ',
                        certificate
                    )
                    os.remove(
                        os.path.join(user_device_path, name, certificate))
                if os.path.isfile(os.path.join(
                                      user_device_path, name, clientcert)):
                    cert_removed += '\n Certificate "{0} deleted\n" '.format(
                        clientcert
                    )
                    os.remove(
                        os.path.join(user_device_path, name, clientcert))
                if os.path.isfile(os.path.join(
                                      user_device_path, name, clientkey)):
                    cert_removed += '\n Client Key "{0} deleted\n" '.format(
                        clientkey
                    )
                    os.remove(
                        os.path.join(user_device_path, name, clientkey))
                if os.path.isfile(os.path.join(
                                      user_device_path, name, servercert)):
                    cert_removed += '\n {0} "{1} deleted\n" '.format(
                        'Server Certificate',
                        servercert
                    )
                    os.remove(
                        os.path.join(user_device_path, name, servercert))
                if os.path.isfile(os.path.join(
                                      user_device_path, name, serverkey)):
                    cert_removed += '\n Server Key "{0}" deleted\n'.format(
                        serverkey
                    )
                    os.remove(
                        os.path.join(user_device_path, name, serverkey))
            os.remove(profile)
            return (True, 'Profile "{0}" deleted{1}'.format(
                name, cert_removed)
            )
        elif os.path.isfile(legacy_profile):
            os.remove(legacy_profile)
            return (True, 'Profile "{0}" deleted'.format(name))
        else:
            return (False, 'No such profile "{0}" found'.format(name))

    def write(self):
        """Save this profile for later retrieval.

        Returns:
          tuple: (bool success/failure, str message)
        """
        if not self.base or not self.base.profile_name:
            return (False, "Profile has no defined name")
        profile = get_path('device', device=self.base.profile_name)
        with open(profile, 'w') as fp:
            json.dump(self.dict(), fp, indent=2)
        legacy_profile = os.path.join(get_path('devices_dir'),
                                      self.base.profile_name + '.xml')
        if os.path.exists(legacy_profile):
            log.info("Deleting legacy profile file %s", legacy_profile)
            os.remove(legacy_profile)
        return (True, 'Profile "{0}" saved'.format(self.base.profile_name))

    _plugins = None

    def __init__(self, data=None):
        """Instantiate a YSDeviceProfile with the given data dictionary."""
        if not data:
            data = {}

        self.extra_data = {}

        for key, plugin in self.plugins.items():
            setattr(self, key, self.plugins[key](self))
        errors = self.update(data)
        if errors:
            raise YSDeviceProfileValidationError(errors)

    def __str__(self):
        return 'Device profile "{0}"'.format(self.base.profile_name)

    @property
    def plugins(self):
        """Dictionary of known plugin classes."""
        return self.discover_plugins()

    @classmethod
    def discover_plugins(cls):
        """Dynamically populate the :attr:`plugins` dictionary."""
        if not cls._plugins:
            cls._plugins = {}
            for entry_point in iter_entry_points(group='ysdevices.plugins'):
                try:
                    plugin = entry_point.load()
                    cls._plugins[entry_point.name] = plugin
                except Exception as exc:
                    log.error("Error in loading device plugin %s: %s",
                              entry_point.name, exc)
        return cls._plugins

    def dict(self):
        """Dictionary representation of this profile, suitable for saving.

        Note this includes the encrypted form of passwords, not the plaintext.

        Returns:
          dict: ``{'base': { base data }, 'netconf': { netconf data }, etc.}``
        """
        data = {}

        # Add in dict representations of each plugin's data
        for key in sorted(self.plugins.keys()):
            if not hasattr(self, key):
                continue
            data[key] = getattr(self, key).dict()

        # Add back in any pre-existing opaque data we don't understand.
        data.update(self.extra_data)

        return data

    def update(self, data):
        """Update this profile's data with the given extra data.

        Raises:
          YSDeviceProfileValidationError
        """
        errors = {}
        for key, values_dict in data.items():
            if key in self.plugins:
                errors[key] = getattr(self, key).update(values_dict)
            else:
                # Unknown data, probably from a no-longer-installed plugin.
                # Preserve it in case the plugin is later re-installed.
                if key not in self.extra_data:
                    self.extra_data[key] = {}
                self.extra_data[key].update(values_dict)

        if any(error for error in errors.values()):
            raise YSDeviceProfileValidationError(errors)

    def upload(self, device_key, file_info):
        """Save file associated to this device.

        Args:
          file_info (dict): Info needed to save file
        """
        if file_info.get('user'):
            device_path = get_path('user_devices_dir',
                                   user=file_info.get('user'))
        else:
            device_path = get_path('devices_dir')

        filename = file_info.get('file_name', '')
        replace = file_info.get('file_replace', '')
        data = file_info.get('file_data', '')

        if not filename:
            raise YSDeviceProfileValidationError("No filename for upload")
        if not data:
            raise YSDeviceProfileValidationError(
                "{0} is an empty file".format(filename)
            )

        if filename and replace:
            if os.path.isfile(os.path.join(device_path,
                                           device_key,
                                           replace)):
                log.info('Certificate "{0}" replaced with "{1}"'.format(
                    replace,
                    filename
                ))
                os.remove(os.path.join(device_path,
                                       device_key,
                                       replace))

        if filename:
            if not os.path.isdir(os.path.join(device_path, device_key)):
                os.makedirs(os.path.join(device_path, device_key))
            with open(os.path.join(device_path,
                                   device_key,
                                   filename), 'wb') as fd:
                fd.write(data.encode('utf-8'))

    @classmethod
    def data_format(cls):
        """Dict representation of possible profile data and its constraints.

        Returns:
          OrderedDict: of form::

            {
              'base': {
                label: 'Basic info',
                data: {
                  'profile_name': {
                    type: 'string',
                    required: True,
                    ...
                  },
                  'address': {
                    type: 'string',
                    required: True,
                    ...
                  },
                  'username': { ... },
                  ...
                }
              },
              'netconf': {
                label: 'NETCONF',
                data: { ... }
              },
              ...
            }

        .. seealso:: :meth:`YSDeviceProtocolPlugin.data_format`
        """
        info = OrderedDict()
        for key, plugin in sorted(cls.discover_plugins().items()):
            info[key] = {
                'label': plugin.label,
                'data': plugin.data_format(),
            }
        return info

    def check_reachability(self):
        """Check whether the described device is currently accessible.

        Returns:
          dict: Dictionary of {<method>: {status: <boolean>, reason: <string>}}
          entries, plus the key 'status': <boolean> for the aggregate result.
        """
        result = {}

        for key, plugin in sorted(self.plugins.items()):
            if (not hasattr(self, key)) or not getattr(getattr(self, key),
                                                       'enabled', True):
                continue
            try:
                label, status, reason = plugin.check_reachability(self)
            except NotImplementedError:
                log.debug('No reachability check for "%s"', key)
                continue
            result[key] = {'label': label, 'status': status}
            if reason:
                result[key]['reason'] = reason

        result['status'] = all(method['status'] for method in result.values())

        log.debug("Result: %s", result)
        return result


if __name__ == '__main__':   # pragma: no cover
    import doctest
    doctest.testmod(verbose=True, optionflags=doctest.ELLIPSIS)
