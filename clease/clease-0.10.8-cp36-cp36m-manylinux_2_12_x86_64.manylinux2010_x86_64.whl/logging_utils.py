from typing import Optional, TextIO, Iterator
import logging
import sys
from contextlib import contextmanager

__all__ = ('log_stream', 'log_stream_context', 'get_root_clease_logger')


def get_root_clease_logger() -> logging.Logger:
    """Get the root clease logger."""
    return logging.getLogger('clease')


def log_stream(level: Optional[int] = None,
               stream: TextIO = sys.stdout,
               fmt: Optional[str] = None) -> logging.StreamHandler:
    """Helper function to enable CLEASE logging to a stream. Default stream is stdout.
    This function permanently adjusts the global CLEASE logger. Use ``log_stream_context``
    to temporarily adjust the clease logger.
    Returns the added stream handler, so that it can be adjusted as needed.

    Following example will cause all logging statements of "INFO" or higher to be
    printed to stdout indefinitely.
    >>> log_stream(level=logging.INFO)

    Parameters:

    level: int or ``None``
        Sets the level of CLEASE logger. If ``None``, the level will not be adjusted.

    stream:
        Stream to add logging to, e.g. sys.stdout or an opened file.

    fmt: str
        Custom format message. See the python ``logging`` module for more details.
        Default format is '%(name)s - %(levelname)s - %(message)s'.
    """

    # Get the root CLEASE logger
    root_logger = get_root_clease_logger()

    handler = _make_stream_handler(level, stream, fmt=fmt)

    if level is not None:
        # Update the root log level
        root_logger.setLevel(level)
    root_logger.addHandler(handler)
    return handler


@contextmanager
def log_stream_context(level: Optional[int] = None,
                       stream: TextIO = sys.stdout,
                       fmt: Optional[str] = None) -> Iterator[logging.StreamHandler]:
    """Context which temporarily adds a stream handler to the root CLEASE logger.
    Yields the added stream handler, so that it can be adjusted as needed.

    Example usage:
    with log_stream_context(level=logging.INFO):
        # CLEASE logs will also be printed to stdout
    # the stdout handler is removed, and logs will no longer be printed here.

    Parameters:

    level: int or ``None``
        Sets the level of CLEASE logger. If ``None``, the level will not be adjusted.

    stream:
        Stream to add logging to, e.g. sys.stdout or an opened file.

    fmt: str
        Custom format message. See the python ``logging`` module for more details.
        Default format is '%(name)s - %(levelname)s - %(message)s'.
    """

    root_logger = get_root_clease_logger()
    original_log_level = root_logger.level  # Current log level

    # Creates the handler, and adds it to the root logger
    handler = log_stream(level=level, stream=stream, fmt=fmt)

    try:
        # We yield the handler, so the user can make mutations
        # to the handler directly if they so choose, since it's attached directly
        # into the root logger.
        yield handler
    finally:
        # Remove the handler, and reset the log level (if needed)
        root_logger.removeHandler(handler)
        if level is not None:
            # We adjusted the root logger, reset it
            root_logger.setLevel(original_log_level)


def _make_stream_handler(level: Optional[int],
                         stream: TextIO,
                         fmt: Optional[str] = None) -> logging.StreamHandler:
    """Helper function to create a stream handler with a specified level and stream.
    If the level is None, use the effective level of the CLEASE root logger.
    """
    # Find the effective level to give the handler
    eff_level = _get_effective_level(level)

    # Create the stream handler, and set the level and formatting.
    handler = logging.StreamHandler(stream)
    handler.setLevel(eff_level)
    # Set some formatting
    if fmt is None:
        fmt = '%(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(fmt)
    handler.setFormatter(formatter)
    return handler


def _get_effective_level(level: Optional[int]) -> int:
    """Helper function to get the effective level - if the level is None,
    we use the current level of the CLEASEroot logger, otherwise use the provided level
    """
    # If level is None, use the current level of the root logger
    if level is None:
        return get_root_clease_logger().level
    return level
