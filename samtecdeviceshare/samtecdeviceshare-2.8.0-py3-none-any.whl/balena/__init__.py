import os
import asyncio
import functools
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum
import humps
import httpx
from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module
from ..helper import env_flag

BALENA_PREFIX = 'BALENA' if os.getenv('BALENA') else 'RESIN' if os.getenv('RESIN') else 'SDC'

class CamelModel(BaseModel):
    class Config:
        alias_generator = humps.camelize
        allow_population_by_field_name = True

class BalenaEnvVars(BaseModel):
    device_type: str = os.getenv(f'{BALENA_PREFIX}_DEVICE_TYPE')
    app_id: str = os.getenv(f'{BALENA_PREFIX}_APP_ID')
    device_arch: str = os.getenv(f'{BALENA_PREFIX}_DEVICE_ARCH')
    app_lock_path: str = os.getenv(f'{BALENA_PREFIX}_APP_LOCK_PATH')
    supervisor_version: str = os.getenv(f'{BALENA_PREFIX}_SUPERVISOR_VERSION')
    host_os_version: str = os.getenv(f'{BALENA_PREFIX}_HOST_OS_VERSION')
    device_uuid: str = os.getenv(f'{BALENA_PREFIX}_DEVICE_UUID')
    device_name_at_init: str = os.getenv(f'{BALENA_PREFIX}_DEVICE_NAME_AT_INIT')
    balena: int = os.getenv(f'{BALENA_PREFIX}')
    app_name: str = os.getenv(f'{BALENA_PREFIX}_APP_NAME')

class BalenaSupervisor(CamelModel):
    version: str = os.getenv(f'{BALENA_PREFIX}_SUPERVISOR_VERSION', '0.0.0')
    address: str = os.getenv(f'{BALENA_PREFIX}_SUPERVISOR_ADDRESS', 'http://localhost:48484')
    api_key: str = os.getenv(f'{BALENA_PREFIX}_SUPERVISOR_API_KEY', '')

class BalenaStatus(str, Enum):
    Stopping = 'Stopping'
    Stopped = 'Stopped'
    Running = 'Running'
    Installing = 'Installing'
    Installed = 'Installed'
    Dead = 'Dead'
    Paused = 'paused'
    Restarting = 'restarting'
    Removing = 'removing'
    Exited = 'exited'
    Downloading = 'Downloading'
    Downloaded = 'Downloaded'
    Starting = 'Starting'
    Idle = 'Idle'


class BalenaDeviceInfo(CamelModel):
    api_port: int = 80
    commit: Optional[str] = None
    ip_address: str = ''
    mac_address: str = ''
    status: BalenaStatus = BalenaStatus.Idle
    download_progress: Optional[float] = None
    os_version: str = '0.0.0'
    supervisor_version: str = ''
    update_pending: bool = False
    update_downloaded: bool = False
    update_failed: bool = False

class BalenaServiceInfo(CamelModel):
    status: BalenaStatus = BalenaStatus.Idle
    release_id: int = 0
    download_progress: Optional[int] = None

class BalenaAppInfo(CamelModel):
    app_id: int = 0
    commit: str = ''
    services: Dict[str, BalenaServiceInfo] = Field(default_factory=dict)

    @property
    def update_downloading(self) -> bool:
        return any(s.status == BalenaStatus.Downloading for s in self.services.values())

    @property
    def update_download_progress(self) -> float:
        progress = functools.reduce(
            lambda p, s: p + ((s.download_progress or 0) if s.status == BalenaStatus.Downloading else 100),
            self.services.values(), 0
        )
        return progress / max(1, len(self.services))

    @property
    def update_available(self) -> bool:
        statuses = [s.status for s in self.services.values()]
        return BalenaStatus.Downloaded in statuses and all((s in (BalenaStatus.Downloaded, BalenaStatus.Running, BalenaStatus.Exited) for s in statuses))

    @property
    def update_installing(self) -> bool:
        return any(s.status == BalenaStatus.Installing for s in self.services.values())

class BalenaContainerStatus(CamelModel):
    status: BalenaStatus
    service_name: str
    app_id: int
    image_id: int
    service_id: int
    container_id: str
    created_at: datetime

class BalenaImageStatus(CamelModel):
    name: str
    app_id: int
    service_name: str
    image_id: int
    docker_image_id: str
    status: BalenaStatus
    download_progress: Optional[float] = None
    service_id: int
    container_id: str
    created_at: datetime

class BalenaStateStatus(CamelModel):
    status: str = 'success'
    app_state = 'applied'
    overall_download_progress: Optional[float] = None
    containers: List[BalenaContainerStatus]

