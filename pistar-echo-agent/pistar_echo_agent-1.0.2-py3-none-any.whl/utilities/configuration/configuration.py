"""
description: |
    this module provides the class Configuration.
    the class Configuration can be initialized by file path or yaml string.
    you can access its attribute by __getattr__ or __getitem__.
"""

from pistar_echo_agent.utilities.exceptions import MissingKeyException
from pistar_echo_agent.utilities.exceptions import SyntaxException
from pistar_echo_agent.utilities.exceptions import InvalidTypeException


class Configuration(dict):
    """
    description: |
        this class is used to load and modify the configuration file.
        you can used __getattr__ and __setitem__ to access its attributes.
    """

    def __init__(self, content=None):
        """
        description: this is the constructor.
        """

        super().__init__()

        content = content if content else dict()

        for key, value in content.items():
            if isinstance(value, dict):
                self[key] = Configuration(content=value)
            else:
                self[key] = value

    def __getattr__(self, key):
        """
        description: |
            override the member function __getattr__.
            if access a nonexist attribute, return None.
        """

        return None

    def __setitem__(self, key, value):
        """
        description: |
            override the member function __getitem__.
            call __setattr__ and __setitem__.
        """
        super().__setattr__(key, value)
        super().__setitem__(key, value)

    def __setattr__(self, key, value):
        """
        description: override the member function __setattr__.
        """

        self[key] = value

    def get_value(self, keys):
        """
        description: this function is used to get attribute with keys,
                     such as loggers.user.debug.
        arguments:
            keys:
                type: str
                description: the keys splitted with dot.
        return:
            type: any
        """

        iterator = self
        for key in keys.split('.'):
            if key not in iterator:
                raise MissingKeyException(key=keys)
            iterator = iterator[key]

        if not isinstance(iterator, str):
            raise InvalidTypeException(type(iterator))

        return iterator

    def set_value(self, expression):
        """
        description: this function is used to set attribute with keys,
                     such as loggers.user.level=debug.
        arguments:
            expression:
                type: str
                description: the assignment expression with format keys=value.
        """

        if '=' not in expression:
            raise SyntaxException(expression=expression)

        keys, value = expression.split('=', 1)
        iterator = self

        for index, key in enumerate(keys.split('.')):
            if key not in iterator:
                raise MissingKeyException(key=keys)

            if index < keys.count('.'):
                iterator = iterator[key]
            else:
                iterator[key] = value

    def to_dictionary(self):
        """
        description: this function is used to
                     convert the configuration to dictionary.
        """

        return {
            key: value.to_dictionary()
            if isinstance(value, Configuration)
            else value for key, value in self.items()
        }
