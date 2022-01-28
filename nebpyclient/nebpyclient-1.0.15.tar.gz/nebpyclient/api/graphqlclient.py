#
# Copyright 2020 Nebulon, Inc.
# All Rights Reserved.
#
# DISCLAIMER: THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO
# EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES
# OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#

import platform
import os
import json
from enum import Enum, IntEnum
from requests import Session
from datetime import datetime

__all__ = [
    "NebMixin",
    "GraphQLParam",
    "GraphQLClient",
    "GraphQLError"
]

# TODO: Refactor methods - works for now

_API_SERVER_URI = "https://ucapi.nebcloud.nebuloninc.com/query"
_API_TIMEOUT_SECONDS = 60


class ConsoleColor(IntEnum):
    """Color used for printing to the console"""
    Gray = 0
    Rad = 1
    Green = 2
    Yellow = 3
    Blue = 4
    Purple = 5
    LightBlue = 6
    White = 7


def _color_str(
        text: str,
        color: ConsoleColor = None,
        background_color: ConsoleColor = None
):
    """Converts a string to a color string for printing in the console

    :param text: The text to print to the console
    :type text: str
    :param color: The foreground color
    :type color: ConsoleColor, optional
    :param background_color: The background color
    :type background_color: ConsoleColor, optional

    :returns str: A string that is formatted to be colorized when printed to
        the console
    """

    if color is None and background_color is None:
        return text

    c1 = 98
    c2 = 98

    if color is not None:
        c1 = int(color) + 90

    if background_color is not None:
        c2 = int(background_color) + 100

    return f"\033[{c1}m\033[{c2}m{text}\033[0m"


class NebMixin:
    """Base class for GraphQL client mixins"""

    def _print(self, text, verbose: bool = False):
        """Print to the console"""
        pass

    def _mutation(
            self,
            name: str,
            params: dict,
            fields: [str] = None
    ) -> any:
        """Run a GraphQL mutation.

        :param name: Name of the mutation
        :type name: str
        :param params: A dict of GraphQLParams that shall be supplied to the
            GraphQL mutation.
        :type params: dict
        :param fields: A list of fields that shall be returned by the
            GraphQL query
        :type fields: [str], optional

        :returns any: The response from the server

        :raises GraphQLError:  An error raised by the GraphQL endpoint.
        """
        pass

    def _query(
            self,
            name: str,
            params: dict,
            fields: [str] = None
    ) -> any:
        """Run a GraphQL query.

        :param name: Name of the query
        :type name: str
        :param params: A dict of GraphQLParams that shall be supplied to the
            GraphQL query.
        :type params: dict
        :param fields: A list of fields that shall be returned by the
            GraphQL query
        :type fields: [str], optional

        :returns any: The response from the server

        :raises GraphQLError:  An error raised by the GraphQL endpoint.
        """
        pass


class GraphQLParam:
    """A parameter for a GraphQL query (query or mutation)"""

    def __init__(
            self,
            value: any,
            type_name: str,
            mandatory: bool = False
    ):
        """Constructs a new GraphQL parameter

        :param value: The value that shall be supplied to the GraphQL query
        :type value: any
        :param type_name: The name of the type of the provided value and how
            the GraphQL server should interpret the value
        :type type_name: str
        :param mandatory: Indicates if the provided value is considered
            mandatory in the GraphQL schema. It will append a `!` to the
            type name.
        :type mandatory: bool, optional
        """

        self.__value = value
        self.__type_name = type_name
        self.__mandatory = mandatory

    @property
    def value(self) -> any:
        """The value to supply to the GraphQL query (query or mutation)"""
        return self.__value

    @property
    def type_name(self) -> str:
        """They type name of the provided value as per the GraphQL schema"""
        return self.__type_name

    @property
    def type_spec(self) -> str:
        """Formatted type name for the GraphQL query (query or mutation)"""
        if self.mandatory:
            return f"{self.__type_name}!"
        return self.__type_name

    @property
    def mandatory(self) -> bool:
        """Indicates if the provided GraphQL parameter is mandatory"""
        return self.__mandatory


class GraphQLError(Exception):
    """An error with the GraphQL endpoint"""

    def __init__(
            self,
            request: str = None,
            response: dict = None,
            status_code: int = None
    ):
        """Constructs a new GraphQLError

        :param request: The string body that was sent to nebulon ON
        :type request: str, optional
        :param response: The response from nebulon ON as a dict
        :type response: str, optional
        :param status_code: The HTTP status code from the API server
        :type status_code: int, optional
        """
        self.__errors = []
        self.__status_code = status_code
        self.__request = request

        for error in response["errors"]:
            self.errors.append(error["message"])

    @property
    def errors(self) -> [str]:
        """List of error messages in this GraphQLError"""
        return self.__errors

    @property
    def status_code(self) -> int:
        """HTTP status code from the API server response"""
        return self.__status_code

    @property
    def request(self) -> str:
        """The request that was sent to the server as a string"""
        return self.__request

    def __str__(self):
        result = "<GraphQLException> "
        if self.status_code is not None:
            result += f"HTTP {self.status_code} "
        for error in self.errors:
            result += f" {error}\n"
        if self.request is not None:
            result += f" {self.request}"

        return result


