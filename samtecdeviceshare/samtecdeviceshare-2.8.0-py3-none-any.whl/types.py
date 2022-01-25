import os
import tempfile
from typing import Optional, List, Pattern
from enum import Enum
import json
import yaml
from pyaml_env import parse_config
import humps
from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module


BALENA_PREFIX = 'BALENA' if os.getenv('BALENA') else 'RESIN' if os.getenv('RESIN') else 'SDC'
CUR_DIR = os.path.dirname(os.path.realpath(__file__))

def env_flag(env_var: str, default: bool = False) -> bool:
    environ_string = os.environ.get(env_var, "").strip().lower()
    if not environ_string:
        return default
    return environ_string in ["1", "true", "yes", "on"]

class CamelModel(BaseModel):
    class Config:
        alias_generator = humps.camelize
        allow_population_by_field_name = True

class AppDataV1(BaseModel):
    type: str
    port: int

class TextResponseEnum(str, Enum):
    Success = 'Success'
    Failure = 'Failure'
    @classmethod
    def from_bool(cls, success: bool):
        return cls.Success if success else cls.Failure

class WiredConnectionMethod(str, Enum):
    disabled = 'disabled'
    auto = 'auto'
    link_local = 'link-local'
    manual = 'manual'

class WiredConnectionState(str, Enum):
    DISCONNECTED = 'DISCONNECTED'
    CONNECTING = 'CONNECTING'
    CONNECTED = 'CONNECTED'

class WiredNetworkConfig(CamelModel):
    iface: Optional[str] = None
    iface_regex: Optional[Pattern] = None
    method: WiredConnectionMethod = WiredConnectionMethod.auto
    timeout: float = 15
    fallback: Optional[WiredConnectionMethod] = None
    fallback_timeout: float = -1

class WifiMode(str, Enum):
    HOTSPOT = 'HOTSPOT'
    CLIENT = 'CLIENT'
    DISABLED = 'DISABLED'

class NetworkCredentials(CamelModel):
    mode: WifiMode = WifiMode.DISABLED
    ssid: str = ''
    passphrase: Optional[str] = None
    identity: Optional[str] = None
    iface: Optional[str] = None
    iface_regex: Optional[Pattern] = None
    default: bool = False

class NetworkCredentialCleaned(CamelModel):
    mode: WifiMode = WifiMode.DISABLED
    ssid: str = ''
    identity: Optional[str] = None
    iface: Optional[str] = None
    iface_regex: Optional[Pattern] = None
    default: bool = False

class AppInfo(CamelModel):
    log_path: str = os.getenv('APP_LOG_PATH', '/tmp/logs')
    web_port: int = int(os.getenv('APP_WEB_PORT', '80'))
    img_path: str = os.getenv('APP_IMG_PATH', os.path.join(CUR_DIR, '../static/img.png'))

class DeviceState(CamelModel):
    status: str = 'IDLE'
    app_commit: str = ''
    app_version: str = '0.0.0'
    app_download_progress: int = 0
    app_update_available: bool = False
    app_downloading: bool = False
    app_updating: bool = False
    app_update_check: bool = False
    ip_address: str = ''
    device_UUID: str = ''
    device_name: str = ''
    internet_access: bool = False
    ap_mode: bool = False

