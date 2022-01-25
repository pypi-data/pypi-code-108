# SPDX-FileCopyrightText: 2020 Mintlab B.V.
#
# SPDX-License-Identifier: EUPL-1.2

import re
from ... import Base
from abc import ABC, abstractmethod


class ConfigurationNotFound(FileNotFoundError):
    """Exception raised when configuration can't be found"""

    pass


class ConfigStoreBase(ABC, Base):
    """Abstract base class for configuration store plugins"""

    ALLOWED_CONFIG_NAME = r"^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)*$"

    @abstractmethod
    def retrieve(self, name: str):
        """Retrieve configuration - base/superclass method

        :param name: Name of the configuration to retrieve
        :param name: str
        :raises NameError: If the configuration name is invalid
        """

        if not re.match(self.ALLOWED_CONFIG_NAME, name):
            raise NameError
