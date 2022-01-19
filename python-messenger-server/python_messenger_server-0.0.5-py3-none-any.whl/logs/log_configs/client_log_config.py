import logging
from messenger2.config import CLIENT_LOG_DIR

"""
Creates main client log config data
"""

FILE_LOG_NAME = 'client.log'
CLIENT_LOGGER = 'messenger.client'

LOG = logging.getLogger(CLIENT_LOGGER)

FILE_HANDLER = logging.FileHandler(
    f'{CLIENT_LOG_DIR}\\{FILE_LOG_NAME}',
    encoding='utf-8')
FILE_HANDLER.setLevel(logging.DEBUG)

FORMATTER = logging.Formatter("%(asctime)s - %(levelname)s : %(message)s")

FILE_HANDLER.setFormatter(FORMATTER)

LOG.addHandler(FILE_HANDLER)
LOG.setLevel(logging.DEBUG)

if __name__ == '__main__':
    print(CLIENT_LOG_DIR)
    print(LOG)
    LOG.debug('test_error')
