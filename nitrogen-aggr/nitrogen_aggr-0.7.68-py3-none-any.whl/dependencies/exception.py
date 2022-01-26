from botocore.exceptions import ClientError

from dependencies.logging import Log4j
import sys, traceback
import boto3
"""
exception handler
~~~~~~~
This module contains a function to wrap up all exception handlers in one decorator.
"""


def exception_handler(func):
    def inner_function(*args, **kwargs):

        log = args[0].log # self = args[0]
        try:
            return func(*args, **kwargs)
        except TypeError:
            log.error("{} only takes numbers as the argument. Stack Trace: {}".format(func.__name__, traceback.format_exc()))
        except FileNotFoundError as e:
            log.error("{} {} Stack Trace:  {}".format(func.__name__, e.strerror, traceback.format_exc()))
        except ClientError as e:
            log.error("{} No such file. Stack Trace: {}".format(func.__name__, traceback.format_exc()))
        except AssertionError as e:
            log.error("{} Assertion Error. Stack Trace: {}".format(func.__name__, traceback.format_exc()))
        except KeyError as e:
            log.error("{} Key Error. Stack Trace: {}".format(func.__name__, traceback.format_exc()))
        except Exception as e:
            log.error("{} Stack Trace: {}".format(func.__name__, traceback.format_exc()))

        # exit the job
        sys.exit(1)

    return inner_function
