import os
import re
import time
import uuid
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Pattern
from .types import NetworkCredentials

logger = logging.getLogger('sdc.helper')

try:
    import NetworkManager as nm  # type: ignore
    from dbus.mainloop.glib import DBusGMainLoop  # type: ignore
    DBusGMainLoop(set_as_default=True)
except Exception:
    if os.getenv('PYTHON_ENV') == 'development':
        logger.warning('Failed to load NetworkManager. Using emulator in development.')
    else:
        logger.warning('Failed to load NetworkManager module.')
    from .emulation import networkmanager as nm

def valid_wpa_passphrase(passphrase: Any) -> bool:
    if passphrase is None:
        return True
    if not isinstance(passphrase, str):
        return False
    return len(passphrase) >= 8 and len(passphrase) <= 63

def get_nm_connections() -> List[nm.Connection]:
    return nm.Settings.ListConnections()

def add_nm_connection(settings):
    return nm.Settings.AddConnection(settings)

def get_nm_devices():
    return nm.NetworkManager.GetDevices()

def get_nm_active_connections():
    return nm.NetworkManager.ActiveConnections

def activate_nm_connection(conn, dev, prefix: str) -> nm.ActiveConnection:
    return nm.NetworkManager.ActivateConnection(conn, dev, "/")

def get_ip_addresses() -> List[str]:
    ip_addesses: List[str] = []
    for conn in get_nm_active_connections():
        if conn.Type not in ['802-11-wireless', '802-3-ethernet']:
            continue
        for addr in conn.Ip4Config.AddressData:
            ip_addesses.append(addr['address'])
    return ip_addesses


def get_nm_device_by_type(dtype: int) -> List[nm.Device]:
    return list(filter(lambda d: d.DeviceType == dtype, get_nm_devices()))

def get_nm_device_by_iface(iface: Union[Pattern, str], dtype: Optional[int] = None) -> Optional[nm.Device]:
    if isinstance(iface, str):
        try:
            dev = nm.NetworkManager.GetDeviceByIpIface(iface)
        except Exception:
            return None

    for dev in get_nm_devices():
        if dtype is not None and dev.DeviceType != dtype:
            continue
        if isinstance(iface, re.Pattern) and iface.fullmatch(dev.Interface):
            return dev
        if iface is None:
            return dev
    return None

def get_wired_device(iface: Optional[Union[Pattern,str]] = None):
    for dev in get_nm_devices():
        if dev.DeviceType != nm.NM_DEVICE_TYPE_ETHERNET:
            continue
        if iface is None:
            return dev
        if isinstance(iface, re.Pattern) and iface.fullmatch(dev.Interface):
            return dev
        if isinstance(iface, str) and iface == dev.Interface:
            return dev
    return None


def get_nm_connection_with_id(conn_id: str):
    for conn in get_nm_connections():
        settings = conn.GetSettings()
        if settings['connection']['id'] == conn_id:
            return conn
    return None

def create_wifi_hotspot_connection(ssid: str, passphrase: Optional[str] = None, conn_uuid: Optional[str] = None):
    if not isinstance(ssid, str):
        raise TypeError('Invalid wifi credentials: SSID missing or incorrect.')
    if not valid_wpa_passphrase(passphrase):
        raise TypeError('Invalid wifi credentials: Passphrase incorrect.')
    if passphrase:
        s_wsec = {'key-mgmt': 'wpa-psk', 'proto': ['rsn'], 'psk': passphrase}
    else:
        s_wsec = {'key-mgmt': 'none', 'auth-alg': 'open'}
    conn = {
        'connection': dict(type='802-11-wireless', uuid=conn_uuid or str(uuid.uuid4()), id=ssid),
        '802-11-wireless': dict(ssid=ssid.encode("utf-8"), mode='ap', band='bg', channel=1),
        '802-11-wireless-security': s_wsec,
        'ipv4': dict(method='shared'),
        'ipv6': dict(method='ignore')
    }
    return conn

