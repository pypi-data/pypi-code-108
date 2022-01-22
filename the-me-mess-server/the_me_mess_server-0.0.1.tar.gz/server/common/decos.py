"""Декораторы"""

import sys
import logging
from socket import socket

import lesson_7.logs.configs.config_server_log
import lesson_7.logs.configs.config_client_log
import traceback
import inspect

# метод определения модуля, источника запуска.
# Метод find () возвращает индекс первого вхождения искомой подстроки,
# если он найден в данной строке.
# Если его не найдено, - возвращает -1.
# os.path.split(sys.argv[0])[1]
if sys.argv[0].find('client') == -1:
    # если не клиент то сервер!
    CURRENT_LOGGER = logging.getLogger('server')
else:
    # ну, раз не сервер, то клиент
    CURRENT_LOGGER = logging.getLogger('client')


# Реализация в виде функции
def log(function_to_log):
    """
    Декоратор, выполняющий логирование вызовов функций.
    Сохраняет события типа debug, содержащие
    информацию о имени вызываемой функиции, параметры с которыми
    вызывается функция, и модуль, вызывающий функцию.
    """

    def log_saver(*args, **kwargs):
        """Обертка"""
        ret_func = function_to_log(*args, **kwargs)
        CURRENT_LOGGER.debug(f'Была вызвана функция {function_to_log.__name__} c параметрами {args}, {kwargs}. '
                             f'Вызов из модуля {function_to_log.__module__}.'
                             f'Вызов из функции {traceback.format_stack()[0].strip().split()[-1]}.'
                             f'Вызов из функции {inspect.stack()[1][3]}', stacklevel=2)
        return ret_func

    return log_saver


# Реализация в виде класса
class Log:
    """Класс-декоратор"""

    def __call__(self, function_to_log):
        def log_saver(*args, **kwargs):
            """Обертка"""
            ret_func = function_to_log(*args, **kwargs)
            CURRENT_LOGGER.debug(f'Была вызвана функция {function_to_log.__name__} c параметрами {args}, {kwargs}. '
                                 f'Вызов из модуля {function_to_log.__module__}. Вызов из'
                                 f' функции {traceback.format_stack()[0].strip().split()[-1]}.'
                                 f'Вызов из функции {inspect.stack()[1][3]}', stacklevel=2)
            return ret_func

        return log_saver


def login_required(func):
    """
    Декоратор, проверяющий, что клиент авторизован на сервере.
    Проверяет, что передаваемый объект сокета находится в
    списке авторизованных клиентов.
    За исключением передачи словаря-запроса
    на авторизацию. Если клиент не авторизован,
    генерирует исключение TypeError
    """

    def checker(*args, **kwargs):
        # проверяем, что первый аргумент - экземпляр MessageProcessor
        # Импортить необходимо тут, иначе ошибка рекурсивного импорта.
        from lesson_6.server.core import MessageProcessor
        from lesson_6.common.variables import ACTION, PRESENCE
        if isinstance(args[0], MessageProcessor):
            found = False
            for arg in args:
                if isinstance(arg, socket):
                    # Проверяем, что данный сокет есть в списке names класса
                    # MessageProcessor
                    for client in args[0].names:
                        if args[0].names[client] == arg:
                            found = True

            # Теперь надо проверить, что передаваемые аргументы не presence
            # сообщение. Если presense, то разрешаем
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
