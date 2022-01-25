"""
Декораторы
"""

import logging
import inspect
import log.client_log_config
import log.server_log_config
from sys import argv
from functools import wraps


class Log:
    """
    Класс-декоратор для логгирования вызова функций
    """
    def __init__(self):
        # определяем логгер
        if argv[0].find('run_server.py') != -1:
            self.func_logger = logging.getLogger('server')
        else:
            self.func_logger = logging.getLogger('client')

    def __call__(self, function):
        # возвращаем имя и док-стринг декорируемой функции
        @wraps(function)
        def wrapper(*args, **kwargs):
            result = function(*args, **kwargs)
            self.func_logger.debug(f'Вызвана функция {function.__name__} с параметрами: {args} {kwargs}.')
            self.func_logger.debug(f'Функция {function.__name__} вызвана из функции {inspect.stack()[1][3]}')
            return result
        return wrapper
