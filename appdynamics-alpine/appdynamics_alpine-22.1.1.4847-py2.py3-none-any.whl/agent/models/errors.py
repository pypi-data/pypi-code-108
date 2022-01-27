# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Models for errors and exceptions.

"""

from __future__ import unicode_literals
from collections import namedtuple
import traceback

from appdynamics.lang import bytes, str, zip
from appdynamics.agent.models.frames import is_internal_frame
from appdynamics.agent.core.pb import (
    PY_HTTP_ERROR,
    PY_INFO,
    PY_WARNING,
    PY_ERROR)


class ErrorInfo(object):
    __slots__ = ('level', 'message', 'display_name')

    @classmethod
    def convert_to_threshold(cls, level):
        threshold = PY_INFO
        if level == PY_HTTP_ERROR:
            threshold = PY_HTTP_ERROR
        elif level >= PY_ERROR:
            threshold = PY_ERROR
        elif level >= PY_WARNING:
            threshold = PY_WARNING
        return threshold

    def __init__(self, message, display_name, level):
        super(ErrorInfo, self).__init__()
        self.level = self.convert_to_threshold(level)
        self.message = message
        self.display_name = display_name


class ExceptionInfo(object):
    __slots__ = ('klass', 'message', 'stack_trace_frames')

    def __init__(self, exc_type, exc_value, exc_tb):
        super(ExceptionInfo, self).__init__()

        stack_entries = traceback.extract_tb(exc_tb)

        self.klass = get_exception_name(exc_value)
        self.message = get_exception_message(exc_value)
        self.stack_trace_frames = [
            StackTraceInfo(filename=filename, line_no=line_no, klass=None, method=text)
            for filename, line_no, _, text in stack_entries
            if not is_internal_frame(filename)]


def get_exception_name(exc):
    """Get the qualified name of an exception.

    This is the name of the exception class, qualified by the module that
    defines it. In the case of builtin exceptions, this is just the exception
    class's name (e.g., ``'ValueError'``), whereas for other exceptions it
    will have the module name (e.g., ``'queue.Empty'``).

    Parameters
    ----------
    exc : BaseException

    Returns
    -------
    name : str

    """
    class_ = exc.__class__
    class_name = class_.__name__
    module_name = class_.__module__

    if module_name in ('builtins', '__builtin__', 'exceptions'):
        return class_name
    else:
        return '%s.%s' % (module_name, class_name)


def get_exception_message(exc):
    """Get the message from an exception.

    Parameters
    ----------
    exc : BaseException

    Returns
    -------
    message : str

    """
    return str(exc)


StackTraceInfo = namedtuple('StackTraceInfo', ('klass', 'method', 'filename', 'line_no'))


def make_bt_errors_dict(errors, exceptions):
    """Map errors and exceptions into a dict representing the wire format.

    Parameters
    ----------
    errors : list[errors.ErrorInfo]
    exceptions : list[errors.ExceptionInfo]

    Returns
    -------
    dict
        Mapping representing an :py:class:`appdynamics.agent.pb.BTErrors`

    """
    errors_dict = {}

    if errors:
        errors_dict['errorInfo'] = make_error_info_dict(errors)

    if exceptions:
        errors_dict['exceptionInfo'] = make_exception_info_dict(exceptions)

    return errors_dict


def make_error_info_dict(errors):
    """Map ErrorInfo objects to a dict representing the wire format.

    Parameters
    ----------
    errors : list[errors.ErrorInfo]

    Returns
    -------
    dict
        Mapping representing an :py:class:`appdynamics.agent.pb.ErrorInfo`

    """
    return {
        'errors': [
            {
                'pythonErrorThreshold': err.level,
                'displayName': bytes(err.display_name),
                'errorMessage': bytes(err.message),
            }
            for err in errors
        ],
    }


def make_exception_info_dict(exceptions):
    """Map ExceptionInfo objects to the dict representing the wire format.

    Parameters
    ----------
    exceptions : list[errors.ExceptionInfo]

    Returns
    -------
    dict
        Mapping representing an :py:class:`appdynamics.agent.pb.ExceptionInfo`

    """
    if not exceptions:
        return None

    traces = {'id': 0}

    def format_exc(exc):
        exc_info = {
            'root': {
                'klass': bytes(exc.klass),
                'message': bytes(exc.message),
            },
            'count': 1,
        }
        stack_trace_info = None

        if exc.stack_trace_frames:
            exc_info['root']['stackTraceID'] = traces['id']
            traces['id'] += 1
            stack_trace_info = {
                'elements': [
                    {
                        'method': bytes(elt.method),
                        'fileName': bytes(elt.filename),
                        'lineNumber': elt.line_no,
                    }
                    for elt in exc.stack_trace_frames
                ],
            }

        return exc_info, stack_trace_info

    # zip(*[(a0,b0,c0), (a1,b1,c1), (a2,b2,c2)]) => ((a0,a1,a2), (b0,b1,b2), (c0,c1,c2))
    exceptions, stack_traces = zip(*[format_exc(exc) for exc in exceptions])
    return {'exceptions': list(exceptions), 'stackTraces': list(stack_traces)}
