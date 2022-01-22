"""Кофнфигурация клиентского логгера"""

import sys
import os
import logging.handlers
from common.variables import LOGGING_LEVEL


LOGGER = logging.getLogger('client')

# файл для логирования
PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'client.log')

CLIENT_FORMATTER = logging.Formatter('%(asctime)s %(levelname)-8s %(filename)s %(message)s')

STREAM_HANDLER = logging.StreamHandler(sys.stderr)
STREAM_HANDLER.setFormatter(CLIENT_FORMATTER)
STREAM_HANDLER.setLevel(logging.ERROR)

LOG_FILE_HANDLER = logging.FileHandler(PATH, encoding='utf-8')
LOG_FILE_HANDLER.setFormatter(CLIENT_FORMATTER)

LOGGER.addHandler(STREAM_HANDLER)
LOGGER.addHandler(LOG_FILE_HANDLER)
LOGGER.setLevel(LOGGING_LEVEL)

# отладка
if __name__ == '__main__':
    LOGGER.critical('Критическая ошибка')
    LOGGER.error('Ошибка')
    LOGGER.debug('Отладочная информация')
    LOGGER.info('Информационное сообщение')
