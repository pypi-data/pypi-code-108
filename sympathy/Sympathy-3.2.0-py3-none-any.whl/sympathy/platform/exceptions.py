# This file is part of Sympathy for Data.
# Copyright (c) 2014, Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
"""Exceptions for use in Sympathy nodes."""
import sys
import warnings
import traceback
import dataclasses
from typing import Union, Generic, Callable, TypeVar, Tuple, cast
from . import parameter_types
# import linecache


# def _show_warning(message, category, filename, lineno, file=None, line=None):
#     """Function hook to show warning with better unicode support."""
#     if file is None:
#         file = sys.stderr
#     try:
#         print(_formatwarning(message, category, filename, lineno, line),
#               file=file)
#     except IOError:
#         pass

# warnings.showwarning = _show_warning


# def _formatwarning(message, category, filename, lineno, line=None):
#     """Function to format a warning with better unicode support."""
#     s = u'{}:{}: {}: {}'.format(filename, lineno, category.__name__,
#                                 message)
#     line = linecache.getline(filename, lineno) if line is None else line
#     if line:
#         line = line.strip()
#         s += u'\n  {}'.format(line)
#     return s


def sywarn(message, stack=False, stacklevel=2):
    """Notify the user of a node error."""
    if stack:
        with warnings.catch_warnings():
            warnings.simplefilter('always')
            warnings.warn(message, stacklevel=stacklevel)
    else:
        print(message, file=sys.stderr)


class SyError(Exception):
    pass


class NoDataError(SyError):
    """Raised when trying to access data on an input port which has no data."""
    pass


class SyColumnTypeError(SyError):
    pass


class SyNodeError(SyError):
    type = 'text'

    """
    An error occurred in the node. See the specific error message for details.
    For further information, please refer to the node's documentation.
    """

    def __init__(self, msg, details="", **kwargs):
        """
        First argument should be a short description of the error. details
        argument can be an arbitrarily long string describing the error
        in more detail.
        """
        self._msg = msg
        self._details = details
        self._kwargs = kwargs
        super(SyNodeError, self).__init__(msg)

    @property
    def help_text(self):
        """Detailed help text."""
        return self._details

    def to_dict(self):
        kwargs = dict(self._kwargs)
        kwargs['msg'] = self._msg
        kwargs['details'] = self._details
        return {'type': self.__class__.__name__, 'kwargs': kwargs}

    @classmethod
    def from_dict(cls, data):
        assert cls.__name__ == data['type']
        kwargs = data['kwargs']
        return cls(**kwargs)

    def __str__(self):
        return self._msg


class SyDataError(SyNodeError):
    """
    Used to indicate that something is wrong with the data that this node
    received.
    """
    def __init__(self, msg, details=""):
        """Same arguments as SyNodeError.__init__()."""
        super(SyDataError, self).__init__(
            msg, details or "Error in input data.")


class SyCredentialError(SyNodeError):
    """Common base for credentials, do not instantiate directly."""

    def __init__(self, msg, *, connection, **kwargs):
        self._connection = connection
        super().__init__(msg, **kwargs)

    @property
    def resource(self):
        return self._connection.resource

    @property
    def connection(self):
        return self._connection

    def to_dict(self):
        data = super().to_dict()
        data['kwargs']['connection'] = self._connection.to_dict()
        return data

    @classmethod
    def from_dict(cls, data):
        assert cls.__name__ == data['type']
        kwargs = dict(data['kwargs'])
        connection = parameter_types.Connection.from_dict(kwargs['connection'])
        kwargs['connection'] = connection
        return cls(**kwargs)


class SyLoginCredentialError(SyCredentialError):
    type = 'login'

    @classmethod
    def from_connection(cls, connection):
        msg = 'Login Credentials are missing'
        resource = connection.resource
        return cls(msg=msg,
                   details=f'{msg} for: {resource}',
                   connection=connection)


class SySecretCredentialError(SyCredentialError):
    type = 'secrets'

    @classmethod
    def from_connection(cls, connection, missing_secrets):
        msg = 'Secret Credentials are missing'
        resource = connection.resource
        return cls(msg=msg,
                   details=(
                       f'{msg} for: {resource}\n'
                       f'{", ".join(missing_secrets)}'),
                   connection=connection)


class SyAzureCredentialError(SyCredentialError):
    type = 'azure'

    @classmethod
    def from_connection(cls, connection):
        msg = 'Azure Credentials are missing'
        resource = connection.resource
        return cls(msg=msg,
                   details=f'{msg} for: {resource}',
                   connection=connection)


class SyConfigurationError(SyNodeError):
    """
    Used to indicate an error in the node's configuration.
    """
    def __init__(self, msg, details="", *args):
        """Same arguments as SyNodeError.__init__()."""
        super(SyConfigurationError, self).__init__(
            msg, details or "Error in node configuration.", *args)


class SyUserCodeError(SyNodeError):
    """
    Used to indicate an error in the user-supplied code for this node.
    """
    def __init__(self, exc_info=None, msg=None, brief=None, details=None,
                 **kwargs):
        """
        First argument should be a tuple with three elements such as the tuple
        returned from sys.exc_info(). Optional argument msg can be used to
        change the default short error description.

        Parameters
        ----------
        exc_info : (type, value, traceback)
            Tuple with three elements such as the
            tuple returned from sys.exc_info().
        msg
            Optional argument msg can be used to
            change the default short error description.
        brief
            Brief text, required when not using exc_info
        details
            Details text, required when not using exc_info
        """
        if exc_info:
            if msg is None:
                msg = "Error in user-supplied code: {}".format(exc_info[1])
            etype, value, tb = exc_info
            details = "".join(traceback.format_exception(etype, value, tb))
            brief = "".join(traceback.format_exception_only(etype, value))
        else:
            assert msg is not None
            assert brief is not None

        self._brief = brief
        super().__init__(msg=msg, details=details, brief=brief)

    @property
    def brief_help_text(self):
        return self._brief

    def to_dict(self):
        data = super().to_dict()
        data['kwargs']['brief'] = self._brief
        return data


