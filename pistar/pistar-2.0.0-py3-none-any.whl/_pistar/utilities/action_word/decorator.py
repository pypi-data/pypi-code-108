"""
description: this module provides Keyword decorator.
"""

import functools
import inspect
import logging
from _pistar.pistar_pytest.utils import now
from _pistar.utilities.exceptions import DeprecatedActionWordException
from _pistar.utilities.exceptions import DisabledActionWordException
from _pistar.utilities.exceptions import UnknownStatusException
from _pistar.utilities.testcase import BaseTestCase
from .checker import ActionWordChecker


def get_testcase_from_call_stack():
    """
    description: |
        this function is used to get the testcase from the call stack.
        so, with this function, we can get which testcase call this action word
    """

    caller_frame = inspect.currentframe()
    while True:
        if 'self' in caller_frame.f_locals:
            testcase = caller_frame.f_locals['self']
            if isinstance(testcase, BaseTestCase):
                return testcase, caller_frame.f_code.co_name

        caller_frame = caller_frame.f_back
        if caller_frame is None:
            return None, None


def wrap_generator(aw, checker):
    """
    description: this function is used to wrap action word, which is generator.
    """

    @functools.wraps(aw)
    def wrapper(*args, **kwargs):
        # get the testcase.
        testcase, caller = get_testcase_from_call_stack()

        logger = testcase.user_logger if testcase else logging

        # check status value.
        exception = checker.check_status()
        if isinstance(exception, DisabledActionWordException):
            raise exception

        if isinstance(exception, DeprecatedActionWordException):
            logger.warning(exception)

        # check the arguments.
        exception = checker.check_arguments(*args, **kwargs)
        if exception:
            logger.error(exception)
            raise exception

        # add globals for this action word.
        aw.__globals__['logger'] = logger

        # execute this action word.
        time_consuming = 0
        start_time = now()
        return_value = aw(*args, **kwargs)
        time_consuming += now() - start_time

        if testcase is not None:
            testcase.append_action_word_execution_information(
                module_name=aw.__module__,
                caller_name=caller,
                action_word_name=aw.__name__,
                time_consuming=time_consuming
            )

        while True:
            try:
                start_time = now()
                item = next(return_value)
                time_consuming += now() - start_time
            except StopIteration:
                break

            exception = checker.check_return_value(item)
            if exception:
                logger.error(exception)
                raise exception
            yield item

    return wrapper


def wrap_non_generator(aw, checker):
    """
    description: this function is used to wrap action word,
                 which is non-generator.
    """

    @functools.wraps(aw)
    def wrapper(*args, **kwargs):
        # get the testcase.
        testcase, caller = get_testcase_from_call_stack()

        logger = testcase.user_logger if testcase else logging

        # check the status.
        exception = checker.check_status()
        if isinstance(exception,
                      (DisabledActionWordException, UnknownStatusException)):
            raise exception

        if isinstance(exception, DeprecatedActionWordException):
            logger.warning(exception)

        # check the arguments.
        exception = checker.check_arguments(*args, **kwargs)
        if exception:
            logger.error(exception)
            raise exception

        # add globals for this action word.
        aw.__globals__['logger'] = logger

        # execute this action word.
        start_time = now()
        return_value = aw(*args, **kwargs)
        end_time = now()

        # check the return value.
        exception = checker.check_return_value(return_value)
        if exception:
            logger.error(exception)
            raise exception

        if testcase is not None:
            testcase.append_action_word_execution_information(
                module_name=aw.__module__,
                caller_name=caller,
                action_word_name=aw.__name__,
                time_consuming=end_time - start_time
            )

        # return the return value.
        return return_value

    return wrapper


class Keyword:
    """
    description: it is the class of decorator action_word.
    """
    __logger = None

    def __call__(self, aw):
        # initialize an action word checker.
        checker = ActionWordChecker(aw)

        # first, check the fields of __doc__.
        exception = checker.check_fields()
        if exception:
            raise exception

        # second, check the argument schemata.
        exception = checker.check_argument_schemata()
        if exception:
            raise exception

        # third, check the argument schemata.
        exception = checker.check_return_schema()
        if exception:
            raise exception

        # forth, instantiate assertion lambda expressions.
        checker.instantiate_assertions()

        # fifth, check status validation.
        exception = checker.check_status()
        if isinstance(exception, UnknownStatusException):
            raise exception

        if inspect.isgeneratorfunction(aw):
            wrapper = wrap_generator(aw=aw, checker=checker)
        else:
            wrapper = wrap_non_generator(aw=aw,
                                         checker=checker)
        return wrapper


def action_word(function):
    return Keyword()(function)
