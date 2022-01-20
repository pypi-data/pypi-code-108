from base64 import b64decode
import os
import logging
from time import sleep

from omegaconf import OmegaConf
from memoization import cached
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from dotenv import load_dotenv
from kubernetes import client as kube_client, config as kube_config
from kubernetes.config import ConfigException

load_dotenv()


def __connect_to_kubernetes():
    try:
        kube_config.load_incluster_config()
    except Exception as ex:
        logging.debug(str(ex))
        kube_config.load_kube_config()


def __get_kubernetes_secret(path: str):
    try:
        __connect_to_kubernetes()
    except ConfigException:
        logging.warn(f'Failed to obtain a secret value "kube:{path}": no available configuration')
        return '???'
    except Exception as exc:
        logging.warn(f'Failed to obtain a secret value "kube:{path}": {type(exc).__name__}')
        return '???'

    split = path.split('/')
    namespace = 'default'
    secret_name = split[0]
    secret_key = split[1]
    if len(split) > 2:
        namespace = split[0]
        secret_name = split[1]
        secret_key = split[2]
    v1 = kube_client.CoreV1Api()

    try:
        secret = v1.read_namespaced_secret(secret_name, namespace).data[secret_key]
    except Exception as exc:
        logging.warn(f'Failed to obtain a secret value "kube:{path}": {type(exc).__name__}')
        return '???'

    secret = b64decode(secret).decode('utf-8')
    return secret


def __get_secrets_client():
    delphai_environment = os.environ.get('DELPHAI_ENVIRONMENT')
    credential = DefaultAzureCredential()
    return SecretClient(f'https://delphai-{delphai_environment}-kv.vault.azure.net', credential)


def __get_secret(name: str):
    try:
        secrets_client = __get_secrets_client()
        res = secrets_client.get_secret(name).value
    except Exception as exc:
        logging.warn(f'Failed to obtain a secret value "azkv:{name}": {type(exc).__name__}')
        return '???'
    return res


def __get_keyring_secret(name: str):
    import keyring
    service_n_user = name.split('/')
    service_name = '/'.join(service_n_user[:-1])
    username = ''.join(service_n_user[-1:])
    return keyring.get_password(service_name, username) or '???'


OmegaConf.register_new_resolver('azkv', __get_secret)
OmegaConf.register_new_resolver('kube', __get_kubernetes_secret)
OmegaConf.register_new_resolver('keyring', __get_keyring_secret)


CURRENT_CONFIG = None
CONFIG_IS_LOADING = False


def __load_config():
    global CURRENT_CONFIG, CONFIG_IS_LOADING
    while CONFIG_IS_LOADING:
        sleep(0.05)
    if CURRENT_CONFIG is not None:
        return CURRENT_CONFIG
    while CONFIG_IS_LOADING:
        sleep(0.05)
    CONFIG_IS_LOADING = True
    try:
        if 'DELPHAI_ENVIRONMENT' not in os.environ:
            raise Exception('DELPHAI_ENVIRONMENT is not defined')
        default_config = OmegaConf.load('./config/default.yml')
        delphai_environment = os.environ.get('DELPHAI_ENVIRONMENT')
        if os.path.isfile(f'./config/{delphai_environment}.yml'):
            delphai_env_config = OmegaConf.load(f'./config/{delphai_environment}.yml')
        else:
            delphai_env_config = OmegaConf.create()
        CURRENT_CONFIG = OmegaConf.merge(default_config, delphai_env_config)
        OmegaConf.set_readonly(CURRENT_CONFIG, True)
        return CURRENT_CONFIG
    finally:
        CONFIG_IS_LOADING = False


@cached
def get_config(path: str = ''):
    config = __load_config()
    if path is None:
        return config
    selected = OmegaConf.select(config, path)
    if OmegaConf.is_config(selected):
        return OmegaConf.to_container(selected, resolve=True)
    else:
        return selected
