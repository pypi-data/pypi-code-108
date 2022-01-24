from asyncio import wrap_future
from concurrent.futures import ThreadPoolExecutor, Future
from logging import getLogger, Logger, DEBUG, INFO, WARNING, ERROR, CRITICAL, raiseExceptions, LogRecord

import sys
import typing
import warnings
from contextlib import asynccontextmanager, contextmanager

__all__ = ['AsyncLogWrapper', 'getAsyncLogger', 'async_log_exception', 'log_exception']

DEFAULT_WAIT_FOR_COMPLETION = False
_executor = ThreadPoolExecutor(max_workers=1)
_last_future: typing.Optional[Future] = None


# noinspection PyPep8Naming
class AsyncLogWrapper:
    """ Wraps a Python logger for async use.
    The original logger is available on the `sync` attribute for use in synchronous code.

    Most properties and methods from the original logger are proxied.

    :param logger: The Python logger to wrap
    :param wait_for_completion: If `True` all logging statements will only return when the line is written to the log.
                                If `False` will queue the line to be logged and return immediately.
                                If `None` (default) will wait if the level of the logger is DEBUG
    """
    # noinspection PyProtectedMember
    def __init__(self, logger: Logger, *, wait_for_completion: typing.Optional[bool] = DEFAULT_WAIT_FOR_COMPLETION):
        self._logger = logger
        self._sync_log = logger._log
        self._wait_for_completion: typing.Optional[bool] = logger.isEnabledFor(DEBUG) \
            if wait_for_completion is None else wait_for_completion

    @property
    def name(self):
        """ Get the name of the logger """
        return self._logger.name

    @property
    def level(self):
        """ Get the level of the logger """
        return self._logger.level

    @property
    def propagate(self):
        """ Get/set the `propagate` property of the logger """
        return self._logger.propagate

    @propagate.setter
    def propagate(self, value):
        self._logger.propagate = value

    @property
    def disabled(self):
        """ Get/set the `disabled` property of the logger """
        return self._logger.disabled

    @disabled.setter
    def disabled(self, value):
        self._logger.disabled = value

    def setLevel(self, level):
        """
        Set the logging level of this logger.  level must be an int or a str.
        """
        return self._logger.setLevel(level)

    def getEffectiveLevel(self):
        """
        Get the effective level for this logger.

        Loop through this logger and its parents in the logger hierarchy,
        looking for a non-zero logging level. Return the first one found.
        """
        return self._logger.getEffectiveLevel()

    def isEnabledFor(self, level):
        """
        Is this logger enabled for level 'level'?
        """
        return self._logger.isEnabledFor(level)

    async def debug(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'DEBUG'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.debug("Houston, we have a %s", "thorny problem", exc_info=1)
        """
        if self.isEnabledFor(DEBUG):
            await self._log(DEBUG, msg, args, **kwargs)

    async def info(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'INFO'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.info("Houston, we have a %s", "interesting problem", exc_info=1)
        """
        if self.isEnabledFor(INFO):
            await self._log(INFO, msg, args, **kwargs)

    async def warning(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'WARNING'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.warning("Houston, we have a %s", "bit of a problem", exc_info=1)
        """
        if self.isEnabledFor(WARNING):
            await self._log(WARNING, msg, args, **kwargs)

    async def warn(self, msg, *args, **kwargs):
        warnings.warn("The 'warn' method is deprecated, use 'warning' instead", DeprecationWarning, 2)
        await self.warning(msg, *args, **kwargs)

    async def error(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'ERROR'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.error("Houston, we have a %s", "major problem", exc_info=1)
        """
        if self.isEnabledFor(ERROR):
            await self._log(ERROR, msg, args, **kwargs)

    async def exception(self, msg, *args, exc_info=True, **kwargs):
        """
        Convenience method for logging an ERROR with exception information.
        """
        await self.error(msg, *args, exc_info=exc_info, **kwargs)

    async def critical(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'CRITICAL'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.critical("Houston, we have a %s", "major disaster", exc_info=1)
        """
        if self.isEnabledFor(CRITICAL):
            await self._log(CRITICAL, msg, args, **kwargs)

    fatal = critical

    async def log(self, level, msg, *args, **kwargs):
        """
        Log 'msg % args' with the integer severity 'level'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.log(level, "We have a %s", "mysterious problem", exc_info=1)
        """
        if not isinstance(level, int):
            if raiseExceptions:
                raise TypeError("level must be an integer")
            else:
                return

        if self.isEnabledFor(level):
            await self._log(level, msg, args, **kwargs)

    @staticmethod
    async def flush():
        """ Wait until the last submitted logging statement has completed
        """
        global _last_future

        fut: typing.Optional[Future] = _last_future
        _last_future = None
        if fut:
            # noinspection PyBroadException
            try:
                await wrap_future(fut)
            except:
                pass

    @staticmethod
    def flush_sync():
        """ Wait until the last submitted logging statement has completed
        """
        global _last_future

        fut: typing.Optional[Future] = _last_future
        _last_future = None
        if fut is not None:
            # noinspection PyBroadException
            try:
                fut.result()
            except:
                pass

    async def _log(self, level, msg, args, exc_info=None, **kwargs):
        global _last_future, _executor

        if args:
            msg = msg % args

        if exc_info:
            if isinstance(exc_info, BaseException):
                exc_info = (type(exc_info), exc_info, exc_info.__traceback__)
            elif not isinstance(exc_info, tuple):
                exc_info = sys.exc_info()

        wait_for_completion = kwargs.pop(
            'wait_for_completion',
            self._wait_for_completion or level >= CRITICAL or bool(exc_info)
        )

        _last_future = _executor.submit(self._sync_log, level, msg, [], exc_info=exc_info, **kwargs)

        # Wait until the message has been processed if `wait_for_completion` is True, or if the
        # log message is critical or has exception info
        if wait_for_completion:
            await self.flush()

    async def handle(self, record: LogRecord):
        """
        Call the handlers for the specified record.

        This method is used for unpickled records received from a socket, as
        well as those created locally. Logger-level filtering is applied.
        """
        global _last_future, _executor

        if (not self.disabled) and self._logger.filter(record):
            wait_for_completion = self._wait_for_completion or record.levelno >= CRITICAL or bool(record.exc_info)

            _last_future = _executor.submit(self._logger.callHandlers, record)

            # Wait until the message has been processed if `wait_for_completion` is True, or if the
            # log message is critical or has exception info
            if wait_for_completion:
                await self.flush()

    @property
    def sync(self) -> Logger:
        """
        Get the original logger instance, for use in synchronous code, e.g.

        logger.sync.info("This is logged from synchronous code")
        """
        # Wait until all async log messages have been processed
        self.flush_sync()

        return self._logger


# noinspection PyPep8Naming
def getAsyncLogger(name, *, wait_for_completion: typing.Optional[bool] = DEFAULT_WAIT_FOR_COMPLETION) \
        -> AsyncLogWrapper:

    """ Convenience function to create an asynchronous logger.
    Creates the logger by calling :py:func:`logging.getLogger` and wraps it with
    :py:class:`~momotor.shared.log.AsyncLogWrapper`

    :param name: name of the logger
    :param wait_for_completion: If `True` all logging statements will only return when the line is written to the log.
                                If `False` will queue the line to be logged and return immediately.
                                If `None` (default) will wait if the level of the logger is DEBUG
    """
    return AsyncLogWrapper(getLogger(name), wait_for_completion=wait_for_completion)


def is_iterable(x):
    try:
        iter(x)
    except TypeError:
        return False
    else:
        return True


@asynccontextmanager
async def async_log_exception(async_logger: AsyncLogWrapper, msg: str, *args,
                              reraise: bool = False,
                              ignore: typing.Union[Exception, typing.Sequence[Exception], None] = None):
    """ An async context manager that captures exceptions, logs them, and optionally re-raises them.

    :param async_logger: The async logger to log the exception to
    :param msg: A message to add to the exception
    :param args: Any optional arguments for the message
    :param reraise: If `True`, the exception will be re-raised after logging
    :param ignore: An exception, or list of exceptions, to ignore. These exceptions will not be logged but always
                   re-raised
    """
    # noinspection PyBroadException
    try:
        yield
    except Exception as e:
        if ignore and isinstance(e, tuple(ignore) if is_iterable(ignore) else ignore):
            raise

        await async_logger.exception(msg, *args)
        if reraise:
            raise


@contextmanager
def log_exception(logger: Logger, msg: str, *args, reraise=False, ignore=None):
    """ A context manager that captures exceptions, logs them, and optionally re-raises them.

    :param logger: The logger to log the exception to
    :param msg: A message to add to the exception
    :param args: Any optional arguments for the message
    :param reraise: If `True`, the exception will be re-raised after logging
    :param ignore: An exception, or list of exceptions, to ignore. These exceptions will not be logged but always
                   re-raised
    """
    # noinspection PyBroadException
    try:
        yield
    except Exception as e:
        if ignore and isinstance(e, tuple(ignore) if is_iterable(ignore) else ignore):
            raise

        logger.exception(msg, *args)
        if reraise:
            raise
