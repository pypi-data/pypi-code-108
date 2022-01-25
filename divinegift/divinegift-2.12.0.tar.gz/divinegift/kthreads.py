from threading import Thread
import sys
from divinegift import logger
from divinegift.errors import KillException


class KThread(Thread):
    def __init__(self, *args, **keywords):
        Thread.__init__(self, *args, **keywords)
        self.killed = False

    def start(self):
        """Start the thread."""
        logger.log_warning(f'Thread {self.name} started')
        self.__run_backup = self.run
        self.run = self.__run    # Force the Thread to install our trace.
        Thread.start(self)

    def __run(self):
        """Hacked run function, which installs the
        trace."""
        sys.settrace(self.globaltrace)
        try:
            self.__run_backup()
        except KillException:
            pass
        logger.get_logger().log_warn(f'Thread {self.name} exited')
        self.run = self.__run_backup

    def globaltrace(self, frame, why, arg):
        if why == 'call':
            return self.localtrace
        else:
            return None

    def localtrace(self, frame, why, arg):
        if self.killed:
            if why == 'line':
                raise KillException()
        return self.localtrace

    def kill(self):
        logger.get_logger().log_warn(f'Thread {self.name} killed')
        self.killed = True
