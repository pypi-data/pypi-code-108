import os
import sys
import threading
import time
from multiprocessing import Queue
from queue import Empty

from .utils.utilities import remove_file


class ConsolePrinter(threading.Thread):

    """
    ConsolePrinter is a thread providing information of the current status of all concurrent simulations.
    """

    UPDATE: float = 1
    CUT_OFF_LENGTH: int = 120
    SPACES: int = 3
    FILE: str = os.getcwd() + '/' + 'progress.log'
    STOP_SIGNAL: str = 'STOP'
    REGISTER_SIGNAL: str = 'REGISTER'

    def __init__(self, queue: Queue):
        """
        Constructor of ConsolePrinter

        Parameters
        ----------
        queue :
            Multiprocessing queue exchanging information between concurrent processes

        """
        super().__init__()
        self.__output: dict = dict()
        self.__running: bool = True
        self.__registered: dict = dict()
        self.__file_writer = None
        self.__queue: Queue = queue
        remove_file(self.FILE)

    def register(self, name: str) -> None:
        """
        Register process with name

        Parameters
        ----------
        name :
            process name

        Returns
        -------

        """
        if name not in self.__registered.keys():
            self.__registered[name] = True
        # if self.not_started_yet:
            # self.__file_writer = open(self.FILE, mode='a+')
            # self.start()

    @property
    def not_started_yet(self) -> bool:
        return self.__registered.keys() and not self.is_alive() and self.__running

    def set(self, name: str, line: str) -> None:
        """
        Setting value for process name if process is registered

        Parameters
        ----------
        name :
            process name
        line :
            value to display for process

        Returns
        -------

        """
        if name in self.__registered.keys():
            if self.__registered[name]:
                self.__output[name] = line

    def stop(self, name) -> None:
        """
        Signals that ConsolePrinter is not used for process with 'name' anymore

        Parameters
        ----------
        name :
            name of process

        Returns
        -------

        """
        self.__registered[name] = False
        keys: [str] = list(self.__output.keys())
        if name in keys:
            del self.__output[name]
        stopping: bool = True
        for running in self.__registered.values():
            stopping = stopping and not running
        # if all threads are not running any more stopping stays true -> running = false!
        # This could stop further simulations from running since they have a blocking call for register and stop,
        # only if the first set of simulations finishes before the next simulations are registered.
        # Todo: Fix this! (MM)
        # self.__running = not stopping

    def stop_immediately(self) -> None:
        """
        Stops ConsolePrinter immediately for all (!) processes
        Returns
        -------

        """
        self.__running = False

    @property
    def max_key_length(self) -> int:
        """

        Returns
        -------
        int:
            maximal key length of all processes
        """
        max_length: int = 0
        for key in self.__output.keys():
            length: int = len(key)
            if length > max_length:
                max_length = length
        return max_length

    # Moving cursor and delete multiple lines does not work on windows. Hence, string gets cut off.
    # @staticmethod
    # def move_up(lines: str) -> None:
    #     for _ in range(lines.count('\n')):
    #         sys.stdout.write("\033[F")  # move cursor to the beginning of the previous line
    #         # sys.stdout.write('\b' * len(lines))  # Move back cursor
    #         # sys.stdout.write('\033[A')  # move cursor up one line
    #         # sys.stdout.write('\033[K')  # Clear line
    #         # sys.stdout.write('\x1b[A')  # Cursor up one line
    #         # sys.stdout.write('\x1b[1A\x1b[2K')
    #         # sys.stdout.flush()

    def cut_off(self, line: str) -> str:
        if len(line) > self.CUT_OFF_LENGTH:
            return line[:self.CUT_OFF_LENGTH] + ' ...'
        else:
            return line

    @property
    def line(self) -> str:
        line: str = '\r' # '\r'
        string_format: str = '{:'+str(self.max_key_length)+'s}'
        for key in self.__output.keys():
            line += '[' + string_format.format(key) + ': ' + self.__output[key] + ']' + ' ' * self.SPACES
        return self.cut_off(line) + ''

    @staticmethod
    def clear_screen():
        # os.system('cls' if os.name == 'nt' else 'clear')
        print('\n' * 10000)

    def update(self) -> None:
        try:
            while not self.__queue.empty():
                output: dict = self.__queue.get_nowait()
                items = output.items()
                for key, value in items:
                    if value == self.REGISTER_SIGNAL:
                        self.register(key)
                    elif value == self.STOP_SIGNAL:
                        self.stop(key)
                    else:
                        self.set(key, value)
        except Empty:
            return

    def run(self) -> None:
        while self.__running:
            # self.clear_screen()
            self.update()
            line: str = self.line
            # self.__file_writer.write(line)
            # self.__file_writer.flush()
            sys.stdout.write(line)
            sys.stdout.flush()
            # print(self.__queue.qsize())
            time.sleep(self.UPDATE)
        # self.__file_writer.close()
