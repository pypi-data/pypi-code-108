# -*- coding: utf-8 -*-

"""
This file contains custom Exceptions that are used within the CloudCIX API library
"""


class CloudCIXAuthException(Exception):
    """
    This exception is raised when there are errors returned from the methods used to generate Tokens;
        - `cloudcix.auth.get_token`
        - `cloudcix.auth.get_admin_token`

    The exception will contain both an `error_code` and `detail` field, giving information on the error itself.
    """

    def __init__(self, error_code, detail):
        """
        Intialize an instance of the exception.

        :param error_code: The error code from the API
        :type error_code: str
        :param detail: The error message from the API
        :type detail: str
        """
        self.error_code = error_code
        self.detail = detail

    def __str__(self):
        """
        Return a full string representation of the Exception
        """
        return '{}: {}'.format(self.error_code, self.detail)

    def __repr__(self):
        """
        Return a short string representation of the Exception
        """
        return '<CloudCIXAuthException [{}]>'.format(self.error_code)


class ImproperlyConfiguredException(Exception):
    """
    This exception is raised when the CloudCIX library has not been properly configured.

    This can usually happen in the following ways:

        - The ``settings`` file has not been specified in the environment variables
        - The ``settings`` file is missing a required setting
          (see `Required Settings <https://cloudcix.github.io/python-cloudcix/readme.html#required-settings>`_)
    """
    pass


class MissingClientKeywordArgumentException(Exception):
    """
    This exception is raised when a method is called on a service that requires one or more keyword arguments that were
    not supplied by the user.

    For example: if a service's URL is ``address/{address_id}/link/``, the call to ``Membership.address_link.list`` must
    include an ``address_id`` keyword argument, or else this exception will be thrown.

    The message for the exception will look like this;
    ``The "address_id" keyword argument is required by <Client [{.../address/{address_id}/link/}]>``.
    """

    def __init__(self, name, cli):
        """
        Initialize an instance of the exception

        :param name: The name of the keyword argument that is missing
        :type name: str
        :param cli: The Client instance that is missing the keyword argument
        :type cli: cloudcix.client.Client
        """
        self.name = name
        self.message = 'The "{}" keyword argument is required by {}'.format(name, cli)

    def __str__(self):
        return self.message

    def __repr__(self):
        return '<MissingClientKeywordArgument [{}]>'.format(self.name)
