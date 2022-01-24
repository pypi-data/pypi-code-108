__all__ = ["Null"]


from qtpy import QtWidgets, QtGui

from ._base import Base
from ._signals import Signals


class Widget(Signals, QtWidgets.QWidget):
    pass


class Null(Base):
    defaults = dict()
    defaults["value"] = None

    def _create_widget(self):
        return Widget()

    def on_updated(self, value: dict):
        pass
