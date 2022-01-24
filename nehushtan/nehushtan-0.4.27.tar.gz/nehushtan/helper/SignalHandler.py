import signal
from abc import abstractmethod
from typing import List


class SignalHandler:
    """
    Since 0.2.8

    If you use multi-threads, sub-processes inside shovel,
    you may need to catch the signal SIGTERM(15), which would be sent by Daemon
    to let all children die as soon as possible.
    By default, the parent process would finish when this signal comes,
    but children would not receive it and become orphaned.

    Usage
    Override this class and determine which signal(s) and a handle code block.
    The overrode class should be called in the `__init__` method of Shovel.

    See https://docs.python.org/zh-cn/3/library/signal.html?#signal.signal
    """

    @abstractmethod
    def get_target_signal_list(self) -> List[int]:
        """
        return a list of signal number, commonly use the defined constants
        signal.SIGTERM, etc.
        """
        pass

    @abstractmethod
    def handle_signal(self, signal_number, frame):
        pass

    def apply(self):
        signals = self.get_target_signal_list()
        for one_signal in signals:
            signal.signal(one_signal, self.handle_signal)

    def apply_default(self):
        signals = self.get_target_signal_list()
        for one_signal in signals:
            signal.signal(one_signal, signal.SIG_DFL)

    def apply_ignore(self):
        signals = self.get_target_signal_list()
        for one_signal in signals:
            signal.signal(one_signal, signal.SIG_IGN)
