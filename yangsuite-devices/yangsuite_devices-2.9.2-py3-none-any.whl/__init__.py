# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
from yangsuite.paths import register_path
from ._version import get_versions
from .devprofile import YSDeviceProfile
from .plugin import YSDeviceProtocolPlugin, SshSession

__version__ = get_versions()['version']
del get_versions

default_app_config = 'ysdevices.apps.YSDevicesConfig'

# TODO, this should probably be parented under 'user' rather than base - #58
register_path('user_devices_dir', 'devices', parent='user', autocreate=True)
register_path('devices_dir', 'devices', autocreate=True)
register_path('device', '{device}.devprofile', parent='devices_dir',
              autocreate=False, slugify=True)

__all__ = (
    'YSDeviceProfile',
    'YSDeviceProtocolPlugin',
    'SshSession',
)
