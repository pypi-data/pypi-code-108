# -*- coding: utf-8 -*-
"""
    pip_services3_components.auth.CredentialParams
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Credential parameters implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import List, Any

from pip_services3_commons.config.ConfigParams import ConfigParams
from pip_services3_commons.data import StringValueMap


class CredentialParams(ConfigParams):
    """
    Contains credentials to authenticate against external services.

    They are used together with connection parameters,
    but usually stored in a separate store, protected from unauthorized access.

    ### Configuration parameters ###
        - store_key:     key to retrieve parameters from credential store
        - username:      user name
        - user:          alternative to username
        - password:      user password
        - pass:          alternative to password
        - access_id:     application access id
        - client_id:     alternative to access_id
        - access_key:    application secret key
        - client_key:    alternative to access_key
        - secret_key:    alternative to access_key

    In addition to standard parameters CredentialParams
    may contain any number of custom parameters

    Example:

    .. code-block:: python

        credential = CredentialParams.from_tuples
        ("user", "jdoe", "pass", "pass123", "pin", "321")

        username = credential.get_username()           # Result: "jdoe"
        password = credential.get_password()           # Result: "pass123"
        pin = credential.get_as_nullable_string("pin") # Result: 321
    """

    def __init__(self, values: Any = None):
        """
        Creates a new credential parameters and fills it with values.

        :param values: (optional) an object to be converted into key-value pairs to initialize these credentials.
        """
        super(CredentialParams, self).__init__(values)

    def use_credential_store(self) -> bool:
        """
        Checks if these credential parameters shall be retrieved from :class:`ICredentialStore <pip_services3_components.auth.ICredentialStore.ICredentialStore>`.
        The credential parameters are redirected to :class:`ICredentialStore <pip_services3_components.auth.ICredentialStore.ICredentialStore>` when store_key parameter is set.

        :return: true if credentials shall be retrieved from :class:`ICredentialStore <pip_services3_components.auth.ICredentialStore.ICredentialStore>`
        """
        return "store_key" in self

    def get_store_key(self) -> str:
        """
        Gets the key to retrieve these credentials from :class:`ICredentialStore <pip_services3_components.auth.ICredentialStore.ICredentialStore>`.
        If this key is null, than all parameters are already present.

        :return: the store key to retrieve credentials.
        """
        return self.get_as_nullable_string("store_key")

    def set_store_key(self, value: str):
        """
        Sets the key to retrieve these parameters from :class:`ICredentialStore <pip_services3_components.auth.ICredentialStore.ICredentialStore>`.

        :param value: a new key to retrieve credentials.
        """
        self.put("store_key", value)

    def get_username(self) -> str:
        """
        Gets the user name. The value can be stored in parameters "username" or "user".

        :return: the user name.
        """
        username = self.get_as_nullable_string("username")
        username = username if not (username is None) else self.get_as_nullable_string("user")
        return username

    def set_username(self, value: str):
        """
        Sets the user name.

        :param value: a new user name.
        """
        self.put("username", value)

    def get_password(self) -> str:
        """
        Get the user password. The value can be stored in parameters "password" or "pass".

        :return: the user password.
        """
        password = self.get_as_nullable_string("password")
        password = password if not (password is None) else self.get_as_nullable_string("pass")
        return password

    def set_password(self, password: str):
        """
        Sets the user password.

        :param password: a new user password.
        """
        self.put("password", password)

    def get_access_id(self) -> str:
        """
        Gets the application access id. The value can be stored in parameters "access_id" pr "client_id"

        :return: the application access id.
        """
        access_id = self.get_as_nullable_string("access_id")
        access_id = access_id if not (access_id is None) else self.get_as_nullable_string("client_id")
        return access_id

    def set_access_id(self, value: str):
        """
        Sets the application access id.

        :param value: a new application access id.
        """
        self.put("access_id", value)

    def get_access_key(self) -> str:
        """
        Gets the application secret key.
        The value can be stored in parameters "access_key", "client_key" or "secret_key".

        :return: the application secret key.
        """
        access_key = self.get_as_nullable_string("access_key")
        access_key = access_key if not (access_key is None) else self.get_as_nullable_string("access_key")
        return access_key

    def set_access_key(self, value: str):
        """
        Sets the application secret key.

        :param value: a new application secret key.
        """
        self.put("access_key", value)

    @staticmethod
    def from_string(line: str) -> 'CredentialParams':
        """
        Creates a new CredentialParams object filled with key-value pairs serialized as a string.

        :param line: a string with serialized key-value pairs as **"key1=value1;key2=value2;..."**
                     Example: **"Key1=123;Key2=ABC;Key3=2016-09-16T00:00:00.00Z"**

        :return: a new CredentialParams object.
        """
        map = StringValueMap.from_string(line)
        return CredentialParams(map)

    @staticmethod
    def from_tuples(*tuples: Any) -> 'CredentialParams':
        """
        Creates a new CredentialParams object filled with provided key-value pairs called tuples.
        Tuples parameters contain a sequence of key1, value1, key2, value2, ... pairs.

        :param tuples: the tuples to fill a new CredentialParams object.

        :return: a new CredentialParams object.
        """
        map = StringValueMap.from_tuples_array(tuples)
        return CredentialParams(map)

    @staticmethod
    def many_from_config(config: ConfigParams) -> List['CredentialParams']:
        """
        Retrieves all CredentialParams from configuration parameters
        from "credentials" section. If "credential" section is present instead,
        than it returns a list with only one CredentialParams.

        :param config: a configuration parameters to retrieve credentials

        :return: a list of retrieved CredentialParams
        """
        result = []

        # Try to get multiple credentials first
        credentials = config.get_section("credentials")
        if len(credentials) > 0:
            sections_names = credentials.get_section_names()
            for section in sections_names:
                credential = credentials.get_section(section)
                result.append(CredentialParams(credential))
        # Then try to get a single credential
        else:
            credential = config.get_section("credential")
            result.append(CredentialParams(credential))

        return result

    @staticmethod
    def from_config(config: ConfigParams) -> 'CredentialParams':
        """
        Retrieves a single CredentialParams from configuration parameters
        from "credential" section. If "credentials" section is present instead,
        then is returns only the first credential element.

        :param config: ConfigParams, containing a section named "credential(s)".

        :return: the generated CredentialParams object.
        """
        credentials = CredentialParams.many_from_config(config)
        return credentials[0] if len(credentials) > 0 else None
