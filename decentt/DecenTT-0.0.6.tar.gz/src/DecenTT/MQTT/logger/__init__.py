import coloredlogs, logging
from DecenTT.env.config import LOG_PATH

logging.basicConfig(filename= f"{LOG_PATH}",format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
coloredlogs.install(level="DEBUG", logger=logger)
