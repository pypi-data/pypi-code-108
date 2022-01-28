# -*- coding: utf-8 -*-

class InvalidSSHConnectionAttribute(Exception):
    """
        Raised when SSHConnection has one or
        more invalid attributes
    """
pass

class UserOrHostnameNotInformed(Exception):
    """
        Raised when user or hostname were not
        informed when trying to connect or add
        a new connection
    """
pass

class SSHConnectionNotFoundError(Exception):
    """
       Raised when an SSHConnection was not found
    """
pass

class SSHConnectionNameNotInformed(Exception):
    """
        Raised when a name was not informed 
        when trying to add a new connection
    """
pass

