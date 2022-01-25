"""
description: this module provides the function get_arguments.
"""

import re
import json

from pistar_echo_agent.utilities.constants import ENCODE
from pistar_echo_agent.utilities.constants import API_DOCUMENT_FIELD
from pistar_echo_agent.utilities.constants import API_ARGUMENT_FIELD
from pistar_echo_agent.utilities.constants import FROM

from pistar_echo_agent.utilities.exceptions import ServerWrongArgumentTypeException
from pistar_echo_agent.utilities.exceptions import ServerMissingArgumentInRequestException
from pistar_echo_agent.utilities.exceptions import ServerRequestBodyFormatException


def get_type(schema):
    """
    description: this function is used to get type from the schema.
    """

    data_type = schema[API_ARGUMENT_FIELD.TYPE]
    if data_type == "dict":
        return type({})
    elif data_type == "list":
        return type([])
    else:
        return type("")


def get_arguments(request, specification, document, application_name):
    """
    description: this function is used to get arguments from the request.
    """
    defaults = dict()
    specification_defaults = specification.defaults if specification.defaults else list()
    for argument_name, argument_value in zip(specification.args[::-1], specification_defaults):
        defaults[argument_name] = argument_value

    path_arguments = re.search(document[API_DOCUMENT_FIELD.API_PATH], request.uri.split('?')[0]).groupdict()

    arguments = dict()
    for argument_name in specification.args:
        schema = document[API_DOCUMENT_FIELD.ARGUMENTS][argument_name]

        if schema[API_ARGUMENT_FIELD.FROM] == FROM.QUERY:
            # if it can not found in request.
            if argument_name in request.query_arguments:
                argument_type = get_type(schema)
                arguments[argument_name] = argument_type(request.query_arguments[argument_name][0].decode(ENCODE.UTF8))
                continue

            # else if it has default value.
            if argument_name in defaults:
                arguments[argument_name] = defaults[argument_name]
                continue

            raise ServerMissingArgumentInRequestException(application_name, schema[API_ARGUMENT_FIELD.FROM],
                                                          argument_name)

        if schema[API_ARGUMENT_FIELD.FROM] == FROM.PATH:
            deal_argument(argument_name, schema, arguments, defaults, path_arguments, application_name)
            continue

        if schema[API_ARGUMENT_FIELD.FROM] == FROM.HEADER:
            deal_argument(argument_name, schema, arguments, defaults, request.headers, application_name)
            continue

        if schema[API_ARGUMENT_FIELD.FROM] == FROM.BODY:
            try:
                body = json.loads(request.body.decode(ENCODE.UTF8))
            except json.decoder.JSONDecodeError as exception:
                raise ServerRequestBodyFormatException(application_name, exception.args[0]) from exception

            if argument_name in body:
                check_argument_type(schema, body, argument_name, application_name)
                arguments[argument_name] = body[argument_name]
                continue

            if argument_name in defaults:
                arguments[argument_name] = defaults[argument_name]
                continue

        raise ServerMissingArgumentInRequestException(application_name, schema[API_ARGUMENT_FIELD.FROM], argument_name)
    return arguments


def deal_argument(argument_name, schema, arguments, defaults, dictionary, application_name):
    if argument_name in dictionary:
        argument_type = get_type(schema)
        arguments[argument_name] = argument_type(dictionary[argument_name])
        return None

    if argument_name in defaults:
        arguments[argument_name] = defaults[argument_name]
        return None

    raise ServerMissingArgumentInRequestException(
        argument_name=argument_name,
        application_name=application_name,
        source=schema[API_ARGUMENT_FIELD.FROM]
    )


def check_argument_type(schema, body, argument_name, application_name):
    data_type = schema[API_ARGUMENT_FIELD.TYPE]
    type_dict = {"dict": dict, "list": list, "str": str, "bool": bool, "int": int, "float": float}
    if not isinstance(body[argument_name], type_dict.get(data_type)):
        raise ServerWrongArgumentTypeException(
            application_name=application_name,
            argument_name=argument_name,
            data_type=data_type,
            actual_type=type(body[argument_name])
        )
