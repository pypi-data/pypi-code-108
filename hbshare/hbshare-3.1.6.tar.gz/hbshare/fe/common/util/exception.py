# -*- coding: utf-8 -*-


class BaseError(Exception):
    def __init__(self, message=''):
        Exception.__init__(self, '%s' % message)


class AlgoError(BaseError):
    def __init__(self, message=''):
        BaseError.__init__(self, message)


class PreprocessError(BaseError):
    def __init__(self, message=''):
        BaseError.__init__(self, message)


class InputParameterError(BaseError):
    def __int__(self, message='invalid input parameter'):
        BaseError.__init__(self, message)
