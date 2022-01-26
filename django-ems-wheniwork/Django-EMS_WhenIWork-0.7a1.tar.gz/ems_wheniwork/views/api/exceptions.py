"""
Custom exceptions used by EMS Scheduler.
"""


class MissingParamException(Exception):
    pass


class InvalidParamException(Exception):
    pass


class NotFoundException(Exception):
    pass
