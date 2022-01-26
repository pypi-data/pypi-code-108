import logging
import sys

from urllib3.connection import HTTPConnection

from pytestapilib.core.system import ProjectVariables


class LogProvider:
    @staticmethod
    def init_log(name: str) -> logging.Logger:
        __log_formatter = logging.Formatter(
            "%(asctime)s - %(threadName)-12.12s - %(processName)s - %(levelname)-5.5s - "
            "%(pathname)s.%(funcName)s.%(lineno)d - %(message)s")

        __stream_handler = logging.StreamHandler(sys.stdout)
        __stream_handler.setLevel(logging.DEBUG)
        __stream_handler.setFormatter(__log_formatter)

        __file_handler = logging.FileHandler("{0}/{1}.log".format(ProjectVariables.PROJECT_ROOT_DIR, 'main_log'))
        __file_handler.setLevel(logging.DEBUG)
        __file_handler.setFormatter(__log_formatter)

        HTTPConnection.debuglevel = 0

        logg = logging.getLogger(name)
        logg.setLevel(logging.DEBUG)

        logg.addHandler(__stream_handler)
        logg.addHandler(__file_handler)
        return logg


__log_urllib3 = LogProvider.init_log('urllib3')

log = LogProvider.init_log('main_log')
