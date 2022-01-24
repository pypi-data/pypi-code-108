from abc import abstractmethod

from nehushtan.logger.NehushtanFileLogger import NehushtanFileLogger


class NehushtanMPJob:
    """
    Since 0.2.13
    """

    def __init__(self, name: str):
        """
        Override this and extend the parameters
        Since 0.2.16, remove `logger`
        """
        self.__name = name
        self.__pid = 0

    def get_name(self):
        return self.__name

    @abstractmethod
    def get_logger(self) -> NehushtanFileLogger:
        """
        Since 0.2.16
        """
        pass

    def set_pid(self, pid: int):
        """
        Available in Main Process
        """
        self.__pid = pid
        return self

    def get_pid(self):
        """
        Available in Main Process
        """
        return self.__pid

    @abstractmethod
    def handle(self):
        """
        Run in sub process
        """
        pass

    def when_exited(self, exit_code: int):
        """
        Run in main process
        It is called when main process found worker process exited
        """
        pass
