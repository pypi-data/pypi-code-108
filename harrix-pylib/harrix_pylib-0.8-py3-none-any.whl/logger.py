import logging
from logging.handlers import RotatingFileHandler


class Logger(object):
    def __new__(self):
        if not hasattr(self, "instance"):
            self.instance = super(Logger, self).__new__(self)
        return self.instance

    def __init__(self):
        self.is_log_console = True
        self.is_log_file = False

        log_format = logging.Formatter("[%(levelname)s] %(asctime)s - %(message)s")

        self.__logger_console = logging.getLogger("dev.harrix.logger.console")
        self.__logger_console.setLevel(logging.DEBUG)

        handler_console = logging.StreamHandler()
        handler_console.setFormatter(log_format)
        handler_console.setLevel(logging.DEBUG)
        self.__logger_console.addHandler(handler_console)

        self.__logger_file = logging.getLogger("dev.harrix.logger.file")
        self.__logger_file.setLevel(logging.DEBUG)
        handler_file = RotatingFileHandler(
            "harrix.log", maxBytes=104857600, backupCount=100
        )
        handler_file.setFormatter(log_format)
        handler_file.setLevel(logging.DEBUG)
        self.__logger_file.addHandler(handler_file)

        self.__logger_file_error = logging.getLogger("dev.harrix.logger.file.error")
        self.__logger_file_error.setLevel(logging.ERROR)
        handler_file_error = RotatingFileHandler(
            "harrix_error.log", maxBytes=104857600, backupCount=100
        )
        handler_file_error.setFormatter(log_format)
        handler_file_error.setLevel(logging.ERROR)
        self.__logger_file_error.addHandler(handler_file_error)

    def debug(self, msg):
        if self.is_log_console:
            self.__logger_console.debug(msg)
        if self.is_log_file:
            self.__logger_file.debug(msg)
            self.__logger_file_error.debug(msg)

    def info(self, msg):
        if self.is_log_console:
            self.__logger_console.info(msg)
        if self.is_log_file:
            self.__logger_file.info(msg)
            self.__logger_file_error.info(msg)

    def warning(self, msg):
        if self.is_log_console:
            self.__logger_console.warning(msg)
        if self.is_log_file:
            self.__logger_file.warning(msg)
            self.__logger_file_error.warning(msg)

    def error(self, msg):
        if self.is_log_console:
            self.__logger_console.error(msg)
        if self.is_log_file:
            self.__logger_file.error(msg)
            self.__logger_file_error.error(msg)

    def critical(self, msg):
        if self.is_log_console:
            self.__logger_console.critical(msg)
        if self.is_log_file:
            self.__logger_file.critical(msg)
            self.__logger_file_error.critical(msg)

    def exception(self, msg):
        if self.is_log_console:
            self.__logger_console.exception(msg)
        if self.is_log_file:
            self.__logger_file.exception(msg)
            self.__logger_file_error.exception(msg)


log = Logger()

if __name__ == "__main__":
    log.info("Test me 1")
    log.info("Test me 2")
    log.info("Test me 3")
