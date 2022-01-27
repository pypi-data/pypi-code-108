import logging
from pathlib import Path

import boto3


class AOLogger:
    """
    Sets up logging and message distribution.

    Uses logging enums:

    CRITICAL: 'CRITICAL',
    ERROR: 'ERROR',
    WARNING: 'WARNING',
    INFO: 'INFO',
    DEBUG: 'DEBUG',
    NOTSET: 'NOTSET',
    """

    logging_session: boto3.Session
    logging_sns_client: boto3.client

    def __init__(self, app_name: str, loglevel: str, logFileRoot: Path):
        """
        app global start up logger. All app libraries use
        import logging

        my_log = logging.get_logger(__name__)
        to emit
        <time> <__name__>-LEVEL: message
        :param loglevel: string rep of python logging level
        :type loglevel: str
        :return:
        """
        from os import getpid
        from datetime import datetime
        from logging.handlers import RotatingFileHandler

        now: datetime = datetime.now()

        instance_id = f"{now.year}-{now.month}-{now.day}_{now.hour}_{now.minute}_{getpid()}"

        log_file_path: Path = Path(logFileRoot, instance_id)

        main_handler = RotatingFileHandler(log_file_path, maxBytes=4096000, backupCount=100)

        log_num_level: int = (getattr(logging, loglevel.upper(), logging.INFO))
        logging.basicConfig(format='%(asctime)s:%(name)s-%(levelname)s: %(message)s', level=log_num_level,
                            handlers=[main_handler])

        # create formatter and add it to the handlers
        # formatter = logging.Formatter()
        #
        # # Nothing fancy, just rotating log handler
        #
        # main_handler.setFormatter(formatter)
        # main_handler.setLevel(log_num_level)
        #
        # # This should be the parent of all loggers
        # logging.getLogger('').addHandler(main_handler)

        for quiet_logger in ['boto', 'botocore', 'boto3', 'requests', 'urllib3', 'request', 's3transfer']:
            ql = logging.getLogger(quiet_logger)
            ql.setLevel(logging.CRITICAL)
            ql.propagate = True

        #
        # SNS client

        self.logging_session = boto3.session.Session(region_name='us-east-1')
        self.logging_sns_client = self.logging_session.client('sns')

    def log(self, logging_level: int, message: str):
        """
        Sends a message to the logging and sns streams
        :param logging_level:
        :param message:
        :return:
        """
