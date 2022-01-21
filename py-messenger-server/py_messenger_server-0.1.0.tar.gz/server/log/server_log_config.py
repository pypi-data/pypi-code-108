"""Кофнфигурация серверного логгера"""

import sys
import os
import logging.handlers
from server_distrib.server.common.variables import LOGGING_LEVEL


LOGGER = logging.getLogger('server')

# файл для логирования
PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'server.log')

SERVER_FORMATTER = logging.Formatter('%(asctime)s %(levelname)-8s %(filename)s %(message)s')

STREAM_HANDLER = logging.StreamHandler(sys.stderr)
STREAM_HANDLER.setFormatter(SERVER_FORMATTER)
STREAM_HANDLER.setLevel(logging.ERROR)

LOG_FILE_HANDLER = logging.handlers.TimedRotatingFileHandler(PATH, encoding='utf8', interval=1, when='D')
LOG_FILE_HANDLER.setFormatter(SERVER_FORMATTER)

LOGGER.addHandler(STREAM_HANDLER)
LOGGER.addHandler(LOG_FILE_HANDLER)
LOGGER.setLevel(LOGGING_LEVEL)

# отладка
if __name__ == '__main__':
    LOGGER.critical('Критическая ошибка')
    LOGGER.error('Ошибка')
    LOGGER.debug('Отладочная информация')
    LOGGER.info('Информационное сообщение')
