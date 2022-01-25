# -*- coding: future_fstrings -*-
import os

from sumoappclient.configmanager.base import BaseConfigHandler


class AzureConfigHandler(BaseConfigHandler):

    def setup(self, *args, **kwargs):
        pass

    def fetch_user_config(self):
        return self._override_section_config(os.environ)

    def decrypt(self, decrypt_type, key, value):
        return value
