# -*- coding: future_fstrings -*-
from sumoappclient.configmanager.gcp import GCPConfigHandler
from sumoappclient.omnistorage.gcp import GCPKVStorage

from sumoappclient.provider.base import Provider


class GCPProvider(Provider):

    def setup(self, *args, **kwargs):
        pass

    def get_kvstorage(self, name, *args, **kwargs):
        return GCPKVStorage(name, *args, **kwargs)

    def generate_config(self, *args, **kwargs):
        return GCPConfigHandler(*args, **kwargs)
