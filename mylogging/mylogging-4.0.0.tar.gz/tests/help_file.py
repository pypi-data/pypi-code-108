"""Simulate imported module."""
import warnings
import mylogging


def warn_outside(message):
    """Mocking function"""
    mylogging.warn(message)


def traceback_outside(message):
    """Mocking function"""
    try:
        print(10 / 0)
    except ZeroDivisionError:  # pylint: disable=broad-except
        mylogging.traceback(message)


def info_outside(message):
    """Mocking function"""
    mylogging.info(message)


def warn_to_be_filtered():
    """Mocking function"""
    warnings.warn("It mean of empty slice it is")
