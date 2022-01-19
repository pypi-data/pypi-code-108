import logging
from messenger2.logs.log_configs import client_log_config, server_log_config
import traceback
import sys

WAY = traceback.format_stack()[0].split()[1].strip('",').split('/')[-1]
if WAY == 'server_start.py':
    LOGGER = logging.getLogger(server_log_config.SERVER_LOGGER)
else:
    LOGGER = logging.getLogger(client_log_config.CLIENT_LOGGER)


def login_required():
    """
    decorator that check if user is register in system
    :return: func(*args, **kwargs) or alert request
    """
    def deco(func):
        def wrap(*args, **kwargs):
            if WAY == "server_start.py":
                from messenger2.server.core import Server
                from messenger2.protocols.JIM import JIM
                from socket import socket
                print("check login required")
                server = None
                client = None
                protocol = None
                for arg in args:
                    if isinstance(arg, Server):
                        server = arg

                    if isinstance(arg, socket):
                        client = arg

                    if isinstance(arg, JIM):
                        protocol = arg

                if server is None or client is None or protocol is None:
                    for key, item in kwargs.items():
                        if isinstance(item, Server):
                            server = item

                        if isinstance(item, socket):
                            client = item

                        if isinstance(item, JIM):
                            protocol = item

                print(server, protocol, client)
                if server is None:
                    raise Exception

                elif client is None:
                    raise Exception

                elif protocol is None:
                    msg = "Клиентский запрос использует неправильный протокол"
                    LOGGER.error(msg)
                    return JIM().get_request(action=JIM.ALERT, message=msg)
                else:

                    if protocol.presence_type or protocol.alert_type:
                        LOGGER.info("Подключение нового клиента")
                        return func(*args, **kwargs)
                    else:
                        database = server.db
                        active_users = [
                            user[1].login for user in database.get_active_user_list(
                                join_users=True)]
                        msg = "Попытка неавторизированного доступа"
                        if protocol.join_type:
                            LOGGER.info("Авторизация нового клиента")
                            return func(*args, **kwargs)
                        elif client in server.clients:
                            for login, client_socket in server.client_names.items():
                                if client_socket == client:
                                    if login in active_users:
                                        return func(*args, **kwargs)
                                    else:
                                        LOGGER.info(msg)
                                        return JIM().get_request(action=JIM.ALERT, message=msg)
                            LOGGER.info(msg)
                            return JIM().get_request(action=JIM.ALERT, message=msg)

                        else:
                            LOGGER.info(msg)
                            return JIM().get_request(action=JIM.ALERT, message=msg)

            else:
                LOGGER.critical("Несанкционированный запуск сервера")
                raise Exception
        return wrap

    return deco


def log_exception(exception):
    """
    decorator that log raised exceptions
    :param exception: Exception
    :return: func(*args, **kwargs)
    """
    def deco(func):
        def wrap(*args, **kwargs):

            try:
                log_msg = f'Была вызвана функция {func.__name__} с параметрами {args}, {kwargs} ' \
                          f'В модуле {func.__module__}'
                LOGGER.info(log_msg)
                return func(*args, **kwargs)

            except exception:

                log_msg = f'Возникла критическая ошибка в функции {func.__name__}' \
                          f'С параметрами {args}, {kwargs}' \
                          f'В модуле {func.__module__}' \
                          f'В файле {WAY}'
                LOGGER.critical(log_msg)
                LOGGER.critical(traceback.format_exc())
                sys.exit(-1)

        return wrap

    return deco


def thread_lock(locker):

    def deco(func):

        def wrap(*args, **kwargs):
            locker.acquire()
            result = func(*args, **kwargs)
            locker.release()
            return result

        return wrap

    return deco


class LogException:

    def __init__(self, exception):
        self.exception = exception

    def __call__(self, func):

        def deco(*args, **kwargs):
            try:
                log_msg = f'Была вызвана функция {func.__name__} с параметрами {args}, {kwargs} ' \
                          f'В модуле {func.__module__}'
                LOGGER.info(log_msg)
                return func(*args, **kwargs)

            except self.exception:
                log_msg = f'Возникла критическая ошибка в функции {func.__name__}' \
                          f'С параметрами {args}, {kwargs}' \
                          f'В модуле {func.__module__}' \
                          f'В файле {WAY}'
                LOGGER.critical(log_msg)
                LOGGER.critical(traceback.format_exc())
                sys.exit(-1)

        return deco


if __name__ == "__main__":
    pass
