import logging as loglevel
import traceback
from collections import namedtuple
from logging import Handler
from os import path
from threading import current_thread

from papyru.logger_stdout import make_stdout_sink
from papyru.logger_types import Message, Sequence, Trace
from papyru.stack_context import get_stackcontext, put_stackcontext

_STACK_MARKER = '__papyru_log'


def log_root(sink=None):
    def wrapper(fn):
        @put_stackcontext(_STACK_MARKER,
                          lambda: LogRoot(sink or _make_default_sink()))
        def impl(*args, **kwargs):
            return fn(*args, **kwargs)
        return impl
    return wrapper


class PapyruHandler(Handler):
    def emit(self, record):
        _get_root().put(Message(
            severity=PapyruHandler._assess_severity(record.levelno),
            message=self.format(record)))

    def _assess_severity(level):
        if level == loglevel.CRITICAL:
            return Message.CRITICAL
        elif level == loglevel.ERROR:
            return Message.FAILURE
        elif level == loglevel.WARNING:
            return Message.WARNING
        else:
            return Message.INFO


class SequenceGuard:
    def __init__(self, description):
        self.description = description

    def __enter__(self):
        _get_root().save(Sequence(description=self.description,
                                  resolution=Message.SUCCESS))
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        root = _get_root()

        if exc_type is not None:
            root.head.resolution = Message.FAILURE
            _get_root().put(_to_trace(exc_value))

        root.restore()


class LogRoot:
    Context = namedtuple('Context', ['items'])

    def __init__(self, sink):
        self._stack = [LogRoot.Context([])]
        self._sink = sink

    def save(self, context):
        self._stack.append(context)

    def restore(self):
        top = self._stack.pop()
        return self.put(top)

    def put(self, item):
        self.head.items.append(item)
        return self._commit()

    @property
    def head(self):
        return self._stack[-1]

    def _commit(self):
        if len(self._stack) == 1:
            for item in self.head.items:
                self._sink.commit(item)

            self._stack = [LogRoot.Context([])]


class LogSink:
    def commit(self, item):
        raise NotImplementedError()


def _make_default_sink():
    return make_stdout_sink()


def _make_default_root():
    return LogRoot(_make_default_sink())


_thread_roots = {}


def _get_root():
    thread_id = current_thread().ident

    if thread_id not in _thread_roots:
        _thread_roots[thread_id] = _make_default_root()

    return get_stackcontext(_STACK_MARKER, _thread_roots[thread_id])


def _to_trace(exception):
    trace = traceback.TracebackException.from_exception(exception)

    return Trace(
        Trace.Summary(type(exception).__name__, str(exception)),
        list(map(lambda frame: Trace.Frame(path.basename(frame.filename),
                                           frame.lineno,
                                           frame.line),
                 trace.stack)))


# === LEGACY API -- Use the PapyruHandler instead! ============================


def log_item(message):
    return _get_root().put(Message(Message.INFO, message))


def log_info(message):
    return _get_root().put(Message(Message.INFO, message))


def log_ok(message):
    return _get_root().put(Message(Message.SUCCESS, message))


def log_fail(message):
    return _get_root().put(Message(Message.FAILURE, message))


def log_warn(message):
    return _get_root().put(Message(Message.WARNING, message))


def log_trace(exception):
    return _get_root().put(_to_trace(exception))


class LogSequence(SequenceGuard):
    '''
    The LogSequence can be used to create an easy human readable logging trace.

    **Example Call:**

    .. code-block:: python

      with LogSequence('foobar') as log:
          log.info('foobar started')
          log.warn('something is not perfect')
          with LogSequence('bar') as lo:
              lo.ok('child logging')
          with LogSequence('foo') as lo:
              lo.fail('foo failed')
              raise Exception('Something went wrong..')

    **Example Output:**

    ::

      ⚫ foobar
         - foobar started
         ⚠ something is not perfect
         ⚫ bar
            ✓ child logging
            ☀ succeeded
         ⚫ foo
            ✗ foo failed
            ☇ failed
               ↪ foobar.py l.11 | raise Exception('Something went wrong..')
               ↪ Exception: Something went wrong..
         ☇ failed
            ↪ foobar.py l.11 | raise Exception('Something went wrong..')
            ↪ Exception: Something went wrong..
    '''

    def ok(self, message):
        return log_ok(message)

    def fail(self, message):
        return log_fail(message)

    def warn(self, message):
        return log_warn(message)

    def info(self, message):
        return log_info(message)