class SDCConfiguration(CamelModel):
    # SERVER
    rest_address: str = '0.0.0.0'
    rest_port: int = 47546
    root_path: str = ''
    # APP
    app_name: str = 'SDC App'
    app_version: str = '0.0.0'
    app_web_port: int = 80
    app_img_path: str = os.path.join(CUR_DIR, '../static/img.png')
    app_log_path: str = Field(default_factory=tempfile.gettempdir)
    app_lock_path: str = '.__sdc.lock'
    # _app_image_bytes: bytes = PrivateAttr()
    # NETWORKS
    wired_networks: List[WiredNetworkConfig] = []
    wireless_networks: List[NetworkCredentials] = []

    def __init__(self, **data) -> None:
        super().__init__(**data)

        self.rest_address = os.getenv('SDC_REST_ADDRESS', os.getenv('REST_ADDRESS', self.rest_address))
        self.rest_port = int(os.getenv('SDC_REST_PORT') or os.getenv('REST_PORT') or self.rest_port)
        self.root_path = os.getenv('SDC_ROOT_PATH', os.getenv('ROOT_PATH', self.root_path))

        self.app_name = os.getenv('SDC_APP_NAME', os.getenv('APP_NAME', self.app_name))
        self.app_version = os.getenv('SDC_APP_VERSION', os.getenv('APP_VERSION', self.app_version))
        self.app_web_port = int(os.getenv('SDC_APP_WEB_PORT') or os.getenv('APP_WEB_PORT') or self.app_web_port)
        self.app_img_path = os.getenv('SDC_APP_IMG_PATH', os.getenv('APP_IMG_PATH', self.app_img_path))
        self.app_log_path = os.getenv('SDC_APP_LOG_PATH', os.getenv('APP_LOG_PATH', self.app_log_path))
        self.app_lock_path = os.getenv('SDC_APP_LOCK_PATH', os.getenv('APP_LOCK_PATH', self.app_lock_path))

        net_idx = 1
        while True:
            ssid = os.getenv(f'SDC_WIFI{net_idx}_SSID')
            if ssid is None:
                break

            wireless_network = NetworkCredentials(
                ssid = ssid,
                mode = os.getenv(f'SDC_WIFI{net_idx}_MODE'),
                passphrase = os.getenv(f'SDC_WIFI{net_idx}_PASS'),
                identity = os.getenv(f'SDC_WIFI{net_idx}_IDENTITY'),
                iface = os.getenv(f'SDC_WIFI{net_idx}_IFACE'),
                iface_regex = os.getenv(f'SDC_WIFI{net_idx}_REGEX_IFACE'),
                default = env_flag(f'SDC_WIFI{net_idx}_DEFAULT')
            )
            if net_idx <= len(self.wireless_networks):
                self.wireless_networks[net_idx-1] = wireless_network
            else:
                self.wireless_networks.append(wireless_network)
            net_idx += 1
        # END WHILE

        net_idx = 1
        while True:
            iface = os.getenv(f'SDC_ETH{net_idx}_IFACE')
            iface_regex = os.getenv(f'SDC_ETH{net_idx}_REGEX_IFACE')
            if iface is None and iface_regex is None:
                break
            wired_network = WiredNetworkConfig(
                iface = iface,
                iface_regex = iface_regex,
                method = os.getenv(f'SDC_ETH{net_idx}_METHOD', 'auto'),
                timeout = float(os.getenv(f'SDC_ETH{net_idx}_TIMEOUT', '15')),
                fallback = os.getenv(f'SDC_ETH{net_idx}_FALLBACK'),
                fallback_timeout = float(os.getenv(f'SDC_ETH{net_idx}_FALLBACK_TIMEOUT', '-1'))
            )
            if net_idx <= len(self.wired_networks):
                self.wired_networks[net_idx-1] = wired_network
            else:
                self.wired_networks.append(wired_network)
            net_idx += 1
        # END WHILE

    @classmethod
    def load_default(cls):
        config_path = os.getenv('SDC_CONFIGURATION_PATH')
        if config_path and os.path.isfile(config_path):
            # If JSON, convert to yaml to support env var replacement
            if os.path.splitext(config_path)[1].lower() == '.json':
                with open(config_path, 'r') as fp:
                    config = parse_config(data=yaml.dump(json.load(fp)), raise_if_na=True)
                return cls(**config)

            if os.path.splitext(config_path)[1].lower() in ('.yml', '.yaml'):
                config = parse_config(config_path, raise_if_na=True)
                return cls(**config)
        return cls()
