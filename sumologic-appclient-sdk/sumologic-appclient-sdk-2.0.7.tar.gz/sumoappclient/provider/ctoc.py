# -*- coding: future_fstrings -*-
import os

from sumoappclient.configmanager.ctoc import CtoCConfigHandler
from sumoappclient.omnistorage.ctoc import CToCKVStorage
from sumoappclient.provider.base import Provider


class CToCProvider(Provider):

    def setup(self, *args, **kwargs):
        self.c2c_base_url = os.getenv("BASE_URL", '')

    def get_kvstorage(self, name, *args, **kwargs):
        return CToCKVStorage(name, c2c_base_url=self.c2c_base_url, *args, **kwargs)

    def generate_config(self, *args, **kwargs):
        return CtoCConfigHandler(c2c_base_url=self.c2c_base_url, *args, **kwargs)
