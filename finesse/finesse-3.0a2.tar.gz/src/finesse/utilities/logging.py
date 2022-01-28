"""Loging utilities."""

import logging
from contextlib import contextmanager
from fnmatch import fnmatch


@contextmanager
def logs(logger, level=None, handler=None, close=True):
    """Emit logs at or above `level` in the encapsulated context, optionally using the
    specified `handler`.

    See `the Python logging cookbook
    <https://docs.python.org/3/howto/logging-cookbook.html#using-a-context-manager-for-selective-logging>`__
    for more information.

    Parameters
    ----------
    logger : :class:`logging.Logger`
        The logger to use for the encapsulated context.

    level : str or int, optional
        The minimum log levels to emit. The standard log levels "debug", "info",
        "warning", "error" and "critical" are supported, as are their corresponding
        level numbers (see :mod:`logging`).

    handler : :class:`logging.LogHandler`, optional
        The handler to add to `logger` for the encapsulated context.

    close : bool, optional
        Close `handler` once finished. Defaults to `True`.

    Examples
    --------
    Print debug logs during parsing, excluding compilation messages.

    >>> import logging
    >>> from finesse import Model
    >>> from finesse.utilities import logs
    >>> from finesse.utilities.logging import FinesseStreamHandler
    >>> handler = FinesseStreamHandler()
    >>> handler.exclude("finesse.script.compiler")
    >>> model = Model()
    >>> with logs(logging.getLogger(), level="debug", handler=handler):
    >>>     model.parse("laser l1 P=1")
    """
    old_level = None

    if level is not None:
        try:
            # Convert level name to uppercase.
            level = level.upper()
        except AttributeError:
            # Probably a number.
            pass

        old_level = logger.level
        logger.setLevel(level)

    if handler:
        logger.addHandler(handler)

    yield

    if level is not None:
        logger.setLevel(old_level)

    if handler:
        logger.removeHandler(handler)

        if close:
            handler.close()


@contextmanager
def tracebacks(tracebacks=True):
    """Show or hide tracebacks in the encapsulated context.

    Some environments, such as Jupyterlab, hide tracebacks by default. This context
    allows tracebacks to be forcefully shown or hidden temporarily.

    Parameters
    ----------
    tracebacks : bool, optional
        Show tracebacks. Defaults to True.

    Examples
    --------
    Print tracebacks during a run.

    >>> from finesse import Model
    >>> from finesse.utilities import tracebacks
    >>> model = Model()
    >>> with tracebacks():
    >>>     model.parse("laser l1 L=1")
    """
    from .. import show_tracebacks

    old_tracebacks = show_tracebacks(tracebacks)
    yield
    show_tracebacks(old_tracebacks)


class FinesseStreamHandler(logging.StreamHandler):
    """Finesse stream handler.

    This class provides a mechanism to exclude displayed log channels by wildcard. It is
    otherwise identical to :class:`logging.StreamHandler`.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__excluded_channels = None
        self.reset_exclude_patterns()

    def exclude(self, pattern):
        self.__excluded_channels.add(pattern)

    def reset_exclude_patterns(self):
        """Empty the configured log channel exclude patterns, and return what was
        there."""
        old_excludes = set(self.__excluded_channels or [])
        self.__excluded_channels = set()
        return old_excludes

    def filter(self, record):
        for pattern in self.__excluded_channels:
            if fnmatch(record.name, pattern):
                # Skip the record.
                return
        return record
