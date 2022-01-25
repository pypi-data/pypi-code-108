"""
description: this module provides exceptions of testcase.
"""


class DecorationException(Exception):
    """
    description: if the test case decorator is used illegally，raise exception。
    """


class ControlUsageException(DecorationException):
    """
    description: if the control decorator is used illegally，raise this exception。
    """

    def __init__(self):
        super().__init__("the @control decorator should only be used for test cases")


class ControlArgumentTypeException(DecorationException):
    """
    description: if the @control argument type is illegal, raise this exception.
    """

    def __init__(self, arg_name, arg, arg_type_expected):
        super().__init__(
            f"@control argument '{arg_name}' value is '{arg}', type is '{arg.__class__.__name__}', "
            f"but the type '{arg_type_expected}' is expected"
        )


class UnsupportedParameterTypeException(DecorationException):
    """
    description: if the parameters' type are not tuple or dict,
                 raise this exception.
    """

    def __init__(self, parameter):
        super().__init__(
            f"the type of parameter '{parameter}' is '{parameter.__class__.__name__}', "
            "but the 'tuple' or 'dict' is expected"
        )


class UnsupportedStartTypeException(DecorationException):
    """
    description: if the format of start are not \'xxxx.end\' or \'boolean
                 expression consisting of xxxx.end\', raise this exception.
                 (xxxx is function name of teststep)
    """

    def __init__(self, parameter):
        super().__init__(
            f"the start is '{parameter}', "
            "but the format of 'xxxx.end' or 'boolean expression consisting "
            "of xxxx.end' is expected.(xxxx is function name of teststep)"
        )


class TestCaseException(Exception):
    """
    description: this is the base exception.
    """


class DuplicatedTestStepNameException(TestCaseException):
    """
    description: if a testcase has duplicated step names, raise this exception.
    """

    def __init__(self, teststep_name):
        super().__init__(f"duplicated teststep name '{teststep_name}'")


class HasNoAttributeException(TestCaseException):
    """
    description: if access a nonexisting attribute, raise this exception.
    """

    def __init__(self, class_name, attribute_name):
        message = f"class '{class_name}' has not attribute '{attribute_name}'"
        super().__init__(message)


class TestCaseStatusException(Exception):
    """
    description: the base exception of the testcase status exceptions.
    """


class PassedException(TestCaseStatusException):
    """
    description: when user sets the testcase status to passed,
                 raise this exception.
    """

    def __init__(self, line_number):
        super().__init__(f"this test case has been set to passed, in line {line_number}")


class FailedException(TestCaseStatusException):
    """
    description: when user sets the testcase status to failed,
                 raise this exception.
    """

    def __init__(self, line_number):
        super().__init__(f"this test case has been set to failed, in line {line_number}")


class InvestigatedException(TestCaseStatusException):
    """
    description: when user sets the testcase status to investigated,
                 raise this exception.
    """

    def __init__(self, line_number):
        super().__init__(f"this test case has been set to investigated, in line {line_number}")


class UnavailableException(TestCaseStatusException):
    """
    description: when user sets the testcase status to unavaiable,
                 raise this exception.
    """

    def __init__(self, line_number):
        super().__init__(f"this test case has been set to unavailable, in line {line_number}")


class BlockedException(TestCaseStatusException):
    """
    description: when user sets the testcase status to blocked,
                 raise this exception.
    """

    def __init__(self, line_number):
        super().__init__(f"this test case has been set to blocked, in line {line_number}")


class UnexecutedException(TestCaseStatusException):
    """
    description: when user sets the testcase status to unexecuted,
                 raise this exception.
    """

    def __init__(self, line_number):
        super().__init__(f"this test case has been set to Unexecuted, in line {line_number}")


class UsageError(Exception):
    """
    Error in pistar usage or invocation.
    """
