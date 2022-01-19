import logging
from messenger2.config import SERVER_LOG_DIR
from logging.handlers import TimedRotatingFileHandler

"""
Creates main server config data
"""

FILE_LOG_NAME = 'server.log'
SERVER_LOGGER = 'messenger.server'

LOG = logging.getLogger(SERVER_LOGGER)

FILE_HANDLER = TimedRotatingFileHandler(
    f'{SERVER_LOG_DIR}\\{FILE_LOG_NAME}',
    when='D',
    interval=1,
    encoding='utf-8')
FILE_HANDLER.setLevel(logging.DEBUG)

FORMATTER = logging.Formatter("%(asctime)s - %(levelname)s : %(message)s")

FILE_HANDLER.setFormatter(FORMATTER)

LOG.addHandler(FILE_HANDLER)
LOG.setLevel(logging.DEBUG)

if __name__ == '__main__':
    print(SERVER_LOG_DIR)
    print(LOG)
    LOG.debug('test_error')
