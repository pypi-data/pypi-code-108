"""
    Module containing general utilities
"""

import argparse
import json
import logging
import os
import sys
import traceback
from datetime import datetime, timezone

from monasca_predictor.common.config import PredictorConfig

LOGGING_MAX_BYTES = 5 * 1024 * 1024

DEFAULT_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
SUPPORTED_TIMESTAMP_FORMAT_LIST = [
    DEFAULT_TIMESTAMP_FORMAT,
    "%Y-%m-%dT%H:%M:%S.%fZ",
    "%Y-%m-%d %H:%M:%S",
]

log = logging.getLogger(__name__)


class NewLineFormatter(logging.Formatter):
    """
    Custom logging formatter to better handle multi-line messages
    (inspired by https://stackoverflow.com/q/49049044)
    """

    def __init__(self, fmt, datefmt=None):
        """
        Init given the log line format and date format
        """
        logging.Formatter.__init__(self, fmt, datefmt)

    def format(self, record):
        """
        Override format function such that it replicates the
        timestamp/logging-preamble in each line, after every newline.
        """
        msg = logging.Formatter.format(self, record)

        if record.message != "":
            parts = msg.split(record.message)
            msg = msg.replace("\n", "\n" + parts[0])

        return msg


def initialize_logging(logger_name):
    """
    Inspired by monasca_agent.common.util.initialize_logging()
    """
    try:
        log_format = (
            "%%(asctime)s | %%(levelname)s | %s | %%(name)s(%%(filename)s:%%(lineno)s) "
            "| %%(message)s" % logger_name
        )
        log_date_format = "%Y-%m-%d %H:%M:%S %Z"
        config = PredictorConfig()
        logging_config = config.get_config(sections="Logging")

        logging.basicConfig(
            format=log_format,
            level=logging_config["log_level"] or logging.INFO,
            datefmt=log_date_format,
        )

        newline_formatter = NewLineFormatter(log_format, log_date_format)

        root_log = logging.getLogger()
        root_log.handlers[0].setFormatter(newline_formatter)

        # set up file loggers
        log_file = logging_config.get(f"{logger_name}_log_file")
        if log_file is not None and not logging_config["disable_file_logging"]:
            # make sure the log directory is writable
            # NOTE: the entire directory needs to be writable so that rotation works
            if os.access(os.path.dirname(log_file), os.R_OK | os.W_OK):
                if logging_config["enable_logrotate"]:
                    file_handler = logging.handlers.RotatingFileHandler(
                        log_file, maxBytes=LOGGING_MAX_BYTES, backupCount=1
                    )
                else:
                    file_handler = logging.FileHandler(log_file)

                formatter = NewLineFormatter(log_format, log_date_format)
                file_handler.setFormatter(formatter)

                root_log = logging.getLogger()
                root_log.addHandler(file_handler)
            else:
                sys.stderr.write(f"Log file is unwritable: '{log_file}'\n")

        # set up syslog
        if logging_config["log_to_syslog"]:
            try:
                syslog_format = (
                    "%s[%%(process)d]: %%(levelname)s (%%(filename)s:%%(lineno)s): "
                    "%%(message)s" % logger_name
                )

                if (
                    logging_config["syslog_host"] is not None
                    and logging_config["syslog_port"] is not None
                ):
                    sys_log_addr = (
                        logging_config["syslog_host"],
                        logging_config["syslog_port"],
                    )
                else:
                    sys_log_addr = "/dev/log"
                    # Special-case macs
                    if sys.platform == "darwin":
                        sys_log_addr = "/var/run/syslog"

                handler = logging.handlers.SysLogHandler(
                    address=sys_log_addr,
                    facility=logging.handlers.SysLogHandler.LOG_DAEMON,
                )
                handler.setFormatter(NewLineFormatter(syslog_format, log_date_format))

                root_log = logging.getLogger()
                root_log.addHandler(handler)
            except Exception as err:  # pylint: disable=broad-except
                sys.stderr.write(f"Error setting up syslog: '{str(err)}'\n")
                traceback.print_exc()

    except Exception as err:  # pylint: disable=broad-except
        sys.stderr.write(f"Couldn't initialize logging: {str(err)}\n")
        traceback.print_exc()

        # if config fails entirely, enable basic stdout logging as a fallback
        logging.basicConfig(
            format=log_format,
            level=logging.INFO,
            datefmt=log_date_format,
        )

    # re-get the log after logging is initialized
    global log
    log = logging.getLogger(__name__)


def format_datetime_str(timestamp):
    return datetime.strftime(timestamp, DEFAULT_TIMESTAMP_FORMAT)


def get_parsed_datetime(timestamp_str, time_zone=timezone.utc):
    for timestamp_format in SUPPORTED_TIMESTAMP_FORMAT_LIST:
        try:
            date_time = datetime.strptime(timestamp_str, timestamp_format)
            return date_time.replace(tzinfo=time_zone)
        except ValueError:
            pass
    raise ValueError(f"Cannot parse '{timestamp_str}', unsupported datetime format.")


def format_object_str(obj):
    return json.dumps(obj, indent=2)


def get_parsed_args(prog=None):
    parser = argparse.ArgumentParser(prog=prog)
    parser.add_argument(
        "-c", "--clean", action="store_true", default=False, dest="clean"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        dest="verbose",
        help="Print out stacktraces for errors in checks",
    )
    parser.add_argument(
        "-f",
        "--config-file",
        default=None,
        dest="config_file",
        help="Location for an alternate config rather than "
        "using the default config location.",
    )

    # TODO: provide options to add instances/auto-scaling groups details

    options = parser.parse_known_args(sys.argv[1:])

    return options
