# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for Synapse Error Details."""


class SynapseErrorDetails:

    """ Synapse Error Details. Error related information including priority.
        Higher priority get precedence for error display at user end.
        Set correct priority in error detail object compare to all other possible errors.
    """

    def __init__(self, error_code=None, error_message=None, error_priority=-1):
        """ Synapse Error Details. init method for initialize properties"""
        self._error_code = error_code
        self._error_message = error_message
        self._error_priority = error_priority

    # getter methods
    @property
    def error_code(self):
        """ Synapse Error Details. get error_code"""
        return self._error_code

    @property
    def error_message(self):
        """ Synapse Error Details. get error_message"""
        return self._error_message

    @property
    def error_priority(self):
        """ Synapse Error Details. get error_priority"""
        return self._error_priority

    # setter methods
    @error_code.setter
    def set_error_code(self, error_code):
        """ Synapse Error Details. set error_code"""
        self._error_code = error_code

    @error_message.setter
    def set_error_message(self, error_message):
        """ Synapse Error Details. set error_message"""
        self._error_message = error_message

    @error_priority.setter
    def set_error_priority(self, error_priority):
        """ Synapse Error Details. set error_priority"""
        self._error_priority = error_priority
