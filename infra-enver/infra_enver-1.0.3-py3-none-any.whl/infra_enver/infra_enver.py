import requests
from . import config
from . import infra_enver_exceptions as ee
import os
from dotenv import load_dotenv
import pydantic
import typing as t

class Enver(object):
    """infra_enver class"""
    project_name: str
    secret_key: str
    is_fallback_enabled: bool
    pydantic_settings: t.Optional[pydantic.BaseSettings] = None


    def __getattr__(self, item):
        return self.get_setting(item)


    def __init__(
        self,
        project_name: str,
        secret_key: str,
        is_fallback_enabled: bool = False,
        pydantic_settings: t.Optional[pydantic.BaseSettings] = None
    ):
        self.project_name = project_name
        self.secret_key = secret_key
        self.is_fallback_enabled = is_fallback_enabled
        if is_fallback_enabled:
            self.pydantic_settings = pydantic_settings

    def get_setting(self, setting_name: str):
        json = {
            "project_name": self.project_name,
            "secret_key": self.secret_key
        }
        r = requests.post(config.SETTINGS_URL + setting_name, json=json)
        if not r.ok:
            if self.is_fallback_enabled:
                return getattr(self.pydantic_settings, setting_name)
            try:
                raise ee.InfraEnverException(r.json()['detail'])
            except KeyError:
                raise ee.InfraEnverException(r.text)
        return r.json()['value']


    def get_experiment(self, experiment_name: str, arg: t.Any, fallback_value: t.Any = None):
        json = {
            "project_name": self.project_name,
            "secret_key": self.secret_key,
            "experiment_name": experiment_name,
            "arg": arg
        }
        r = requests.post(config.EXPERIMENT_URL, json=json)
        if not r.ok:
            return fallback_value
        return r.json()
