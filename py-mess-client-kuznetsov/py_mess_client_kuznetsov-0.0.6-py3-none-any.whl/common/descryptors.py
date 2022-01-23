import logging
import sys

# Инициализиция логера
# метод определения модуля, источника запуска.
if sys.argv[0].find("client") == -1:
    # если не клиент то сервер!
    logger = logging.getLogger("server")
else:
    # ну, раз не сервер, то клиент
    logger = logging.getLogger("client")


class Port:
    """
    The descriptor class for the port number.
    Allows you to use only ports 1023 to 65536.
    An exception is thrown when trying to set an unsuitable port number.
    """

    def __set__(self, instance, value):
        if not 1023 < value < 65536:
            logger.critical(
                f"Попытка запуска с указанием неподходящего порта {value}. Допустимы адреса с 1024 до 65535."
            )
            raise TypeError("Некорректрый номер порта")
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name
