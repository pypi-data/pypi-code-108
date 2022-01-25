# -*- coding: future_fstrings -*-

import os

from sumoappclient.configmanager.aws import AWSConfigHandler
from sumoappclient.omnistorage.aws import AWSKVStorage

from sumoappclient.provider.base import Provider


class AWSProvider(Provider):

    def setup(self, *args, **kwargs):
        self.region_name = kwargs.get('region_name', os.getenv("AWS_REGION"))

    def get_kvstorage(self, name, *args, **kwargs):
        return AWSKVStorage(name, self.region_name, *args, **kwargs)

    def generate_config(self, *args, **kwargs):
        return AWSConfigHandler(self.region_name, *args, **kwargs)
