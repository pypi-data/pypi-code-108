"""Кофнфиг клиентского логгера"""

import sys
import os
from logging import handlers, Formatter, StreamHandler, getLogger
from lesson_7.common.variables import LOGGING_LEVEL, LOGGING_LEVEL_FOR_STREAM_HANDLER

# sys.path.append('../')

# создаём формировщик логов (formatter):
CLIENT_FORMATTER = Formatter('%(asctime)s %(levelname)s %(filename)s %(message)s')

# Подготовка имени файла для логирования
PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, '../log_files/client.log')

# создаём потоки вывода логов
STREAM_HANDLER = StreamHandler(sys.stderr)
STREAM_HANDLER.setFormatter(CLIENT_FORMATTER)
STREAM_HANDLER.setLevel(LOGGING_LEVEL_FOR_STREAM_HANDLER)
LOG_FILE = handlers.TimedRotatingFileHandler(PATH, encoding='utf8', interval=1, when='D')
LOG_FILE.setFormatter(CLIENT_FORMATTER)

# создаём регистратор и настраиваем его
LOGGER = getLogger('client')
LOGGER.addHandler(STREAM_HANDLER)
LOGGER.addHandler(LOG_FILE)
LOGGER.setLevel(LOGGING_LEVEL)

# отладка
if __name__ == '__main__':
    LOGGER.critical('Тестовое сообщение! Критическая ошибка')
    LOGGER.error('Тестовое сообщение! Ошибка')
    LOGGER.debug('Тестовое сообщение! Отладочная информация')
    LOGGER.info('Тестовое сообщение! Информационное сообщение')
