import os
import sys
import click
import logging

from logging.handlers import TimedRotatingFileHandler
from cnvrgv2.config import Config, GLOBAL_CNVRG_PATH


class CnvrgLogger:
    DEFAULT_KEEP_DURATION_DAYS = 7
    CLI_LOGGER = "cli-logger"

    def __init__(self, click):
        # TODO: Assuming config file exist. make sure it exist on cli start
        config = Config()
        keep_duration_days = (
            config.keep_duration_days or
            CnvrgLogger.DEFAULT_KEEP_DURATION_DAYS
        )

        self.click = click
        self.logger = logging.getLogger(CnvrgLogger.CLI_LOGGER)
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s \t [%(levelname)s] > %(message)s')

        dirname = os.path.join(GLOBAL_CNVRG_PATH, "logs")

        if not os.path.isdir(dirname):
            os.mkdir(dirname)

        handler = TimedRotatingFileHandler(dirname + "/cnvrg.log",
                                           when="midnight",
                                           backupCount=keep_duration_days)
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

    def log_and_echo(self, message, error=False):
        """
        logs the message to the log file and prints it to stdout through click echo function
        @param message: The message to log
        @param error: Boolean. Whenever the log is an error. If it is, program will exit with status code 1
        @return: None
        """
        self.click.echo(message, err=error)
        if error:
            self.logger.error(message)
            sys.exit(1)
        else:
            self.logger.info(message)

    def __getattr__(self, item):
        return getattr(self.logger, item)

    @staticmethod
    @click.command()
    @click.option('--days',
                  default=7,
                  prompt='Please specify the number of days to keep logs',
                  help='Number of days to keep logs'
                  )
    def set_logs_keep_duration(days):
        """
        Sets the number of days to keep logs as backup
        """
        config = Config()
        config.keep_duration_days = days
        config.save()
