import watchtower
import logging

from botocore.exceptions import BotoCoreError

LOGGING_FORMAT = '%(asctime)s - %(levelname)-7s - %(message)s'


def get_logger(log_name: str = __name__,
               level: int=logging.INFO,
               log_group: str="etl") -> logging.Logger:
    logging.basicConfig(level=level, format=LOGGING_FORMAT)
    logger = logging.getLogger(log_name)
    try:
        logger.addHandler(watchtower.CloudWatchLogHandler(log_group=log_group))
    except BotoCoreError:
        logger.warning("Failed to initialise AWS Cloudwatch log handler."
                       "Please verify your AWS configuration.")
    return logger

