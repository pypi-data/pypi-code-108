"""

ВНИМАНИЕ! Только для использования внутри кода SDK
Запрещено добавление общих утилит в этот файл

"""
import platform
from os.path import expanduser

import os

import json


def read_developer_settings():
    """
    Читает конфигурации разработчика с локальной машины или из переменных окружения
    При этом переменная окружения приоритетнее

    :return: dict|None
    """
    ret = read_cfg("/.rwmeta/developer_settings.json")

    env_developer_settings = os.environ.get('META_SERVICE_ACCOUNT_SECRET', None)
    if not env_developer_settings:
        env_developer_settings = os.environ.get('X-META-Developer-Settings', None)
    if env_developer_settings:
        ret = json.loads(env_developer_settings)

    return ret


def read_cfg(path) -> dict:
    """
    :param path:  example: "/.rwmeta/developer_settings.json"
    :return: dict
    """
    ret = None
    full_path = __build_path(path)
    if os.path.isfile(full_path):
        with open(full_path, 'r') as myfile:
            ret = json.loads(myfile.read())
    return ret


def write_cfg(path, value) -> None:
    """
    :param path:  example: "/.rwmeta/developer_settings.json"
    :param value: dict
    """
    full_path = __build_path(path)
    with open(full_path, 'w') as myfile:
        myfile.write(json.dumps(value))


def __build_path(path):
    if OS_NAME == "windows":
        path = path.replace("/", "\\")
    full_path = expanduser("~") + path
    return full_path


def __get_os():
    if os.name == "nt":
        return "windows"

    if platform.system() == "Darwin":
        return "macos"

    return "linux"


OS_NAME = __get_os()