class BalenaServiceContainerIds(CamelModel):
    status: str
    services: Dict[str, str]

class BalenaAppsInfo(CamelModel):
    __root__: Dict[str, BalenaAppInfo]

    def __iter__(self):
        return iter(self.__root__)

    def __getitem__(self, item):
        return self.__root__[item]

class BalenaProxyType(str, Enum):
    socks4 = 'socks4'
    socks5 = 'socks5'
    http_connect = 'http-connect'
    http_relay = 'http-relay'

class BalenaProxyConfig(CamelModel):
    type: Optional[BalenaProxyType] = None
    ip: Optional[str] = None
    port: int = None
    login: Optional[str] = None
    password: Optional[str] = None
    no_proxy: Optional[List[str]] = None

class BalenaHostNetwork(CamelModel):
    proxy: Optional[BalenaProxyConfig] = None
    hostname: Optional[str] = None

class BalenaHostConfig(CamelModel):
    network: BalenaHostNetwork

class BalenaServiceInput(CamelModel):
    service_name: str
    image_id: Optional[str] = None

class BalenaVersionResponse(CamelModel):
    status: str
    version: str

def is_on_balena() -> bool:
    return env_flag('BALENA') or env_flag('RESIN')


def supervisor_address() -> str:
    return os.getenv(f'{BALENA_PREFIX}_SUPERVISOR_ADDRESS', 'http://localhost:48484')

def supervisor_api_key() -> str:
    return os.getenv(f'{BALENA_PREFIX}_SUPERVISOR_API_KEY', '')

def supervisor_uuid() -> str:
    return os.getenv(f'{BALENA_PREFIX}_DEVICE_UUID')

def get_app_id() -> int:
    return int(os.getenv(f'{BALENA_PREFIX}_APP_ID', '0'))

async def ping() -> bool:
    async with httpx.AsyncClient() as client:
        r = await client.get(supervisor_address()+'/ping', params={'apikey': supervisor_api_key()})
    return r.status_code >= 200 and r.status_code <= 299

async def blink() -> bool:
    async with httpx.AsyncClient() as client:
        r = await client.post(supervisor_address()+'/v1/blink', params={'apikey': supervisor_api_key()})
    return r.status_code == httpx.codes.OK

async def update_check(force: bool = False, delay: int = 0) -> bool:
    if delay:
        await asyncio.sleep(delay)
    async with httpx.AsyncClient() as client:
        r = await client.post(
            supervisor_address()+'/v1/update',
            params={'apikey': supervisor_api_key()}, json=dict(force=force)
        )
    return r.status_code == httpx.codes.NO_CONTENT

async def reboot(force: bool = False) -> bool:
    async with httpx.AsyncClient() as client:
        r = await client.post(
            supervisor_address()+'/v1/reboot',
            params={'apikey': supervisor_api_key()}, json=dict(force=force)
        )
    return r.status_code == httpx.codes.ACCEPTED

async def shutdown(force: bool = False) -> bool:
    async with httpx.AsyncClient() as client:
        r = await client.post(
            supervisor_address()+'/v1/shutdown',
            params={'apikey': supervisor_api_key()}, json=dict(force=force)
        )
    return r.status_code == httpx.codes.ACCEPTED

async def purge() -> bool:
    async with httpx.AsyncClient() as client:
        r = await client.post(
            supervisor_address()+'/v1/purge', params={'apikey': supervisor_api_key()}
        )
    return r.status_code == httpx.codes.OK

async def restart(app_id: Optional[int] = None) -> bool:
    app_id = get_app_id() if app_id is None else app_id
    async with httpx.AsyncClient() as client:
        r = await client.post(
            supervisor_address()+'/v1/restart',
            params={'apikey': supervisor_api_key()}, json=dict(appId=app_id)
        )
    return r.status_code == httpx.codes.OK

async def regenerate_api_key() -> str:
    async with httpx.AsyncClient() as client:
        r = await client.post(
            supervisor_address()+'/v1/regenerate-api-key', params={'apikey': supervisor_api_key()}
        )
    return r.text

async def get_device_state() -> BalenaDeviceInfo:
    async with httpx.AsyncClient() as client:
        r = await client.get(supervisor_address()+'/v1/device', params={'apikey': supervisor_api_key()})
    dev_state = BalenaDeviceInfo.parse_raw(r.text)
    return dev_state

