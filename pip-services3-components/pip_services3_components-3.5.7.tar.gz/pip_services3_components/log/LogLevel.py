# -*- coding: utf-8 -*-
"""
    pip_services3_components.log.LogLevel
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Log level enumeration
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""


class LogLevel:
    """
    Standard log levels.

    Logs at debug and trace levels are usually captured only locally for troubleshooting
    and never sent to consolidated log services.
    """

    Nothing = 0
    """
    Nothing to be logged
    """

    Fatal = 1
    """
    Logs only fatal errors that cause microservice to fail
    """

    Error = 2
    """
    Logs all errors - fatal or recoverable
    """

    Warn = 3
    """
    Logs errors and warnings
    """

    Info = 4
    """
    Logs errors and important information messages
    """

    Debug = 5
    """
    Logs everything up to high-level debugging information
    """

    Trace = 6
    """
    Logs everything down to fine-granular debugging messages
    """
