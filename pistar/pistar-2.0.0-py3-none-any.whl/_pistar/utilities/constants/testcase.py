"""
description: |
    this module provides four constants TESTCASE_KEYS,
    TESTCASE_PROPERTIES, TESTCASE_STATUS, and TESTCASE_EXECUTION_STATUS.

"""


class TESTCASE_KEYS:
    """
    description: the testcase document keys.
    """

    VERSION = 'version'
    AUTHOR = 'author'
    DESCRIPTION = 'description'
    MODIFY_RECORDS = 'modify_records'
    PRECONDITIONS = 'preconditions'
    STEPS = 'steps'
    RESULTS = 'results'
    TAGS = 'tags'
    STATUS = 'status'
    ENVIRONMENT = 'environment'
    CASE_NUMBER = 'case_number'


class TESTCASE_PROPERTIES:
    """
    description: the testcase property names.
    """

    FAILURE = 'failure'
    SETUP = 'setup'
    TEARDOWN = 'teardown'
    EXECUTE = 'execute'
    TESTSTEP = '__teststep__'


class TESTCASE_STATUS:
    """
    description: the testcase static status.
    """

    ENABLE = 'enable'
    DISABLE = 'disable'
    DEPRECATE = 'deprecate'
    DESIGN = 'design'
    REPAIR = 'repair'


class TESTCASE_EXECUTION_STATUS:
    """
    description: the testcase execution status.
    """

    PASSED = '0'
    FAILED = '1'
    INVESTIGATED = '2'
    UNAVAILABLE = '3'
    BLOCKED = '4'
    UNEXECUTED = '5'


class PISTAR_TESTCASE_EXECUTION_STATUS:
    """
    description: the testcase execution status.
    """

    PASSED = 1
    FAILED = 2
    TIMEOUT = 3
    ERROR = 4
    BROKEN = 5
    SKIPPED = 6
    UNKNOWN = 7


class STEP_TYPE:
    SETUP = 'set_up'
    TEARDOWN = 'tear_down'
    TESTSTEP = 'test'


class ControlArgs:
    RIGOROUS = '_rigorous'
