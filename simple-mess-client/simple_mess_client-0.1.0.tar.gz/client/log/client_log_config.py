"""
Конфигурационный файл для логгирования клиента
"""
import logging
import os

CLIENT_LOGGER = logging.getLogger('client')
LOG_FILE_NAME = os.path.join(os.path.dirname(__file__), "client_log.log")

FORMATTER = logging.Formatter("%(asctime)s - %(levelname)-8s - %(filename)-10s - %(message)s")

FILE_HANDLER = logging.FileHandler(LOG_FILE_NAME, encoding='utf-8')
FILE_HANDLER.setFormatter(FORMATTER)

STREAM_HANDLER = logging.StreamHandler()
STREAM_HANDLER.setFormatter(FORMATTER)
STREAM_HANDLER.setLevel(logging.ERROR)

CLIENT_LOGGER.addHandler(FILE_HANDLER)
CLIENT_LOGGER.addHandler(STREAM_HANDLER)
CLIENT_LOGGER.setLevel(logging.DEBUG)

if __name__ == '__main__':
    CLIENT_LOGGER.debug('Test. Debug info')
    CLIENT_LOGGER.info('Test. Information')
    CLIENT_LOGGER.warning('Test. Warning')
    CLIENT_LOGGER.error(f'Test. Error')
    CLIENT_LOGGER.critical(f'Test. Critical error')
