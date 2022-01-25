__all__ = [
    'DataSourceTypeNotRecognized',
    'LabelNotFound',
    'APIConnectionError',
    'DataStreamError',
    'WrongDatabaseSchemaOrTable',
    'WrongFileLocation',
    'WrongLocationProperty',
    'UnsupportedConnection',
    'UnsupportedOutputConnection',
    'MissingFileName',
    'FileUploadFailed',
    'FlightServiceInfoNotAvailable'
]

#  (C) Copyright IBM Corp. 2021.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from ibm_watson_machine_learning.wml_client_error import WMLClientError


class DataSourceTypeNotRecognized(WMLClientError, NotImplementedError):
    def __init__(self, value_name, reason=None):
        WMLClientError.__init__(self, f"Data source type: {value_name} not recognized!", reason)


class LabelNotFound(WMLClientError, KeyError):
    def __init__(self, value_name, reason=None):
        WMLClientError.__init__(self, f"Cannot find label: {value_name}", reason)


class APIConnectionError(WMLClientError, ConnectionError):
    def __init__(self, value_name, reason=None):
        WMLClientError.__init__(self, f"Cannot connect to: {value_name}", reason)


class DataStreamError(WMLClientError, ConnectionError):
    def __init__(self, value_name=None, reason=None):
        WMLClientError.__init__(self, "Cannot fetch data via Flight Service. Try again.", reason)


class WrongLocationProperty(WMLClientError, ConnectionError):
    def __init__(self, value_name=None, reason=None):
        WMLClientError.__init__(self, "Cannot fetch data via Flight Service. Try again.", reason)


class WrongFileLocation(WMLClientError, ValueError):
    def __init__(self, value_name=None, reason=None):
        WMLClientError.__init__(self, "Cannot fetch data via Flight Service. Try again.", reason)


class WrongDatabaseSchemaOrTable(WMLClientError, ValueError):
    def __init__(self, value_name=None, reason=None):
        WMLClientError.__init__(self, "Cannot fetch data via Flight Service. Try again.", reason)


class UnsupportedOutputConnection(WMLClientError, ValueError):
    def __init__(self, connection_id=None, reason=None):
        WMLClientError.__init__(self, f"Connection with ID: {connection_id} is not supported as an Output connection",
                                reason)


class UnsupportedConnection(WMLClientError, ValueError):
    def __init__(self, conn_type=None, reason=None):
        WMLClientError.__init__(self, f"Connection type: {conn_type} is not supported.",
                                reason)


class MissingFileName(WMLClientError, KeyError):
    def __init__(self, reason=None):
        WMLClientError.__init__(self, f"Connection location requires a 'file_name' to be specified.",
                                reason)


class FileUploadFailed(WMLClientError, ConnectionError):
    def __init__(self, reason=None):
        WMLClientError.__init__(self, f"Failed to upload file.",
                                reason)


class FlightServiceInfoNotAvailable(WMLClientError, ConnectionError):
    def __init__(self, reason=None):
        WMLClientError.__init__(self, "To use the data connection service from outside of Watson Studio "
                                      "you must explicitly set environment variables 'FLIGHT_SERVICE_LOCATION' "
                                      "and 'FLIGHT_SERVICE_PORT' to point to the location of the Flight Server. "
                                      "Ask your cluster administrator for the external route "
                                      "to the Flight Server for data connections.",
                                reason)
