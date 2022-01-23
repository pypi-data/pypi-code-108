import logging
import os
from colorama import Fore

class Logging:
        # logging.basicConfig(format="%{asctime}s - %{levelname}s - %{message}s", datefmt="%d-%b-%y %H:%M:%S",
        # level=logging.INFO, filename=os.path.join(path, fileName), filemode="a", style='{')

    def __init__(self, fileName: str, path: str) -> None:
        self.__logger = logging.getLogger(__name__)
        self.__fileHander = logging.FileHandler(os.path.join(path, fileName))
        self.__formatter = logging.Formatter("{asctime} - {levelname} - {name} - {message}", datefmt="%d-%b-%y %H:%M:%S", style="{")
        self.__fileHander.setFormatter(self.__formatter)
        self.__streamHander = logging.StreamHandler()
        self.__streamHander.setFormatter(self.__formatter)
        self.__logger.addHandler(self.__fileHander)
        self.__logger.setLevel(logging.DEBUG)
        self.__logger.addHandler(self.__streamHander)

    def printInfoLog(self, log: str) -> None:
        self.__logger.info(log)

    def printErrorLog(self, error: str) -> None:
        self.__logger.error(Fore.RED + error + Fore.RESET)

    def printWarningLog(self, warning: str) -> None:
        self.__logger.warning(warning)

    def printDebugLog(self, debug: str) -> None:
        self.__logger.debug(Fore.YELLOW + debug + Fore.RESET)

    def clearLogs(self, path: str) -> bool:
        pass
