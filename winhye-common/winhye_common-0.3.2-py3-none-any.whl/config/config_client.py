import os
import logging
import threading
import yaml

from .apollo_client import ApolloClient
from .config_group import ConfigGroup
from .configger import Configger
from ..utils.exception_base import ConfigException

__all__ = ["ConfigClient"]

LEGAL_ENV = {"DEV", "PRO"}

logger = logging.getLogger(__name__)

_lock = threading.RLock()


def _acquire_lock():
    if _lock:
        _lock.acquire()


def _release_lock():
    if _lock:
        _lock.release()


class ConfigClient(object):
    """
    Wrapper for pyapollo
    """
    client = None
    configger_dict = {}

    @staticmethod
    def init(lib_app_id: str = None, url: str = None, timeout: int = 120):
        """
        Initialize Apollo client

        :param lib_app_id: str, required for library, optional for app, application identification
        :param url: str, required when "DEV", optional for others, Apollo config service url, default value is None
        :param timeout: int, optional, default value is 120(s)
        """
        if ConfigClient.client is not None:
            return

        # APP's init, looking in environment variables
        if lib_app_id is None:
            app_id = os.environ.get("APP_ID", "NOT_EXIST")
            if app_id is "NOT_EXIST":
                raise ConfigException("environment variable APP_ID is empty")
        # library's init
        else:
            app_id = lib_app_id

        env = os.environ.get("ENV", "")
        if env not in LEGAL_ENV:
            raise ConfigException("invalid environment variable ENV")

        idc = os.environ.get("IDC", "NOT_EXIST")
        if idc is "NOT_EXIST":
            raise ConfigException("environment variable IDC is empty")

        if url is None:
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")) as yaml_file:
                apollo_urls = yaml.safe_load(yaml_file)
                url = apollo_urls.get(env)

        logger.debug("Apollo: {config_server_url}, application: {application}, cluster: {idc}".format(
            config_server_url=url,
            application=app_id,
            idc=idc
        ))
        ConfigClient.client = ApolloClient(app_id=app_id, cluster=idc, config_server_url=url, timeout=timeout)
        ConfigClient.client.start(catch_signals=False)
        return

    @staticmethod
    def get_value(key: str, namespace: str):
        """
        Get value from Apollo by key and namespace

        :param key: str, config key
        :param namespace: str, config namespace
        :return: str, config value
        """
        if ConfigClient.client is None:
            raise ConfigException("ConfigClient has not been initialized")
        return ConfigClient.client.get_value(key, namespace=namespace, auto_fetch_on_cache_miss=True)

    @staticmethod
    def get_group(group: str, namespace: str):
        """
        Get ConfigGroup by prefix and namespace

        :param group: str, config common prefix
        :param namespace: str, config namespace
        :return: ConfigGroup, convenient config getter (reference ConfigGroup defined above)
        """
        if ConfigClient.client is None:
            raise ConfigException("ConfigClient has not been initialized")
        return ConfigGroup(ConfigClient.client, namespace, group)

    @staticmethod
    def get_configger(namespace: str):
        """
        Get Configger by namespace

        :param namespace: str, config namespace
        :return: Configger, wrapped ApolloClient with specific namespace (reference Python's logger)
        """
        if ConfigClient.client is None:
            raise ConfigException("ConfigClient has not been initialized")
        _acquire_lock()
        if namespace in ConfigClient.configger_dict:
            configger = ConfigClient.configger_dict[namespace]
        else:
            configger = Configger(ConfigClient.client, namespace)
            ConfigClient.configger_dict[namespace] = configger
        _release_lock()
        return configger

    @staticmethod
    def register_callback(key: str, namespace: str, callback):
        """
        Register callback function for specific config's change

        :param key: str
        :param namespace: str
        :param callback: function
        """
        if ConfigClient.client is None:
            raise ConfigException("ConfigClient has not been initialized")
        ConfigClient.client.register_callback(key, namespace, callback)
