"""
Конфигурационный файл для логгирования сервера
"""
import logging
import logging.handlers
import os

SERVER_LOGGER = logging.getLogger('server')
LOG_FILE_NAME = os.path.join(os.path.dirname(__file__), "server_log.log")

FORMATTER = logging.Formatter("%(asctime)s - %(levelname)-8s - %(filename)-10s - %(message)s")

FILE_HANDLER = logging.handlers.TimedRotatingFileHandler(LOG_FILE_NAME,
                                                         interval=1, when='D',
                                                         encoding='utf-8')
FILE_HANDLER.setFormatter(FORMATTER)

STREAM_HANDLER = logging.StreamHandler()
STREAM_HANDLER.setFormatter(FORMATTER)
STREAM_HANDLER.setLevel(logging.INFO)

SERVER_LOGGER.addHandler(FILE_HANDLER)
SERVER_LOGGER.addHandler(STREAM_HANDLER)
SERVER_LOGGER.setLevel(logging.DEBUG)

if __name__ == '__main__':
    SERVER_LOGGER.debug('Test. Debug info')
    SERVER_LOGGER.info('Test. Information')
    SERVER_LOGGER.warning('Test. Warning')
    SERVER_LOGGER.error(f'Test. Error')
    SERVER_LOGGER.critical(f'Test. Critical error')
