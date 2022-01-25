#!usr/bin/python

# Copyright 2021 Deep Intelligence
# See LICENSE for details.

import os
import configparser
from ..error import DeepintCredentialsError


class Credentials:
    """Loads credentials (token), and manages it during runtime.
    
    This class must not be instantiated directly, but the :obj:`deepint_sdk.auth.Credentials.build` 
    method must be used. Due to this fact, for details on how to provide the access token, see the 
    :obj:`deepint_sdk.auth.Credentials.build` method.

    Attributes:
        token: Token to access the deepint.net API that must be used to authenticate each transaction.
        instance : Host to connect with. By default is the hostname of the SaaS instance, however if you are working with an on-premise instance, this must be specified.
    """

    def __init__(self, token: str, instance:str) -> None:
        self.token = token
        self.instance = instance

    @classmethod
    def build(cls, token: str = None, instance: str = 'app.deepint.net') -> 'Credentials':
        """Instances a :obj:`deepint_sdk.auth.Credentials` with one of the provided methods.
        
        The priority of credentials loading is the following:
            - if the credentials are provided as a parameter, this one is used.
            - then the credentials are tried to be extracted from the environment variable ```DEEPINT_TOKEN``` and ```DEEPINT_INSTANCE```.
            - then the credentials are tried to be extracted from the file ```~/.deepint.ini``` located in the user's directory.

        If the token is not provided in any of these ways, an :obj:`deepint_sdk.error.DeepintCredentialsError` will be thrown.
        
        Example:
            [DEFAULT]
            token=a token
            instance=host to connect with (if not providen app.deepint.net will be taken by default)

        Args:
            token : Token to access the deepint.net API that must be used to authenticate each transaction.
            instance : Host to connect with. By default is the hostname of the SaaS instance, however if you are working with an on-premise instance, this must be specified.

        Returns:
            An instanced credentials object.
        """

        if token is None or instance is None:
            for f in [cls._load_env, cls._load_home_file]:
                token, instance = f()
                if token is not None and instance is not None:
                    break

        if token is None:
            raise DeepintCredentialsError()

        cred = Credentials(token=token, instance=instance)

        return cred

    @classmethod
    def _load_env(cls) -> tuple:
        """Loads the credentials values from the environment variables ```DEEPINT_TOKEN``` and ```DEEPINT_INSTANCE```
        
        Returns:
            The value of the ```DEEPINT_TOKEN``` and ```DEEPINT_INSTANCE``` environment variables. If the any of the 
            variables is not declared in environment, the retrieved value will be None, otherwise will be the 
            value stored in that variable. Excepting the ```DEEPINT_INSTANCE``` variable that will be the SaaS instance
            hostname, app.deepint.net.
        """

        return os.environ.get('DEEPINT_TOKEN', None), os.environ.get('DEEPINT_INSTANCE', 'app.deepint.net') 

    @classmethod
    def _load_home_file(cls) -> tuple:
        """Loads the credentials values from the file located in the user's home directory.
        
        The file loaded is the one located in ```~/.deepint.ini```, and must be a .ini file with the following format:

        Example:
            [DEFAULT]
            token=a token
            instance=host to connect with (if not providen app.deepint.net will be taken by default)

        Returns:
            The value of the token stored in the file.
        """

        home_folder = os.path.expanduser("~")
        credentials_file = f'{home_folder}/.deepint.ini'

        if not os.path.isfile(credentials_file):
            return None
        else:
            config = configparser.ConfigParser()
            config.read(credentials_file)

            try:
                token = config['DEFAULT'].get('token', None)
            except:
                token = None

            try:
                instance = config['DEFAULT'].get('instance', 'app.deepint.net')
            except:
                instance = None

            return token, instance

    def update_credentials(self, token: str, instance: str) -> None:
        """Updates the token value.
        
        Alternative of updating directly the token value accessing the attribute :obj:`deepint_sdk.auth.Credentials.token`.

        Args:
            token: token to replace current token stored in :obj:`deepint_sdk.auth.Credentials.token`.
            instance : Host to connect with. By default is the hostname of the SaaS instance, however if you are working with an on-premise instance, this must be specified.
        """

        self.token = token
        self.instance = instance
