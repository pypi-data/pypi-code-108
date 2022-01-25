"""
description: this module provides exceptions which may appear in pistar echo agent.
"""


class ServerMissingArgumentSchemaException(Exception):
    """
    description: if the schema of argument does not exist,
                 raise this exception.
    """

    def __init__(self, application_name, argument_name):
        super().__init__(
            f"cannot find the schema of argument '{argument_name}' "
            f"in application '{application_name}'"
        )


class ServerMissingArgumentSchemaFieldException(Exception):
    """
    description: if an argument field does not exist, raise this exception.
    """

    def __init__(self, field_name, application_name, argument_name):
        super().__init__(
            f"cannot find field '{field_name}' in schema of argument "
            f"'{argument_name}' in application '{application_name}'"
        )


class ServerMissingDocumentFieldException(Exception):
    """
    description: if these is no __doc__ in an application,
                 raise this exception.
    """

    def __init__(self, application_name, field_name):
        super().__init__(
            f"cannot find the field '{field_name}' in application '{application_name}'"
        )


class ServerUnknownArgumentSchemaException(Exception):
    """
    description: if there is an unknown argument in the arguments schema,
                 raise this exception.
    """

    def __init__(self, application_name, schema_name):
        super().__init__(
            f"unknown schema '{schema_name}' in application '{application_name}'"
        )


class ServerWrongArgumentTypeException(Exception):
    """
    description: if the argument type is wrong, raise this exception.
    """

    def __init__(self, application_name, argument_name, data_type, actual_type):
        super().__init__(
            f"wrong type of argument '{argument_name}' expected type is {data_type}, "
            f"actual type is {actual_type} in application '{application_name}'"
        )


class ServerWrongArgumentValueException(Exception):
    """
    description: if the argument value is wrong, raise this exception.
    """

    def __init__(self, argument_name, actual_value):
        super().__init__(
            f"wrong value of argument '{argument_name}' actual value is '{actual_value}'."
        )


class ServerMissingArgumentInRequestException(Exception):
    """
    description: if the request does not contain the argument,
                 raise this exception.
    """

    def __init__(self, application_name, source, argument_name):
        super().__init__(
            f"cannot find argument '{argument_name}' in '{source}' of "
            f"request in application_name '{application_name}'"
        )


class ServerRequestBodyFormatException(Exception):
    """
    description: if the format of request body is invalid,
                 raise this exception.
    """

    def __init__(self, application_name, detail):
        super().__init__(
            f"the request body of application '{application_name}' "
            f"must be in json format, the detail is {detail}"
        )
