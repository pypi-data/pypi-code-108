# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
import traceback
from collections import OrderedDict
from paramiko.ssh_exception import BadHostKeyException
import subprocess
import os
import paramiko
from ncclient import manager
from ncclient.operations import RaiseMode
from operator import itemgetter
from yangsuite import get_logger
from ysdevices import YSDeviceProtocolPlugin
from ysdevices.utilities import encrypt_plaintext, decrypt_ciphertext
from .nconf import (
    ncclient_supported_platforms,
    ncclient_manager_kwargs,
    SessionKey,
    NetconfSession
)
from .rpcbuilder import YSNetconfRPCBuilder

log = get_logger(__name__)


class NetconfPlugin(YSDeviceProtocolPlugin):
    """NETCONF protocol extensions of YSDeviceProfile."""

    label = "NETCONF"
    key = "netconf"

    @classmethod
    def netconf_platform_options(cls):
        """Get tuples of (valid_platform, human-readable string)"""
        PLATFORM_LABELS = {
            'alu': "Alcatel-Lucent 7x50",
            'csr': "Cisco CSR",
            'default': "(Default - RFC-compliant device)",
            'h3c': "H3C",
            'hpcomware': "HP Comware",
            'huawei': 'Huawei',
            'iosxe': "Cisco IOS XE",
            'iosxr': "Cisco IOS XR",
            'junos': "Juniper Junos",
            'nexus': "Cisco Nexus (NX-OS) 5xxx/6xxx/7xxx series",
        }

        result = [(plat, PLATFORM_LABELS.get(plat, plat))
                  for plat in ncclient_supported_platforms()]
        result.append(('iosenxr', 'Cisco IOS XR (ENXR)'))
        return sorted(result, key=itemgetter(1))

    @classmethod
    def data_format(cls):
        result = OrderedDict()
        result['enabled'] = {
            'label': 'Device supports NETCONF',
            'type': 'boolean',
            'default': False,
        }
        result['device_variant'] = {
            'label': 'Device Variant',
            'type': 'enum',
            'description':
            'Value specifying platform-dependent behavior of ncclient.',
            'choices': cls.netconf_platform_options(),
            'required': True,
            'default': "default",
        }
        result['port'] = {
            'label': 'NETCONF port',
            'type': 'int',
            'description': 'Port number NETCONF listens on',
            'min': 1,
            'max': 65535,
            'default': 830,
            'required': True,
        }
        result['ignore_keys'] = {
            'label': "Skip SSH key validation for this device",
            'type': 'boolean',
            'default': False,
        }
        result['address'] = {
            'type': 'string',
            'description': 'Address or hostname to access via NETCONF',
        }
        result['username'] = {
            'type': 'string',
            'description': 'Username to access the device via NETCONF',
            'minLength': 1,
            'maxLength': 50,
        }
        result['password'] = {
            'type': 'password',
            'description': 'Password to access the device via NETCONF',
            'minLength': 1,
            'maxLength': 50,
        }
        result['timeout'] = {
            'type': 'int',
            'description': 'Timeout, in seconds, for NETCONF requests',
            'min': 0,
        }
        return result

    # Inherit the following properties from profile.base if not overridden
    address = YSDeviceProtocolPlugin.inheritable_property(
        'address',
        docstring="Address for NETCONF access, if different from base address")
    username = YSDeviceProtocolPlugin.inheritable_property(
        'username',
        docstring="NETCONF login username, if different from base username")
    password = YSDeviceProtocolPlugin.inheritable_property(
        'password',
        docstring="NETCONF login password, if different from base password")
    timeout = YSDeviceProtocolPlugin.inheritable_property(
        'timeout',
        docstring="NETCONF RPC timeout in seconds, "
        "if different from base timeout")

    def update(self, data):
        if 'password' not in data or not data['password']:
            if 'encrypted_password' in data and data['encrypted_password']:
                data['password'] = decrypt_ciphertext(
                    data['encrypted_password'],
                    (data.get('username') or self.username))
        return super(NetconfPlugin, self).update(data)

    def dict(self):
        data = super(NetconfPlugin, self).dict()
        data['encrypted_password'] = encrypt_plaintext(self._password,
                                                       self.username)
        del data['password']
        return data

    def ssh_to_device(devprofile):
        """
        To add new entry of hostkey in known_host file for unknown host.

        Args:
        devprofile: YSDeviceProfile object
        """
        ssh = paramiko.SSHClient()
        ssh.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            devprofile.base.address,
            22,
            devprofile.base.username,
            devprofile.base.password,
            look_for_keys=False)

    @classmethod
    def check_reachability(cls, devprofile):
        if devprofile.netconf.device_variant == 'iosenxr':
            try:
                key = SessionKey('testconnect', devprofile.base.profile_name)
                with NetconfSession.get(key) as ncs:
                    if ncs.connected:
                        return ('NETCONF', True, '')
            except FileNotFoundError as e:
                log.debug("NETCONF ENXR check failed to reach simulator")
                return ("NETCONF", False, 'Simulator not reachable')
            except Exception as e:
                log.debug("NETCONF ENXR check failed: %s", e)
                log.debug(traceback.format_exc())
                return ("NETCONF", False, str(e))
        try:
            try:
                cls.ssh_to_device(devprofile)
            except BadHostKeyException:
                # Delete the existing hostkey entry from known_hosts if
                # hostkey doesn't match with the server's hostkey
                subprocess.run(
                    ['ssh-keygen', '-R', devprofile.netconf.address])
                cls.ssh_to_device(devprofile)
            except Exception:
                log.debug(
                    "Device does not support password based authentication")

            with manager.connect(**ncclient_manager_kwargs(devprofile)) as m:
                # Make sure we can actually interact with the device, by
                # sending a get-config that should succeed and return nothing.
                # RFC 6241 section 6.4.2: an empty filter should achieve this.
                m.raise_mode = RaiseMode.NONE
                rpcbuilder = YSNetconfRPCBuilder()
                filter = rpcbuilder.netconf_element('filter')
                ret = m.get_config(source="running", filter=filter)

                if ret.ok:
                    return ('NETCONF', True, '')
                else:
                    if ret.error.tag == 'access-denied':
                        return ('NETCONF', False,
                                'Able to connect but operations were rejected '
                                'with "Access denied".\nDoes the configured '
                                'user account have sufficient privileges '
                                'to execute NETCONF operations?')
                    else:
                        # Generic error report
                        return ('NETCONF', False,
                                "Error in executing NETCONF get-config:\n" +
                                str(ret.error))
        except EOFError as e:
            log.debug("NETCONF check failed with EOFError")
            return('NETCONF', False, "Session terminated by device. "
                   "Check device's logs for more information.")
        except Exception as e:
            log.debug("Netconf check failed: %s", e)
            log.debug(traceback.format_exc())
            msg = str(e)
            if "Unknown host key" in msg:
                msg = ('You may need to select "Skip SSH key validation '
                       'for this device":\n' + msg)

            return ('NETCONF', False, msg)