class GraphQLClient:
    """GraphQL client to make requests with nebulon ON"""

    def __init__(
            self,
            verbose: bool = False,
            client_name: str = None,
            client_version: str = None,
    ):
        """Constructs a new GraphQL client

        :param verbose: If set to ``True`` debug information is printed to the
            console
        :type verbose: bool, optional
        :param client_name: Allows specifying a custom application name for auditing
        :type client_name: str, optional
        :param client_version: Allows specifying a custom application version for auditing
        :type client_version: str, optional
        """

        # initialize a reusable session
        self.session = Session()

        # setup platform information for audit log
        client_system = platform.system()
        client_release = platform.release()

        if client_name is None:
            client_name = "nebpyclient"

        if client_version is None:
            try:
                dir_name = os.path.dirname(__file__)
                filename = os.path.join(dir_name, '../VERSION')

                with open(filename, "r") as fh:
                    client_version = fh.read().strip()

            except OSError:
                client_version="unknown"

        self.session.headers.update({
            "Nebulon-Client-App": f"{client_name}/{client_version}",
            "Nebulon-Client-Platform": f"{client_system}/{client_release}"
        })

        self.uri = _API_SERVER_URI
        self.verbose = verbose

    def _print(
            self,
            text: str,
            verbose: bool = False,
            color: ConsoleColor = None,
            background: ConsoleColor = None
    ):
        """Conditionally write to the console

        :param text: The string to print
        :type text: str
        :param verbose: If the information is considered debug info. By default
            the information is considered not to be verbose.
        :type verbose: bool, optional
        :param color: The foreground color to use when writing to the console
        :type color: ConsoleColor, optional
        :param background: The background color to use when writing to the
            console
        :type background: ConsoleColor, optional
        """
        if verbose and not self.verbose:
            return

        color_str = _color_str(
            text=text,
            color=color,
            background_color=background
        )
        print(color_str)

    def _call(
            self,
            name: str,
            method: str,
            variables: dict = None,
            files: dict = None
    ) -> any:
        """Makes a GraphQL request to the specified server

        :param name: The GraphQL method name
        :type name: str
        :param method: The GraphQL method in string representation
        :type method: str
        :param variables: The GraphQL variables for the method
        :type variables: dict, optional
        :param files: List of files to upload to the GraphQL endpoint
        :type files: dict, optional

        :returns any: The response of the GraphQL endpoint

        :raises GraphQLError: An error with the GraphQL endpoint.
        """
        uri = _API_SERVER_URI

        dict_vars = self._convert_dict(variables)

        # DEBUG INFORMATION
        if self.verbose:
            self._print("URI")
            self._print(uri, color=ConsoleColor.Yellow)
            self._print("DATA")
            self._print(method, color=ConsoleColor.Yellow)
            self._print("VARIABLES")
            self._print(
                json.dumps(dict_vars, indent=2),
                color=ConsoleColor.Yellow
            )
            start = datetime.now()

        # initialize payload
        data = dict()

        # if there are files, do a multi-part upload with the files
        if files is not None and len(files.keys()) > 0:
            payload = dict()
            payload["query"] = method
            payload["variables"] = dict_vars
            payload_json = json.dumps(payload)

            file_map = {
                str(i): [f"variables.{path}"] for i, path in enumerate(files)
            }

            file_streams = {
                str(i): files[path] for i, path in enumerate(files)
            }

            data["map"] = (None, json.dumps(file_map), "application/json")
            data["operations"] = (None, payload_json, "application/json")

            for file_stream in file_streams.items():
                with open(file_stream[1], "rb") as f:
                    data[file_stream[0]] = (file_stream[1], f.read())

            # make the request
            response = self.session.post(uri, files=data)
        else:
            data["query"] = method
            data["variables"] = dict_vars
            response = self.session.post(uri, json=data)

        json_data = response.json()

        # DEBUG INFORMATION
        if self.verbose:
            end = datetime.now()
            duration = ((end - start).microseconds / 1000)
            self._print("DURATION")
            self._print("%.2fms" % duration, color=ConsoleColor.Yellow)
            self._print("RESPONSE")
            self._print(
                json.dumps(json_data, indent=2),
                color=ConsoleColor.Yellow
            )
            self._print("")

        # Check for Errors (any HTTP code outside of 2xx)
        if not (200 <= response.status_code < 300) or "errors" in json_data:
            raise GraphQLError(
                request=method,
                response=json_data,
                status_code=response.status_code
            )

        # Make sure only the relevant contents are returned
        if "data" in json_data and name in json_data["data"]:
            return json_data["data"][name]

        return None

    @classmethod
    def _convert_dict(
            cls,
            obj: any
    ) -> any:
        """Converts types to JSON compliant types

        :param obj: The source dict to convert
        :type obj: any
        """

        if obj is None:
            return None

        if isinstance(obj, GraphQLParam):
            obj = obj.value

        if isinstance(obj, dict):
            result = dict()
            for key, value in obj.items():
                processed_value = cls._convert_dict(value)
                if processed_value is not None:
                    result[key] = processed_value
            return result

        if isinstance(obj, list):
            return [cls._convert_dict(v) for v in obj]

        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%dT%H:%M:%SZ")

        if isinstance(obj, Enum):
            return str(obj.value)

        if hasattr(obj, "as_dict"):
            dict_value = getattr(obj, "as_dict", None)
            return cls._convert_dict(dict_value)

        return obj

    @classmethod
    def _extract_files(
            cls,
            params: dict
    ) -> tuple:
        """Extracts file uploads from GraphQL parameters"""

        if params is None:
            return None, {}
        files = {}

        def _extract_files_recursively(path: str, obj: any):
            nonlocal files
            if isinstance(obj, list):
                return [_extract_files_recursively(f"{path}.{k}", v)
                        for k, v in enumerate(obj)]
            elif isinstance(obj, dict):
                null_obj = {}
                for k, v in obj.items():
                    null_obj[key] = _extract_files_recursively(f"{path}.{k}", v)
                return null_obj
            elif isinstance(obj, GraphQLParam):
                # check if it is a file upload (Upload)
                if obj.type_name == "Upload":
                    files[path] = obj.value
                    return GraphQLParam(None, obj.type_name, obj.mandatory)

                # otherwise process the parameter value
                tmp = _extract_files_recursively(path, obj.value)
                return GraphQLParam(tmp, obj.type_name, obj.mandatory)

            # every other case
            return obj

        null_variables = {}
        for key, value in params.items():
            null_variables[key] = _extract_files_recursively(key, value)

        return null_variables, files

    def _mutation(
            self,
            name: str,
            params: dict,
            fields: [str]
    ) -> any:
        """Run a GraphQL mutation.

        :param name: The name of the mutation
        :type name: str
        :param params: Parameters for the GraphQL mutation
        :type params: dict
        :param fields: Fields to query the result for
        :type fields: [str]

        :returns any: The response from the server

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # DEBUG INFORMATION
        self._print(
            text=f"# MUTATION: {name} ----------",
            verbose=True,
            background=ConsoleColor.Blue
        )

        parameters, files = self._extract_files(params)
        method = self._format_method("mutation", name, parameters, fields)
        return self._call(name, method, parameters, files)

    def _query(
            self,
            name: str,
            params: dict,
            fields: [str]
    ) -> any:
        """Run a GraphQL query.

        :param name: The name of the query
        :type name: str
        :param params: Parameters for the GraphQL query
        :type params: dict
        :param fields: Fields to query the result for
        :type fields: [str]

        :returns any: The response from the server

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # DEBUG INFORMATION
        self._print(
            text=f"# QUERY: {name} ----------",
            verbose=True,
            background=ConsoleColor.Purple
        )

        method = self._format_method("query", name, params, fields)
        return self._call(name, method, params)

    @classmethod
    def _format_method(
            cls,
            method: str,
            name: str,
            params: dict = None,
            fields: [str] = None
    ) -> str:
        """Create a str formatted GraphQL method from the provided parameters

        :param method: Method type oof the GraphQL query. This can either be
            a mutation or a query.
        :type method: str
        :param name: Name of the GraphQL query (query or mutation) to execute
        :type name: str
        :param params: Parameters for the GraphQL query
        :type params: dict, optional
        :param fields: List of fields to return by the GraphQL query
        :type fields: [str], optional

        :returns str: A str encoded GraphQL query.

        :raises ValueError: An error when invalid parameters were supplied
        """

        variable_specs = []
        variable_mappings = []

        if params is not None:
            for key, value in params.items():

                # if it is a tuple, it contains needed info for parameter type
                # (value, type_name, mandatory)
                if isinstance(value, GraphQLParam):
                    variable_specs.append(f"${key}:{value.type_spec}")
                    variable_mappings.append(f"{key}: ${key}")
                    continue

                # raise an error so we know if we missed specifying a
                # graphQL parameter.
                raise ValueError(f"parameter {key} is not a GraphQLParam")

        if fields is not None:
            query_fields = ",".join(fields)
        else:
            query_fields = ""

        if len(variable_specs) == 0 and len(query_fields) == 0:
            return "%s{%s}" % (method, name)

        if len(variable_specs) == 0 and len(query_fields) > 0:
            return "%s{%s{%s}}" % (method, name, query_fields)

        if len(variable_specs) > 0 and len(query_fields) == 0:
            return "%s(%s){%s(%s)}" % (
                method,
                ",".join(variable_specs),
                name,
                ", ".join(variable_mappings)
            )

        return "%s(%s){%s(%s){%s}}" % (
            method,
            ",".join(variable_specs),
            name,
            ", ".join(variable_mappings),
            query_fields
        )
