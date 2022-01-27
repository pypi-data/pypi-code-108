import logging
import os
import warnings
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

    logging_session: object
    logging_sns_client: boto3.client
    py_logger: logging = None
    app_name: str

    def __init__(self, app_name: str, log_level: str, log_file_root: Path):
        """
        app global start up logger. All app libraries use
        import logging

        my_log = logging.get_logger(__name__)
        to emit
        <time> <__name__>-LEVEL: message
        :type log_file_root: object
        :param log_level: string rep of python logging level
        :type log_level: str
        :return:
        """
        from os import getpid
        from datetime import datetime
        from logging.handlers import RotatingFileHandler

        # Params
        self.app_name = app_name
        now: datetime = datetime.now()

        instance_id = f"{now.year}-{now.month:02}-{now.day:02}_{now.hour:02}_{now.minute:02}_{getpid()}.{app_name}.log"

        self._log_file_path: Path = Path(str(log_file_root), instance_id)
        if not os.access(str(log_file_root), os.W_OK):
            raise NotADirectoryError(f"{log_file_root} is not  writable or does not exist")

        main_handler = RotatingFileHandler(str(self.log_file_name), maxBytes=4096000, backupCount=100)

        log_num_level: int = (getattr(logging, log_level.upper(), logging.INFO))
        # noinspection PyArgumentList
        logging.basicConfig(format='%(asctime)s:%(name)s-%(levelname)s: %(message)s', level=log_num_level,
                            handlers=[main_handler])
        # This gets a sublogger which should use the root logger above.
        # submodule
        self.py_logger = logging.getLogger(app_name)

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

        for quiet_logger in ['boto', 'botocore', 'boto3', 'requests', 'urllib3', 'request', 's3transfer', 'PIL', 'asyncio' ]:
            ql = logging.getLogger(quiet_logger)
            ql.setLevel(logging.CRITICAL)
            ql.propagate = True

        #
        # SNS client

        # Do we have an ARN? Dont encode in public.
        # See https://serverfault.com/questions/413397/how-to-set-environment-variable-in-systemd-service
        self.sns_arn = os.environ.get('AO_AWS_SNS_TOPIC_ARN')
        self.logging_session = boto3.session.Session(region_name='us-east-1')
        self.logging_sns_client = self.logging_session.client('sns')

    def log(self, logging_level: int, message: str):
        """
        Sends a message to the logging and sns streams
        :param logging_level: Use a value of logging. See https://docs.python.org/3/howto/logging.html#logging-levels
        :param message:
        :return:
        """

        if logging_level != logging.NOTSET \
                and logging_level != logging.CRITICAL \
                and logging_level != logging.ERROR \
                and logging_level != logging.WARNING \
                and logging_level != logging.INFO \
                and logging_level != logging.DEBUG:
            warnings.warn(f"Invalid logging {logging_level} given. Contact author")
            return

        print(f"{logging.getLevelName(logging_level)} - {message}")
        self.py_logger.log(logging_level, message)

        # jimk: volume-manifest-builder #37 hushing the SNS message
        if not self.hush:
            if self.sns_arn:
                if logging_level == logging.CRITICAL \
                        or (logging_level == logging.ERROR and message != "KeyboardInterrupt"):
                    try:
                        self.logging_sns_client.publish(TopicArn=self.sns_arn,
                                                        Message=f'{message}',
                                                        Subject=f"{logging.getLevelName(logging_level)} "
                                                                f"in {self.app_name}",
                                                        MessageStructure='string')
                    finally:
                        pass

    def error(self, message: str):
        self.log(logging.ERROR, message)

    def critical(self, message: str):
        self.log(logging.CRITICAL, message)

    def warn(self, message: str):
        self.log(logging.WARN, message)

    def info(self, message: str):
        self.log(logging.INFO, message)

    def debug(self, message: str):
        self.log(logging.DEBUG, message)

    def exception(self, message: str):
        self.log(logging.CRITICAL, message)

    _hush: bool = False

    @property
    def hush(self):
        return self._hush

    @hush.setter
    def hush(self, value: bool):
        self._hush = value

    @property
    def log_file_name(self) -> str:
        return str(self._log_file_path)
