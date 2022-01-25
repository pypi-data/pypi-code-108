""" Wired Network Handler """
#!/usr/bin/env python
import re
import os
import copy
import time
import logging
from typing import Optional, Pattern, Union
from .types import CamelModel, WiredConnectionMethod, WiredConnectionState, WiredNetworkConfig
from .nm_utils import nm, get_nm_device_by_iface, get_nm_active_connections, activate_nm_connection

logger = logging.getLogger('sdc.wirednetwork')

class WiredConnectionFsm(CamelModel):
    dev_iface: str = ''
    dev_state: int = nm.NM_DEVICE_STATE_UNAVAILABLE
    con_name: Optional[str] = None
    con_state: str = WiredConnectionState.DISCONNECTED
    con_method: WiredConnectionMethod = WiredConnectionMethod.disabled
    con_counter: int = 0
    con_needs_init: bool = True

def get_active_wired_connection(iface: Optional[Union[Pattern,str]] = None, con_name: Optional[str] = None):
    for act in get_nm_active_connections():
        try:
            # Skip if connection isnt 802-3-ethernet or no devices attached
            if act.Type != '802-3-ethernet' or not act.Devices:
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

def update_active_conn_ipv4_method(con=None, dev=None, method: WiredConnectionMethod = WiredConnectionMethod.auto):
    success = False
    try:
        settings = con.GetSettings()
        # Add IPv4 setting if it doesn't yet exist
        if 'ipv4' not in settings:
            settings['ipv4'] = {}
        # Set the method and change properties
        settings['ipv4']['method'] = method.value
        settings['ipv4']['addresses'] = []
        con.Update(settings)
        con.Save()
        activate_nm_connection(con, dev, "/")
        success = True
    except Exception:
        success = False
    return success

class WiredNetworkHandler:
    NM_CONNECTED_STATES = [nm.NM_DEVICE_STATE_ACTIVATED]
    NM_CONNECTING_STATES = [
        nm.NM_DEVICE_STATE_IP_CHECK,
        nm.NM_DEVICE_STATE_IP_CONFIG
    ]
    NM_DISCONNECTED_STATES = [
        nm.NM_DEVICE_STATE_FAILED,
        nm.NM_DEVICE_STATE_UNAVAILABLE,
        nm.NM_DEVICE_STATE_UNMANAGED
    ]

    def __init__(self, config: WiredNetworkConfig):
        self.config = config
        self.fsm = WiredConnectionFsm(con_method=self.config.method)

    def update(self):

        if os.getenv('PYTHON_ENV') == 'development':
            # logger.debug('WIRED %s updating...', self.config.iface_regex or self.config.iface)
            return

        next_fsm = copy.deepcopy(self.fsm)

        # Get active connection and device
        con, dev = get_active_wired_connection(iface=self.config.iface_regex or self.config.iface, con_name=self.fsm.con_name)
        if dev is None:
            dev = get_nm_device_by_iface(iface=self.config.iface_regex or self.config.iface, dtype=nm.NM_DEVICE_TYPE_ETHERNET)

        # If no conn or no device, then treat as unplugged (requires initializing)
        if dev is None or con is None:
            logger.debug('No ethernet device found for %s. Sleeping...', self.config.iface_regex or self.config.iface)
            next_fsm.dev_iface = dev.Interface if dev else self.config.iface
            next_fsm.dev_state = dev.State if dev else nm.NM_DEVICE_STATE_UNAVAILABLE
            next_fsm.con_name = None
            next_fsm.con_method = self.config.method
            next_fsm.con_counter = 0
            next_fsm.con_needs_init = True
            self.fsm = next_fsm
            return # Nothing to do

        # Both connection and device exist, update state
        con_settings = con.GetSettings()
        con_method = WiredConnectionMethod(con_settings.get('ipv4', {}).get('method', self.config.method.value))

        # If method doesnt match, NM is using file config which is different than specified.
        # Need to change method and re-initialize process
        if con_method not in (self.config.method, self.config.fallback):
            logger.warning('Wired device connection method doesnt match. Reinitialzing...')
            con_method = self.config.method
            next_fsm.con_counter = 0
            next_fsm.con_needs_init = True

        next_fsm.con_name = con_settings.get('connection', {}).get('id', '')
        next_fsm.dev_iface = dev.Interface
        next_fsm.dev_state = dev.State

        # CONNECTED
        if next_fsm.dev_state in WiredNetworkHandler.NM_CONNECTED_STATES:
            next_fsm.con_counter = 0
            next_fsm.con_state = WiredConnectionState.CONNECTED
            next_fsm.con_method = con_method

        # CONNECTING
        elif next_fsm.dev_state in WiredNetworkHandler.NM_CONNECTING_STATES:
            next_fsm.con_state = WiredConnectionState.CONNECTING
            # primary method timeout, go to fallback
            if con_method == self.config.method and next_fsm.con_counter >= self.config.timeout:
                logger.info('Primary method timeout- switching to fallback')
                next_fsm.con_method = self.config.fallback if self.config.fallback and self.config.fallback_timeout > 0 else self.config.method
                next_fsm.con_counter = 0
            # fallback timeout, go to primary
            elif con_method == self.config.fallback and next_fsm.con_counter >= self.config.fallback_timeout:
                logger.info('Fallback method timeout- switching back to primary')
                next_fsm.con_method = self.config.method
                next_fsm.con_counter = 0
            # Still trying to connect
            else:
                next_fsm.con_method = con_method
                next_fsm.con_counter += 1

        # DISCONNECTED
        elif next_fsm.dev_state in WiredNetworkHandler.NM_DISCONNECTED_STATES:
            next_fsm.con_counter = 0
            next_fsm.con_state = WiredConnectionState.DISCONNECTED
            next_fsm.con_method = self.config.method
        else:
            next_fsm.con_method = con_method

        if next_fsm.dev_iface != self.fsm.dev_iface:
            logger.info('Wired device iface changed to {0}'.format(next_fsm.dev_iface))
        if next_fsm.con_name != self.fsm.con_name:
            logger.info('Wired connection name changed to {0}'.format(next_fsm.con_name))
        if next_fsm.con_state != self.fsm.con_state:
            logger.info('Wired connection state changed to {0}'.format(next_fsm.con_state))

        # If have connection and want method to change or needs initialization
        if next_fsm.con_needs_init or (next_fsm.con_method != con_method):
            # IMPORTANT: On init we must start with primary method
            next_con_method = self.config.method if next_fsm.con_needs_init else next_fsm.con_method
            logger.info('Setting connection {0} to method {1}'.format(next_fsm.con_name, next_con_method))
            success = update_active_conn_ipv4_method(con, dev, next_con_method)
            # NOTE: If failed to activate, restart process
            if not success:
                next_fsm.con_needs_init = True
                logger.error('Failed setting active connection method.')
            else:
                next_fsm.con_needs_init = False
                logger.info('Successfully set active connection method.')
        self.fsm = next_fsm

def run(config: WiredNetworkConfig):
    try:
        handler = WiredNetworkHandler(config)
        while True:
            handler.update()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.warning('Process cancelled by user. Shutting down...')
    except Exception as err:
        logger.exception('Failed running w/ error: %s', err)
        raise err

if __name__ == '__main__':
    run(WiredNetworkConfig())
