"""
Дескриптор для класса серверного сокета.
Реализует проверку номера порта.
Это должно быть целое число (>=0). Значение порта по умолчанию равняется 7777.
Номер порта передается в экземпляр дескриптора при запуске сервера.
"""
import logging
import log.server_log_config
server_log = logging.getLogger('server')


class PortDescriptor:
    """
    Класс-дескриптор для проверки номера серверного порта
    """
    def __set__(self, instance, port):
        if not 1024 <= port <= 65535:
            server_log.critical(f'Неверное значение порта {port}.'
                                f'Порт должен находиться в диапазоне от 1024 до 65535.')
            exit(1)

        instance.__dict__[self.name] = port

    def __set_name__(self, owner, name):
        self.name = name
