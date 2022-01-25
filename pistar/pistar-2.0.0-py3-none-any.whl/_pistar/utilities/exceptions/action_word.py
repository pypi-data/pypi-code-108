"""
this is the set of exceptions of action word.
"""


class ActionWordException(Exception):
    """
    description: this is the base class action word exception.
    """


class MissingPropertyException(Exception):
    """
    description: if any properties are missing in action word docstring,
                 raise this exception.
    """

    def __init__(self, property_name, value_name):
        message = f"cannot find property '{property_name}' in '{value_name}'"
        super().__init__(message)


class TypeMismatchException(Exception):
    """
    description: if the argument's type does not match the docstring,
                 raise this exception.
    """

    def __init__(self, name, value, expect_type):
        message = f"{name} = {value}, but the type should be {expect_type}"
        super().__init__(message)


class AssertionFailureException(Exception):
    """
    description: if the assertion of argument fails, raise this exception.
    """

    def __init__(self, name, value, assertion):
        message = f"{name} = {value}, cannot pass the assertion '{assertion}'"
        super().__init__(message)


class EnumerationFailureException(Exception):
    """
    description: if the argument value is not in enumerate,
                 raise this exception.
    """

    def __init__(self, name, value, enumeration):
        message = f"{name} = {value}, does not in enumeration {enumeration}"
        super().__init__(message)


class MissingFieldInActionWordException(ActionWordException):
    """
    description: if the argument's type does not match the docstring,
                 raise this exception.
    """

    def __init__(self, field_name, action_word_name):
        message = f"cannot find field '{field_name}' in action word '{action_word_name}'"
        super().__init__(message)


class UnknownStatusException(ActionWordException):
    """
    description: if status of action word is not in enumeration,
                 raise this exception.
    """

    def __init__(self, status, action_word_name):
        message = f"unknown status '{status}' of the action word '{action_word_name}'"
        super().__init__(message)


class DisabledActionWordException(ActionWordException):
    """
    description: if status of action word is disable, raise this exception.
    """

    def __init__(self, action_word_name):
        message = f"the action word '{action_word_name}' is disabled"
        super().__init__(message)


class DeprecatedActionWordException(ActionWordException):
    """
    description: if status of action word is deprecated, raise this exception.
    """

    def __init__(self, action_word_name):
        message = f"the action word '{action_word_name}' is deprecated"
        super().__init__(message)


class MissingArgumentSchemaException(ActionWordException):
    """
    description: if schema of argument is missing, raise this exception.
    """

    def __init__(self, argument_name, action_word_name):
        message = f"cannot find schema of argument '{argument_name}' of action word '{action_word_name}'"
        super().__init__(message)


class MissingReturnSchemaException(ActionWordException):
    """
    description: if schema of return is missing, raise this exception.
    """

    def __init__(self, action_word_name):
        message = f"cannot find schema of return of action word '{action_word_name}'"
        super().__init__(message)


class DocumentError(Exception):
    """Error should be raised when an action word missing documents"""

    ...
