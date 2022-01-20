# Copyright 2020-2021 Axis Communications AB.
#
# For a full list of individual contributors, please see the commit history.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""ETOS logger.

Example::

    import logging
    from uuid import uuid4
    from etos_lib.logging.logger import setup_logging, FORMAT_CONFIG

    FORMAT_CONFIG.identifier = str(uuid4())
    setup_logging("myApp", "1.0.0", "production")
    logger = logging.getLogger(__name__)
    logger.info("Hello!")
    >>> [2020-12-16 10:35:00][cb7c8cd9-40a6-4ecc-8321-a1eae6beae35] INFO: Hello!

"""
import sys
from pathlib import Path
import threading
import logging
import logging.config
from box import Box
from etos_lib.logging.filter import EtosFilter
from etos_lib.logging.formatter import EtosLogFormatter
from etos_lib.lib.debug import Debug

DEFAULT_CONFIG = Path(__file__).parent.joinpath("default_config.yaml")
DEFAULT_LOG_PATH = Debug().default_log_path

FORMAT_CONFIG = threading.local()


def setup_file_logging(config, log_filter):
    """Set up logging to file using the ETOS log formatter.

    Cofiguration file parameters ('file' must exist or no file handler is set up):

        logging:
          file:
            # Log level for file logging. Default=DEBUG.
            loglevel: INFO
            # Where to store logfile. Default=/home/you/etos/output.log.json
            logfile: path/to/log/file
            # Maximum number of files to rotate. Default=10
            max_files: 5
            # Maximum number of bytes in each logfile. Default=1048576/1MB
            max_bytes: 100

    :param config: File logging configuration.
    :type config: :obj:`Box`
    :param log_filter: Logfilter to add to file handler.
    :type log_filter: :obj:`EtosFilter`
    """
    loglevel = getattr(logging, config.get("loglevel", "DEBUG"))
    logfile = Path(config.get("logfile", DEFAULT_LOG_PATH))
    logfile.parent.mkdir(parents=True, exist_ok=True)

    max_files = config.get("max_files", 10)
    max_bytes = config.get("max_bytes", 10485760)  # Default is 10 MB
    root_logger = logging.getLogger()

    file_handler = logging.handlers.RotatingFileHandler(
        logfile, maxBytes=max_bytes, backupCount=max_files
    )
    file_handler.setFormatter(EtosLogFormatter())
    file_handler.setLevel(loglevel)
    file_handler.addFilter(log_filter)
    root_logger.addHandler(file_handler)


def setup_stream_logging(config, log_filter):
    """Set up logging to stdout stream.

    Cofiguration file parameters ('stream' must exist or no stream handler is set up):

        logging:
          stream:
            # Log level for stream logging. Default=INFO.
            loglevel: ERROR
            # Format to print logs with.
            # Default: [%(asctime)s][%(identifier)s] %(levelname)s:%(name)s: %(message)s
            logformat: %(message)s
            # Dateformat for %(asctime) format. Default: %Y-%m-%d %H:%M:%S
            dateformat: %Y-%d-%m %H:%M:%S

    :param config: Stream logging configuration.
    :type config: :obj:`Box`
    :param log_filter: Logfilter to add to stream handler.
    :type log_filter: :obj:`EtosFilter`
    """
    loglevel = getattr(logging, config.get("loglevel", "INFO"))

    logformat = config.get(
        "logformat", "[%(asctime)s][%(identifier)s] %(levelname)s:%(name)s: %(message)s"
    )
    dateformat = config.get("dateformat", "%Y-%m-%d %H:%M:%S")
    root_logger = logging.getLogger()
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(logging.Formatter(logformat, datefmt=dateformat))
    stream_handler.setLevel(loglevel)
    stream_handler.addFilter(log_filter)
    root_logger.addHandler(stream_handler)


def setup_logging(application, version, environment, config_file=DEFAULT_CONFIG):
    """Set up basic logging.

    :param application: Name of application to setup logging for.
    :type application: str
    :param version: Version of application to setup logging for.
    :type version: str
    :param environment: Environment in which this application resides.
    :type environment: str
    :param config_file: Filename of logging configuration.
    :type config_file: str
    """
    with open(config_file, encoding="utf-8") as yaml_file:
        config = Box.from_yaml(yaml_file)
    logging_config = config.logging

    log_filter = EtosFilter(application, version, environment, FORMAT_CONFIG)

    # Create a default logger which will not propagate messages
    # to the root logger. This logger will create records for all
    # messages, but not print them to stdout. Stdout printing
    # is setup in "setup_stream_logging" if the "stream" key exists
    # in the configuration file.
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.propagate = 0

    if logging_config.get("stream"):
        setup_stream_logging(logging_config.get("stream"), log_filter)
    if logging_config.get("file"):
        setup_file_logging(logging_config.get("file"), log_filter)
