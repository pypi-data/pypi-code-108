# Copyright (c) Qotto, 2021

"""
Simple logging handler

>>> import sys
>>> import logging
>>> logger = logging.getLogger('my_logger')
>>> logger.setLevel('DEBUG')
>>> handler = SimpleHandler(stream=sys.stdout)
>>> logger.addHandler(handler)
>>> logger.info('test')
[...] [RID:] [CID:] <MainThread> INFO my_logger (<doctest eventy.logging L1) test
"""

from logging import Formatter, StreamHandler

from coloredlogs import ColoredFormatter

from .info_providers import correlation_id_provider, request_id_provider

__all__ = [
    'SimpleHandler',
]


class SimpleHandler(StreamHandler):
    """
    Simple logging handler, extending StreamHandler with optional colors and context information
    """

    def __init__(
        self,
        stream=None,
        fmt='%(asctime)s '
            '[RID:%(request_id)s] [CID:%(correlation_id)s] '
            '<%(threadName)s> '
            '%(levelname)s %(name)s (%(module)s L%(lineno)d) '
            '%(message)s',
        datefmt='[%Y-%m-%d %H:%M:%S.%f %z]',
        colored=False,
        level='DEBUG',
    ) -> None:
        """
        Initialize the handler

        :param stream: output stream, default None (sys.stderr), propagated to StreamHandler.__init__
        :param fmt: Format string used to initialize the :obj:`logging.Formatter`, can use the ``correlation_id`` and ``request_id`` fields of the log record
        :param datefmt: Date format string used to initialized the :obj:`logging.Formatter`
        :param colored: Output colored messages (different colors for log levels)
        :param level: log level, default 'DEBUG'. A log record is printed if its level is above both Handler level and Logger level
        """
        super().__init__(stream=stream)
        self.addFilter(correlation_id_provider)
        self.addFilter(request_id_provider)
        if colored:
            self.setFormatter(ColoredFormatter(fmt=fmt, datefmt=datefmt))
        else:
            self.setFormatter(Formatter(fmt=fmt, datefmt=datefmt))
        self.setLevel(level=level)
