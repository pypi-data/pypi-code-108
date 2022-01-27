"""
Wrapper around the python requests module for ease of interaction with all CloudCIX services

Basic usage: ``cloudcix.api.<application>.<service>.<method>``

More detailed usage information will be available under each of the above terms

To see even more details about the API you can visit our `HTTP API Reference <https://docs.cloudcix.com/>`_

To see more information about the various methods (list, read, etc.), see the :doc:`client_reference` page

For examples of a call for each of these methods, see the :doc:`examples` page

.. note:: Any service that implements the ``update`` method also implements the ``partial_update`` method, which does
  the same thing without needing to pass a full representation of the object, only the fields that need updating
"""

from .app_manager import AppManager
from .asset import Asset
from .circuit import Circuit
from .contacts import Contacts
from .documentation import Documentation
from .financial import Financial
from .helpdesk import Helpdesk
from .iaas import IAAS
from .membership import Membership
from .otp import OTP
from .reporting import Reporting
from .repository import Repository
from .scheduler import Scheduler
from .scm import SCM
from .security import Security
from .training import Training
from .vault import Vault

__all__ = [
    'AppManager',
    'Asset',
    'Circuit',
    'Contacts',
    'Documentation',
    'Financial',
    'Helpdesk',
    'IAAS',
    'Membership',
    'OTP',
    'Reporting',
    'Repository',
    'Scheduler',
    'SCM',
    'Security',
    'Training',
    'Vault',
]
