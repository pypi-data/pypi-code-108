"""Decorators"""

import sys
import socket
import logging
import types
from functools import wraps

import logs.config_server_log
import logs.config_client_log
import traceback
import inspect

# метод определения модуля, источника запуска.
# Метод find () возвращает индекс первого вхождения искомой подстроки,
# если он найден в данной строке.
# Если его не найдено, - возвращает -1.
# if sys.argv[0].find('client') == -1:
#     # если не клиент то сервер!
#     LOGGER = logging.getLogger('server')
# else:
#     # ну, раз не сервер, то клиент
#     LOGGER = logging.getLogger('client')


def get_module_name(arg):
    """ Method for determining the startup source module ('client', 'server',...) """
    start = arg.rfind('/')+1
    end = arg.rfind('.py')
    return arg[start:end]

LOGGER = logging.getLogger(get_module_name(sys.argv[0]))

def log_func(func_to_log):
    """Function decorator for functions"""
    @wraps(func_to_log)
    def log_saver(*args, **kwargs):
        # It happens that parameters are passed, but the function does not "wait" for them
        try:
            ret = func_to_log(*args, **kwargs)
        except:
            ret = func_to_log()
        func_name = func_to_log.__name__ if hasattr(func_to_log, '__name__') else \
            func_to_log.name if hasattr(func_to_log, 'name') else ''
        LOGGER.debug(f'Была вызвана функция {func_name} c параметрами {args}, {kwargs}. '
                     f'Вызов из модуля {func_to_log.__module__}.'
                     f'Вызов из функции {traceback.format_stack()[0].strip().split()[-1]}.'
                     f'Вызов из функции {inspect.stack()[1][3]}')
        return ret
    return log_saver


def log_class(cls):
    """Decorator function for Classes"""
    for name, method in cls.__dict__.items():
        if not name.startswith('_'):
            if isinstance(method, types.FunctionType) or not hasattr(method, '__func__'):
                setattr(cls, name, method_decorator(method))
            else:                                                                       # @staticmethod not callable
                setattr(cls, name, method_decorator(method.__func__, is_static=True))   # доступ с помощью __func__

    return cls


def method_decorator(func_to_log, is_static=False):
    @wraps(func_to_log)
    def wrapper(self, *args, **kwargs):
        func_name = func_to_log.__name__ if hasattr(func_to_log, '__name__') else \
            func_to_log.name if hasattr(func_to_log, 'name') else ''
        args_all = [self].extend(args) if is_static else args
        LOGGER.debug(f'Была вызвана функция {func_name} c параметрами {args_all}, {kwargs}. '
                     f'Вызов из модуля {func_to_log.__module__}.'
                     f'Вызов из функции {traceback.format_stack()[0].strip().split()[-1]}.'
                     f'Вызов из функции {inspect.stack()[1][3]}')
        return func_to_log(self, *args, **kwargs)
        # return func_to_log(*args, **kwargs) if is_static else func_to_log(self, *args, **kwargs)
    return wrapper


def login_required(func):
    """
    A decorator that verifies that the client is authorized on the server.
    Checks that the transmitted socket object is in
    the list of authorized clients.
    Except for the transfer of the dictionary-
    authorization request. If the client is not logged in,
    generates a TypeError exception
    """

    def checker(*args, **kwargs):
        # проверяем, что первый аргумент - экземпляр MessageProcessor
        # Импортить необходимо тут, иначе ошибка рекурсивного импорта.
        from server.core import MessageProcessor
        from common.variables import ACTION, PRESENCE
        if isinstance(args[0], MessageProcessor):
            found = False
            for arg in args:
                if isinstance(arg, socket.socket):
                    # Проверяем, что данный сокет есть в списке names класса
                    # MessageProcessor
                    for client in args[0].names:
                        if args[0].names[client] == arg:
                            found = True

            # Теперь надо проверить, что передаваемые аргументы не presence
            # сообщение. Если presence, то разрешаем
            for arg in args:
                if isinstance(arg, dict):
                    if ACTION in arg and arg[ACTION] == PRESENCE:
                        found = True
            # Если не не авторизован и не сообщение начала авторизации, то
            # вызываем исключение.
            if not found:
                raise TypeError
        return func(*args, **kwargs)

    return checker