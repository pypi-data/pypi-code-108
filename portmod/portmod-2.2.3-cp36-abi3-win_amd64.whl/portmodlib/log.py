# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import logging

from .colour import bright, red, yellow
from .l10n import l10n


class PortmodFormatter(logging.Formatter):
    FORMATS = {
        logging.WARNING: logging.StrFormatStyle(
            bright(yellow("WARNING")) + ": {message}"
        ),
        logging.ERROR: logging.StrFormatStyle(bright(red("ERROR")) + ": {message}"),
        logging.CRITICAL: logging.StrFormatStyle(
            bright(red("CRITICAL")) + ": {message}"
        ),
        "DEFAULT": logging.StrFormatStyle("{message}"),
    }

    def __init__(self):
        super().__init__(style="{")

    def format(self, record):
        self._style = self.FORMATS.get(record.levelno, self.FORMATS["DEFAULT"])
        return logging.Formatter.format(self, record)


_LOG_HANDLER = None


def init_logger(args):
    """Initializes python logger"""
    global _LOG_HANDLER
    if not _LOG_HANDLER:
        _LOG_HANDLER = logging.StreamHandler()
        logging.root.addHandler(_LOG_HANDLER)
        formatter = PortmodFormatter()
        _LOG_HANDLER.setFormatter(formatter)

    if args.verbose:
        _LOG_HANDLER.setLevel(logging.DEBUG)
        logging.root.setLevel(logging.DEBUG)
    elif args.quiet:
        _LOG_HANDLER.setLevel(logging.WARN)
        logging.root.setLevel(logging.WARN)
    else:
        _LOG_HANDLER.setLevel(logging.INFO)
        logging.root.setLevel(logging.INFO)


def add_logging_arguments(parser):
    parser.add_argument("-q", "--quiet", help=l10n("quiet-help"), action="store_true")
    parser.add_argument(
        "-v", "--verbose", help=l10n("verbose-help"), action="store_true"
    )


__MESSAGES = set()


def warn_once(message: str):
    if message not in __MESSAGES:
        logging.warning(message)
        __MESSAGES.add(message)
