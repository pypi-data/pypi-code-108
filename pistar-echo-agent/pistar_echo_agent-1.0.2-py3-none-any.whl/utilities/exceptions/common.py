"""
description: this module provides common exceptions.
"""


class MissingKeyException(Exception):
    """
    description: if there is no the specific key in configuration,
                 raise this exception.
    """

    def __init__(self, key):
        super().__init__(
            'cannot find the key \'{key}\' in configuration'.format(key=key)
        )


class SyntaxException(Exception):
    """
    description: if there is syntax error, raise this exception.
    """

    def __init__(self, expression):
        super().__init__(
            'there is syntax error in the expression \'{expression}\''.format(expression=expression)
        )


class InvalidTypeException(Exception):
    """
    description: if the type is not string, raise this exception.
    """

    def __init__(self, type_name):
        super().__init__(
            'invalid type \'{type_name}\', expect string'.format(type_name=type_name)
        )