async def healthy() -> bool:
    async with httpx.AsyncClient() as client:
        r = await client.get(
            supervisor_address()+'/v1/healthy', params={'apikey': supervisor_api_key()}
        )
    return r.status_code == httpx.codes.OK

async def set_host_config(host_config: BalenaHostConfig) -> bool:
    async with httpx.AsyncClient() as client:
        r = await client.patch(
            supervisor_address()+'/v1/device/host-config',
            params={'apikey': supervisor_api_key()}, json=host_config.dict(by_alias=True)
        )
    return r.status_code == httpx.codes.OK

async def get_host_config() -> BalenaHostConfig:
    async with httpx.AsyncClient() as client:
        r = await client.get(
            supervisor_address()+'/v1/device/host-config',
            params={'apikey': supervisor_api_key()}
        )
    return BalenaHostConfig.parse_raw(r.text)

async def get_applications_state() -> BalenaAppsInfo:
    async with httpx.AsyncClient() as client:
        r = await client.get(supervisor_address()+'/v2/applications/state', params={'apikey': supervisor_api_key()})
    return BalenaAppsInfo.parse_raw(r.text)

async def get_application_state(name: Optional[str] = None) -> BalenaAppInfo:
    if name is None:
        name = os.getenv(f'{BALENA_PREFIX}_APP_NAME', 'App')
    apps_state = await get_applications_state()
    if name not in apps_state:
        raise ValueError(f'Failed getting app state for name {name}')
    return apps_state[name]

async def get_state_status() -> BalenaStateStatus:
    async with httpx.AsyncClient() as client:
        r = await client.get(supervisor_address()+'/v2/state/status', params={'apikey': supervisor_api_key()})
    return BalenaStateStatus.parse_raw(r.text)

async def get_version() -> str:
    async with httpx.AsyncClient() as client:
        r = await client.get(supervisor_address()+'/v2/version', params={'apikey': supervisor_api_key()})
    return r.json().get('version', 'v0.0.0')

async def get_container_ids() -> BalenaServiceContainerIds:
    async with httpx.AsyncClient() as client:
        r = await client.get(supervisor_address()+'/v2/containerId', params={'apikey': supervisor_api_key()})
    return BalenaServiceContainerIds.parse_raw(r.text)

async def get_container_id(service: str) -> str:
    async with httpx.AsyncClient() as client:
        r = await client.get(
            supervisor_address()+' /v2/containerId',
            params={'apikey': supervisor_api_key(), 'service': service}
        )
    return r.json().get('containerId', '')

async def restart_service(service: str, app_id: Optional[int] = None, force: bool = False) -> bool:
    if app_id is None:
        app_id = get_app_id()
    async with httpx.AsyncClient() as client:
        r = await client.get(
            supervisor_address()+f'/v2/applications/{app_id}/restart-service',
            params={'apikey': supervisor_api_key()}, json=dict(serviceName=service, force=force)
        )
    return r.status_code == httpx.codes.OK

async def stop_service(service: str, app_id: Optional[int] = None, force: bool = False) -> bool:
    if app_id is None:
        app_id = get_app_id()
    async with httpx.AsyncClient() as client:
        r = await client.get(
            supervisor_address()+f'/v2/applications/{app_id}/stop-service',
            params={'apikey': supervisor_api_key()}, json=dict(serviceName=service, force=force)
        )
    return r.status_code == httpx.codes.OK

async def start_service(service: str, app_id: Optional[int] = None, force: bool = False) -> bool:
    if app_id is None:
        app_id = get_app_id()
    async with httpx.AsyncClient() as client:
        r = await client.get(
            supervisor_address()+f'/v2/applications/{app_id}/start-service',
            params={'apikey': supervisor_api_key()}, json=dict(serviceName=service, force=force)
        )
    return r.status_code == httpx.codes.OK

async def restart_services(app_id: Optional[int] = None, force: bool = False) -> bool:
    app_id = get_app_id() if app_id is None else app_id
    async with httpx.AsyncClient() as client:
        r = await client.get(
            supervisor_address()+f'/v2/applications/{app_id}/restart',
            params={'apikey': supervisor_api_key()}, json=dict(force=force)
        )
    return r.status_code == httpx.codes.OK

async def purge_all_user_data(app_id: Optional[int] = None, force: bool = False) -> bool:
    app_id = get_app_id() if app_id is None else app_id
    async with httpx.AsyncClient() as client:
        r = await client.get(
            supervisor_address()+f'/v2/applications/{app_id}/purge',
            params={'apikey': supervisor_api_key()}, json=dict(force=force)
        )
    return r.status_code == httpx.codes.OK
