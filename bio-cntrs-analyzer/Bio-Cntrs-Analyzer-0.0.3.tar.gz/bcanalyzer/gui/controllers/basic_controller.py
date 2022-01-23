
from abc import ABC, abstractmethod

from PyQt5.QtCore import pyqtSignal, QObject


class MetaAbstractView(type(ABC), type(QObject)):
    pass


class AbstractController(ABC, QObject, metaclass=MetaAbstractView):
    # signal to interact with other windows
    next_window_signal = pyqtSignal(int)

    @abstractmethod
    def run(self):
        raise NotImplementedError
