# Copyright 2020-2021 Axis Communications AB.
#
# For a full list of individual contributors, please see the commit history.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""ETOS Library secret file handler."""
import os
from .config import Config
from .debug import Debug


class Secrets:
    """Load K8S secrets."""

    def __init__(self):
        """Initialize config."""
        self.config = Config()
        self.debug = Debug()

    def load_password(self, service):
        """Load password secret if it exist.

        :param service: Name of service to load password secret from.
        :type service: str
        :return: Service dictionary with all secrets.
        :rtype: dict
        """
        self.load("password", service)
        return self.config.get(service) or {}

    def load_username(self, service):
        """Load username secret if it exist.

        :param service: Name of service to load username secret from.
        :type service: str
        :return: Service dictionary with all secrets.
        :rtype: dict
        """
        self.load("username", service)
        return self.config.get(service) or {}

    def load_all(self, service):
        """Load all secrets if they exist.

        :param service: Name of service to load all secrets from.
        :type service: str
        :return: Service dictionary with all secrets.
        :rtype: dict
        """
        self.load_password(service)
        self.load_username(service)
        return self.config.get(service) or {}

    def load(self, filename, service):
        """Load a filename from service in the base secret path.

        :param filename: Name of file to load.
        :type filename: str
        :param service: From which service to load file from.
        :type service: str
        """
        path = os.path.join(self.debug.default_secret_path, service, filename)
        if os.path.isfile(path):
            if self.config.get(service) is None:
                self.config.set(service, {})
            with open(path, encoding="utf-8") as secret:
                self.config.get(service)[filename] = secret.read()
