# -*- coding: future_fstrings -*-
from sumoappclient.configmanager.azure import AzureConfigHandler
from sumoappclient.omnistorage.azure import AzureKVStorage

from sumoappclient.provider.base import Provider


class AzureProvider(Provider):  # should we disallow direct access to these classes

    def setup(self, *args, **kwargs):
        pass

    def get_kvstorage(self, name, *args, **kwargs):
        return AzureKVStorage(name, *args, **kwargs)

    def generate_config(self, *args, **kwargs):
        return AzureConfigHandler(*args, **kwargs)
