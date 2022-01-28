# -*- coding: utf-8 -*-
"""
    pip_services3_components.auth.MemoryCredentialStore
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Memory credential store implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Optional

from pip_services3_commons.config.ConfigParams import ConfigParams
from pip_services3_commons.config.IReconfigurable import IReconfigurable
from pip_services3_commons.data.StringValueMap import StringValueMap

from .CredentialParams import CredentialParams
from .ICredentialStore import ICredentialStore


class MemoryCredentialStore(ICredentialStore, IReconfigurable):
    """
    Credential store that keeps credentials in memory.

    ### Configuration parameters ###
        - [credential key 1]:
        - ...                          credential parameters for key 1
        - [credential key 2]:
        - ...                          credential parameters for key N
        - ...

    Example:

    .. code-block:: python
    
        config = ConfigParams.from_tuples("key1.user", "jdoe",
                                          "key1.pass", "pass123",
                                          "key2.user", "bsmith",
                                          "key2.pass", "mypass")

        credentialStore = MemoryCredentialStore()
        credentialStore.read_credentials(config)
        credentialStore.lookup("123", "key1")
    """

    def __init__(self, config: ConfigParams = None):
        """
        Creates a new instance of the credential store.

        :param config: (optional) configuration with credential parameters.
        """
        self.__items: StringValueMap = StringValueMap()
        if not (config is None):
            self.configure(config)

    def configure(self, config: ConfigParams):
        """
        Configures component by passing configuration parameters.

        :param config: configuration parameters to be set.
        """
        self.read_credentials(config)

    def read_credentials(self, config: ConfigParams):
        """
        Reads credentials from configuration parameters.
        Each section represents an individual CredentialParams

        :param config: configuration parameters to be read
        """
        self.__items.clear()
        for section in config.get_section_names():
            value = config.get_section(section)
            self.__items.append(CredentialParams.from_tuples(section, value))

    def store(self, correlation_id: Optional[str], key: str, credential: CredentialParams):
        """
        Stores credential parameters into the store.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param key: a key to uniquely identify the credential parameters.

        :param credential: a credential parameters to be stored.
        """
        if not (credential is None):
            self.__items.put(key, credential)
        else:
            self.__items.remove(key)

    def lookup(self, correlation_id: Optional[str], key: str) -> CredentialParams:
        """
        Lookups credential parameters by its key.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param key: a key to uniquely identify the credential.

        :return: found credential parameters or None if nothing was found
        """
        return self.__items.get_as_object(key)
