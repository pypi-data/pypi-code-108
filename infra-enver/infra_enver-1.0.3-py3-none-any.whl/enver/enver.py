import requests
from . import config
from . import enver_exceptions as ee
import os
from dotenv import load_dotenv
import pydantic
import typing as t

class Enver(object):
    """enver class"""
    project_name: str
    secret_key: str
    is_fallback_enabled: bool
    pydantic_settings: t.Optional[pydantic.BaseSettings] = None

    def __init__(
        self,
        project_name: str,
        secret_key: str,
        is_use_env_on_error: bool = False,
        pydantic_settings: t.Optional[pydantic.BaseSettings] = None
    ):
        self.project_name = project_name
        self.secret_key = secret_key
        self.is_use_env_on_error = is_use_env_on_error
        if is_use_env_on_error:
            self.pydantic_settings = pydantic_settings

    def get_setting(self, setting_name: str):
        json = {
            "project_name": self.project_name,
            "secret_key": self.secret_key
        }
        r = requests.get(config.SETTINGS_URL + setting_name, json=json)
        if not r.ok:
            if self.is_use_env_on_error:
                return getattr(self.pydantic_settings, setting_name)
            try:
                raise ee.EnverException(r.json()['detail'])
            except KeyError:
                raise ee.EnverException(r.text)
        return r.json()['value']
