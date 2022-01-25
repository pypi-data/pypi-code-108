# -*- coding: future_fstrings -*-
import os
import urllib
from sumoappclient.common.errors import FetchConfigException, InValidConfigException
from sumoappclient.sumoclient.httputils import ClientMixin
from sumoappclient.configmanager.base import BaseConfigHandler


class CtoCConfigHandler(BaseConfigHandler):

    def setup(self, ctoc_base_url='', *args, **kwargs):
        self.ctoc_base_url = ctoc_base_url if ctoc_base_url else os.getenv("BASE_URL", '')
        self.ctoc_config_endpoint = self.ctoc_base_url + "/config"

    def fetch_user_config(self):
        if not self.ctoc_base_url:
            raise InValidConfigException("Base URL not found")
        self.base_config["SumoLogic"] = self.base_config.get("SumoLogic", {})
        self.base_config["SumoLogic"]["CTOC_BASE_URL"] = self.ctoc_base_url
        return self._get_config_from_ctoc(self.ctoc_base_url)

    def _get_config_from_ctoc(self, base_url):
        self.log.debug("fetching parameters from ctoc framework")
        status, data = ClientMixin.make_request(self.ctoc_config_endpoint, "get", logger=self.log)
        if status:
            cfg = self._override_section_config(data["config"])
            cfg["SumoLogic"]["systemConfig"] = data["systemConfig"]
            if data["systemConfig"].get("debugModeEnabled", False):
                cfg["Logging"]["LOG_LEVEL"] = "DEBUG"
            del data
            return cfg
        else:
            raise FetchConfigException(data)

    def decrypt(self, decrypt_type, key, value):
        return value

    def _override_section_config(self, other_config):
        cfg = {}
        for section, section_cfg in self.base_config.items():
            new_section_cfg = {}
            for k, v in section_cfg.items():
                if k in other_config:
                    new_section_cfg[k] = other_config[k]
                elif k.lower() in other_config:
                    # all small letters in config
                    new_section_cfg[k] = other_config[k.lower()]
                else:
                    new_section_cfg[k] = v
            cfg[section] = new_section_cfg

        del other_config
        return cfg
