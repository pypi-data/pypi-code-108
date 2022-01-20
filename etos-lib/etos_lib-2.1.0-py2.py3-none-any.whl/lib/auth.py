# Copyright 2020 Axis Communications AB.
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
"""ETOS Library authentication handler.

DEPRECATED: Use kubernetes secrets instead!
"""
import configparser
from cryptography.fernet import Fernet


class Auth:
    """Authentication helper for ETOS.

    Example:
        auth = Auth()
        auth.load_password_file("password.secret")
        username, password = auth.credentials("my_service")
    """

    config = None
    key = None

    def load_password_file(self, _file):
        """Load a password file into memory.

        :param _file: Path to file to load.
        :type _file: str
        """
        self.config = configparser.ConfigParser()
        self.config.read(_file)
        self.key = self.config["global"]["key"]

    def decrypt(self, token):
        """Decrypt a password hash into a password.

        :param token: Password hash to decrypt.
        :type token: str
        :return: Password in clear-text.
        :rtype: str
        """
        cipher_suite = Fernet(self.key)
        uncipher_text = cipher_suite.decrypt(token.encode("utf-8"))
        return bytes(uncipher_text).decode("utf-8")

    def credentials(self, service):
        """Get credentials from a specific service defined in password file.

        :param service: Which service to get credentials for.
        :type service: str
        :return: Username and password for service.
        :rtype: tuple
        """
        service = self.config[service]
        return service.get("username"), self.decrypt(service.get("password"))
