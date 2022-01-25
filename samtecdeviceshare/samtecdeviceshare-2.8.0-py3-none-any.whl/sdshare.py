import os
import time
import glob
import asyncio
import io
import logging
import zipfile
from typing import Optional, List
from asyncio import CancelledError, shield
from starlette.concurrency import run_in_threadpool
from . import balena
from .types import DeviceState, SDCConfiguration, WifiMode, NetworkCredentials, BALENA_PREFIX
from .aiofilelock import FileLock, LockTimeout
from .helper import is_online_async, is_on_balena, get_hostname
from .nm_utils import get_ip_addresses, setup_wifi_hotspot, setup_wifi_client
from .wiredhandler import WiredNetworkHandler

logger = logging.getLogger('sdc.core')

class SamtecDeviceShare:

    def __init__(self):
        self.config = SDCConfiguration.load_default()
        self.update_lock = FileLock(self.config.app_lock_path)
        self.wired_network_handlers: List[WiredNetworkHandler] = []
        self.update_check_in_progress: bool = False

    async def open(self) -> None:
        try:
            await self.enable_update_lock()
        except Exception as err:
            logger.exception('Failed acquiring lock w/ error: %s', err)
        try:
            await self.launch_default_wifi()
        except Exception as err:
            logger.exception('Failed launching WiFi w/ error: %s', err)

        await self.register_wired_networks()

    async def close(self) -> None:
        pass

    async def update(self) -> None:
        try:
            await self.update_wired_networks()
        except CancelledError:
            logger.warning('Background task(s) cancelled')
        except Exception as err:
            logger.exception('Failed performing update routine w/ error: %s', err)

    async def register_wired_networks(self) -> None:
        self.wired_network_handlers = []
        for wired_config in self.config.wired_networks:
            self.wired_network_handlers.append(WiredNetworkHandler(
                config=wired_config
            ))

    async def update_wired_networks(self) -> None:
        try:
            await asyncio.gather(*[run_in_threadpool(func=handler.update) for handler in self.wired_network_handlers])
        except (CancelledError, ConnectionResetError) as err:
            logger.exception('Failed updating network due to cancelled or reset error: %s', err)
            raise err
        except Exception as err:
            logger.exception('Failed updating network w/ error: %s', err)
            raise err

    async def get_device_state(self) -> DeviceState:
        if is_on_balena():
            device_state, app_state, internet_access = await asyncio.gather(
                balena.get_device_state(), balena.get_application_state(), is_online_async()
            )
            return DeviceState(
                status=device_state.status,
                app_commit=app_state.commit,
                app_version=self.config.app_version,
                app_download_progress=app_state.update_download_progress,
                app_update_available=app_state.update_available,
                app_downloading=app_state.update_downloading,
                app_updating=app_state.update_installing,
                app_update_check=self.update_check_in_progress,
                ip_address=device_state.ip_address,
                device_UUID=os.getenv(f'{BALENA_PREFIX}_DEVICE_UUID', '0000000'),
                device_name=os.getenv(f'{BALENA_PREFIX}_DEVICE_NAME_AT_INIT', ''),
                internet_access=internet_access,
                ap_mode='10.42.0.1' in device_state.ip_address
            )
        internet_access = await is_online_async()
        ip_addresses = ','.join(get_ip_addresses())
        return DeviceState(
            status='IDLE',
            app_commit='',
            app_version=self.config.app_version,
            app_update_check=self.update_check_in_progress,
            ip_adress=ip_addresses,
            device_UUID=get_hostname(),
            device_name=get_hostname(),
            internet_access=internet_access,
            ap_mode='10.42.0.1' in ip_addresses
        )

    def get_default_wifi(self) -> Optional[NetworkCredentials]:
        return next((n for n in self.config.wireless_networks if n.default), None)

    def set_default_wifi(self, wifi: NetworkCredentials):
        self.config.wireless_networks = list(filter(lambda w: not w.default, self.config.wireless_networks))
        self.config.wireless_networks.append(wifi)

    async def launch_default_wifi(self) -> None:
        credentials = self.get_default_wifi()
        if credentials is None or credentials.mode == WifiMode.DISABLED:
            return
        # NOTE: This is a hack that allows us to dynamically set the ssid when default hotspot
        if credentials.mode == WifiMode.HOTSPOT and credentials.ssid == '':
            device_state = await self.get_device_state()
            credentials.ssid = f'SDC-{device_state.device_UUID[:7]}'
        await self.launch_wifi(credentials=credentials)

    async def launch_wifi(self, credentials: Optional[NetworkCredentials] = None):
        if credentials.mode == WifiMode.DISABLED:
            return
        if credentials.mode == WifiMode.CLIENT:
            await shield(setup_wifi_client(credentials=credentials, action='UP', timeout=20))
        elif credentials.mode == WifiMode.HOTSPOT:
            if not credentials.ssid:
                device_state = await self.get_device_state()
                credentials.ssid = f'SDC-{device_state.device_UUID[:7]}'
            await shield(setup_wifi_hotspot(credentials=credentials, action='UP', timeout=20))
        if credentials.default:
            self.set_default_wifi(credentials)

    def get_log_zip_data_sync(self) -> bytes:
        bf = io.BytesIO()
        zip_fp = zipfile.ZipFile(bf, 'w', zipfile.ZIP_DEFLATED)  # pylint: disable=consider-using-with
        for log_file in glob.glob(os.path.join(self.config.app_log_path, '*.log')):
            zip_fp.write(log_file, f'app_logs/{os.path.basename(log_file)}')
        zip_fp.close()
        bf.seek(0)
        return bf.read()

    async def get_log_zip_data(self):
        return await run_in_threadpool(self.get_log_zip_data_sync)

    async def blink_device(self):
        if is_on_balena():
            return await balena.blink()
        return True

    async def enable_update_lock(self, timeout: int = 6):
        if self.update_lock.is_locked:
            return
        try:
            await self.update_lock.acquire(timeout=timeout, poll_intervall=0.1)
        except LockTimeout:
            logger.warning('Failed locking update lock w/ timeout.')
        logger.info('Update lock successfully enabled.')

    async def remove_update_lock(self, timeout: int = 6):
        if not self.update_lock.is_locked:
            return
        try:
            await self.update_lock.release()
        except LockTimeout:
            logger.warning('Forcefully breaking update lock file.')
            await self.update_lock.release(force=True)
        logger.info('Update lock successfully removed.')

    async def restart_device(self, force: bool = False):
        if not is_on_balena():
            return
        return await balena.reboot(force=force)

    async def update_application(self) -> bool:
        if not is_on_balena():
            return True
        await balena.update_check(force=False)
        app_state = await balena.get_application_state()
        if app_state.update_installing:
            return True
        if app_state.update_downloading:
            logger.warning('App update still downloading')
            return False
        if not app_state.update_available:
            logger.warning('No app update available')
            return False
        # Remove update lock file
        await self.remove_update_lock()
        await balena.update_check(force=True)
        return True

    async def perform_ota_update_check(self, credentials: Optional[NetworkCredentials], timeout=1800) -> None:
        if not is_on_balena():
            return

        if self.update_check_in_progress:
            return
        try:
            self.update_check_in_progress = True

            # Already online so just check
            if await is_online_async():
                await shield(balena.update_check(force=False))
                await asyncio.sleep(1)
                return

            # Must provide wifi credentials
            if credentials is None:
                raise Exception('No internet access and no Wi-Fi credentials provided.')
            await self.launch_wifi(credentials=credentials)
            # Wait 20 seconds for internet access
            num_attempts = 0
            online = False
            while num_attempts < 20 and not online:
                await asyncio.sleep(1)
                online = await is_online_async()
                num_attempts += 1
            if not online:
                raise Exception('Timeout reached trying to contact server.')

            # Trigger supervisor to check for an update
            logger.info('OTA Update Check: Started')
            await balena.update_check(force=False)
            await asyncio.sleep(20)
            tic = time.time()
            app_state = await balena.get_application_state()
            while True:
                logger.info('OTA Update Check: Waiting for potential app download to complete')
                app_state = await balena.get_application_state()
                if not app_state.update_downloading and (app_state.update_installing or app_state.update_available):
                    break
                if time.time() - tic > timeout:
                    break
                await asyncio.sleep(5)
            logger.info('OTA Update Check: Finished')
            return
        except Exception as err:
            logger.exception('OTA Update Check: Failed due to error: %s', err)
            raise err
        finally:
            await self.launch_default_wifi()
            self.update_check_in_progress = False