def create_wifi_client_connection(ssid: str, passphrase: Optional[str] = None, identity: Optional[str] = None, conn_uuid: Optional[str] = None):
    if not isinstance(ssid, str):
        raise TypeError('Invalid wifi credentials: SSID missing or incorrect.')
    if passphrase and not valid_wpa_passphrase(passphrase):
        raise TypeError('Invalid wifi credentials: Passphrase incorrect.')
    # WPA2 Enterprise
    if isinstance(identity, str) and len(identity) > 1:
        s_wsec = {'key-mgmt': 'wpa-eap', 'auth-alg': 'open'}
        s_eap = {'eap': 'peap', 'identity': identity, 'phase2-auth': 'mschapv2', 'password': passphrase}
    # WPA2 Regular
    elif passphrase:
        s_wsec = {'key-mgmt': 'wpa-psk', 'psk': passphrase, 'auth-alg': 'open'}
        s_eap = None
    # WEP open
    else:
        s_wsec = {'key-mgmt': 'none', 'auth-alg': 'open'}
        s_eap = None

    conn = {
        'connection': dict(type='802-11-wireless', uuid=conn_uuid or str(uuid.uuid4()), id=ssid),
        '802-11-wireless': dict(ssid=ssid.encode("utf-8"), security='802-11-wireless-security'),
        '802-11-wireless-security': s_wsec,
        'ipv4': {'method': 'auto'},
        'ipv6': {'method': 'auto'}
    }
    if s_eap:
        conn['802-1x'] = s_eap
    return conn

async def setup_wifi_connection(conn_settings: Dict[str, Any], iface: Optional[Union[Pattern, str]] = None, action=None, timeout: float = 10):
    try:
        # Get existing connection if exists or create new one
        conn = get_nm_connection_with_id(conn_settings['connection']['id'])
        if conn:
            conn_settings['connection']['uuid'] = conn.uuid
            conn.Update(conn_settings)
            conn.Save()
        else:
            conn = add_nm_connection(conn_settings)

        # If no action, return
        if action is None:
            return

        dev = get_nm_device_by_iface(iface, dtype=nm.NM_DEVICE_TYPE_WIFI)
        if dev is None:
            return

        # Now start or stop the connection on the requested device
        if str(action).upper() == 'UP':
            act_conn = activate_nm_connection(conn, dev, "/")
            time.sleep(0.5)
            # Wait for the connection to start up
            start = time.time()
            while time.time() < start + int(timeout):
                if act_conn.State == nm.NM_ACTIVE_CONNECTION_STATE_ACTIVATED:
                    return
                await asyncio.sleep(1)
            raise Exception('Failed to start wifi connection due to timeout')
        if str(action).upper() == 'DOWN':
            dev.Disconnect()
            return
        raise Exception('Unsupported action')
    except Exception as err:
        logger.exception(err)
        raise

async def setup_wifi_hotspot(credentials: NetworkCredentials, conn_uuid: Optional[uuid.UUID] = None, action: Optional[str] = None, timeout: float = 10):
    conn_settings = create_wifi_hotspot_connection(ssid=credentials.ssid, passphrase=credentials.passphrase, conn_uuid=conn_uuid)
    await setup_wifi_connection(conn_settings=conn_settings, iface=credentials.iface_regex or credentials.iface, action=action, timeout=timeout)

async def setup_wifi_client(credentials: NetworkCredentials, conn_uuid=None, action=None, timeout=10):
    conn_settings = create_wifi_client_connection(ssid=credentials.ssid, passphrase=credentials.passphrase, identity=credentials.identity, conn_uuid=conn_uuid)
    await setup_wifi_connection(conn_settings=conn_settings, iface=credentials.iface_regex or credentials.iface, action=action, timeout=timeout)

def get_active_wifi_connection(iface: Optional[Union[Pattern,str]] = None, con_name: Optional[str] = None):
    for act in nm.NetworkManager.ActiveConnections:
        try:
            # Skip if connection isnt 802-11-wireless or no devices attached
            if act.Type != '802-11-wireless' or not act.Devices:
                continue

            if isinstance(iface, re.Pattern):
                found_dev = next((d for d in act.Devices if iface.fullmatch(d.Interface)), None)
                if not found_dev:
                    continue
                return act.Connection, found_dev

            if isinstance(iface, str):
                found_dev = next((d for d in act.Devices if d.Interface == iface), None)
                if not found_dev:
                    continue
                return act.Connection, found_dev
            if con_name:
                if con_name != act.Id:
                    continue
                return act.Connection, act.Devices[0]
            # If no input, pick first dev
            return act.Connection, act.Devices[0]
        except Exception as err:
            logger.warning('Skipping active connection. Failed parsing with error: %s', err)

    return None, None
