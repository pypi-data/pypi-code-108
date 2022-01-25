"""
description: this module provides the function check_arguments.
"""

from pistar_echo_agent.utilities.constants import API_ARGUMENT_FIELD

from pistar_echo_agent.utilities.exceptions import ServerMissingArgumentSchemaException
from pistar_echo_agent.utilities.exceptions import ServerMissingArgumentSchemaFieldException
from pistar_echo_agent.utilities.exceptions import ServerUnknownArgumentSchemaException


def check_arguments(document, specification, application_name):
    """
    description: this function is used to check the arguments of requests.
    """
    required_fields = [
        API_ARGUMENT_FIELD.FROM,
        API_ARGUMENT_FIELD.TYPE,
        API_ARGUMENT_FIELD.DESCRIPTION
    ]
    defaults = list(specification.defaults) \
        if specification.defaults else list()

    for argument_name in specification.args[::-1]:
        if argument_name not in document:
            raise ServerMissingArgumentSchemaException(
                argument_name=argument_name,
                application_name=application_name
            )

        for field_name in required_fields:
            if field_name not in document[argument_name]:
                raise ServerMissingArgumentSchemaFieldException(
                    field_name=field_name,
                    argument_name=argument_name,
                    application_name=application_name
                )

        if defaults:
            document[argument_name][API_ARGUMENT_FIELD.DEFAULT] = defaults.pop(-1)
        else:
            document[argument_name][API_ARGUMENT_FIELD.REQUIRED] = True

    for schema_name in document.keys():
        if schema_name not in specification.args:
            raise ServerUnknownArgumentSchemaException(
                schema_name=schema_name,
                application_name=application_name
            )