_node_errors = {
    cls.__name__: cls
    for cls in [
            SyDataError,
            SyConfigurationError,
            SyUserCodeError,
            SyLoginCredentialError,
            SySecretCredentialError,
            SyAzureCredentialError,
    ]}


def _internal_node_error_from_dict(data):
    """
    Construct SyNodeError subclass from data.
    Internal use only.
    """
    return _node_errors[data['type']].from_dict(data)


class FlowError(SyError):
    pass


class ReadSyxFileError(FlowError):
    """
    Exception used when a syx file could not be read from disk for any reason.

    The cause property should be a short sentence about why the file wasn't
    loaded aimed at the average user. The details property should be aimed at
    an advanced user who tries to find and remedy the problem.
    """
    def __init__(self, cause, details):
        super(ReadSyxFileError, self).__init__()
        self._cause = cause
        self._details = details

    @property
    def cause(self):
        return self._cause

    @property
    def details(self):
        return self._details

    def __str__(self):
        return self._cause


class LibraryError(SyError):
    pass


class NoLibraryError(LibraryError):
    def __init__(self, lib):
        super(NoLibraryError, self).__init__()
        self._lib = lib

    def __str__(self):
        return 'NoLibraryError({})'.format(self._lib)


class ConflictingFlowLibrariesError(LibraryError):
    def __init__(self, libs):
        super(ConflictingFlowLibrariesError, self).__init__()
        self._libs = libs

    def __str__(self):
        return 'ConflictingFlowLibrariesError({})'.format(self._libs)

    @property
    def help_text(self):
        return ('Workflow libraries: {} are in conflict with those of other '
                'libraries'.format(
                    ', '.join(self._libs)))


class ConflictingGlobalLibrariesError(LibraryError):
    def __init__(self, libs):
        super(ConflictingGlobalLibrariesError, self).__init__()
        self._libs = libs or []

    @property
    def libs(self):
        return self._libs

    def __str__(self):
        return 'ConflictingGlobalLibrariesError({})'.format(self._libs)

    @property
    def help_text(self):
        return ('Workflow libraries: {} are in conflict with those of global '
                'libraries'.format(
                    ', '.join(self._libs)))


class ConflictingInternalLibrariesError(LibraryError):
    def __init__(self, libs):
        super(ConflictingInternalLibrariesError, self).__init__()
        self._libs = libs

    def __str__(self):
        return 'ConflictingInternalLibrariesError({})'.format(self._libs)

    @property
    def help_text(self):
        return ('Workflow libraries: {} are in conflict with those of its '
                'internal libraries'.format(
                    ', '.join(self._libs)))


class LinkLoopError(ReadSyxFileError):
    pass


class SyListIndexError(SyError):
    def __init__(self, index, exc_info=None):
        super(SyListIndexError, self).__init__(index)
        self.exc_info = exc_info
        self.index = index


class SyChildError(SyNodeError):
    def __init__(self, *args):
        super(SyChildError, self).__init__(*args)


A1 = TypeVar('A1')
A2 = TypeVar('A2')

F1 = TypeVar('F1', bound=Exception)
F2 = TypeVar('F2', bound=Exception)


class Ok(Generic[A1]):

    def __init__(self, value: A1):
        self.value = value

    @property
    def is_ok(self) -> bool:
        return True

    def ok(self) -> A1:
        return self.value

    def fail(self) -> None:
        raise Exception('No fail.')

    def map_ok(self, func: Callable[[A1], A2]) -> 'Result[A2, F1]':
        return Ok(func(self.value))

    def map_fail(self, func: Callable[[F1], F2]) -> 'Result[A1, F2]':
        return cast(Result[A1, F2], self)

    def try_map_ok(self, func: Callable[[A1], A2],
                   exception: Union[Exception, Tuple[Exception]] = Exception
                   ) -> 'Result[A2, F1]':
        try:
            return self.map_ok(func)
        except exception as e:
            return Fail(e)

    def raise_fail(self) -> None:
        pass


class Fail(Generic[F1]):
    def __init__(self, value: F1):
        self.value = value

    @property
    def is_ok(self) -> bool:
        return False

    def ok(self) -> None:
        self.raise_fail()

    def fail(self) -> F1:
        return self.value

    def map_ok(self, func: Callable[[A1], A2]) -> 'Result[A2, F1]':
        return cast(Result[A2, F1], self)

    def map_fail(self, func: Callable[[F1], F2]) -> 'Result[A1, F2]':
        return Fail(func(self.value))

    def try_map_ok(self, func: Callable[[A1], A2],
                   exception: Union[Exception, Tuple[Exception]] = Exception
                   ) -> 'Result[A2, F1]':
        return cast(Result[A2, F1], self)

    def raise_fail(self) -> None:
        raise self.value


Result = Union[Ok[A1], Fail[F1]]


def try_result(exception: Union[Exception, Tuple[Exception]],
               func: Callable[..., A1], *args, **kwargs) -> Result[A1, F1]:
    try:
        return Ok(func(*args, **kwargs))
    except exception as e:
        return Fail(e)


def filename_not_empty(**kwargs):
    return SyDataError('Filename must not be empty')
