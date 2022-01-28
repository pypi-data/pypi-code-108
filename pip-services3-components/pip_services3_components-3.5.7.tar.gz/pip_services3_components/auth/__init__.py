# -*- coding: utf-8 -*-
"""
    pip_services3_components.auth.__init__
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Contains credentials implementation.

    Credentials – passwords, logins,
    application keys, secrets. This information is usually linked with connection parameters.
    Connection parameters separate from authentication, because auth is saved as a secret,
    and stored separately from configuration parameters (host name, ip addresses).
    They need added security and protection, so they were separated.

    Credential parameters include various credentials.

    Interfaces and abstract classes for credential stores, which can save or retrieve various credential parameters.

    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

__all__ = ['CredentialParams', 'ICredentialStore', 'CredentialResolver',
           'MemoryCredentialStore', 'DefaultCredentialStoreFactory']

from .CredentialParams import CredentialParams
from .CredentialResolver import CredentialResolver
from .DefaultCredentialStoreFactory import DefaultCredentialStoreFactory
from .ICredentialStore import ICredentialStore
from .MemoryCredentialStore import MemoryCredentialStore
