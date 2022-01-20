"""
Useful handlers are provided in the package
"""

from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.GENERIC_OPERATING_SYSTEM_SERVICES)
class WatchedFileHandler:
    """
    It is a FileHandler which watches the file it is logging to. If the file changes, it is closed and reopened using the file name.
    """

    pass


@tags(TagConsts.GENERIC_OPERATING_SYSTEM_SERVICES)
class RotatingFileHandler:
    """
    It supports rotation of disk log files.
    """

    pass


@tags(TagConsts.GENERIC_OPERATING_SYSTEM_SERVICES)
class TimedRotatingFileHandler:
    """
    It supports rotation of disk log files at certain timed intervals.
    """

    pass


@tags(TagConsts.GENERIC_OPERATING_SYSTEM_SERVICES)
class SocketHandler:
    """
    It sends logging output to a network socket.
    """

    pass


@tags(TagConsts.GENERIC_OPERATING_SYSTEM_SERVICES)
class DatagramHandler:
    """
    It support sending logging messages over UDP sockets.
    """

    pass


@tags(TagConsts.GENERIC_OPERATING_SYSTEM_SERVICES)
class SysLogHandler:
    """
    It supports sending logging messages to a remote or local Unix syslog.
    """

    pass


@tags(TagConsts.GENERIC_OPERATING_SYSTEM_SERVICES)
class NTEventLogHandler:
    """
    It supports sending logging messages to a local Windows NT, Windows 2000 or Windows XP event log.
    """

    pass


@tags(TagConsts.GENERIC_OPERATING_SYSTEM_SERVICES)
class SMTPHandler:
    """
    It supports sending logging messages to an email address via SMTP.
    """

    pass


@tags(TagConsts.GENERIC_OPERATING_SYSTEM_SERVICES)
class MemoryHandler:
    """
    It supports buffering of logging records in memory, periodically flushing them to a target handler.
    """

    pass


@tags(TagConsts.GENERIC_OPERATING_SYSTEM_SERVICES)
class HTTPHandler:
    """
    It supports sending logging messages to a Web server, using either GET or POST semantics.
    """

    pass
