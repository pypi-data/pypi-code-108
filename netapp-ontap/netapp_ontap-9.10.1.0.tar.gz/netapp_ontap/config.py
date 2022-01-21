"""
Copyright &copy; 2021 NetApp Inc. All rights reserved.

This module contains the global configuration options and related functions for the library.
"""

from typing import Optional

from netapp_ontap.host_connection import HostConnection

CONNECTION = None  # type: Optional[HostConnection]
"""This `netapp_ontap.host_connection.HostConnection` object, if set, is used
as the default connection for all library operations if no other connection is set
at a more specific level. The hierarchy of lookups is:

- Any connection being used as a context manager (i.e. inside a with block)
- The connection set on a resource using `netapp_ontap.resource.Resource.set_connection`
- The global connection set here.

If none of these are set, an exception will be raised when a request is attempted.
"""

ENABLE_VALIDATIONS = True
"""If set to True, the library will enforce validations, e.g. minimum and maximum values,
for object fields as specified in the API spec. If a field does not meet the validation
criteria when being sent to the API host, a `netapp_ontap.error.NetAppRestError` will be
raised with the reason for the violation. If this value is set to False, then no
validation will take place prior to sending the values to the API host.
"""

RAISE_API_ERRORS = True
"""If set to True, the library will raise an exception if a request fails. If set
to false, the library will not raise an exception and the application is responsible
to check if the response was an error or not.
"""

RETRY_API_ON_ERROR = False
"""If set to True, more granular retry functionality will
 be enabled for this library.  An exception will only be
 raised when retry attempts are exhausted."""

RETRY_API_ERROR_CODES = [429, 500, 502, 503, 504]
"""If the status code returned does not exist in this
list, no additional retry attempts will be made."""

RETRY_API_HTTP_METHODS = ["GET", "PATCH"]
"""If a request is made with an HTTP method not in this
list, no retry attempts will be made."""

RETRY_API_ATTEMPTS = 5
"""The number of retry attempts that will be made before
raising an exception to proapagate the failure."""

RETRY_API_BACKOFF_FACTOR = 1.0
"""This setting configures the delay between retry attempts
according to the following formula:
    {backoff factor} * (2 ** ({number of total retries} - 1))
"""

def set_error_model(raise_api_errors: bool = True) -> None:
    """Set the error model for the library.

    By default, operations (GET, POST, PATCH, DELETE) will raise an exception if
    the response code from the host is >= 400. The exception object will contain
    the response so that it can be handled in the client code.

    Optionally, settings raise_api_errors to False will return the response and
    the client will be responsible for checking and handling any errors.

    Args:
        raise_api_errors: If set to true, the library will raise errors back to the
            application. If set to faise, errors will not be raised and the
            application must verify the responses itself.
    """

    global RAISE_API_ERRORS  # pylint: disable=global-statement
    RAISE_API_ERRORS = raise_api_errors
