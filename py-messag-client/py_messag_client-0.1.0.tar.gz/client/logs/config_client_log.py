"""Кофнфиг клиентского логгера"""

import sys
import os
import logging
sys.path.append('../')
from common.variables import LOGGING_LEVEL, SERVER_FORMATTER_TYPE

# создаём формировщик логов (formatter):
# --------------------добавила переменную, которая будет содержать формат сообщений в файл varibales
CLIENT_FORMATTER = logging.Formatter(SERVER_FORMATTER_TYPE)

# Подготовка имени файла для логирования
PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'client.log')


# -------создаем лог для ввыода в файл
LOG_FILE = logging.FileHandler(PATH, encoding='utf8')
LOG_FILE.setFormatter(CLIENT_FORMATTER)

# создаём регистратор и настраиваем его
LOGGER = logging.getLogger('client')
LOGGER.addHandler(LOG_FILE)
#---------- устанавливаем уровень с которого будут выводится сообщения
LOGGER.setLevel(LOGGING_LEVEL)


if __name__ == '__main__':
    LOGGER.critical('Критическая ошибка')
    LOGGER.error('Ошибка')
    LOGGER.debug('Отладочная информация')
    LOGGER.info('Информационное сообщение')
