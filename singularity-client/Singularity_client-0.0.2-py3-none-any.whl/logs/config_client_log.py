import logging
import sys
import os

from common.variables import LOGGING_LEVEL, FORMATTER_DEFAULT

'''
Конфигуратор логов клиента
'''

FORMATTER = FORMATTER_DEFAULT
PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH,'client.log')

STREAM_HANDLER = logging.StreamHandler(sys.stderr)
STREAM_HANDLER.setFormatter(FORMATTER)
STREAM_HANDLER.setLevel(logging.DEBUG)
LOG_FILE = logging.FileHandler(PATH, encoding='utf-8')
LOG_FILE.setFormatter(FORMATTER)

LOGGER = logging.getLogger('client_file')
LOGGER.addHandler(STREAM_HANDLER)
LOGGER.addHandler(LOG_FILE)
LOGGER.setLevel(LOGGING_LEVEL)

if __name__ == '__main__':
    LOGGER.critical('Критическая ошибка')
    LOGGER.error('Ошибка')
    LOGGER.info('Информацияонное сообщение')
    LOGGER.debug('Отладочная информация')

