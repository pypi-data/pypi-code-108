# This file is part of Sympathy for Data.
# Copyright (c) 2013 Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
import argparse
import logging

UNIVERSAL = 60


logging.addLevelName(UNIVERSAL, 'UNIVERSAL')


LEVELS = {
    'universal': UNIVERSAL,
    'critical': logging.CRITICAL,
    'error': logging.ERROR,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG
}

LOGGERS = [
    'all',
    'app',
    'app.backup',
    'app.stats',
    'app.undo',
    'app.hooks',
    'core',
    'core.env',
    'core.flowdict',
    'core.migrations',
    'core.syx',
    'core.tasks',
    'node',
    'node.perf',
    'test',
    'common',
    'common.credentials'
]


def get_logger(name):
    if name not in LOGGERS or name == 'all':
        raise ValueError("Could not get logger named {}".format(name))
    return logging.getLogger(name)


def _setup_logger(name, level):
    if name == 'all':
        name = None
    logging_level = LEVELS[level]
    logger = logging.getLogger(name)
    logger.setLevel(logging_level)


def setup_log_levels(log_levels):

    # Default levels
    log_levels.setdefault('all', 'error')
    log_levels.setdefault('node', 'info')

    for logger, level in log_levels.items():
        _setup_logger(logger, level)

    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter(logging.BASIC_FORMAT)

    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.DEBUG)

    root_logger = logging.getLogger()
    root_logger.addHandler(stream_handler)


class LogLevelAction(argparse.Action):
    """Action for parsing log levels from command line."""

    def __call__(self, parser, namespace, values, option_string=None):
        if len(values) == 1:
            logger = 'node' if self.dest == 'node_loglevel' else 'core'
            level = values[0]
        elif len(values) == 2:
            logger = values[0]
            level = values[1]
        else:
            raise argparse.ArgumentError(self, "expected 1 or 2 arguments")

        if logger not in LOGGERS:
            raise argparse.ArgumentError(
                self, "invalid logger: {!r}\n(choose from {})".format(
                    logger, ", ".join(LOGGERS)))

        log_level = None
        if level.isdigit():
            level = int(level)
            if level in range(len(LEVELS)):
                log_level = list(LEVELS.keys())[level]
        elif level in LEVELS.keys():
            log_level = level
        if log_level is None:
            raise argparse.ArgumentError(
                self, "invalid log level: {!r}\n(choose from {})".format(
                    level, ", ".join(LEVELS.keys())))

        namespace.loglevel[logger] = log_level
