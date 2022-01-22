import coloredlogs, logging

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
coloredlogs.install(level="DEBUG", logger=logger)
