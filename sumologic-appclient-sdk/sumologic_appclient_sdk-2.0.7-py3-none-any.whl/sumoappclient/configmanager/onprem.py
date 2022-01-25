# -*- coding: future_fstrings -*-
from sumoappclient.common.utils import read_first_file
from sumoappclient.configmanager.base import BaseConfigHandler


class OnPremConfigHandler(BaseConfigHandler):

    def setup(self, *args, **kwargs):
        pass

    def fetch_user_config(self):
        config_locations = self.get_file_locations(self.cfgpath, self.config_filename)
        user_cfg, path = read_first_file(config_locations)
        self.log.info(f"Reading config file {path}")
        return user_cfg

    def decrypt(self, decrypt_type, key, value):
        return value
