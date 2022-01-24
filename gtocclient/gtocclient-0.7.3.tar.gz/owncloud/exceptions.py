from __future__ import absolute_import

from . import utils

import sys
if sys.version_info >= (3, 0):
    PY3 = True
    # In python 3, unicode -> str, and str -> bytes
    unicode = str
else:
    PY3 = False


class OCBaseException(Exception):
    def __init__(self, message=""):
        self.message = utils.unicodise(message)

    def __str__(self):
        ## Don't return self.message directly because
        ## __unicode__() method could be overridden in subclasses!
        if PY3:
            return self.__unicode__()
        else:
            return utils.deunicodise(self.__unicode__())

    def __unicode__(self):
        return self.message

    ## (Base)Exception.message has been deprecated in Python 2.6
    def _get_message(self):
        return self._message

    def _set_message(self, message):
        self._message = message
    message = property(_get_message, _set_message)


class InvalidFileError(OCBaseException):
    pass


class ParameterError(OCBaseException):
    pass


class OCFileExistsError(OCBaseException):
    def __init__(self, path='', message=''):
        super(OCFileExistsError, self).__init__(message)
        self.path = path


class OCDirExistsError(OCBaseException):
    def __init__(self, path='', message=''):
        super(OCDirExistsError, self).__init__(message)
        self.path = path


class OCUnexpectedDirError(OCBaseException):
    def __init__(self, path='', message=''):
        super(OCUnexpectedDirError, self).__init__(message)
        self.path = path
