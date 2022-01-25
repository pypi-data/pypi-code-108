# -*- coding: future_fstrings -*-
from sumoappclient.configmanager.onprem import OnPremConfigHandler
from sumoappclient.omnistorage.onprem import OnPremKVStorage

from sumoappclient.provider.base import Provider


class OnPremProvider(Provider):

    def setup(self, *args, **kwargs):
        pass

    def get_kvstorage(self, name, *args, **kwargs):
        return OnPremKVStorage(name, *args, **kwargs)

    def generate_config(self, *args, **kwargs):
        return OnPremConfigHandler(*args, **kwargs)
