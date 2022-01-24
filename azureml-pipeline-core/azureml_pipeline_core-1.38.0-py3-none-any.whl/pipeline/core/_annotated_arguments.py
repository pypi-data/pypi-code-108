# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# Classes to define the argument list for a step, which can include inputs, outputs, parameters, and literal strings


class _InputArgument(object):
    """
    A reference to an input in a  module argument list
    """

    def __init__(self, name):
        """Initialize _InputArgument.
        :param name: Name of the input
        :type name: str
        """
        self.name = name

    def __str__(self):
        """
        __str__ override.

        :return: A string representation of the input argument.
        :rtype: str
        """
        return "input:{0}".format(self.name)


class _OutputArgument(object):
    """
    A reference to an output in a  module argument list
    """

    def __init__(self, name):
        """Initialize _OutputArgument.
        :param name: Name of the output
        :type name: str
        """
        self.name = name

    def __str__(self):
        """
        __str__ override.

        :return: A string representation of the output argument.
        :rtype: str
        """
        return "output:{0}".format(self.name)


class _ParameterArgument(object):
    """
    A reference to a parameter in a  module argument list
    """

    def __init__(self, name):
        """Initialize _ParameterArgument.
        :param name: Name of the parameter
        :type name: str
        """
        self.name = name

    def __str__(self):
        """
        __str__ override.

        :return: A string representation of the parameter argument.
        :rtype: str
        """
        return "parameter:{0}".format(self.name)


class _StringArgument(object):
    """
    A string literal in a  module argument list
    """

    def __init__(self, text):
        """Initialize _StringArgument.
        :param text: Text of the argument
        :type text: str
        """
        self.text = text

    def __str__(self):
        """
        __str__ override.

        :return: A string representation of the string argument.
        :rtype: str
        """
        return self.text
