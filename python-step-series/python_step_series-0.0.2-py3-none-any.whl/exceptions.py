#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Custom exceptions raised by this library."""


class StepSeriesException(Exception):
    """Base exception for the library."""

    original_exc: Exception = None


class ClientNotFoundError(Exception):
    """The requested client could not be found."""


class ClientClosedError(Exception):
    """The client's connection is not open."""


class InvalidCommandError(Exception):
    """The command cannot be executed."""


class ParseError(StepSeriesException):
    """Failed to parse the message from the device."""

    response: str
