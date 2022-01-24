# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from msrest.serialization import Model
from msrest.exceptions import HttpOperationError


class ErrorResponse(Model):
    """The error response.

    :param error: The top level error that occurred.
    :type error: ~reinforcementlearning.models.RootError
    :param correlation: Dictionary containing correlation details for the
     error.
    :type correlation: dict[str, str]
    :param environment: The hosting environment.
    :type environment: str
    :param location: The Azure region.
    :type location: str
    :param time: The time in UTC.
    :type time: datetime
    """

    _attribute_map = {
        'error': {'key': 'error', 'type': 'RootError'},
        'correlation': {'key': 'correlation', 'type': '{str}'},
        'environment': {'key': 'environment', 'type': 'str'},
        'location': {'key': 'location', 'type': 'str'},
        'time': {'key': 'time', 'type': 'iso-8601'},
    }

    def __init__(self, **kwargs):
        super(ErrorResponse, self).__init__(**kwargs)
        self.error = kwargs.get('error', None)
        self.correlation = kwargs.get('correlation', None)
        self.environment = kwargs.get('environment', None)
        self.location = kwargs.get('location', None)
        self.time = kwargs.get('time', None)


class ErrorResponseException(HttpOperationError):
    """Server responsed with exception of type: 'ErrorResponse'.

    :param deserialize: A deserializer
    :param response: Server response to be deserialized.
    """

    def __init__(self, deserialize, response, *args):

        super(ErrorResponseException, self).__init__(deserialize, response, 'ErrorResponse', *args)
